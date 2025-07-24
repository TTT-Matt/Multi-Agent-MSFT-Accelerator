
from kernel_agents.agent_base import BaseAgent
from kernel_agents.intelligent_agent_selector import IntelligentAgentSelector
from kernel_agents.cross_agent_intelligence import CrossAgentIntelligence

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
        
        # Set default system message if not provided
        if not system_message:
            system_message = self.default_system_message(agent_name)
        
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
            logging.info("Initializing AzureAssessmentPlannerAgent")

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
            logging.error(f"Failed to create AzureAssessmentPlannerAgent: {e}")
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
    
    async def create_assessment_plan(self, scope: str, assessment_type: str) -> Plan:
        """Create an intelligent assessment plan based on discovered resources."""
        
        # Step 1: Resource Discovery
        resources = await self.discover_azure_resources(scope)
        logger.info(f"Discovered {len(resources)} resources")
        
        # Step 2: Intelligent Agent Selection
        agent_assignments = self.agent_selector.select_agents_for_resources(resources)
        logger.info(f"Selected {len(agent_assignments)} specialized agents")
        
        # Step 3: Create Optimized Execution Plan
        plan = self.create_parallel_execution_plan(agent_assignments)
        
        # Step 4: Add Cross-Resource Analysis Steps
        plan.add_correlation_step(self.cross_agent_intelligence)
        
        return plan
    
    async def discover_azure_resources(self, scope: str) -> List[Dict]:
        """Use Azure Resource Graph to discover all resources."""
        query = """
        Resources
        | where subscriptionId =~ '{subscription}'
        | project id, name, type, resourceGroup, location, tags, properties
        """
        # Execute via MCP
        return await self.mcp_client.execute_resource_graph_query(query)