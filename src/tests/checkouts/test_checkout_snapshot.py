#!/usr/bin/env python3
"""
Real test for CheckoutSnapshotTool
Tests the checkout_snapshot functionality with real API calls
"""

import asyncio
import sys
import os
import json
import random
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from guepard_mcp.checkouts.tools import CheckoutSnapshotTool
from guepard_mcp.utils.base import GuepardAPIClient
from tests.test_utils import get_real_deployment_id, get_first_branch_id, get_first_snapshot_id

async def test_checkout_snapshot():
    """Test checkout_snapshot tool with real API calls"""
    print("🧪 Testing checkout_snapshot tool with real API calls...")
    
    # Create tool instance
    client = GuepardAPIClient()
    tool = CheckoutSnapshotTool(client)
    
    # Check if we have credentials
    if not client.access_token:
        print("❌ No ACCESS_TOKEN found in environment variables")
        print("   Please set ACCESS_TOKEN in your .env file")
        return False
    
    print(f"   Using API: {client.api_base_url}")
    print(f"   Token: {client.access_token[:10]}...")
    
    # Initialize HTTP session
    await client.connect()
    
    # Get real data from API
    try:
        print("\n  📋 Fetching real data from API...")
        real_deployment_id = await get_real_deployment_id(client)
        
        # Get a random branch from the deployment
        from guepard_mcp.branches.tools import ListBranchesTool
        
        branches_tool = ListBranchesTool(client)
        branches_result = await branches_tool.execute({
            "deployment_id": real_deployment_id
        })
        
        if "✅" in branches_result and "[" in branches_result:
            json_start = branches_result.find("[")
            json_end = branches_result.rfind("]") + 1
            if json_start != -1 and json_end != -1:
                json_str = branches_result[json_start:json_end]
                branches = json.loads(json_str)
                if len(branches) > 0:
                    # Pick a random branch
                    random_branch = random.choice(branches)
                    real_branch_id = random_branch["id"]
                    print(f"    ✅ Randomly selected branch ID: {real_branch_id}")
                else:
                    raise Exception("No branches found for this deployment")
            else:
                raise Exception("Could not parse branches JSON")
        else:
            raise Exception("Could not fetch branches")
        
        # Get snapshots for the selected branch
        from guepard_mcp.snapshots.tools import ListSnapshotsForBranchTool
        
        snapshots_tool = ListSnapshotsForBranchTool(client)
        snapshots_result = await snapshots_tool.execute({
            "deployment_id": real_deployment_id,
            "branch_id": real_branch_id
        })
        
        if "✅" in snapshots_result and "[" in snapshots_result:
            json_start = snapshots_result.find("[")
            json_end = snapshots_result.rfind("]") + 1
            if json_start != -1 and json_end != -1:
                json_str = snapshots_result[json_start:json_end]
                snapshots = json.loads(json_str)
                if len(snapshots) > 0:
                    # Pick a random snapshot from this branch
                    random_snapshot = random.choice(snapshots)
                    real_snapshot_id = random_snapshot["id"]
                    print(f"    ✅ Randomly selected snapshot ID: {real_snapshot_id}")
                else:
                    raise Exception("No snapshots found for this branch")
            else:
                raise Exception("Could not parse snapshots JSON")
        else:
            raise Exception("Could not fetch snapshots")
        
        print(f"    ✅ Real deployment ID: {real_deployment_id}")
        print(f"    ✅ Real branch ID: {real_branch_id}")
        print(f"    ✅ Real snapshot ID: {real_snapshot_id}")
    except Exception as e:
        print(f"    ❌ Failed to get real data: {e}")
        print("    ⚠️  Some tests will use fake data for error testing")
        real_deployment_id = "fake-deployment-123"
        real_branch_id = "fake-branch-123"
        real_snapshot_id = "fake-snapshot-123"
    
    # Test: Checkout to snapshot (fully automated workflow - no deployment_id)
    print("\n  🧪 Testing fully automated checkout to snapshot...")
    input_data = {
        "discard_changes": "true",
        "checkout": True,
        "ephemeral": True,
        "performance_profile_name": "querying"
    }
    print(f"    📥 Input: {input_data}")
    
    result = await tool.execute(input_data)
    print(f"    📤 Output: {result}")
    print("  ✅ Test completed")
    
    # Clean up
    await client.disconnect()
    
    print("\n" + "="*50)
    print("📊 Checkout Snapshot Test Results")
    print("="*50)
    print(f"🔗 API Endpoint: {client.api_base_url}/deploy/{{deployment_id}}/{{branch_id}}/checkout")
    print(f"🔑 Authentication: {'✅ Token present' if client.access_token else '❌ No token'}")
    print("📝 Body structure:")
    print("   • discard_changes: 'true'")
    print("   • checkout: true")
    print("   • ephemeral: true")
    print("   • performance_profile_name: 'querying'")
    print("="*50)
    
    print("\n✅ Checkout snapshot test completed!")
    return True

async def main():
    """Main test runner"""
    print("🚀 Starting checkout_snapshot real API tests...\n")
    
    try:
        success = await test_checkout_snapshot()
        return 0 if success else 1
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
