# src/backend/kernel_agents/mcp_enhanced_base_agent.py
from typing import Optional, List, Dict, Any
from kernel_agents.agent_base import BaseAgent
from kernel_plugins.mcp_plugin import MCPPlugin
from semantic_kernel import Kernel
import json
import logging

logger = logging.getLogger(__name__)

class MCPEnhancedBaseAgent(BaseAgent):
    """Base agent enhanced with MCP capabilities."""
    
    def __init__(self, *args, **kwargs):
        # Extract MCP plugin if provided
        self.mcp_plugin: Optional[MCPPlugin] = kwargs.pop('mcp_plugin', None)
        super().__init__(*args, **kwargs)
        
    async def setup_mcp_tools(self, kernel: Kernel):
        """Add MCP plugin to the agent's kernel."""
        if self.mcp_plugin and hasattr(self, '_kernel'):
            self._kernel.add_plugin(self.mcp_plugin, "mcp")
            logger.info(f"MCP plugin added to {self._agent_name}")
    
    async def query_azure_resources(self, query: str, subscription_ids: List[str] = None) -> List[Dict]:
        """Query Azure resources using MCP Server."""
        if not self.mcp_plugin:
            logger.error("MCP plugin not available")
            return []
            
        try:
            # Use MCP plugin to query resources
            result_json = await self.mcp_plugin.query_azure_resources(
                query=query,
                subscription_id=subscription_ids[0] if subscription_ids else None
            )
            
            result = json.loads(result_json)
            if "error" in result:
                logger.error(f"MCP query error: {result['error']}")
                return []
                
            # Extract data from result
            return result.get("data", [])
            
        except Exception as e:
            logger.error(f"Failed to query resources via MCP: {e}")
            return []
    
    async def get_resource_details(self, resource_id: str) -> Dict:
        """Get detailed resource information using MCP."""
        if not self.mcp_plugin:
            logger.error("MCP plugin not available")
            return {}
            
        try:
            result_json = await self.mcp_plugin.get_resource_details(resource_id)
            result = json.loads(result_json)
            
            if "error" in result:
                logger.error(f"MCP error getting resource details: {result['error']}")
                return {}
                
            return result
            
        except Exception as e:
            logger.error(f"Failed to get resource details via MCP: {e}")
            return {}
    
    async def execute_azure_cli_command(self, command: str) -> Dict:
        """Execute Azure CLI command via MCP."""
        if not self.mcp_plugin:
            logger.error("MCP plugin not available")
            return {"error": "MCP plugin not available"}
            
        try:
            result_json = await self.mcp_plugin.execute_azure_cli(command)
            return json.loads(result_json)
            
        except Exception as e:
            logger.error(f"Failed to execute CLI command via MCP: {e}")
            return {"error": str(e)}
    
    async def get_waf_best_practices(self, resource_type: str, pillars: List[str] = None) -> Dict:
        """Get WAF best practices using MCP plugin."""
        if not self.mcp_plugin:
            logger.warning("MCP plugin not available")
            return {}
            
        try:
            # Search for WAF guidance
            search_query = f"Well-Architected Framework {resource_type}"
            if pillars:
                search_query += f" {' '.join(pillars)}"
                
            result_json = await self.mcp_plugin.search_learn_docs(
                query=search_query,
                limit=5
            )
            
            result = json.loads(result_json)
            if "error" in result:
                logger.error(f"MCP docs error: {result['error']}")
                return {}
                
            return result
            
        except Exception as e:
            logger.error(f"Failed to get WAF guidance: {e}")
            return {}