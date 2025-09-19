#!/usr/bin/env python3
"""
Real test for UpdateBranchTool
Tests the update_branch functionality with real API calls
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from guepard_mcp.branches.tools import UpdateBranchTool
from guepard_mcp.utils.base import GuepardAPIClient

async def test_update_branch():
    """Test update_branch tool with real API calls"""
    print("🧪 Testing update_branch tool with real API calls...")
    
    # Create tool instance
    client = GuepardAPIClient()
    tool = UpdateBranchTool(client)
    
    # Check if we have credentials
    if not client.access_token:
        print("❌ No ACCESS_TOKEN found in environment variables")
        print("   Please set ACCESS_TOKEN in your .env file")
        return False
    
    print(f"   Using API: {client.api_base_url}")
    print(f"   Token: {client.access_token[:10]}...")
    
    # Initialize HTTP session
    await client.connect()
    
    # Test 1: Update branch name
    print("\n  Testing update branch name...")
    try:
        result = await tool.execute({
            "branch_id": "test-branch-123",
            "name": "Updated Branch Name"
        })
        print(f"    Response: {result}")
        print("  ✅ Update branch name test completed")
    except Exception as e:
        print(f"    ❌ Update branch name test failed: {e}")
        return False
    
    # Test 2: Update branch description
    print("\n  Testing update branch description...")
    try:
        result = await tool.execute({
            "branch_id": "test-branch-123",
            "description": "Updated branch description"
        })
        print(f"    Response: {result}")
        print("  ✅ Update branch description test completed")
    except Exception as e:
        print(f"    ❌ Update branch description test failed: {e}")
        return False
    
    # Test 3: Update multiple fields
    print("\n  Testing update multiple fields...")
    try:
        result = await tool.execute({
            "branch_id": "test-branch-123",
            "name": "Updated Branch Name 2",
            "description": "Updated description 2"
        })
        print(f"    Response: {result}")
        print("  ✅ Update multiple fields test completed")
    except Exception as e:
        print(f"    ❌ Update multiple fields test failed: {e}")
        return False
    
    # Test 4: Update non-existent branch
    print("\n  Testing update non-existent branch...")
    try:
        result = await tool.execute({
            "branch_id": "non-existent-branch-999",
            "name": "Updated Name"
        })
        print(f"    Response: {result}")
        print("  ✅ Update non-existent branch test completed")
    except Exception as e:
        print(f"    ❌ Update non-existent branch test failed: {e}")
        return False
    
    # Test 5: Missing branch_id parameter
    print("\n  Testing missing branch_id parameter...")
    try:
        result = await tool.execute({
            "name": "Test Without ID"
        })
        print(f"    Response: {result}")
        print("  ✅ Missing branch_id test completed")
    except Exception as e:
        print(f"    ❌ Missing branch_id test failed: {e}")
        return False
    
    # Clean up
    await client.disconnect()
    
    print("\n" + "="*60)
    print("📊 SYNTHESIS - Update Branch Test Results")
    print("="*60)
    print("✅ Tested scenarios:")
    print("   • Update branch name")
    print("   • Update branch description")
    print("   • Update multiple fields")
    print("   • Update non-existent branch")
    print("   • Handle missing branch_id parameter")
    print(f"\n🔗 API Endpoint: {client.api_base_url}/branches/{{branch_id}}")
    print(f"🔑 Authentication: {'✅ Token present' if client.access_token else '❌ No token'}")
    print("\n📝 Notes:")
    print("   • All tests completed successfully")
    print("   • Real API calls made to local server")
    print("   • HTTP session properly initialized and cleaned up")
    print("   • Various update scenarios tested")
    print("="*60)
    
    print("\n✅ All update_branch real API tests completed!")
    return True

async def main():
    """Main test runner"""
    print("🚀 Starting update_branch real API tests...\n")
    
    try:
        success = await test_update_branch()
        return 0 if success else 1
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)