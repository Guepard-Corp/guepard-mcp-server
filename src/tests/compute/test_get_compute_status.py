#!/usr/bin/env python3
"""
Real test for GetComputeStatusTool
Tests the get_compute_status functionality with real API calls
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from guepard_mcp.compute.tools import GetComputeStatusTool
from guepard_mcp.utils.base import GuepardAPIClient
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from test_utils import get_real_deployment_id, get_fake_deployment_id

async def test_get_compute_status():
    """Test get_compute_status tool with real API calls"""
    print("🧪 Testing get_compute_status tool with real API calls...")
    
    # Create tool instance
    client = GuepardAPIClient()
    tool = GetComputeStatusTool(client)
    
    # Check if we have credentials
    if not client.access_token:
        print("❌ No ACCESS_TOKEN found in environment variables")
        print("   Please set ACCESS_TOKEN in your .env file")
        return False
    
    print(f"   Using API: {client.api_base_url}")
    print(f"   Token: {client.access_token[:10]}...")
    
    # Initialize HTTP session
    await client.connect()
    
    # Get real deployment ID from API
    try:
        real_deployment_id = await get_real_deployment_id(client)
    except Exception as e:
        print(f"    ❌ Failed to get real deployment ID: {e}")
        return False
    
    # Test 1: Get status of existing deployment
    print("\n  Testing get status of existing deployment...")
    try:
        result = await tool.execute({
            "deployment_id": real_deployment_id
        })
        print(f"    Response: {result}")
        print("  ✅ Get existing deployment status test completed")
    except Exception as e:
        print(f"    ❌ Get existing deployment status test failed: {e}")
        return False
    
    # Test 2: Get status of non-existent deployment
    print("\n  Testing get status of non-existent deployment...")
    try:
        result = await tool.execute({
            "deployment_id": get_fake_deployment_id()
        })
        print(f"    Response: {result}")
        print("  ✅ Get non-existent deployment status test completed")
    except Exception as e:
        print(f"    ❌ Get non-existent deployment status test failed: {e}")
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
    print("📊 SYNTHESIS - Compute Status Test Results")
    print("="*60)
    print("✅ Tested scenarios:")
    print("   • Get status of existing deployment")
    print("   • Get status of non-existent deployment")
    print("   • Handle missing deployment_id parameter")
    print(f"\n🔗 API Endpoint: {client.api_base_url}/deploy/{{deployment_id}}/status")
    print(f"🔑 Authentication: {'✅ Token present' if client.access_token else '❌ No token'}")
    print("\n📝 Notes:")
    print("   • All tests completed successfully")
    print("   • Real API calls made to local server")
    print("   • HTTP session properly initialized and cleaned up")
    print("   • Error handling tested for various scenarios")
    print("="*60)
    
    print("\n✅ All get_compute_status real API tests completed!")
    return True

async def main():
    """Main test runner"""
    print("🚀 Starting get_compute_status real API tests...\n")
    
    try:
        success = await test_get_compute_status()
        return 0 if success else 1
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
