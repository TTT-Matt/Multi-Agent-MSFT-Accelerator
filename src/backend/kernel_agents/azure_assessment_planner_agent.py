# src/backend/kernel_agents/azure_assessment_planner_agent.py

import logging
import json
from typing import Dict, List, Optional, Set
from datetime import datetime

from context.cosmos_memory_kernel import CosmosMemoryContext
from kernel_agents.agent_base import BaseAgent
from kernel_agents.intelligent_agent_selector import IntelligentAgentSelector
from kernel_agents.cross_agent_intelligence import CrossAgentIntelligence
from models.messages_kernel import AgentType, Plan, Step, StepStatus
from semantic_kernel.functions import KernelFunction, kernel_function
from semantic_kernel.kernel_pydantic import KernelBaseModel

logger = logging.getLogger(__name__)


class AzureMCPClient:
    """Client for interacting with Azure MCP servers."""
    
    async def execute_az_command(self, command: str) -> Dict:
        """Execute an Azure CLI command via MCP server."""
        # This would integrate with your actual MCP server
        # For now, showing the structure
        try:
            # In production:
            # result = await mcp_docker.azmcp_extension_az(command=command)
            logger.info(f"Executing Azure CLI command: az {command}")
            
            # Simulated response structure
            return {
                "success": True,
                "result": {},
                "error": None
            }
        except Exception as e:
            logger.error(f"Azure CLI command failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def execute_resource_graph_query(self, query: str, subscription_id: str = None) -> List[Dict]:
        """Execute an Azure Resource Graph query."""
        try:
            # Format the query command
            command = f"graph query -q \"{query}\""
            if subscription_id:
                command += f" --subscription {subscription_id}"
            
            result = await self.execute_az_command(command)
            
            if result["success"]:
                return result.get("result", {}).get("data", [])
            else:
                logger.error(f"Resource Graph query failed: {result['error']}")
                return []
                
        except Exception as e:
            logger.error(f"Resource Graph query failed: {e}")
            return []


class AssessmentPlan(KernelBaseModel):
    """Represents an assessment execution plan."""
    plan_id: str
    session_id: str
    user_id: str
    scope: str
    assessment_type: str
    execution_waves: List[Dict]
    total_agents: int
    total_resources: int
    estimated_total_time: int
    created_at: datetime
    correlation_step_added: bool = False
    
    def add_correlation_step(self, cross_agent_intelligence):
        """Add a cross-resource correlation analysis step."""
        correlation_step = {
            "wave": len(self.execution_waves) + 1,
            "agents": {
                "CrossResourceAnalysis": {
                    "agent_type": "correlation_analysis",
                    "resources": ["all"],
                    "priority": 1,
                    "estimated_time": 60,
                    "dependencies": self._get_all_previous_agents(),
                    "intelligence": cross_agent_intelligence
                }
            },
            "estimated_time": 60,
            "description": "Analyze findings across all resources for cross-resource issues"
        }
        self.execution_waves.append(correlation_step)
        self.correlation_step_added = True
    
    def _get_all_previous_agents(self) -> Set[str]:
        """Get all agents from previous waves for dependency tracking."""
        all_agents = set()
        for wave in self.execution_waves:
            for agent_type in wave.get("agents", {}).keys():
                all_agents.add(agent_type)
        return all_agents


class AzureAssessmentPlannerAgent(BaseAgent):
    """Enhanced planner that discovers resources and orchestrates specialized agents."""
    
    def __init__(
        self,
        session_id: str,
        user_id: str,
        memory_store: CosmosMemoryContext,
        tools: Optional[List[KernelFunction]] = None,
        system_message: Optional[str] = None,
        agent_name: str = "Azure_Assessment_Planner_Agent",
        client=None,
        definition=None,
        **kwargs
    ):
        # Initialize specialized components
        self.agent_selector = IntelligentAgentSelector()
        self.cross_agent_intelligence = CrossAgentIntelligence()
        self.mcp_client = AzureMCPClient()
        
        # Set default system message if not provided
        if not system_message:
            system_message = self.default_system_message(agent_name)
        
        # Initialize tools if not provided
        if not tools:
            tools = self._get_planner_tools()
        
        super().__init__(
            agent_name=agent_name,
            session_id=session_id,
            user_id=user_id,
            memory_store=memory_store,
            tools=tools,
            system_message=system_message,
            client=client,
            definition=definition
        )
    
    def _get_planner_tools(self) -> List[KernelFunction]:
        """Get the planning-specific tools."""
        tools = []
        
        # Add all methods decorated with @kernel_function
        for method_name in dir(self):
            method = getattr(self, method_name)
            if hasattr(method, '_kernel_function_metadata'):
                tools.append(method)
        
        return tools
    
    @classmethod
    async def create(cls, **kwargs) -> 'AzureAssessmentPlannerAgent':
        """Asynchronously create the AzureAssessmentPlannerAgent."""
        session_id = kwargs.get("session_id")
        user_id = kwargs.get("user_id")
        memory_store = kwargs.get("memory_store")
        tools = kwargs.get("tools", None)
        system_message = kwargs.get("system_message", None)
        agent_name = kwargs.get("agent_name", "Azure_Assessment_Planner_Agent")
        client = kwargs.get("client")

        try:
            logger.info("Initializing AzureAssessmentPlannerAgent")

            # Create the Azure AI Agent definition
            agent_definition = await cls._create_azure_ai_agent_definition(
                agent_name=agent_name,
                instructions=system_message or cls.default_system_message(agent_name),
                temperature=0.0,
                response_format=None,
            )

            return cls(
                session_id=session_id,
                user_id=user_id,
                memory_store=memory_store,
                tools=tools,
                system_message=system_message,
                agent_name=agent_name,
                client=client,
                definition=agent_definition,
            )

        except Exception as e:
            logger.error(f"Failed to create AzureAssessmentPlannerAgent: {e}")
            raise
    
    @staticmethod
    def default_system_message(agent_name=None) -> str:
        """Get the default system message for the agent."""
        return """You are an Azure Assessment Planning Specialist that orchestrates comprehensive assessments of Azure environments. Your role is to:

1. **Discover Resources**: Use Azure Resource Graph to find all resources in the specified scope
2. **Select Appropriate Agents**: Based on resource types, intelligently select specialized assessment agents
3. **Create Execution Plans**: Organize agents for optimal parallel execution
4. **Coordinate Assessment**: Ensure all resources are properly assessed
5. **Identify Cross-Resource Issues**: Look for problems that span multiple resources

You have access to 50+ specialized assessment agents covering:
- Core Infrastructure (VMs, Storage, Networking, Databases)
- Developer & DevOps (Pipelines, Registries, API Management)
- Data & Analytics (Synapse, Data Factory, Event Hubs)
- Security & Identity (Key Vault, Azure AD, Defender)
- Monitoring & Management (Log Analytics, Cost Management)
- AI & Cognitive Services (ML, Cognitive Services, Bot Service)

Always create comprehensive assessment plans that maximize parallel execution while respecting dependencies."""
    
    @kernel_function(
        name="create_assessment_plan",
        description="Create a comprehensive assessment plan for Azure resources"
    )
    async def create_assessment_plan(self, scope: str, assessment_type: str = "comprehensive") -> str:
        """Create an intelligent assessment plan based on discovered resources."""
        
        logger.info(f"Creating assessment plan for scope: {scope}, type: {assessment_type}")
        
        try:
            # Step 1: Resource Discovery
            resources = await self.discover_azure_resources(scope)
            logger.info(f"Discovered {len(resources)} resources")
            
            if not resources:
                return "No resources found in the specified scope. Please check the scope and try again."
            
            # Step 2: Intelligent Agent Selection
            execution_plan = self.agent_selector.select_agents_for_resources(resources)
            logger.info(f"Selected agents and created execution plan")
            
            # Step 3: Create Assessment Plan object
            plan = self.create_parallel_execution_plan(
                scope=scope,
                assessment_type=assessment_type,
                execution_plan=execution_plan
            )
            
            # Step 4: Add Cross-Resource Analysis Step
            plan.add_correlation_step(self.cross_agent_intelligence)
            
            # Step 5: Store plan in memory
            await self.memory_store.save_plan(plan)
            
            # Step 6: Format response
            return self._format_plan_response(plan, resources)
            
        except Exception as e:
            logger.error(f"Failed to create assessment plan: {e}")
            return f"Error creating assessment plan: {str(e)}"
    
    @kernel_function(
        name="discover_resources",
        description="Discover Azure resources in a given scope"
    )
    async def discover_azure_resources(self, scope: str) -> List[Dict]:
        """Use Azure Resource Graph to discover all resources."""
        
        # Parse scope (subscription, resource group, etc.)
        subscription_id = None
        resource_group = None
        
        if scope.startswith("/subscriptions/"):
            parts = scope.split("/")
            if len(parts) >= 3:
                subscription_id = parts[2]
            if len(parts) >= 5 and parts[3] == "resourceGroups":
                resource_group = parts[4]
        else:
            # Assume it's just a subscription ID or resource group name
            if scope.lower().startswith("sub-") or len(scope) == 36:
                subscription_id = scope
            else:
                resource_group = scope
        
        # Build Resource Graph query
        if resource_group:
            query = f"""
            Resources
            | where resourceGroup =~ '{resource_group}'
            | project id, name, type, resourceGroup, location, tags, properties, kind, sku
            | order by type asc, name asc
            """
        else:
            query = """
            Resources
            | project id, name, type, resourceGroup, location, tags, properties, kind, sku
            | order by type asc, name asc
            """
        
        # Execute query
        resources = await self.mcp_client.execute_resource_graph_query(query, subscription_id)
        
        # Enrich resources with additional metadata
        for resource in resources:
            resource["assessmentMetadata"] = {
                "discovered_at": datetime.utcnow().isoformat(),
                "requires_assessment": True,
                "assessment_priority": self._calculate_resource_priority(resource)
            }
        
        return resources
    
    def create_parallel_execution_plan(self, scope: str, assessment_type: str, execution_plan: Dict) -> AssessmentPlan:
        """Create an optimized execution plan from agent assignments."""
        
        plan_id = f"plan-{self.session_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        # Extract execution waves from the intelligent selector's output
        execution_waves = execution_plan.get("execution_waves", [])
        
        # Create the assessment plan
        plan = AssessmentPlan(
            plan_id=plan_id,
            session_id=self.session_id,
            user_id=self.user_id,
            scope=scope,
            assessment_type=assessment_type,
            execution_waves=execution_waves,
            total_agents=execution_plan.get("total_agents", 0),
            total_resources=execution_plan.get("total_resources", 0),
            estimated_total_time=execution_plan.get("estimated_total_time", 0),
            created_at=datetime.utcnow()
        )
        
        return plan
    
    def _calculate_resource_priority(self, resource: Dict) -> int:
        """Calculate assessment priority for a resource (1-10)."""
        priority = 5  # Default
        
        resource_type = resource.get("type", "").lower()
        
        # Critical infrastructure gets higher priority
        if any(critical in resource_type for critical in ["keyvault", "sql", "cosmos", "storage"]):
            priority += 2
        
        # Public-facing resources get higher priority
        if any(public in resource_type for public in ["publicip", "loadbalancer", "applicationgateway", "frontdoor"]):
            priority += 2
        
        # Security-related resources
        if any(security in resource_type for security in ["firewall", "nsg", "waf"]):
            priority += 1
        
        # Production resources (based on tags)
        tags = resource.get("tags", {})
        if tags.get("environment", "").lower() in ["prod", "production"]:
            priority += 2
        
        return min(priority, 10)
    
    def _format_plan_response(self, plan: AssessmentPlan, resources: List[Dict]) -> str:
        """Format the assessment plan for user display."""
        
        # Group resources by type for summary
        resource_summary = {}
        for resource in resources:
            rtype = resource.get("type", "Unknown")
            resource_summary[rtype] = resource_summary.get(rtype, 0) + 1
        
        response = f"""
🎯 **Azure Assessment Plan Created**

**Plan ID**: {plan.plan_id}
**Scope**: {plan.scope}
**Assessment Type**: {plan.assessment_type}

📊 **Resource Discovery Summary**:
- Total Resources: {plan.total_resources}
- Resource Types: {len(resource_summary)}
- Specialized Agents Selected: {plan.total_agents}

📋 **Top Resource Types**:
"""
        # Show top 5 resource types
        for rtype, count in sorted(resource_summary.items(), key=lambda x: x[1], reverse=True)[:5]:
            response += f"- {rtype}: {count}\n"
        
        response += f"""
⚡ **Execution Strategy**:
- Execution Waves: {len(plan.execution_waves)}
- Estimated Total Time: {plan.estimated_total_time} seconds
- Parallelization: {len(plan.execution_waves[0]['agents']) if plan.execution_waves else 0} agents in first wave

🔄 **Execution Waves**:
"""
        for i, wave in enumerate(plan.execution_waves, 1):
            agents = wave.get("agents", {})
            response += f"\n**Wave {i}** ({wave.get('estimated_time', 0)}s):\n"
            for agent_type, details in list(agents.items())[:3]:  # Show first 3 agents
                resource_count = len(details.get("resources", []))
                response += f"  - {agent_type}: {resource_count} resources\n"
            if len(agents) > 3:
                response += f"  - ... and {len(agents) - 3} more agents\n"
        
        response += """
✅ **Next Steps**:
1. Review the plan details
2. Execute the assessment with `run_assessment`
3. Monitor progress in real-time
4. Review comprehensive findings report

Would you like to proceed with the assessment?
"""
        
        return response
    
    @kernel_function(
        name="list_available_agents",
        description="List all available assessment agents and their capabilities"
    )
    async def list_available_agents(self) -> str:
        """List all available assessment agents."""
        
        # Get all agent capabilities from the selector
        capabilities = self.agent_selector.agent_capabilities
        
        response = "🤖 **Available Azure Assessment Agents**\n\n"
        
        # Group by category
        categories = {
            "Core Infrastructure": [],
            "Developer & DevOps": [],
            "Data & Analytics": [],
            "Security & Identity": [],
            "Monitoring & Management": [],
            "AI & Cognitive": []
        }
        
        # Map agents to categories (simplified - in production, this would be more sophisticated)
        for agent_type, caps in capabilities.items():
            agent_name = agent_type.value if hasattr(agent_type, 'value') else str(agent_type)
            
            if any(x in agent_name.lower() for x in ["vm", "storage", "network", "sql", "cosmos"]):
                category = "Core Infrastructure"
            elif any(x in agent_name.lower() for x in ["devops", "api", "container_registry", "logic"]):
                category = "Developer & DevOps"
            elif any(x in agent_name.lower() for x in ["synapse", "data", "event", "stream"]):
                category = "Data & Analytics"
            elif any(x in agent_name.lower() for x in ["security", "identity", "key", "defender"]):
                category = "Security & Identity"
            elif any(x in agent_name.lower() for x in ["monitor", "log", "cost", "automation"]):
                category = "Monitoring & Management"
            else:
                category = "AI & Cognitive"
            
            categories[category].append({
                "name": agent_name,
                "checks": caps.get("checks", []),
                "execution_time": caps.get("execution_time", 0)
            })
        
        # Format response
        for category, agents in categories.items():
            if agents:
                response += f"**{category}** ({len(agents)} agents):\n"
                for agent in agents[:3]:  # Show first 3
                    checks = ", ".join(agent["checks"][:3])
                    response += f"  • {agent['name']} - {checks} ({agent['execution_time']}s)\n"
                if len(agents) > 3:
                    response += f"  • ... and {len(agents) - 3} more\n"
                response += "\n"
        
        response += f"\n**Total Agents Available**: {len(capabilities)}"
        
        return response