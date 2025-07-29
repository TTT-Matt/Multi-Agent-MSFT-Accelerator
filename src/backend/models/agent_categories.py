from enum import Enum

class AgentType(str, Enum):
    """Agent types for WAF assessment"""
    
    # Core Assessment Agents
    PLANNER = "Assessment_Planner_Agent"
    COMPUTE = "Compute_Assessment_Agent"  # VMs, AKS, App Service, Functions, etc.
    STORAGE = "Storage_Assessment_Agent"  # All storage types
    NETWORKING = "Networking_Assessment_Agent"  # VNets, NSGs, LBs, Gateways, etc.
    DATA = "Data_Assessment_Agent"  # SQL, Cosmos, Synapse, Data Factory, etc.
    SECURITY = "Security_Assessment_Agent"  # KeyVault, Identity, Defender, etc.
    MONITORING = "Monitoring_Assessment_Agent"  # Log Analytics, App Insights, etc.
    INTEGRATION = "Integration_Assessment_Agent"  # Logic Apps, Service Bus, API Management
    AI_COGNITIVE = "AI_Cognitive_Assessment_Agent"  # ML, Cognitive Services, etc.
    
    # Special Purpose Agents
    CROSS_RESOURCE = "Cross_Resource_Correlation_Agent"
    COST_OPTIMIZATION = "Cost_Optimization_Agent"