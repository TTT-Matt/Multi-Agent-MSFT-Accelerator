# src/backend/kernel_plugins/mcp_plugin.py
from typing import Annotated, Dict, List, Any, Optional
from semantic_kernel.functions import kernel_function
from semantic_kernel.kernel_pydantic import KernelBaseModel
from mcp import Client, StdioServerParameters, HttpServerParameters
import os
import logging
import json
import aiohttp

logger = logging.getLogger(__name__)

class MCPPlugin(KernelBaseModel):
    """Semantic Kernel plugin that wraps MCP server functionality with multiple transport types."""
    
    def __init__(self):
        super().__init__()
        self.mcp_clients: Dict[str, Client] = {}
        self._initialized = False
        self._http_session: Optional[aiohttp.ClientSession] = None
        
    async def initialize(self):
        """Initialize all MCP server connections."""
        if self._initialized:
            return
            
        try:
            # Create HTTP session for HTTP-based MCP servers
            self._http_session = aiohttp.ClientSession()
            
            # 1. Azure MCP Server (stdio)
            await self._init_azure_mcp_server()
            
            # 2. Microsoft Learn Docs MCP Server (HTTP)
            await self._init_docs_mcp_server()
            
            # 3. Custom WAF Assessment MCP Server (stdio)
            await self._init_waf_mcp_server()
            
            self._initialized = True
            logger.info("All MCP servers initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize MCP servers: {e}")
            raise
    
    async def _init_azure_mcp_server(self):
        """Initialize Azure MCP Server connection (stdio transport)."""
        try:
            azure_client = Client("azure-mcp-server", "stdio")
            await azure_client.initialize(StdioServerParameters(
                command="npx",
                args=["@microsoft/azure-mcp-server"],
                env={
                    "AZURE_SUBSCRIPTION_ID": os.getenv("AZURE_SUBSCRIPTION_ID"),
                    "AZURE_TENANT_ID": os.getenv("AZURE_TENANT_ID"),
                    "AZURE_CLIENT_ID": os.getenv("AZURE_CLIENT_ID"),
                    "AZURE_CLIENT_SECRET": os.getenv("AZURE_CLIENT_SECRET"),
                }
            ))
            self.mcp_clients['azure'] = azure_client
            logger.info("Azure MCP Server initialized (stdio)")
        except Exception as e:
            logger.error(f"Failed to initialize Azure MCP Server: {e}")
            
    async def _init_docs_mcp_server(self):
        """Initialize Microsoft Learn Docs MCP Server (HTTP transport)."""
        try:
            # Microsoft Learn Docs uses HTTP transport
            docs_client = Client("ms-learn-docs", "http")
            
            # Configure HTTP parameters
            docs_url = os.getenv("MS_LEARN_DOCS_MCP_URL", "https://learn.microsoft.com/api/mcp")
            
            await docs_client.initialize(HttpServerParameters(
                url=docs_url,
                headers={
                    "Authorization": f"Bearer {os.getenv('MS_LEARN_API_KEY', '')}",
                    "Content-Type": "application/json"
                },
                session=self._http_session
            ))
            
            self.mcp_clients['docs'] = docs_client
            logger.info(f"Microsoft Learn Docs MCP Server initialized (HTTP) at {docs_url}")
        except Exception as e:
            logger.error(f"Failed to initialize Docs MCP Server: {e}")
            
    async def _init_waf_mcp_server(self):
        """Initialize custom WAF Assessment MCP Server (stdio transport)."""
        try:
            waf_client = Client("waf-assessment", "stdio")
            await waf_client.initialize(StdioServerParameters(
                command="python",
                args=["-m", "waf_assessment_server"],
                env={"PYTHONPATH": os.path.dirname(os.path.abspath(__file__))}
            ))
            self.mcp_clients['waf'] = waf_client
            logger.info("WAF Assessment MCP Server initialized (stdio)")
        except Exception as e:
            logger.warning(f"Failed to initialize WAF MCP Server: {e}")
    
    # ========== Azure Resource Operations (stdio) ==========
    
    @kernel_function(
        name="query_azure_resources",
        description="Query Azure resources using Resource Graph via MCP"
    )
    async def query_azure_resources(
        self,
        query: Annotated[str, "KQL query for Azure Resource Graph"],
        subscription_id: Annotated[Optional[str], "Optional subscription ID filter"] = None,
        resource_group: Annotated[Optional[str], "Optional resource group filter"] = None
    ) -> str:
        """Execute Azure Resource Graph query through MCP."""
        try:
            client = self.mcp_clients.get('azure')
            if not client:
                return json.dumps({"error": "Azure MCP client not initialized"})
            
            args = {"query": query}
            if subscription_id:
                args["subscription_id"] = subscription_id
            if resource_group:
                args["resource_group"] = resource_group
                
            result = await client.call_tool("resource_graph_query", args)
            return json.dumps(result)
            
        except Exception as e:
            logger.error(f"Resource Graph query failed: {e}")
            return json.dumps({"error": str(e)})
    
    # ========== Documentation and Best Practices (HTTP) ==========
    
    @kernel_function(
        name="get_waf_guidance",
        description="Get WAF guidance from Microsoft Learn documentation"
    )
    async def get_waf_guidance(
        self,
        resource_type: Annotated[str, "Azure resource type (e.g., Microsoft.Storage/storageAccounts)"],
        waf_pillars: Annotated[List[str], "WAF pillars to focus on"] = None
    ) -> str:
        """Get WAF best practices for a resource type via HTTP MCP server."""
        try:
            client = self.mcp_clients.get('docs')
            if not client:
                # Try direct HTTP call as fallback
                return await self._direct_http_docs_query(resource_type, waf_pillars)
            
            if waf_pillars is None:
                waf_pillars = ["reliability", "security", "cost-optimization", 
                             "operational-excellence", "performance-efficiency"]
                
            result = await client.call_tool(
                "search_waf_docs",
                {
                    "query": f"Well-Architected Framework {resource_type}",
                    "pillars": waf_pillars,
                    "include_examples": True,
                    "language": "en-us"
                }
            )
            return json.dumps(result)
            
        except Exception as e:
            logger.error(f"Docs query failed: {e}")
            return json.dumps({"error": str(e)})
    
    async def _direct_http_docs_query(self, resource_type: str, pillars: List[str]) -> str:
        """Direct HTTP query to MS Learn API as fallback."""
        if not self._http_session:
            return json.dumps({"error": "HTTP session not initialized"})
            
        try:
            url = f"{os.getenv('MS_LEARN_API_URL', 'https://learn.microsoft.com/api/search')}"
            headers = {
                "Authorization": f"Bearer {os.getenv('MS_LEARN_API_KEY', '')}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "search": f"Well-Architected Framework {resource_type}",
                "filter": "product eq 'azure' and category eq 'architecture'",
                "facets": ["pillar"],
                "top": 10
            }
            
            async with self._http_session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return json.dumps({"results": data})
                else:
                    return json.dumps({"error": f"HTTP {response.status}"})
                    
        except Exception as e:
            logger.error(f"Direct HTTP query failed: {e}")
            return json.dumps({"error": str(e)})
    
    @kernel_function(
        name="search_azure_docs",
        description="Search Microsoft Learn documentation for Azure guidance"
    )
    async def search_azure_docs(
        self,
        query: Annotated[str, "Search query for documentation"],
        service: Annotated[Optional[str], "Specific Azure service to filter"] = None,
        doc_type: Annotated[Optional[str], "Type of documentation (tutorial, how-to, reference)"] = None,
        limit: Annotated[int, "Maximum number of results"] = 10
    ) -> str:
        """Search Azure documentation via HTTP MCP server."""
        try:
            client = self.mcp_clients.get('docs')
            if not client:
                return json.dumps({"error": "Docs MCP client not initialized"})
                
            args = {
                "query": query,
                "limit": limit,
                "locale": "en-us"
            }
            if service:
                args["service"] = service
            if doc_type:
                args["doc_type"] = doc_type
                
            result = await client.call_tool("search_docs", args)
            return json.dumps(result)
            
        except Exception as e:
            logger.error(f"Docs search failed: {e}")
            return json.dumps({"error": str(e)})
    
    @kernel_function(
        name="get_resource_specific_guidance",
        description="Get specific WAF guidance for a particular Azure resource"
    )
    async def get_resource_specific_guidance(
        self,
        resource_id: Annotated[str, "Full Azure resource ID"],
        focus_areas: Annotated[List[str], "Specific areas to focus on"] = None
    ) -> str:
        """Get resource-specific guidance by combining resource info with docs."""
        try:
            # First, get resource details from Azure
            resource_json = await self.get_resource_configuration(resource_id)
            resource_data = json.loads(resource_json)
            
            if "error" in resource_data:
                return resource_json
                
            # Extract resource type and properties
            resource_type = resource_data.get("type", "")
            resource_name = resource_data.get("name", "")
            
            # Then get specific guidance from docs
            docs_client = self.mcp_clients.get('docs')
            if docs_client:
                result = await docs_client.call_tool(
                    "get_resource_guidance",
                    {
                        "resource_type": resource_type,
                        "resource_properties": resource_data.get("properties", {}),
                        "focus_areas": focus_areas or ["security", "performance", "cost"],
                        "include_remediation": True
                    }
                )
                return json.dumps(result)
            else:
                # Fallback to general guidance
                return await self.get_waf_guidance(resource_type)
                
        except Exception as e:
            logger.error(f"Failed to get resource-specific guidance: {e}")
            return json.dumps({"error": str(e)})
    
    # ========== Mixed Transport Operations ==========
    
    @kernel_function(
        name="assess_resource_compliance",
        description="Assess a resource's compliance with WAF best practices"
    )
    async def assess_resource_compliance(
        self,
        resource_id: Annotated[str, "Full Azure resource ID"],
        pillars: Annotated[List[str], "WAF pillars to assess"] = None
    ) -> str:
        """Assess resource compliance by combining data from multiple MCP servers."""
        try:
            # Get resource config from Azure (stdio)
            config_json = await self.get_resource_configuration(resource_id)
            config = json.loads(config_json)
            
            if "error" in config:
                return config_json
                
            resource_type = config.get("type", "")
            
            # Get best practices from docs (HTTP)
            practices_json = await self.get_waf_guidance(resource_type, pillars)
            practices = json.loads(practices_json)
            
            # Calculate compliance score (stdio or local)
            waf_client = self.mcp_clients.get('waf')
            if waf_client:
                result = await waf_client.call_tool(
                    "assess_compliance",
                    {
                        "resource_config": config,
                        "best_practices": practices,
                        "pillars": pillars or ["all"]
                    }
                )
                return json.dumps(result)
            else:
                # Local compliance calculation
                return self._calculate_local_compliance(config, practices, pillars)
                
        except Exception as e:
            logger.error(f"Compliance assessment failed: {e}")
            return json.dumps({"error": str(e)})
    
    def _calculate_local_compliance(self, config: Dict, practices: Dict, pillars: List[str]) -> str:
        """Calculate compliance score locally."""
        # Simple compliance scoring logic
        score = 0
        findings = []
        
        # Example: Check for common compliance issues
        if config.get("type", "").lower().contains("storage"):
            if config.get("properties", {}).get("allowBlobPublicAccess", True):
                findings.append({
                    "pillar": "security",
                    "issue": "Public blob access enabled",
                    "severity": "high"
                })
            else:
                score += 20
                
        return json.dumps({
            "score": score,
            "max_score": 100,
            "findings": findings,
            "pillars_assessed": pillars or ["all"]
        })
    
    async def cleanup(self):
        """Cleanup MCP connections and HTTP session."""
        # Close all MCP clients
        for server_name, client in self.mcp_clients.items():
            try:
                await client.shutdown()
                logger.info(f"Shut down MCP server: {server_name}")
            except Exception as e:
                logger.error(f"Error shutting down {server_name}: {e}")
        
        # Close HTTP session
        if self._http_session:
            await self._http_session.close()
            
        self.mcp_clients.clear()
        self._initialized = False