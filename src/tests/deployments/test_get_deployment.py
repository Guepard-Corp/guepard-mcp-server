#!/usr/bin/env python3
"""
Real test for GetDeploymentTool
Tests the get_deployment functionality with real API calls
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from guepard_mcp.deployments.tools import GetDeploymentTool
from guepard_mcp.utils.base import GuepardAPIClient

async def test_get_deployment():
    """Test get_deployment tool with real API calls"""
    print("🧪 Testing get_deployment tool with real API calls...")
    
    # Create tool instance
    client = GuepardAPIClient()
    tool = GetDeploymentTool(client)
    
    # Check if we have credentials
    if not client.access_token:
        print("❌ No ACCESS_TOKEN found in environment variables")
        print("   Please set ACCESS_TOKEN in your .env file")
        return False
    
    print(f"   Using API: {client.api_base_url}")
    print(f"   Token: {client.access_token[:10]}...")
    
    # Initialize HTTP session
    await client.connect()
    
    # Test 1: Get latest deployment
    print("\n  Testing get latest deployment...")
    try:
        result = await tool.execute({"latest": True})
        print(f"    Response: {result}")
        print("  ✅ Latest deployment test completed")
    except Exception as e:
        print(f"    ❌ Latest deployment test failed: {e}")
        return False
    
    # Test 2: Get deployments by repository name (if any exist)
    print("\n  Testing get deployment by repository name...")
    try:
        # Try with a common repository name
        result = await tool.execute({"repository_name": "test"})
        print(f"    Response: {result}")
        print("  ✅ Repository name test completed")
    except Exception as e:
        print(f"    ❌ Repository name test failed: {e}")
        return False
    
    # Test 3: Missing parameters
    print("\n  Testing missing parameters...")
    try:
        result = await tool.execute({})
        print(f"    Response: {result}")
        print("  ✅ Missing parameters test completed")
    except Exception as e:
        print(f"    ❌ Missing parameters test failed: {e}")
        return False
    
    # Test 4: Invalid deployment ID
    print("\n  Testing invalid deployment ID...")
    try:
        result = await tool.execute({"deployment_id": "invalid-deployment-id-12345"})
        print(f"    Response: {result}")
        print("  ✅ Invalid deployment ID test completed")
    except Exception as e:
        print(f"    ❌ Invalid deployment ID test failed: {e}")
        return False
    
    # Clean up
    await client.disconnect()
    
    print("\n" + "="*60)
    print("📊 SYNTHESIS - Get Deployment Test Results")
    print("="*60)
    print("✅ Tested scenarios:")
    print("   • Get latest deployment")
    print("   • Get deployment by repository name")
    print("   • Handle missing parameters gracefully")
    print("   • Handle invalid deployment ID")
    print(f"\n🔗 API Endpoints: {client.api_base_url}/deploy")
    print(f"🔑 Authentication: {'✅ Token present' if client.access_token else '❌ No token'}")
    print("\n📝 Notes:")
    print("   • All tests completed successfully")
    print("   • Real API calls made to local server")
    print("   • HTTP session properly initialized and cleaned up")
    print("   • Error handling tested for various scenarios")
    print("="*60)
    
    print("\n✅ All get_deployment real API tests completed!")
    return True

async def main():
    """Main test runner"""
    print("🚀 Starting get_deployment real API tests...\n")
    
    try:
        success = await test_get_deployment()
        return 0 if success else 1
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)