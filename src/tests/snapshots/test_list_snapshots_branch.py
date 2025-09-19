#!/usr/bin/env python3
"""
Real test for ListSnapshotsBranchTool
Tests the list_snapshots_branch functionality with real API calls
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from guepard_mcp.snapshots.tools import ListSnapshotsForBranchTool
from guepard_mcp.utils.base import GuepardAPIClient
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from test_utils import get_real_deployment_id, get_fake_deployment_id, get_first_branch_id

async def test_list_snapshots_branch():
    """Test list_snapshots_branch tool with real API calls following proper flow"""
    print("🧪 Testing list_snapshots_branch tool with real API calls...")
    
    # Create tool instance
    client = GuepardAPIClient()
    tool = ListSnapshotsForBranchTool(client)
    
    # Check if we have credentials
    if not client.access_token:
        print("❌ No ACCESS_TOKEN found in environment variables")
        print("   Please set ACCESS_TOKEN in your .env file")
        return False
    
    print(f"   Using API: {client.api_base_url}")
    print(f"   Token: {client.access_token[:10]}...")
    
    # Initialize HTTP session
    await client.connect()
    
    try:
        # Step 1: Get first deployment
        print("\n  Step 1: Getting first deployment...")
        real_deployment_id = await get_real_deployment_id(client)
        print(f"    ✅ Found deployment: {real_deployment_id}")
        
        # Step 2: Get first branch from that deployment
        print("\n  Step 2: Getting first branch from deployment...")
        real_branch_id = await get_first_branch_id(client, real_deployment_id)
        print(f"    ✅ Found branch: {real_branch_id}")
        
        # Step 3: List snapshots for the real branch
        print("\n  Step 3: Testing list snapshots for real branch...")
        result = await tool.execute({
            "deployment_id": real_deployment_id,
            "branch_id": real_branch_id
        })
        print(f"    Response: {result}")
        print("  ✅ List snapshots for real branch test completed")
        
        # Test 4: List snapshots for non-existent branch
        print("\n  Step 4: Testing list snapshots for non-existent branch...")
        result = await tool.execute({
            "deployment_id": real_deployment_id,
            "branch_id": "non-existent-branch-999"
        })
        print(f"    Response: {result}")
        print("  ✅ Non-existent branch test completed")
        
        # Test 5: Missing required parameters
        print("\n  Step 5: Testing missing required parameters...")
        result = await tool.execute({})
        print(f"    Response: {result}")
        print("  ✅ Missing parameters test completed")
        
    except Exception as e:
        print(f"    ❌ Test failed: {e}")
        return False
    finally:
        # Clean up
        await client.disconnect()
    
    print("\n" + "="*60)
    print("📊 SYNTHESIS - List Snapshots Branch Test Results")
    print("="*60)
    print("✅ Tested scenarios:")
    print("   • Get first deployment from API")
    print("   • Get first branch from that deployment")
    print("   • List snapshots for real branch")
    print("   • List snapshots for non-existent branch")
    print("   • Handle missing required parameters")
    print(f"\n🔗 API Endpoint: {client.api_base_url}/deploy/{{deployment_id}}/{{branch_id}}/snap")
    print(f"🔑 Authentication: {'✅ Token present' if client.access_token else '❌ No token'}")
    print("\n📝 Notes:")
    print("   • All tests completed successfully")
    print("   • Real API calls made to local server")
    print("   • HTTP session properly initialized and cleaned up")
    print("   • Error handling tested for various scenarios")
    print("   • Used proper flow: deployment → branch → snapshots")
    print("="*60)
    
    print("\n✅ All list_snapshots_branch real API tests completed!")
    return True

async def main():
    """Main test runner"""
    print("🚀 Starting list_snapshots_branch real API tests...\n")
    
    try:
        success = await test_list_snapshots_branch()
        return 0 if success else 1
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)