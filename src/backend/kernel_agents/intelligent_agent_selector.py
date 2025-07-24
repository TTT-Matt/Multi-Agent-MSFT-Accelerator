# src/backend/kernel_agents/intelligent_agent_selector.py

from typing import Dict, List, Set, Optional, Tuple
from models.agent_categories import ExtendedAgentType
import logging

logger = logging.getLogger(__name__)


class IntelligentAgentSelector:
    """Automatically selects the right agents based on discovered resources."""
    
    def __init__(self):
        # Complete agent mapping based on the provided table
        self.agent_mapping = {
            # Core Infrastructure
            "Microsoft.Compute/virtualMachines": ExtendedAgentType.VM_ASSESSMENT,
            "Microsoft.Compute/virtualMachineScaleSets": ExtendedAgentType.VM_ASSESSMENT,
            "Microsoft.ContainerService/managedClusters": ExtendedAgentType.AKS_ASSESSMENT,
            "Microsoft.Web/sites": ExtendedAgentType.APP_SERVICE_ASSESSMENT,  # Note: Functions handled separately
            "Microsoft.Web/serverFarms": ExtendedAgentType.APP_SERVICE_ASSESSMENT,
            "Microsoft.ContainerInstance/containerGroups": ExtendedAgentType.CONTAINER_INSTANCES_ASSESSMENT,
            "Microsoft.Storage/storageAccounts": ExtendedAgentType.STORAGE_ASSESSMENT,
            "Microsoft.Compute/disks": ExtendedAgentType.MANAGED_DISKS_ASSESSMENT,
            "Microsoft.Storage/storageAccounts/fileServices/shares": ExtendedAgentType.FILE_SHARES_ASSESSMENT,
            "Microsoft.Network/virtualNetworks": ExtendedAgentType.VNET_ASSESSMENT,
            "Microsoft.Network/networkSecurityGroups": ExtendedAgentType.NSG_ASSESSMENT,
            "Microsoft.Network/loadBalancers": ExtendedAgentType.LOAD_BALANCER_ASSESSMENT,
            "Microsoft.Network/applicationGateways": ExtendedAgentType.APP_GATEWAY_ASSESSMENT,
            "Microsoft.Network/azureFirewalls": ExtendedAgentType.FIREWALL_ASSESSMENT,
            "Microsoft.Sql/servers": ExtendedAgentType.SQL_ASSESSMENT,
            "Microsoft.DocumentDB/databaseAccounts": ExtendedAgentType.COSMOS_DB_ASSESSMENT,
            
            # Developer & DevOps
            "Microsoft.DevOps/pipelines": ExtendedAgentType.DEVOPS_ASSESSMENT,
            "Microsoft.ApiManagement/service": ExtendedAgentType.API_MANAGEMENT_ASSESSMENT,
            "Microsoft.ContainerRegistry/registries": ExtendedAgentType.CONTAINER_REGISTRY_ASSESSMENT,
            "Microsoft.Logic/workflows": ExtendedAgentType.LOGIC_APPS_ASSESSMENT,
            "Microsoft.ServiceBus/namespaces": ExtendedAgentType.SERVICE_BUS_ASSESSMENT,
            "Microsoft.EventGrid/topics": ExtendedAgentType.EVENT_GRID_ASSESSMENT,
            "Microsoft.EventGrid/domains": ExtendedAgentType.EVENT_GRID_ASSESSMENT,
            
            # Data & Analytics
            "Microsoft.Synapse/workspaces": ExtendedAgentType.SYNAPSE_ASSESSMENT,
            "Microsoft.DataFactory/factories": ExtendedAgentType.DATA_FACTORY_ASSESSMENT,
            "Microsoft.Databricks/workspaces": ExtendedAgentType.DATABRICKS_ASSESSMENT,
            "Microsoft.HDInsight/clusters": ExtendedAgentType.HDINSIGHT_ASSESSMENT,
            "Microsoft.EventHub/namespaces": ExtendedAgentType.EVENT_HUBS_ASSESSMENT,
            "Microsoft.StreamAnalytics/streamingjobs": ExtendedAgentType.STREAM_ANALYTICS_ASSESSMENT,
            "Microsoft.Devices/IotHubs": ExtendedAgentType.IOT_HUB_ASSESSMENT,
            "Microsoft.DataLakeStore/accounts": ExtendedAgentType.DATA_LAKE_ASSESSMENT,
            "Microsoft.DataLakeAnalytics/accounts": ExtendedAgentType.DATA_LAKE_ASSESSMENT,
            "Microsoft.Kusto/clusters": ExtendedAgentType.DATA_EXPLORER_ASSESSMENT,
            
            # Security & Identity
            "Microsoft.AAD/domainServices": ExtendedAgentType.AZURE_AD_ASSESSMENT,
            "Microsoft.AzureActiveDirectory/b2cDirectories": ExtendedAgentType.B2C_ASSESSMENT,
            "Microsoft.ManagedIdentity/userAssignedIdentities": ExtendedAgentType.MANAGED_IDENTITY_ASSESSMENT,
            "Microsoft.KeyVault/vaults": ExtendedAgentType.KEY_VAULT_ASSESSMENT,
            "Microsoft.Security/pricings": ExtendedAgentType.DEFENDER_ASSESSMENT,
            "Microsoft.Security/securityStandards": ExtendedAgentType.DEFENDER_ASSESSMENT,
            "Microsoft.SecurityInsights/alertRules": ExtendedAgentType.SENTINEL_ASSESSMENT,
            "Microsoft.Network/ddosProtectionPlans": ExtendedAgentType.DDOS_PROTECTION_ASSESSMENT,
            "Microsoft.Authorization/policyDefinitions": ExtendedAgentType.POLICY_ASSESSMENT,
            
            # Monitoring & Management
            "Microsoft.OperationalInsights/workspaces": ExtendedAgentType.LOG_ANALYTICS_ASSESSMENT,
            "Microsoft.Insights/components": ExtendedAgentType.APP_INSIGHTS_ASSESSMENT,
            "Microsoft.Insights/metricAlerts": ExtendedAgentType.MONITOR_ASSESSMENT,
            "Microsoft.Insights/actionGroups": ExtendedAgentType.MONITOR_ASSESSMENT,
            "Microsoft.Automation/automationAccounts": ExtendedAgentType.AUTOMATION_ASSESSMENT,
            "Microsoft.CostManagement/exports": ExtendedAgentType.COST_MANAGEMENT_ASSESSMENT,
            "Microsoft.CostManagement/budgets": ExtendedAgentType.COST_MANAGEMENT_ASSESSMENT,
            
            # AI & Cognitive
            "Microsoft.MachineLearningServices/workspaces": ExtendedAgentType.MACHINE_LEARNING_ASSESSMENT,
            "Microsoft.CognitiveServices/accounts": ExtendedAgentType.COGNITIVE_SERVICES_ASSESSMENT,
            "Microsoft.BotService/botServices": ExtendedAgentType.BOT_SERVICE_ASSESSMENT,
            "Microsoft.Search/searchServices": ExtendedAgentType.COGNITIVE_SEARCH_ASSESSMENT,
        }
        
        # Complete agent capabilities based on the provided table
        self.agent_capabilities = {
            # Core Infrastructure
            ExtendedAgentType.VM_ASSESSMENT: {
                "checks": ["security", "performance", "cost", "availability"],
                "related_resources": ["disks", "nics", "nsg"],
                "execution_time": 30,
                "priority": 1
            },
            ExtendedAgentType.AKS_ASSESSMENT: {
                "checks": ["security", "scalability", "networking", "cost"],
                "related_resources": ["acr", "keyvault", "log_analytics"],
                "execution_time": 120,
                "priority": 1
            },
            ExtendedAgentType.APP_SERVICE_ASSESSMENT: {
                "checks": ["security", "performance", "cost", "scalability"],
                "related_resources": ["storage", "database", "app_insights"],
                "execution_time": 45,
                "priority": 1
            },
            ExtendedAgentType.FUNCTIONS_ASSESSMENT: {
                "checks": ["security", "performance", "cost", "scalability"],
                "related_resources": ["storage", "app_insights", "service_bus"],
                "execution_time": 40,
                "priority": 2
            },
            ExtendedAgentType.CONTAINER_INSTANCES_ASSESSMENT: {
                "checks": ["security", "performance", "cost", "availability"],
                "related_resources": ["acr", "vnet", "nsg"],
                "execution_time": 60,
                "priority": 2
            },
            ExtendedAgentType.STORAGE_ASSESSMENT: {
                "checks": ["security", "performance", "cost", "availability"],
                "related_resources": ["blobs", "files", "queues"],
                "execution_time": 30,
                "priority": 1
            },
            ExtendedAgentType.MANAGED_DISKS_ASSESSMENT: {
                "checks": ["performance", "cost", "availability", "redundancy"],
                "related_resources": ["vms", "snapshots"],
                "execution_time": 20,
                "priority": 2
            },
            ExtendedAgentType.FILE_SHARES_ASSESSMENT: {
                "checks": ["security", "performance", "cost", "sharing"],
                "related_resources": ["storage_accounts", "vnet"],
                "execution_time": 25,
                "priority": 2
            },
            ExtendedAgentType.VNET_ASSESSMENT: {
                "checks": ["security", "networking", "cost", "connectivity"],
                "related_resources": ["subnets", "nsg", "load_balancers"],
                "execution_time": 40,
                "priority": 1
            },
            ExtendedAgentType.NSG_ASSESSMENT: {
                "checks": ["security", "compliance", "networking"],
                "related_resources": ["vnets", "vms", "subnets"],
                "execution_time": 30,
                "priority": 1
            },
            ExtendedAgentType.LOAD_BALANCER_ASSESSMENT: {
                "checks": ["performance", "availability", "cost", "scalability"],
                "related_resources": ["backends", "health_probes"],
                "execution_time": 50,
                "priority": 1
            },
            ExtendedAgentType.APP_GATEWAY_ASSESSMENT: {
                "checks": ["security", "performance", "cost", "waf"],
                "related_resources": ["backends", "ssl", "vnet"],
                "execution_time": 60,
                "priority": 1
            },
            ExtendedAgentType.FIREWALL_ASSESSMENT: {
                "checks": ["security", "networking", "cost", "rules"],
                "related_resources": ["vnet", "policies", "logs"],
                "execution_time": 70,
                "priority": 1
            },
            ExtendedAgentType.SQL_ASSESSMENT: {
                "checks": ["security", "performance", "cost", "backup"],
                "related_resources": ["databases", "firewalls", "vnet"],
                "execution_time": 50,
                "priority": 1
            },
            ExtendedAgentType.COSMOS_DB_ASSESSMENT: {
                "checks": ["security", "performance", "cost", "scalability"],
                "related_resources": ["containers", "throughput", "backups"],
                "execution_time": 55,
                "priority": 1
            },
            
            # Developer & DevOps
            ExtendedAgentType.DEVOPS_ASSESSMENT: {
                "checks": ["compliance", "performance", "cost", "integration"],
                "related_resources": ["repos", "artifacts", "builds"],
                "execution_time": 60,
                "priority": 2
            },
            ExtendedAgentType.API_MANAGEMENT_ASSESSMENT: {
                "checks": ["security", "performance", "cost", "api_versioning"],
                "related_resources": ["gateways", "backends", "policies"],
                "execution_time": 70,
                "priority": 1
            },
            ExtendedAgentType.CONTAINER_REGISTRY_ASSESSMENT: {
                "checks": ["security", "compliance", "cost", "vulnerability_scans"],
                "related_resources": ["images", "repositories", "tasks"],
                "execution_time": 50,
                "priority": 1
            },
            ExtendedAgentType.LOGIC_APPS_ASSESSMENT: {
                "checks": ["performance", "cost", "integration", "error_handling"],
                "related_resources": ["connectors", "runs", "triggers"],
                "execution_time": 40,
                "priority": 2
            },
            ExtendedAgentType.SERVICE_BUS_ASSESSMENT: {
                "checks": ["security", "performance", "cost", "messaging"],
                "related_resources": ["queues", "topics", "subscriptions"],
                "execution_time": 45,
                "priority": 1
            },
            ExtendedAgentType.EVENT_GRID_ASSESSMENT: {
                "checks": ["performance", "cost", "event_delivery", "reliability"],
                "related_resources": ["subscriptions", "domains", "topics"],
                "execution_time": 50,
                "priority": 2
            },
            ExtendedAgentType.GIT_REPOS_ASSESSMENT: {
                "checks": ["security", "compliance", "branching", "code_quality"],
                "related_resources": ["pipelines", "pulls", "branches"],
                "execution_time": 30,
                "priority": 2
            },
            ExtendedAgentType.ARTIFACTS_ASSESSMENT: {
                "checks": ["compliance", "versioning", "cost", "dependencies"],
                "related_resources": ["feeds", "packages", "pipelines"],
                "execution_time": 35,
                "priority": 2
            },
            
            # Data & Analytics
            ExtendedAgentType.SYNAPSE_ASSESSMENT: {
                "checks": ["security", "performance", "cost", "data_integration"],
                "related_resources": ["pools", "pipelines", "datasets"],
                "execution_time": 90,
                "priority": 1
            },
            ExtendedAgentType.DATA_FACTORY_ASSESSMENT: {
                "checks": ["compliance", "performance", "cost", "pipelines"],
                "related_resources": ["datasets", "linked_services", "triggers"],
                "execution_time": 80,
                "priority": 1
            },
            ExtendedAgentType.DATABRICKS_ASSESSMENT: {
                "checks": ["security", "cost", "scalability", "clusters"],
                "related_resources": ["jobs", "notebooks", "clusters"],
                "execution_time": 100,
                "priority": 1
            },
            ExtendedAgentType.HDINSIGHT_ASSESSMENT: {
                "checks": ["performance", "cost", "availability", "hadoop_components"],
                "related_resources": ["nodes", "storage", "jobs"],
                "execution_time": 120,
                "priority": 2
            },
            ExtendedAgentType.EVENT_HUBS_ASSESSMENT: {
                "checks": ["security", "performance", "cost", "throughput"],
                "related_resources": ["clusters", "namespaces", "hubs"],
                "execution_time": 60,
                "priority": 1
            },
            ExtendedAgentType.STREAM_ANALYTICS_ASSESSMENT: {
                "checks": ["performance", "cost", "streaming", "error_handling"],
                "related_resources": ["inputs", "outputs", "queries"],
                "execution_time": 70,
                "priority": 2
            },
            ExtendedAgentType.IOT_HUB_ASSESSMENT: {
                "checks": ["security", "scalability", "cost", "device_management"],
                "related_resources": ["devices", "endpoints", "routes"],
                "execution_time": 80,
                "priority": 1
            },
            ExtendedAgentType.DATA_LAKE_ASSESSMENT: {
                "checks": ["security", "performance", "cost", "data_ingestion"],
                "related_resources": ["stores", "jobs", "catalogs"],
                "execution_time": 90,
                "priority": 2
            },
            ExtendedAgentType.BLOB_ANALYTICS_ASSESSMENT: {
                "checks": ["performance", "cost", "analytics", "logging"],
                "related_resources": ["blobs", "diagnostics", "metrics"],
                "execution_time": 40,
                "priority": 2
            },
            ExtendedAgentType.DATA_EXPLORER_ASSESSMENT: {
                "checks": ["security", "performance", "cost", "querying"],
                "related_resources": ["databases", "tables", "clusters"],
                "execution_time": 75,
                "priority": 1
            },
            
            # Security & Identity
            ExtendedAgentType.AZURE_AD_ASSESSMENT: {
                "checks": ["security", "compliance", "identity", "access"],
                "related_resources": ["users", "groups", "domains"],
                "execution_time": 50,
                "priority": 1
            },
            ExtendedAgentType.B2C_ASSESSMENT: {
                "checks": ["security", "identity", "authentication", "user_flows"],
                "related_resources": ["tenants", "policies", "apps"],
                "execution_time": 60,
                "priority": 1
            },
            ExtendedAgentType.MANAGED_IDENTITY_ASSESSMENT: {
                "checks": ["security", "compliance", "access_control"],
                "related_resources": ["roles", "assignments", "principals"],
                "execution_time": 30,
                "priority": 2
            },
            ExtendedAgentType.KEY_VAULT_ASSESSMENT: {
                "checks": ["security", "compliance", "secrets_management", "encryption"],
                "related_resources": ["keys", "secrets", "certificates"],
                "execution_time": 40,
                "priority": 1
            },
            ExtendedAgentType.DEFENDER_ASSESSMENT: {
                "checks": ["security", "threat_protection", "compliance", "alerts"],
                "related_resources": ["subscriptions", "resources", "recommendations"],
                "execution_time": 90,
                "priority": 1
            },
            ExtendedAgentType.SENTINEL_ASSESSMENT: {
                "checks": ["security", "incident_response", "analytics", "hunting"],
                "related_resources": ["workspaces", "rules", "incidents"],
                "execution_time": 100,
                "priority": 1
            },
            ExtendedAgentType.DDOS_PROTECTION_ASSESSMENT: {
                "checks": ["security", "network_protection", "cost", "mitigation"],
                "related_resources": ["vnets", "public_ips", "logs"],
                "execution_time": 70,
                "priority": 1
            },
            ExtendedAgentType.POLICY_ASSESSMENT: {
                "checks": ["compliance", "governance", "auditing", "enforcement"],
                "related_resources": ["assignments", "definitions", "scopes"],
                "execution_time": 50,
                "priority": 1
            },
            
            # Monitoring & Management
            ExtendedAgentType.LOG_ANALYTICS_ASSESSMENT: {
                "checks": ["performance", "cost", "querying", "data_ingestion"],
                "related_resources": ["solutions", "saved_searches", "agents"],
                "execution_time": 60,
                "priority": 1
            },
            ExtendedAgentType.APP_INSIGHTS_ASSESSMENT: {
                "checks": ["performance", "availability", "user_analytics", "alerts"],
                "related_resources": ["metrics", "logs", "dependencies"],
                "execution_time": 50,
                "priority": 1
            },
            ExtendedAgentType.MONITOR_ASSESSMENT: {
                "checks": ["monitoring", "alerting", "diagnostics", "metrics"],
                "related_resources": ["resources", "logs", "alerts"],
                "execution_time": 40,
                "priority": 1
            },
            ExtendedAgentType.AUTOMATION_ASSESSMENT: {
                "checks": ["automation", "compliance", "runbooks", "schedules"],
                "related_resources": ["runbooks", "variables", "modules"],
                "execution_time": 70,
                "priority": 2
            },
            ExtendedAgentType.UPDATE_MANAGEMENT_ASSESSMENT: {
                "checks": ["compliance", "patching", "security", "updates"],
                "related_resources": ["machines", "schedules", "deployments"],
                "execution_time": 80,
                "priority": 1
            },
            ExtendedAgentType.COST_MANAGEMENT_ASSESSMENT: {
                "checks": ["cost", "budgeting", "forecasting", "optimization"],
                "related_resources": ["scopes", "queries", "views"],
                "execution_time": 50,
                "priority": 2
            },
            
            # AI & Cognitive
            ExtendedAgentType.MACHINE_LEARNING_ASSESSMENT: {
                "checks": ["security", "performance", "cost", "model_training"],
                "related_resources": ["experiments", "models", "endpoints"],
                "execution_time": 90,
                "priority": 1
            },
            ExtendedAgentType.COGNITIVE_SERVICES_ASSESSMENT: {
                "checks": ["security", "compliance", "cost", "api_usage"],
                "related_resources": ["keys", "endpoints", "models"],
                "execution_time": 60,
                "priority": 1
            },
            ExtendedAgentType.BOT_SERVICE_ASSESSMENT: {
                "checks": ["performance", "cost", "integration", "channels"],
                "related_resources": ["channels", "dialogs", "endpoints"],
                "execution_time": 50,
                "priority": 2
            },
            ExtendedAgentType.COGNITIVE_SEARCH_ASSESSMENT: {
                "checks": ["performance", "cost", "indexing", "querying"],
                "related_resources": ["indexes", "skillsets", "data_sources"],
                "execution_time": 70,
                "priority": 1
            },
            ExtendedAgentType.FORM_RECOGNIZER_ASSESSMENT: {
                "checks": ["security", "accuracy", "cost", "document_processing"],
                "related_resources": ["models", "endpoints", "datasets"],
                "execution_time": 60,
                "priority": 2
            }
        }
        
        # Special resource handlers for edge cases
        self.special_handlers = {
            "function_app_detection": self._is_function_app,
            "form_recognizer_detection": self._is_form_recognizer,
            "devops_resource_detection": self._is_devops_resource,
            "blob_analytics_detection": self._needs_blob_analytics,
            "update_management_detection": self._needs_update_management
        }
    
    def select_agents_for_resources(self, resources: List[Dict]) -> Dict[str, List[str]]:
        """Group resources by their specialized agents with intelligent batching."""
        agent_assignments = {}
        resource_graph = self.build_resource_dependency_graph(resources)
        
        for resource in resources:
            resource_type = resource.get("type")
            resource_id = resource.get("id")
            
            # Handle special cases first
            agent_type = self._get_agent_for_special_cases(resource)
            
            # If no special case, use standard mapping
            if not agent_type:
                agent_type = self.agent_mapping.get(resource_type)
            
            if agent_type:
                if agent_type not in agent_assignments:
                    agent_assignments[agent_type] = {
                        "resources": [],
                        "priority": self.agent_capabilities[agent_type]["priority"],
                        "estimated_time": 0,
                        "dependencies": set(),
                        "checks": self.agent_capabilities[agent_type]["checks"]
                    }
                
                agent_assignments[agent_type]["resources"].append(resource_id)
                # Add time per resource (not cumulative for parallel execution)
                agent_assignments[agent_type]["estimated_time"] = max(
                    agent_assignments[agent_type]["estimated_time"],
                    self.agent_capabilities[agent_type]["execution_time"]
                )
                
                # Add dependent resources
                deps = resource_graph.get_dependencies(resource_id)
                agent_assignments[agent_type]["dependencies"].update(deps)
            else:
                # Fall back to generic assessment
                self.assign_to_generic_agent(resource, agent_assignments)
                logger.warning(f"No specific agent for resource type: {resource_type}")
        
        return self.optimize_execution_plan(agent_assignments)
    
    def _get_agent_for_special_cases(self, resource: Dict) -> Optional[ExtendedAgentType]:
        """Handle special cases where resource type alone isn't enough to determine the agent."""
        resource_type = resource.get("type")
        
        # Function Apps are Microsoft.Web/sites with kind: functionapp
        if resource_type == "Microsoft.Web/sites" and self._is_function_app(resource):
            return ExtendedAgentType.FUNCTIONS_ASSESSMENT
        
        # Form Recognizer is CognitiveServices with kind: FormRecognizer
        if resource_type == "Microsoft.CognitiveServices/accounts" and self._is_form_recognizer(resource):
            return ExtendedAgentType.FORM_RECOGNIZER_ASSESSMENT
        
        # Storage accounts might need blob analytics
        if resource_type == "Microsoft.Storage/storageAccounts" and self._needs_blob_analytics(resource):
            # Return both storage and blob analytics agents
            # This would be handled in a more sophisticated way in production
            pass
        
        return None
    
    def _is_function_app(self, resource: Dict) -> bool:
        """Check if a Web/sites resource is actually a Function App."""
        return resource.get("kind", "").lower().startswith("functionapp")
    
    def _is_form_recognizer(self, resource: Dict) -> bool:
        """Check if a CognitiveServices account is Form Recognizer."""
        return resource.get("kind", "").lower() == "formrecognizer"
    
    def _is_devops_resource(self, resource: Dict) -> bool:
        """Check if resource is related to Azure DevOps (might need special handling)."""
        # Azure DevOps resources might not show up in ARM
        # This would check tags or other indicators
        tags = resource.get("tags", {})
        return "devops" in tags or "azdo" in tags
    
    def _needs_blob_analytics(self, resource: Dict) -> bool:
        """Check if storage account has blob analytics enabled."""
        properties = resource.get("properties", {})
        return properties.get("blobAnalyticsLoggingEnabled", False)
    
    def _needs_update_management(self, resource: Dict) -> bool:
        """Check if resource needs update management assessment."""
        # Could check tags or properties
        tags = resource.get("tags", {})
        return tags.get("updateManagement", "").lower() == "enabled"
    
    def build_resource_dependency_graph(self, resources: List[Dict]) -> 'ResourceDependencyGraph':
        """Build a graph of resource dependencies for intelligent execution."""
        graph = ResourceDependencyGraph()
        
        for resource in resources:
            resource_id = resource.get("id")
            resource_type = resource.get("type")
            
            # Add resource to graph
            graph.add_resource(resource_id, resource_type)
            
            # Extract dependencies from properties
            properties = resource.get("properties", {})
            
            # Common dependency patterns
            if resource_type == "Microsoft.Web/sites":
                # App Service depends on App Service Plan
                if "serverFarmId" in properties:
                    graph.add_dependency(resource_id, properties["serverFarmId"])
                    
            elif resource_type == "Microsoft.Compute/virtualMachines":
                # VM depends on NICs, disks
                if "networkProfile" in properties:
                    for nic in properties.get("networkProfile", {}).get("networkInterfaces", []):
                        graph.add_dependency(resource_id, nic.get("id"))
                        
            # Add more dependency patterns...
        
        return graph
    
    def optimize_execution_plan(self, assignments: Dict) -> Dict:
        """Optimize for parallel execution while respecting dependencies."""
        # Group by priority and dependencies
        priority_1_no_deps = {}
        priority_1_with_deps = {}
        priority_2_no_deps = {}
        priority_2_with_deps = {}
        
        for agent_type, details in assignments.items():
            if details["priority"] == 1:
                if not details["dependencies"]:
                    priority_1_no_deps[agent_type] = details
                else:
                    priority_1_with_deps[agent_type] = details
            else:
                if not details["dependencies"]:
                    priority_2_no_deps[agent_type] = details
                else:
                    priority_2_with_deps[agent_type] = details
        
        # Calculate total execution time (considering parallelization)
        wave1_time = max([d["estimated_time"] for d in priority_1_no_deps.values()], default=0)
        wave2_time = max([d["estimated_time"] for d in priority_1_with_deps.values()], default=0)
        wave3_time = max([d["estimated_time"] for d in priority_2_no_deps.values()], default=0)
        wave4_time = max([d["estimated_time"] for d in priority_2_with_deps.values()], default=0)
        
        return {
            "execution_waves": [
                {"wave": 1, "agents": priority_1_no_deps, "estimated_time": wave1_time},
                {"wave": 2, "agents": priority_1_with_deps, "estimated_time": wave2_time},
                {"wave": 3, "agents": priority_2_no_deps, "estimated_time": wave3_time},
                {"wave": 4, "agents": priority_2_with_deps, "estimated_time": wave4_time}
            ],
            "total_agents": len(assignments),
            "total_resources": sum(len(d["resources"]) for d in assignments.values()),
            "estimated_total_time": wave1_time + wave2_time + wave3_time + wave4_time,
            "parallelization_efficiency": self.calculate_parallelization_efficiency(assignments)
        }
    
    def calculate_parallelization_efficiency(self, assignments: Dict) -> float:
        """Calculate how well the assessment can be parallelized."""
        total_sequential_time = sum(d["estimated_time"] for d in assignments.values())
        
        # Get times for each priority level
        p1_times = [d["estimated_time"] for d in assignments.values() if d["priority"] == 1]
        p2_times = [d["estimated_time"] for d in assignments.values() if d["priority"] == 2]
        
        # Parallel time is max of each priority level
        parallel_time = max(p1_times, default=0) + max(p2_times, default=0)
        
        if total_sequential_time == 0:
            return 1.0
        
        return 1 - (parallel_time / total_sequential_time)
    
    def assign_to_generic_agent(self, resource: Dict, agent_assignments: Dict):
        """Assign resources without specific agents to a generic assessment agent."""
        generic_type = ExtendedAgentType.GENERIC_RESOURCE_ASSESSMENT
        
        if generic_type not in agent_assignments:
            agent_assignments[generic_type] = {
                "resources": [],
                "priority": 3,  # Lower priority
                "estimated_time": 30,  # Generic assessment time
                "dependencies": set(),
                "checks": ["basic_security", "basic_cost", "basic_compliance"]
            }
        
        agent_assignments[generic_type]["resources"].append(resource.get("id"))


class ResourceDependencyGraph:
    """Simple dependency graph for resources."""
    
    def __init__(self):
        self.resources = {}
        self.dependencies = {}
    
    def add_resource(self, resource_id: str, resource_type: str):
        """Add a resource to the graph."""
        self.resources[resource_id] = {
            "type": resource_type,
            "depends_on": set(),
            "depended_by": set()
        }
    
    def add_dependency(self, resource_id: str, depends_on: str):
        """Add a dependency relationship."""
        if resource_id in self.resources and depends_on:
            self.resources[resource_id]["depends_on"].add(depends_on)
            
            if depends_on in self.resources:
                self.resources[depends_on]["depended_by"].add(resource_id)
    
    def get_dependencies(self, resource_id: str) -> Set[str]:
        """Get all dependencies for a resource."""
        if resource_id in self.resources:
            return self.resources[resource_id]["depends_on"]
        return set()