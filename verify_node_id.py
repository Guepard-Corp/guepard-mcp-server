
import asyncio
from typing import Dict, Any, Optional

# Mock the necessary classes to avoid actual API calls/dependencies
class MockGuepardAPIClient:
    def __init__(self):
        self.api_calls = []
        self.access_token = "mock_token"
        
    async def _make_api_call(self, method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None):
        self.api_calls.append({
            "method": method,
            "endpoint": endpoint,
            "data": data,
            "params": params
        })
        # Return a mock successful response
        return {
            "id": "deploy-123",
            "name": "Test Deployment",
            "repository_name": data.get("repository_name", "repo-123") if data else "repo-123"
        }

    def subscribe_to_event(self, event_type: str, callback):
        pass

# Mock aiohttp and other dependencies before importing tools
import sys
from unittest.mock import MagicMock

# Create mock modules
mock_aiohttp = MagicMock()
sys.modules["aiohttp"] = mock_aiohttp
sys.modules["aiohttp.web"] = MagicMock()

# Mock dotenv
mock_dotenv = MagicMock()
sys.modules["dotenv"] = mock_dotenv

# Mock mcp if needed (mcp.types, etc)
sys.modules["mcp"] = MagicMock()
sys.modules["mcp.types"] = MagicMock()
sys.modules["mcp.server"] = MagicMock()
sys.modules["mcp.server.fastmcp"] = MagicMock()

import os
# Adjust path to import the module
sys.path.insert(0, os.path.abspath("/Users/mghassen/Workspace/GPRD/guepard-mcp-server/src"))

from guepard_mcp.deployments.tools import CreateDeploymentTool

async def test_create_deployment_with_node_id():
    print("🧪 Testing CreateDeploymentTool with node_id...")
    
    client = MockGuepardAPIClient()
    tool = CreateDeploymentTool(client)
    
    # Arguments including node_id
    args = {
        "repository_name": "test-repo",
        "node_id": "node-123",
        "name": "Node Deployment"
    }
    
    # Execute the tool
    try:
        await tool.execute(args)
    except Exception as e:
        print(f"❌ Execution failed: {e}")
        return False
        
    # Check if API call was made with node_id
    if not client.api_calls:
        print("❌ No API calls made")
        return False
        
    last_call = client.api_calls[-1]
    data = last_call.get("data", {})
    
    if "node_id" in data and data["node_id"] == "node-123":
        print(f"✅ Success! API call contained node_id: {data['node_id']}")
        return True
    else:
        print(f"❌ Failed! API call data missing node_id or incorrect: {data}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_create_deployment_with_node_id())
    sys.exit(0 if success else 1)
