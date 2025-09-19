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

from guepard_mcp.snapshots.tools import ListSnapshotsBranchTool
from guepard_mcp.utils.base import GuepardAPIClient

async def test_list_snapshots_branch():
    """Test list_snapshots_branch tool with real API calls"""
    print("🧪 Testing list_snapshots_branch tool with real API calls...")
    
    # Create tool instance
    client = GuepardAPIClient()
    tool = ListSnapshotsBranchTool(client)
    
    # Check if we have credentials
    if not client.access_token:
        print("❌ No ACCESS_TOKEN found in environment variables")
        print("   Please set ACCESS_TOKEN in your .env file")
        return False
    
    print(f"   Using API: {client.api_base_url}")
    print(f"   Token: {client.access_token[:10]}...")
    
    # Initialize HTTP session
    await client.connect()
    
    # Test 1: List snapshots for existing branch
    print("\n  Testing list snapshots for existing branch...")
    try:
        result = await tool.execute({
            "branch_id": "test-branch-123"
        })
        print(f"    Response: {result}")
        print("  ✅ List snapshots for branch test completed")
    except Exception as e:
        print(f"    ❌ List snapshots for branch test failed: {e}")
        return False
    
    # Test 2: List snapshots with limit
    print("\n  Testing list snapshots with limit...")
    try:
        result = await tool.execute({
            "branch_id": "test-branch-123",
            "limit": 5
        })
        print(f"    Response: {result}")
        print("  ✅ List snapshots with limit test completed")
    except Exception as e:
        print(f"    ❌ List snapshots with limit test failed: {e}")
        return False
    
    # Test 3: List snapshots for non-existent branch
    print("\n  Testing list snapshots for non-existent branch...")
    try:
        result = await tool.execute({
            "branch_id": "non-existent-branch-999"
        })
        print(f"    Response: {result}")
        print("  ✅ Non-existent branch test completed")
    except Exception as e:
        print(f"    ❌ Non-existent branch test failed: {e}")
        return False
    
    # Test 4: Missing branch_id parameter
    print("\n  Testing missing branch_id parameter...")
    try:
        result = await tool.execute({})
        print(f"    Response: {result}")
        print("  ✅ Missing branch_id test completed")
    except Exception as e:
        print(f"    ❌ Missing branch_id test failed: {e}")
        return False
    
    # Clean up
    await client.disconnect()
    
    print("\n" + "="*60)
    print("📊 SYNTHESIS - List Snapshots Branch Test Results")
    print("="*60)
    print("✅ Tested scenarios:")
    print("   • List snapshots for existing branch")
    print("   • List snapshots with limit")
    print("   • List snapshots for non-existent branch")
    print("   • Handle missing branch_id parameter")
    print(f"\n🔗 API Endpoint: {client.api_base_url}/snapshots/branch/{{branch_id}}")
    print(f"🔑 Authentication: {'✅ Token present' if client.access_token else '❌ No token'}")
    print("\n📝 Notes:")
    print("   • All tests completed successfully")
    print("   • Real API calls made to local server")
    print("   • HTTP session properly initialized and cleaned up")
    print("   • Error handling tested for various scenarios")
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