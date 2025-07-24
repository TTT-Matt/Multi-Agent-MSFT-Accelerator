# src/backend/kernel_agents/cross_agent_intelligence.py

class CrossAgentIntelligence:
    """Enables agents to share insights and identify cross-resource issues."""
    
    def __init__(self):
        self.resource_relationships = {
            # Core Infrastructure - Compute
            "Microsoft.Compute/virtualMachines": {
                "depends_on": [
                    "Microsoft.Network/networkInterfaces",
                    "Microsoft.Compute/disks",
                    "Microsoft.Network/virtualNetworks",
                    "Microsoft.Network/networkSecurityGroups",
                    "Microsoft.Storage/storageAccounts",  # For diagnostics
                    "Microsoft.KeyVault/vaults"  # For disk encryption keys
                ],
                "impacts": [
                    "Microsoft.Network/loadBalancers",
                    "Microsoft.Network/applicationGateways",
                    "Microsoft.Compute/availabilitySets",
                    "Microsoft.RecoveryServices/vaults"  # Backup
                ]
            },
            
            "Microsoft.Compute/virtualMachineScaleSets": {
                "depends_on": [
                    "Microsoft.Network/virtualNetworks",
                    "Microsoft.Network/loadBalancers",
                    "Microsoft.Compute/images",
                    "Microsoft.Storage/storageAccounts"
                ],
                "impacts": [
                    "Microsoft.Insights/autoscaleSettings",
                    "Microsoft.Network/applicationGateways"
                ]
            },
            
            # Web & Apps
            "Microsoft.Web/sites": {
                "depends_on": [
                    "Microsoft.Web/serverfarms",  # App Service Plan
                    "Microsoft.Sql/servers",
                    "Microsoft.Storage/storageAccounts",
                    "Microsoft.DocumentDB/databaseAccounts",  # Cosmos DB
                    "Microsoft.Cache/Redis",
                    "Microsoft.KeyVault/vaults",
                    "Microsoft.ServiceBus/namespaces",
                    "Microsoft.EventHub/namespaces"
                ],
                "impacts": [
                    "Microsoft.Cdn/profiles",
                    "Microsoft.Network/applicationGateways",
                    "Microsoft.Network/frontDoors",
                    "Microsoft.ApiManagement/service",
                    "Microsoft.Insights/components"  # App Insights
                ]
            },
            
            "Microsoft.Web/serverFarms": {
                "depends_on": [
                    "Microsoft.Network/virtualNetworks"  # For VNet integration
                ],
                "impacts": [
                    "Microsoft.Web/sites",
                    "Microsoft.Web/sites/slots"
                ]
            },
            
            # Containers
            "Microsoft.ContainerService/managedClusters": {
                "depends_on": [
                    "Microsoft.Network/virtualNetworks",
                    "Microsoft.ContainerRegistry/registries",
                    "Microsoft.KeyVault/vaults",
                    "Microsoft.ManagedIdentity/userAssignedIdentities",
                    "Microsoft.OperationalInsights/workspaces",  # For monitoring
                    "Microsoft.Storage/storageAccounts"  # For persistent volumes
                ],
                "impacts": [
                    "Microsoft.Network/loadBalancers",
                    "Microsoft.Network/publicIPAddresses",
                    "Microsoft.Network/applicationGateways",
                    "Microsoft.Monitor/accounts"
                ]
            },
            
            "Microsoft.ContainerRegistry/registries": {
                "depends_on": [
                    "Microsoft.Storage/storageAccounts",
                    "Microsoft.KeyVault/vaults"  # For encryption
                ],
                "impacts": [
                    "Microsoft.ContainerService/managedClusters",
                    "Microsoft.Web/sites",  # Web apps using containers
                    "Microsoft.ContainerInstance/containerGroups"
                ]
            },
            
            "Microsoft.ContainerInstance/containerGroups": {
                "depends_on": [
                    "Microsoft.ContainerRegistry/registries",
                    "Microsoft.Network/virtualNetworks",
                    "Microsoft.Storage/storageAccounts"
                ],
                "impacts": []
            },
            
            # Storage
            "Microsoft.Storage/storageAccounts": {
                "depends_on": [
                    "Microsoft.Network/virtualNetworks",  # For service endpoints
                    "Microsoft.KeyVault/vaults"  # For encryption keys
                ],
                "impacts": [
                    "Microsoft.Compute/virtualMachines",  # Boot diagnostics
                    "Microsoft.Web/sites",  # Static content, logs
                    "Microsoft.Sql/servers",  # Backup storage
                    "Microsoft.DataFactory/factories",  # Data storage
                    "Microsoft.StreamAnalytics/streamingjobs",  # Output
                    "Microsoft.Media/mediaservices"
                ]
            },
            
            "Microsoft.Compute/disks": {
                "depends_on": [
                    "Microsoft.KeyVault/vaults"  # For encryption
                ],
                "impacts": [
                    "Microsoft.Compute/virtualMachines",
                    "Microsoft.Compute/snapshots"
                ]
            },
            
            # Networking
            "Microsoft.Network/virtualNetworks": {
                "depends_on": [
                    "Microsoft.Network/networkSecurityGroups",
                    "Microsoft.Network/routeTables"
                ],
                "impacts": [
                    "Microsoft.Compute/virtualMachines",
                    "Microsoft.Web/sites",
                    "Microsoft.ContainerService/managedClusters",
                    "Microsoft.Sql/servers",
                    "Microsoft.Network/privateEndpoints",
                    "Microsoft.Network/applicationGateways",
                    "Microsoft.Network/loadBalancers",
                    "Microsoft.Network/vpnGateways"
                ]
            },
            
            "Microsoft.Network/networkSecurityGroups": {
                "depends_on": [],
                "impacts": [
                    "Microsoft.Network/networkInterfaces",
                    "Microsoft.Network/virtualNetworks/subnets",
                    "Microsoft.Compute/virtualMachines"
                ]
            },
            
            "Microsoft.Network/loadBalancers": {
                "depends_on": [
                    "Microsoft.Network/virtualNetworks",
                    "Microsoft.Network/publicIPAddresses"
                ],
                "impacts": [
                    "Microsoft.Compute/virtualMachines",
                    "Microsoft.Compute/virtualMachineScaleSets",
                    "Microsoft.ContainerService/managedClusters"
                ]
            },
            
            "Microsoft.Network/applicationGateways": {
                "depends_on": [
                    "Microsoft.Network/virtualNetworks",
                    "Microsoft.Network/publicIPAddresses",
                    "Microsoft.KeyVault/vaults",  # For SSL certificates
                    "Microsoft.ManagedIdentity/userAssignedIdentities"
                ],
                "impacts": [
                    "Microsoft.Web/sites",
                    "Microsoft.Compute/virtualMachines",
                    "Microsoft.ContainerService/managedClusters"
                ]
            },
            
            "Microsoft.Network/azureFirewalls": {
                "depends_on": [
                    "Microsoft.Network/virtualNetworks",
                    "Microsoft.Network/publicIPAddresses",
                    "Microsoft.Network/firewallPolicies"
                ],
                "impacts": [
                    "Microsoft.Network/virtualNetworks",
                    "Microsoft.Compute/virtualMachines",
                    "Microsoft.Web/sites"
                ]
            },
            
            # Databases
            "Microsoft.Sql/servers": {
                "depends_on": [
                    "Microsoft.Network/virtualNetworks",  # For VNet integration
                    "Microsoft.Storage/storageAccounts",  # For backups
                    "Microsoft.KeyVault/vaults"  # For TDE keys
                ],
                "impacts": [
                    "Microsoft.Web/sites",
                    "Microsoft.DataFactory/factories",
                    "Microsoft.Synapse/workspaces"
                ]
            },
            
            "Microsoft.DocumentDB/databaseAccounts": {
                "depends_on": [
                    "Microsoft.Network/virtualNetworks",
                    "Microsoft.KeyVault/vaults"
                ],
                "impacts": [
                    "Microsoft.Web/sites",
                    "Microsoft.Logic/workflows",
                    "Microsoft.DataFactory/factories"
                ]
            },
            
            "Microsoft.Cache/Redis": {
                "depends_on": [
                    "Microsoft.Network/virtualNetworks"
                ],
                "impacts": [
                    "Microsoft.Web/sites",
                    "Microsoft.Compute/virtualMachines"
                ]
            },
            
            "Microsoft.DBforPostgreSQL/servers": {
                "depends_on": [
                    "Microsoft.Network/virtualNetworks",
                    "Microsoft.Storage/storageAccounts"
                ],
                "impacts": [
                    "Microsoft.Web/sites",
                    "Microsoft.ContainerService/managedClusters"
                ]
            },
            
            "Microsoft.DBforMySQL/servers": {
                "depends_on": [
                    "Microsoft.Network/virtualNetworks",
                    "Microsoft.Storage/storageAccounts"
                ],
                "impacts": [
                    "Microsoft.Web/sites",
                    "Microsoft.ContainerService/managedClusters"
                ]
            },
            
            # Data & Analytics
            "Microsoft.DataFactory/factories": {
                "depends_on": [
                    "Microsoft.Storage/storageAccounts",
                    "Microsoft.Sql/servers",
                    "Microsoft.DocumentDB/databaseAccounts",
                    "Microsoft.KeyVault/vaults",
                    "Microsoft.Synapse/workspaces"
                ],
                "impacts": [
                    "Microsoft.Synapse/workspaces",
                    "Microsoft.MachineLearningServices/workspaces"
                ]
            },
            
            "Microsoft.Synapse/workspaces": {
                "depends_on": [
                    "Microsoft.Storage/storageAccounts",
                    "Microsoft.KeyVault/vaults",
                    "Microsoft.Network/virtualNetworks"
                ],
                "impacts": [
                    "Microsoft.DataFactory/factories",
                    "Microsoft.MachineLearningServices/workspaces"
                ]
            },
            
            "Microsoft.Databricks/workspaces": {
                "depends_on": [
                    "Microsoft.Storage/storageAccounts",
                    "Microsoft.Network/virtualNetworks",
                    "Microsoft.KeyVault/vaults"
                ],
                "impacts": [
                    "Microsoft.DataFactory/factories",
                    "Microsoft.MachineLearningServices/workspaces"
                ]
            },
            
            "Microsoft.EventHub/namespaces": {
                "depends_on": [
                    "Microsoft.Network/virtualNetworks",
                    "Microsoft.Storage/storageAccounts"  # For capture
                ],
                "impacts": [
                    "Microsoft.StreamAnalytics/streamingjobs",
                    "Microsoft.Web/sites",
                    "Microsoft.Logic/workflows",
                    "Microsoft.DataFactory/factories"
                ]
            },
            
            "Microsoft.StreamAnalytics/streamingjobs": {
                "depends_on": [
                    "Microsoft.EventHub/namespaces",
                    "Microsoft.Devices/IotHubs",
                    "Microsoft.Storage/storageAccounts"
                ],
                "impacts": [
                    "Microsoft.Sql/servers",
                    "Microsoft.DocumentDB/databaseAccounts",
                    "Microsoft.PowerBI/workspaceCollections"
                ]
            },
            
            "Microsoft.Devices/IotHubs": {
                "depends_on": [
                    "Microsoft.Storage/storageAccounts",
                    "Microsoft.EventHub/namespaces"
                ],
                "impacts": [
                    "Microsoft.StreamAnalytics/streamingjobs",
                    "Microsoft.Logic/workflows",
                    "Microsoft.TimeSeriesInsights/environments"
                ]
            },
            
            # Security & Identity
            "Microsoft.KeyVault/vaults": {
                "depends_on": [
                    "Microsoft.Network/virtualNetworks",  # For private endpoints
                    "Microsoft.ManagedIdentity/userAssignedIdentities"
                ],
                "impacts": [
                    "Microsoft.Compute/virtualMachines",  # Disk encryption
                    "Microsoft.Web/sites",  # App secrets
                    "Microsoft.Sql/servers",  # TDE
                    "Microsoft.Storage/storageAccounts",  # Encryption keys
                    "Microsoft.ContainerService/managedClusters",  # Secrets
                    "Microsoft.DataFactory/factories"  # Linked service credentials
                ]
            },
            
            "Microsoft.ManagedIdentity/userAssignedIdentities": {
                "depends_on": [],
                "impacts": [
                    "Microsoft.Compute/virtualMachines",
                    "Microsoft.Web/sites",
                    "Microsoft.ContainerService/managedClusters",
                    "Microsoft.DataFactory/factories",
                    "Microsoft.Logic/workflows"
                ]
            },
            
            "Microsoft.AAD/domainServices": {
                "depends_on": [
                    "Microsoft.Network/virtualNetworks"
                ],
                "impacts": [
                    "Microsoft.Compute/virtualMachines",
                    "Microsoft.Storage/storageAccounts"
                ]
            },
            
            # Monitoring
            "Microsoft.OperationalInsights/workspaces": {
                "depends_on": [],
                "impacts": [
                    "Microsoft.Compute/virtualMachines",
                    "Microsoft.ContainerService/managedClusters",
                    "Microsoft.Web/sites",
                    "Microsoft.Sql/servers",
                    "Microsoft.Network/applicationGateways"
                ]
            },
            
            "Microsoft.Insights/components": {
                "depends_on": [
                    "Microsoft.OperationalInsights/workspaces"
                ],
                "impacts": [
                    "Microsoft.Web/sites",
                    "Microsoft.ApiManagement/service"
                ]
            },
            
            # Integration
            "Microsoft.Logic/workflows": {
                "depends_on": [
                    "Microsoft.Web/connections",
                    "Microsoft.Storage/storageAccounts",
                    "Microsoft.ServiceBus/namespaces",
                    "Microsoft.EventGrid/topics"
                ],
                "impacts": [
                    "Microsoft.DataFactory/factories",
                    "Microsoft.Web/sites"
                ]
            },
            
            "Microsoft.ServiceBus/namespaces": {
                "depends_on": [
                    "Microsoft.Network/virtualNetworks"
                ],
                "impacts": [
                    "Microsoft.Web/sites",
                    "Microsoft.Logic/workflows",
                    "Microsoft.EventGrid/topics"
                ]
            },
            
            "Microsoft.ApiManagement/service": {
                "depends_on": [
                    "Microsoft.Network/virtualNetworks",
                    "Microsoft.KeyVault/vaults",  # For certificates
                    "Microsoft.Insights/components"  # For monitoring
                ],
                "impacts": [
                    "Microsoft.Web/sites",
                    "Microsoft.Logic/workflows"
                ]
            },
            
            "Microsoft.EventGrid/topics": {
                "depends_on": [],
                "impacts": [
                    "Microsoft.Logic/workflows",
                    "Microsoft.Web/sites",
                    "Microsoft.EventHub/namespaces",
                    "Microsoft.ServiceBus/namespaces"
                ]
            },
            
            # AI & Machine Learning
            "Microsoft.MachineLearningServices/workspaces": {
                "depends_on": [
                    "Microsoft.Storage/storageAccounts",
                    "Microsoft.KeyVault/vaults",
                    "Microsoft.ContainerRegistry/registries",
                    "Microsoft.Insights/components"
                ],
                "impacts": [
                    "Microsoft.ContainerService/managedClusters",
                    "Microsoft.Synapse/workspaces"
                ]
            },
            
            "Microsoft.CognitiveServices/accounts": {
                "depends_on": [
                    "Microsoft.Network/virtualNetworks",
                    "Microsoft.KeyVault/vaults"
                ],
                "impacts": [
                    "Microsoft.Web/sites",
                    "Microsoft.Logic/workflows",
                    "Microsoft.BotService/botServices"
                ]
            },
            
            "Microsoft.BotService/botServices": {
                "depends_on": [
                    "Microsoft.Web/sites",
                    "Microsoft.CognitiveServices/accounts"
                ],
                "impacts": [
                    "Microsoft.Web/sites/slots"
                ]
            },
            
            "Microsoft.Search/searchServices": {
                "depends_on": [
                    "Microsoft.Storage/storageAccounts",
                    "Microsoft.CognitiveServices/accounts"
                ],
                "impacts": [
                    "Microsoft.Web/sites",
                    "Microsoft.DataFactory/factories"
                ]
            }
        }
        
        # Reverse mapping for quick lookups
        self.impacted_by = self._build_reverse_mapping()
        
        # Common relationship patterns
        self.relationship_patterns = {
            "data_flow": [
                ("Microsoft.Storage/storageAccounts", "Microsoft.DataFactory/factories", "Microsoft.Synapse/workspaces"),
                ("Microsoft.EventHub/namespaces", "Microsoft.StreamAnalytics/streamingjobs", "Microsoft.Sql/servers"),
                ("Microsoft.Devices/IotHubs", "Microsoft.EventHub/namespaces", "Microsoft.TimeSeriesInsights/environments")
            ],
            "security_chain": [
                ("Microsoft.KeyVault/vaults", "Microsoft.Compute/virtualMachines", "disk_encryption"),
                ("Microsoft.KeyVault/vaults", "Microsoft.Web/sites", "app_secrets"),
                ("Microsoft.ManagedIdentity/userAssignedIdentities", "Microsoft.KeyVault/vaults", "secret_access")
            ],
            "network_flow": [
                ("Microsoft.Network/virtualNetworks", "Microsoft.Network/networkSecurityGroups", "Microsoft.Compute/virtualMachines"),
                ("Microsoft.Network/applicationGateways", "Microsoft.Web/sites", "web_traffic"),
                ("Microsoft.Network/loadBalancers", "Microsoft.Compute/virtualMachineScaleSets", "load_distribution")
            ]
        }
        
        self.correlation_rules = [
            # ========== SECURITY CORRELATIONS ==========
            {
                "name": "insecure_database_connection",
                "conditions": [
                    ("app_service", "has_connection_string_in_config"),
                    ("sql_database", "allows_public_access")
                ],
                "severity": "critical",
                "recommendation": "Use managed identity with private endpoint",
                "estimated_effort_hours": 4.0,
                "risk_score": 10
            },
            {
                "name": "exposed_sensitive_data_path",
                "conditions": [
                    ("storage_account", "allows_public_blob_access"),
                    ("app_service", "writes_sensitive_data_to_storage"),
                    ("storage_account", "no_encryption_at_rest")
                ],
                "severity": "critical",
                "recommendation": "Disable public access, enable encryption, use private endpoints",
                "estimated_effort_hours": 3.0,
                "risk_score": 10
            },
            {
                "name": "vulnerable_container_supply_chain",
                "conditions": [
                    ("aks_cluster", "pull_secrets_not_using_managed_identity"),
                    ("container_registry", "no_vulnerability_scanning"),
                    ("container_registry", "allows_anonymous_pull")
                ],
                "severity": "critical",
                "recommendation": "Enable managed identity, vulnerability scanning, and disable anonymous access",
                "estimated_effort_hours": 6.0,
                "risk_score": 9
            },
            {
                "name": "weak_encryption_chain",
                "conditions": [
                    ("key_vault", "using_software_protected_keys"),
                    ("storage_account", "customer_managed_keys_from_same_vault"),
                    ("sql_database", "tde_using_same_vault")
                ],
                "severity": "high",
                "recommendation": "Use HSM-protected keys and consider key rotation strategy",
                "estimated_effort_hours": 8.0,
                "risk_score": 8
            },
            {
                "name": "exposed_management_plane",
                "conditions": [
                    ("vm", "rdp_ssh_open_to_internet"),
                    ("vm", "no_just_in_time_access"),
                    ("nsg", "no_ddos_protection")
                ],
                "severity": "critical",
                "recommendation": "Enable JIT access, restrict NSG rules, enable DDoS protection",
                "estimated_effort_hours": 2.0,
                "risk_score": 10
            },
            {
                "name": "insecure_api_gateway",
                "conditions": [
                    ("api_management", "no_client_certificate_required"),
                    ("api_management", "backend_using_http"),
                    ("app_service", "api_backend_allows_anonymous")
                ],
                "severity": "high",
                "recommendation": "Enable mutual TLS, use HTTPS for backends, require authentication",
                "estimated_effort_hours": 5.0,
                "risk_score": 8
            },
            
            # ========== PERFORMANCE CORRELATIONS ==========
            {
                "name": "database_performance_bottleneck",
                "conditions": [
                    ("sql_database", "high_dtu_usage"),
                    ("app_service", "connection_pool_exhaustion"),
                    ("app_service", "no_retry_logic")
                ],
                "severity": "high",
                "recommendation": "Scale database, implement connection pooling and retry patterns",
                "estimated_effort_hours": 6.0,
                "risk_score": 7
            },
            {
                "name": "unoptimized_data_pipeline",
                "conditions": [
                    ("data_factory", "no_parallel_processing"),
                    ("storage_account", "using_standard_tier"),
                    ("synapse", "no_data_partitioning")
                ],
                "severity": "medium",
                "recommendation": "Enable parallel processing, use premium storage, implement partitioning",
                "estimated_effort_hours": 12.0,
                "risk_score": 5
            },
            {
                "name": "container_resource_starvation",
                "conditions": [
                    ("aks_cluster", "no_resource_limits_set"),
                    ("aks_cluster", "no_horizontal_pod_autoscaling"),
                    ("container_registry", "large_image_sizes")
                ],
                "severity": "high",
                "recommendation": "Set resource limits, enable HPA, optimize container images",
                "estimated_effort_hours": 8.0,
                "risk_score": 7
            },
            {
                "name": "inefficient_content_delivery",
                "conditions": [
                    ("storage_account", "serving_static_content"),
                    ("app_service", "no_cdn_configured"),
                    ("storage_account", "not_using_hot_access_tier")
                ],
                "severity": "medium",
                "recommendation": "Enable CDN, use appropriate storage tiers",
                "estimated_effort_hours": 4.0,
                "risk_score": 4
            },
            
            # ========== COST CORRELATIONS ==========
            {
                "name": "redundant_backup_costs",
                "conditions": [
                    ("vm", "azure_backup_enabled"),
                    ("vm", "disk_snapshots_enabled"),
                    ("storage_account", "storing_vm_backups")
                ],
                "severity": "medium",
                "recommendation": "Consolidate backup strategy, use single backup solution",
                "estimated_effort_hours": 3.0,
                "risk_score": 3,
                "monthly_savings_estimate": 200
            },
            {
                "name": "oversized_infrastructure_chain",
                "conditions": [
                    ("vm", "cpu_usage_under_20_percent"),
                    ("sql_database", "dtu_usage_under_20_percent"),
                    ("app_service_plan", "usage_under_30_percent")
                ],
                "severity": "medium",
                "recommendation": "Right-size all components based on actual usage",
                "estimated_effort_hours": 6.0,
                "risk_score": 2,
                "monthly_savings_estimate": 800
            },
            {
                "name": "inefficient_data_transfer_costs",
                "conditions": [
                    ("storage_account", "cross_region_replication"),
                    ("app_service", "in_different_region"),
                    ("sql_database", "in_different_region")
                ],
                "severity": "medium",
                "recommendation": "Colocate resources in same region to reduce egress charges",
                "estimated_effort_hours": 10.0,
                "risk_score": 3,
                "monthly_savings_estimate": 500
            },
            {
                "name": "unused_premium_features",
                "conditions": [
                    ("sql_database", "using_business_critical_tier"),
                    ("sql_database", "no_read_replicas_configured"),
                    ("sql_database", "no_zone_redundancy_needed")
                ],
                "severity": "low",
                "recommendation": "Downgrade to General Purpose tier if premium features unused",
                "estimated_effort_hours": 2.0,
                "risk_score": 1,
                "monthly_savings_estimate": 1200
            },
            
            # ========== RELIABILITY CORRELATIONS ==========
            {
                "name": "single_point_of_failure",
                "conditions": [
                    ("load_balancer", "single_backend_pool_member"),
                    ("vm", "no_availability_set_or_zone"),
                    ("app_service", "single_instance")
                ],
                "severity": "high",
                "recommendation": "Implement redundancy across availability zones",
                "estimated_effort_hours": 8.0,
                "risk_score": 8
            },
            {
                "name": "incomplete_disaster_recovery",
                "conditions": [
                    ("sql_database", "no_geo_replication"),
                    ("storage_account", "no_geo_redundancy"),
                    ("key_vault", "no_backup_configured")
                ],
                "severity": "high",
                "recommendation": "Implement comprehensive DR strategy with geo-redundancy",
                "estimated_effort_hours": 12.0,
                "risk_score": 7
            },
            {
                "name": "cascading_failure_risk",
                "conditions": [
                    ("app_service", "no_health_probes"),
                    ("sql_database", "no_connection_retry"),
                    ("redis_cache", "no_cluster_configuration")
                ],
                "severity": "high",
                "recommendation": "Implement circuit breakers and retry patterns",
                "estimated_effort_hours": 10.0,
                "risk_score": 8
            },
            
            # ========== OPERATIONAL CORRELATIONS ==========
            {
                "name": "monitoring_blind_spots",
                "conditions": [
                    ("vm", "no_diagnostics_enabled"),
                    ("app_service", "no_application_insights"),
                    ("sql_database", "no_query_performance_insights")
                ],
                "severity": "medium",
                "recommendation": "Enable comprehensive monitoring across all layers",
                "estimated_effort_hours": 4.0,
                "risk_score": 6
            },
            {
                "name": "incomplete_automation_pipeline",
                "conditions": [
                    ("devops_pipeline", "manual_approval_steps"),
                    ("key_vault", "manual_secret_rotation"),
                    ("vm", "manual_patching_enabled")
                ],
                "severity": "medium",
                "recommendation": "Automate deployment, secret rotation, and patching",
                "estimated_effort_hours": 16.0,
                "risk_score": 5
            },
            {
                "name": "compliance_gap_chain",
                "conditions": [
                    ("storage_account", "no_immutable_storage"),
                    ("key_vault", "no_purge_protection"),
                    ("log_analytics", "retention_under_90_days")
                ],
                "severity": "high",
                "recommendation": "Enable compliance features for audit requirements",
                "estimated_effort_hours": 6.0,
                "risk_score": 7
            },
            
            # ========== DATA & ANALYTICS CORRELATIONS ==========
            {
                "name": "inefficient_data_ingestion",
                "conditions": [
                    ("event_hub", "single_partition"),
                    ("stream_analytics", "no_parallel_processing"),
                    ("cosmos_db", "low_throughput_provisioned")
                ],
                "severity": "medium",
                "recommendation": "Scale out ingestion pipeline for better throughput",
                "estimated_effort_hours": 8.0,
                "risk_score": 5
            },
            {
                "name": "unprotected_ml_pipeline",
                "conditions": [
                    ("machine_learning", "public_endpoint_enabled"),
                    ("storage_account", "ml_data_publicly_accessible"),
                    ("container_registry", "ml_models_not_scanned")
                ],
                "severity": "high",
                "recommendation": "Secure ML pipeline with private endpoints and scanning",
                "estimated_effort_hours": 10.0,
                "risk_score": 8
            },
            
            # ========== IDENTITY & ACCESS CORRELATIONS ==========
            {
                "name": "identity_sprawl",
                "conditions": [
                    ("app_service", "using_service_principal"),
                    ("vm", "using_different_service_principal"),
                    ("key_vault", "multiple_access_policies")
                ],
                "severity": "medium",
                "recommendation": "Consolidate to managed identities where possible",
                "estimated_effort_hours": 6.0,
                "risk_score": 5
            },
            {
                "name": "privileged_access_exposure",
                "conditions": [
                    ("subscription", "multiple_owner_assignments"),
                    ("key_vault", "broad_access_policies"),
                    ("storage_account", "account_key_in_use")
                ],
                "severity": "critical",
                "recommendation": "Implement least privilege and JIT access",
                "estimated_effort_hours": 8.0,
                "risk_score": 9
            },
            
            # ========== NETWORK CORRELATIONS ==========
            {
                "name": "network_segmentation_gap",
                "conditions": [
                    ("vnet", "no_network_segmentation"),
                    ("nsg", "permissive_rules_between_subnets"),
                    ("firewall", "not_configured")
                ],
                "severity": "high",
                "recommendation": "Implement proper network segmentation with Azure Firewall",
                "estimated_effort_hours": 12.0,
                "risk_score": 8
            },
            {
                "name": "exposed_private_endpoints",
                "conditions": [
                    ("storage_account", "has_private_endpoint"),
                    ("storage_account", "public_access_still_enabled"),
                    ("sql_database", "firewall_allows_azure_services")
                ],
                "severity": "high",
                "recommendation": "Disable public access when using private endpoints",
                "estimated_effort_hours": 2.0,
                "risk_score": 7
            }
        ]
        
        # Index rules by severity for quick filtering
        self.rules_by_severity = self._index_rules_by_severity()
        
        # Index rules by resource type for efficient matching
        self.rules_by_resource = self._index_rules_by_resource()
        
    
    def _build_reverse_mapping(self) -> dict:
        """Build a reverse mapping of what resources are impacted by others."""
        reverse_map = {}
        
        for resource_type, relationships in self.resource_relationships.items():
            # For each resource this one impacts
            for impacted in relationships.get("impacts", []):
                if impacted not in reverse_map:
                    reverse_map[impacted] = []
                reverse_map[impacted].append(resource_type)
        
        return reverse_map
    
    def get_dependencies(self, resource_type: str) -> list:
        """Get all resources this resource type depends on."""
        return self.resource_relationships.get(resource_type, {}).get("depends_on", [])
    
    def get_impacts(self, resource_type: str) -> list:
        """Get all resources this resource type impacts."""
        return self.resource_relationships.get(resource_type, {}).get("impacts", [])
    
    def get_impacted_by(self, resource_type: str) -> list:
        """Get all resources that impact this resource type."""
        return self.impacted_by.get(resource_type, [])
    
    def find_relationship_chain(self, start_type: str, end_type: str) -> list:
        """Find the relationship chain between two resource types."""
        # Implementation of BFS to find relationship path
        visited = set()
        queue = [(start_type, [start_type])]
        
        while queue:
            current, path = queue.pop(0)
            
            if current == end_type:
                return path
            
            if current in visited:
                continue
                
            visited.add(current)
            
            # Check both dependencies and impacts
            for next_resource in self.get_dependencies(current) + self.get_impacts(current):
                if next_resource not in visited:
                    queue.append((next_resource, path + [next_resource]))
        
        return []  # No relationship found
        
    def _index_rules_by_severity(self) -> dict:
        """Index correlation rules by severity level."""
        severity_index = {
            "critical": [],
            "high": [],
            "medium": [],
            "low": []
        }
        
        for rule in self.correlation_rules:
            severity = rule.get("severity", "medium")
            severity_index[severity].append(rule)
        
        return severity_index
    
    def _index_rules_by_resource(self) -> dict:
        """Index correlation rules by resource types involved."""
        resource_index = {}
        
        for rule in self.correlation_rules:
            for condition in rule.get("conditions", []):
                resource_type = condition[0]
                if resource_type not in resource_index:
                    resource_index[resource_type] = []
                if rule not in resource_index[resource_type]:
                    resource_index[resource_type].append(rule)
        
        return resource_index
    
    def get_applicable_rules(self, resource_types: list) -> list:
        """Get correlation rules applicable to given resource types."""
        applicable_rules = set()
        
        for resource_type in resource_types:
            rules = self.rules_by_resource.get(resource_type, [])
            applicable_rules.update(rules)
        
        return list(applicable_rules)