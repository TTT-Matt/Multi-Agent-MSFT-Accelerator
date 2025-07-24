# src/backend/kernel_agents/azure_mcp_client.py

import logging
import json
from typing import Dict, List, Optional, Any
import subprocess
import asyncio
from kernel_agents.intelligent_agent_selector import IntelligentAgentSelector
from kernel_agents.cross_agent_intelligence import CrossAgentIntelligence

logger = logging.getLogger(__name__)


class AzureMCPClient:
    """Client for interacting with Azure MCP tools available in VSCode Dev Container."""
    
    def __init__(self):
        """Initialize the Azure MCP client for VSCode Dev Container environment."""
        logger.info("Initialized MCP client for VSCode Dev Container")
        
    async def execute_mcp_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict:
        """
        Execute an MCP tool that's available in the VSCode environment.
        
        Since MCP_DOCKER is available as a tool in your VSCode container,
        you can call it directly through the MCP integration.
        
        Args:
            tool_name: Name of the MCP tool (e.g., "azmcp-extension-az")
            parameters: Parameters to pass to the tool
        """
        try:
            # In a VSCode Dev Container with MCP integration, tools are typically
            # available through the mcp command or as environment integrations
            
            # Option 1: If MCP tools are available as CLI commands
            if tool_name.startswith("azmcp-"):
                # Construct the command
                cmd_parts = [tool_name]
                
                # Add parameters as command-line arguments
                for key, value in parameters.items():
                    if key == "command":
                        # For az commands, append the command directly
                        cmd_parts.extend(value.split())
                    else:
                        cmd_parts.append(f"--{key}")
                        cmd_parts.append(str(value))
                
                # Execute the command
                result = await self._run_command(cmd_parts)
                return result
            
            # Option 2: If MCP tools are available through a unified mcp command
            else:
                cmd = ["mcp", "call", tool_name, json.dumps(parameters)]
                result = await self._run_command(cmd)
                return result
                
        except Exception as e:
            logger.error(f"MCP tool execution failed: {e}")
            return {
                "success": False,
                "result": None,
                "error": str(e)
            }
    
    async def _run_command(self, cmd: List[str]) -> Dict:
        """Run a command asynchronously."""
        try:
            logger.debug(f"Executing command: {' '.join(cmd)}")
            
            # Run the command
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                # Parse output
                output = stdout.decode().strip()
                try:
                    # Try to parse as JSON
                    result = json.loads(output) if output else {}
                except json.JSONDecodeError:
                    # Return as plain text if not JSON
                    result = output
                
                return {
                    "success": True,
                    "result": result,
                    "error": None
                }
            else:
                error_msg = stderr.decode().strip()
                logger.error(f"Command failed: {error_msg}")
                return {
                    "success": False,
                    "result": None,
                    "error": error_msg
                }
                
        except Exception as e:
            logger.error(f"Command execution error: {e}")
            return {
                "success": False,
                "result": None,
                "error": str(e)
            }
    
    async def execute_az_command(self, command: str, subscription: str = None) -> Dict:
        """
        Execute an Azure CLI command via MCP tools.
        
        Since you have azmcp-extension-az available, we can use it directly.
        """
        parameters = {"command": command}
        
        if subscription:
            parameters["subscription"] = subscription
        
        return await self.execute_mcp_tool("azmcp-extension-az", parameters)
    
    async def list_resources(self, resource_group: str, subscription: str) -> List[Dict]:
        """List resources using azmcp tools."""
        result = await self.execute_mcp_tool(
            "azmcp-group-list",
            {"subscription": subscription}
        )
        
        if result["success"]:
            return result.get("result", [])
        return []


# Alternative: Direct usage if MCP tools are Python-importable
class AzureMCPClientDirect:
    """Direct usage of MCP tools if they're available as Python modules."""
    
    def __init__(self):
        """Initialize direct MCP client."""
        try:
            # Try to import MCP tools if they're available as Python modules
            import mcp_docker
            self.mcp = mcp_docker
            self.direct_access = True
            logger.info("Direct MCP module access available")
        except ImportError:
            self.direct_access = False
            logger.info("MCP tools not available as Python modules")
    
    async def execute_az_command(self, command: str, subscription: str = None) -> Dict:
        """Execute Azure command using direct MCP access."""
        if self.direct_access:
            # If MCP tools are directly accessible
            try:
                result = await self.mcp.azmcp_extension_az(
                    command=command,
                    subscription=subscription
                )
                return {
                    "success": True,
                    "result": result,
                    "error": None
                }
            except Exception as e:
                return {
                    "success": False,
                    "result": None,
                    "error": str(e)
                }
        else:
            # Fall back to command-line execution
            return await AzureMCPClient().execute_az_command(command, subscription)


# Test script to figure out how MCP tools are available
async def discover_mcp_availability():
    """Discover how MCP tools are available in your environment."""
    
    print("🔍 Discovering MCP tool availability...\n")
    
    # Test 1: Check if mcp command exists
    print("1️⃣ Checking for 'mcp' command...")
    try:
        result = subprocess.run(["which", "mcp"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Found mcp at: {result.stdout.strip()}")
        else:
            print("❌ 'mcp' command not found")
    except:
        print("❌ Could not check for mcp command")
    
    # Test 2: Check if azmcp tools are directly available
    print("\n2️⃣ Checking for azmcp-* commands...")
    for tool in ["azmcp-extension-az", "azmcp-group-list", "azmcp-storage-account-list"]:
        try:
            result = subprocess.run(["which", tool], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Found {tool} at: {result.stdout.strip()}")
            else:
                print(f"❌ '{tool}' command not found")
        except:
            pass
    
    # Test 3: Check Python imports
    print("\n3️⃣ Checking Python imports...")
    try:
        import mcp_docker
        print("✅ 'mcp_docker' module is available")
    except ImportError:
        print("❌ 'mcp_docker' module not available")
    
    # Test 4: Check environment variables
    print("\n4️⃣ Checking environment variables...")
    import os
    mcp_vars = {k: v for k, v in os.environ.items() if 'MCP' in k}
    if mcp_vars:
        for key, value in mcp_vars.items():
            print(f"   {key}: {value}")
    else:
        print("   No MCP-related environment variables found")
    
    # Test 5: Try to use az command directly
    print("\n5️⃣ Testing Azure CLI access...")
    try:
        result = subprocess.run(
            ["az", "account", "show"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            account = json.loads(result.stdout)
            print(f"✅ Azure CLI works! Connected to: {account.get('name', 'Unknown')}")
        else:
            print("❌ Azure CLI command failed")
    except:
        print("❌ Azure CLI not available")
    
    # Test 6: Look for MCP configuration files
    print("\n6️⃣ Looking for MCP configuration...")
    config_paths = [
        "/.mcp/config.json",
        "/workspace/.mcp/config.json",
        "/home/vscode/.mcp/config.json",
        "/.devcontainer/mcp-config.json"
    ]
    for path in config_paths:
        if os.path.exists(path):
            print(f"✅ Found MCP config at: {path}")
            try:
                with open(path, 'r') as f:
                    config = json.load(f)
                    print(f"   Config: {json.dumps(config, indent=2)[:200]}...")
            except:
                pass


# Usage in your assessment agent
class AzureAssessmentPlannerAgent(BaseAgent):
    """Assessment planner using VSCode MCP integration."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Initialize MCP client for VSCode environment
        self.mcp_client = AzureMCPClient()
        self.agent_selector = IntelligentAgentSelector()
        self.cross_agent_intelligence = CrossAgentIntelligence()
        
        logger.info("Initialized Assessment Planner with VSCode MCP integration")
    
    async def discover_azure_resources(self, scope: str) -> List[Dict]:
        """Discover resources using VSCode MCP tools."""
        
        # Option 1: Use az resource list
        command = f"resource list --resource-group {scope} --output json"
        result = await self.mcp_client.execute_az_command(command)
        
        if result["success"]:
            resources = result["result"]
            if isinstance(resources, str):
                resources = json.loads(resources)
            return resources
        
        # Option 2: Use Resource Graph
        command = f'graph query -q "Resources | where resourceGroup =~ \'{scope}\'" --output json'
        result = await self.mcp_client.execute_az_command(command)
        
        if result["success"]:
            data = result["result"]
            if isinstance(data, str):
                data = json.loads(data)
            return data.get("data", [])
        
        return []


if __name__ == "__main__":
    # Run the discovery script
    asyncio.run(discover_mcp_availability())