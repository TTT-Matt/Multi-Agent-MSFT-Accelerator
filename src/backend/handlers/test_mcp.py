import asyncio
import logging
from kernel_plugins.mcp_plugin import MCPPlugin

logging.basicConfig(level=logging.INFO)

async def test_azure_mcp_connection():
    """Test the Azure MCP server connection."""
    
    # Initialize MCP plugin
    mcp_plugin = MCPPlugin()
    await mcp_plugin.initialize()
    
    # List available tools
    print("=== Available MCP Tools ===")
    tools_json = await mcp_plugin.list_available_tools()
    print(tools_json)
    
    # Test Resource Graph query
    print("\n=== Testing Resource Graph Query ===")
    query = """
    Resources
    | summarize count() by type
    | order by count_ desc
    | limit 5
    """
    
    result = await mcp_plugin.query_azure_resources(query)
    print(result)
    
    # Test Azure CLI command
    print("\n=== Testing Azure CLI Command ===")
    cli_result = await mcp_plugin.execute_azure_cli("account show")
    print(cli_result)
    
    # Cleanup
    await mcp_plugin.cleanup()

if __name__ == "__main__":
    asyncio.run(test_azure_mcp_connection())