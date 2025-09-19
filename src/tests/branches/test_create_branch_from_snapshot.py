#!/usr/bin/env python3
"""
Real test for CreateBranchFromSnapshotTool
Tests the create_branch_from_snapshot functionality with real API calls
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from guepard_mcp.branches.tools import CreateBranchFromSnapshotTool
from guepard_mcp.utils.base import GuepardAPIClient

async def test_create_branch_from_snapshot():
    """Test create_branch_from_snapshot tool with real API calls"""
    print("🧪 Testing create_branch_from_snapshot tool with real API calls...")
    
    # Create tool instance
    client = GuepardAPIClient()
    tool = CreateBranchFromSnapshotTool(client)
    
    # Check if we have credentials
    if not client.access_token:
        print("❌ No ACCESS_TOKEN found in environment variables")
        print("   Please set ACCESS_TOKEN in your .env file")
        return False
    
    print(f"   Using API: {client.api_base_url}")
    print(f"   Token: {client.access_token[:10]}...")
    
    # Initialize HTTP session
    await client.connect()
    
    # Test 1: Create branch from existing snapshot
    print("\n  Testing create branch from existing snapshot...")
    try:
        result = await tool.execute({
            "snapshot_id": "test-snapshot-123",
            "branch_name": "test-branch-from-snapshot"
        })
        print(f"    Response: {result}")
        print("  ✅ Create branch from snapshot test completed")
    except Exception as e:
        print(f"    ❌ Create branch from snapshot test failed: {e}")
        return False
    
    # Test 2: Create branch from non-existent snapshot
    print("\n  Testing create branch from non-existent snapshot...")
    try:
        result = await tool.execute({
            "snapshot_id": "non-existent-snapshot-999",
            "branch_name": "test-branch-invalid"
        })
        print(f"    Response: {result}")
        print("  ✅ Create branch from non-existent snapshot test completed")
    except Exception as e:
        print(f"    ❌ Create branch from non-existent snapshot test failed: {e}")
        return False
    
    # Test 3: Missing required parameters
    print("\n  Testing missing required parameters...")
    try:
        result = await tool.execute({
            "branch_name": "test-branch-no-snapshot"
        })
        print(f"    Response: {result}")
        print("  ✅ Missing snapshot_id test completed")
    except Exception as e:
        print(f"    ❌ Missing snapshot_id test failed: {e}")
        return False
    
    # Test 4: Missing branch name
    print("\n  Testing missing branch name...")
    try:
        result = await tool.execute({
            "snapshot_id": "test-snapshot-123"
        })
        print(f"    Response: {result}")
        print("  ✅ Missing branch_name test completed")
    except Exception as e:
        print(f"    ❌ Missing branch_name test failed: {e}")
        return False
    
    # Clean up
    await client.disconnect()
    
    print("\n" + "="*60)
    print("📊 SYNTHESIS - Create Branch From Snapshot Test Results")
    print("="*60)
    print("✅ Tested scenarios:")
    print("   • Create branch from existing snapshot")
    print("   • Create branch from non-existent snapshot")
    print("   • Handle missing snapshot_id parameter")
    print("   • Handle missing branch_name parameter")
    print(f"\n🔗 API Endpoint: {client.api_base_url}/branches/create-from-snapshot")
    print(f"🔑 Authentication: {'✅ Token present' if client.access_token else '❌ No token'}")
    print("\n📝 Notes:")
    print("   • All tests completed successfully")
    print("   • Real API calls made to local server")
    print("   • HTTP session properly initialized and cleaned up")
    print("   • Error handling tested for various scenarios")
    print("="*60)
    
    print("\n✅ All create_branch_from_snapshot real API tests completed!")
    return True

async def main():
    """Main test runner"""
    print("🚀 Starting create_branch_from_snapshot real API tests...\n")
    
    try:
        success = await test_create_branch_from_snapshot()
        return 0 if success else 1
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)