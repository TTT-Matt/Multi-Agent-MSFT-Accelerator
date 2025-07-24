from enum import Enum

class AgentCategory(str, Enum):
    """Categories for organizing assessment agents."""
    CORE_INFRASTRUCTURE = "core_infrastructure"
    DEVELOPER_DEVOPS = "developer_devops"
    DATA_ANALYTICS = "data_analytics"
    SECURITY_IDENTITY = "security_identity"
    MONITORING_MANAGEMENT = "monitoring_management"
    AI_COGNITIVE = "ai_cognitive"

class ExtendedAgentType(str, Enum):
    """All 50+ agent types."""
    
    # Core Infrastructure (15 agents)
    VM_ASSESSMENT = "VM_Assessment_Agent"
    AKS_ASSESSMENT = "AKS_Assessment_Agent"
    APP_SERVICE_ASSESSMENT = "App_Service_Assessment_Agent"
    FUNCTIONS_ASSESSMENT = "Functions_Assessment_Agent"
    CONTAINER_INSTANCES_ASSESSMENT = "Container_Instances_Assessment_Agent"
    STORAGE_ASSESSMENT = "Storage_Assessment_Agent"
    MANAGED_DISKS_ASSESSMENT = "Managed_Disks_Assessment_Agent"
    FILE_SHARES_ASSESSMENT = "File_Shares_Assessment_Agent"
    VNET_ASSESSMENT = "VNet_Assessment_Agent"
    NSG_ASSESSMENT = "NSG_Assessment_Agent"
    LOAD_BALANCER_ASSESSMENT = "Load_Balancer_Assessment_Agent"
    APP_GATEWAY_ASSESSMENT = "App_Gateway_Assessment_Agent"
    FIREWALL_ASSESSMENT = "Firewall_Assessment_Agent"
    SQL_ASSESSMENT = "SQL_Assessment_Agent"
    COSMOS_DB_ASSESSMENT = "Cosmos_DB_Assessment_Agent"
    
    # Developer & DevOps (8 agents)
    DEVOPS_ASSESSMENT = "DevOps_Assessment_Agent"
    API_MANAGEMENT_ASSESSMENT = "API_Management_Assessment_Agent"
    CONTAINER_REGISTRY_ASSESSMENT = "Container_Registry_Assessment_Agent"
    LOGIC_APPS_ASSESSMENT = "Logic_Apps_Assessment_Agent"
    SERVICE_BUS_ASSESSMENT = "Service_Bus_Assessment_Agent"
    EVENT_GRID_ASSESSMENT = "Event_Grid_Assessment_Agent"
    GIT_REPOS_ASSESSMENT = "Git_Repos_Assessment_Agent"
    ARTIFACTS_ASSESSMENT = "Artifacts_Assessment_Agent"
    
    # Data & Analytics (10 agents)
    SYNAPSE_ASSESSMENT = "Synapse_Assessment_Agent"
    DATA_FACTORY_ASSESSMENT = "Data_Factory_Assessment_Agent"
    DATABRICKS_ASSESSMENT = "Databricks_Assessment_Agent"
    HDINSIGHT_ASSESSMENT = "HDInsight_Assessment_Agent"
    EVENT_HUBS_ASSESSMENT = "Event_Hubs_Assessment_Agent"
    STREAM_ANALYTICS_ASSESSMENT = "Stream_Analytics_Assessment_Agent"
    IOT_HUB_ASSESSMENT = "IoT_Hub_Assessment_Agent"
    DATA_LAKE_ASSESSMENT = "Data_Lake_Assessment_Agent"
    BLOB_ANALYTICS_ASSESSMENT = "Blob_Analytics_Assessment_Agent"
    DATA_EXPLORER_ASSESSMENT = "Data_Explorer_Assessment_Agent"
    
    # Security & Identity (8 agents)
    AZURE_AD_ASSESSMENT = "Azure_AD_Assessment_Agent"
    B2C_ASSESSMENT = "B2C_Assessment_Agent"
    MANAGED_IDENTITY_ASSESSMENT = "Managed_Identity_Assessment_Agent"
    KEY_VAULT_ASSESSMENT = "Key_Vault_Assessment_Agent"
    DEFENDER_ASSESSMENT = "Defender_Assessment_Agent"
    SENTINEL_ASSESSMENT = "Sentinel_Assessment_Agent"
    DDOS_PROTECTION_ASSESSMENT = "DDoS_Protection_Assessment_Agent"
    POLICY_ASSESSMENT = "Policy_Assessment_Agent"
    
    # Monitoring & Management (6 agents)
    LOG_ANALYTICS_ASSESSMENT = "Log_Analytics_Assessment_Agent"
    APP_INSIGHTS_ASSESSMENT = "App_Insights_Assessment_Agent"
    MONITOR_ASSESSMENT = "Monitor_Assessment_Agent"
    AUTOMATION_ASSESSMENT = "Automation_Assessment_Agent"
    UPDATE_MANAGEMENT_ASSESSMENT = "Update_Management_Assessment_Agent"
    COST_MANAGEMENT_ASSESSMENT = "Cost_Management_Assessment_Agent"
    
    # AI & Cognitive (5 agents)
    MACHINE_LEARNING_ASSESSMENT = "Machine_Learning_Assessment_Agent"
    COGNITIVE_SERVICES_ASSESSMENT = "Cognitive_Services_Assessment_Agent"
    BOT_SERVICE_ASSESSMENT = "Bot_Service_Assessment_Agent"
    COGNITIVE_SEARCH_ASSESSMENT = "Cognitive_Search_Assessment_Agent"
    FORM_RECOGNIZER_ASSESSMENT = "Form_Recognizer_Assessment_Agent"