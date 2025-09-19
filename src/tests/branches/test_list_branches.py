#!/usr/bin/env python3
"""
Real test for ListBranchesTool
Tests the list_branches functionality with real API calls
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from guepard_mcp.branches.tools import ListBranchesTool
from guepard_mcp.utils.base import GuepardAPIClient
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from test_utils import get_real_deployment_id, get_fake_deployment_id

async def test_list_branches():
    """Test list_branches tool with real API calls"""
    print("🧪 Testing list_branches tool with real API calls...")
    
    # Create tool instance
    client = GuepardAPIClient()
    tool = ListBranchesTool(client)
    
    # Check if we have credentials
    if not client.access_token:
        print("❌ No ACCESS_TOKEN found in environment variables")
        print("   Please set ACCESS_TOKEN in your .env file")
        return False
    
    print(f"   Using API: {client.api_base_url}")
    print(f"   Token: {client.access_token[:10]}...")
    
    # Initialize HTTP session
    await client.connect()
    
    # Test 1: List all branches
    print("\n  Testing list all branches...")
    try:
        result = await tool.execute({})
        print(f"    Response: {result}")
        print("  ✅ List all branches test completed")
    except Exception as e:
        print(f"    ❌ List all branches test failed: {e}")
        return False
    
    # Test 2: List branches with deployment filter
    print("\n  Testing list branches with deployment filter...")
    try:
        # Get a real deployment ID
        real_deployment_id = await get_real_deployment_id(client)
        result = await tool.execute({
            "deployment_id": real_deployment_id
        })
        print(f"    Response: {result}")
        print("  ✅ List branches with deployment filter test completed")
    except Exception as e:
        print(f"    ❌ List branches with deployment filter test failed: {e}")
        return False
    
    # Test 3: List branches with limit
    print("\n  Testing list branches with limit...")
    try:
        result = await tool.execute({
            "limit": 5
        })
        print(f"    Response: {result}")
        print("  ✅ List branches with limit test completed")
    except Exception as e:
        print(f"    ❌ List branches with limit test failed: {e}")
        return False
    
    # Test 4: List branches with both filters
    print("\n  Testing list branches with both filters...")
    try:
        # Get a real deployment ID
        real_deployment_id = await get_real_deployment_id(client)
        result = await tool.execute({
            "deployment_id": real_deployment_id,
            "limit": 3
        })
        print(f"    Response: {result}")
        print("  ✅ List branches with both filters test completed")
    except Exception as e:
        print(f"    ❌ List branches with both filters test failed: {e}")
        return False
    
    # Clean up
    await client.disconnect()
    
    print("\n" + "="*60)
    print("📊 SYNTHESIS - List Branches Test Results")
    print("="*60)
    print("✅ Tested scenarios:")
    print("   • List all branches")
    print("   • List branches with deployment filter")
    print("   • List branches with limit")
    print("   • List branches with both filters")
    print(f"\n🔗 API Endpoint: {client.api_base_url}/branches")
    print(f"🔑 Authentication: {'✅ Token present' if client.access_token else '❌ No token'}")
    print("\n📝 Notes:")
    print("   • All tests completed successfully")
    print("   • Real API calls made to local server")
    print("   • HTTP session properly initialized and cleaned up")
    print("   • Filtering capabilities tested")
    print("="*60)
    
    print("\n✅ All list_branches real API tests completed!")
    return True

async def main():
    """Main test runner"""
    print("🚀 Starting list_branches real API tests...\n")
    
    try:
        success = await test_list_branches()
        return 0 if success else 1
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)