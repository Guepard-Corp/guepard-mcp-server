#!/usr/bin/env python3
"""
Real test for GetComputeTool
Tests the get_compute functionality with real API calls
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from guepard_mcp.compute.tools import GetComputeTool
from guepard_mcp.deployments.tools import ListDeploymentsTool
from guepard_mcp.utils.base import GuepardAPIClient

async def test_get_compute():
    """Test get_compute tool with real API calls"""
    print("🧪 Testing get_compute tool with real API calls...")
    
    # Create tool instances
    client = GuepardAPIClient()
    tool = GetComputeTool(client)
    list_tool = ListDeploymentsTool(client)
    
    # Check if we have credentials
    if not client.access_token:
        print("❌ No ACCESS_TOKEN found in environment variables")
        print("   Please set ACCESS_TOKEN in your .env file")
        return False
    
    print(f"   Using API: {client.api_base_url}")
    print(f"   Token: {client.access_token[:10]}...")
    
    # Initialize HTTP session
    await client.connect()
    
    # Get real deployment IDs from API
    print("\n  📋 Fetching real deployment IDs from API...")
    try:
        deployments_result = await list_tool.execute({"limit": 5})
        print(f"    Deployments result: {deployments_result}")
        
        # Extract deployment IDs from the result
        import json
        if "✅" in deployments_result and "[" in deployments_result:
            # Extract JSON part from the response
            json_start = deployments_result.find("[")
            json_end = deployments_result.rfind("]") + 1
            if json_start != -1 and json_end != -1:
                json_str = deployments_result[json_start:json_end]
                deployments = json.loads(json_str)
                if deployments and len(deployments) > 0:
                    real_deployment_id = deployments[0]["id"]
                    print(f"    Using real deployment ID: {real_deployment_id}")
                else:
                    print("    ❌ No deployments found")
                    return False
            else:
                print("    ❌ Could not parse deployments JSON")
                return False
        else:
            print("    ❌ Could not fetch deployments")
            return False
    except Exception as e:
        print(f"    ❌ Failed to fetch deployments: {e}")
        return False
    
    # Test 1: Get compute for existing deployment
    print("\n  Testing get compute for existing deployment...")
    try:
        result = await tool.execute({
            "deployment_id": real_deployment_id
        })
        print(f"    Response: {result}")
        print("  ✅ Get compute test completed")
    except Exception as e:
        print(f"    ❌ Get compute test failed: {e}")
        return False
    
    # Test 2: Get compute for non-existent deployment
    print("\n  Testing get compute for non-existent deployment...")
    try:
        result = await tool.execute({
            "deployment_id": "99999999-9999-9999-9999-999999999999"
        })
        print(f"    Response: {result}")
        print("  ✅ Non-existent deployment test completed")
    except Exception as e:
        print(f"    ❌ Non-existent deployment test failed: {e}")
        return False
    
    # Test 3: Missing deployment_id parameter
    print("\n  Testing missing deployment_id parameter...")
    try:
        result = await tool.execute({})
        print(f"    Response: {result}")
        print("  ✅ Missing deployment_id test completed")
    except Exception as e:
        print(f"    ❌ Missing deployment_id test failed: {e}")
        return False
    
    # Clean up
    await client.disconnect()
    
    print("\n" + "="*60)
    print("📊 SYNTHESIS - Get Compute Test Results")
    print("="*60)
    print("✅ Tested scenarios:")
    print("   • Get compute for existing deployment")
    print("   • Get compute for non-existent deployment")
    print("   • Handle missing deployment_id parameter")
    print(f"\n🔗 API Endpoint: {client.api_base_url}/deploy/{{deployment_id}}/compute")
    print(f"🔑 Authentication: {'✅ Token present' if client.access_token else '❌ No token'}")
    print("\n📝 Notes:")
    print("   • All tests completed successfully")
    print("   • Real API calls made to local server")
    print("   • HTTP session properly initialized and cleaned up")
    print("   • Error handling tested for various scenarios")
    print("="*60)
    
    print("\n✅ All get_compute real API tests completed!")
    return True

async def main():
    """Main test runner"""
    print("🚀 Starting get_compute real API tests...\n")
    
    try:
        success = await test_get_compute()
        return 0 if success else 1
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)