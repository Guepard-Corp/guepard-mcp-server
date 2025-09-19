#!/usr/bin/env python3
"""
Real test for CreateSnapshotTool
Tests the create_snapshot functionality with real API calls
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from guepard_mcp.snapshots.tools import CreateSnapshotTool
from guepard_mcp.utils.base import GuepardAPIClient
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from test_utils import get_real_deployment_id, get_fake_deployment_id

async def test_create_snapshot():
    """Test create_snapshot tool with real API calls"""
    print("🧪 Testing create_snapshot tool with real API calls...")
    
    # Create tool instance
    client = GuepardAPIClient()
    tool = CreateSnapshotTool(client)
    
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
    
    # Test 1: Create snapshot for existing deployment
    print("\n  Testing create snapshot for existing deployment...")
    try:
        result = await tool.execute({
            "deployment_id": real_deployment_id,
            "name": "Test Snapshot"
        })
        print(f"    Response: {result}")
        print("  ✅ Create snapshot for deployment test completed")
    except Exception as e:
        print(f"    ❌ Create snapshot for deployment test failed: {e}")
        return False
    
    # Test 2: Create snapshot for existing branch
    print("\n  Testing create snapshot for existing branch...")
    try:
        result = await tool.execute({
            "branch_id": "test-branch-123",
            "name": "Test Branch Snapshot"
        })
        print(f"    Response: {result}")
        print("  ✅ Create snapshot for branch test completed")
    except Exception as e:
        print(f"    ❌ Create snapshot for branch test failed: {e}")
        return False
    
    # Test 3: Create snapshot with description
    print("\n  Testing create snapshot with description...")
    try:
        result = await tool.execute({
            "deployment_id": "test-deploy-123",
            "name": "Test Snapshot with Description",
            "description": "This is a test snapshot"
        })
        print(f"    Response: {result}")
        print("  ✅ Create snapshot with description test completed")
    except Exception as e:
        print(f"    ❌ Create snapshot with description test failed: {e}")
        return False
    
    # Test 4: Create snapshot for non-existent deployment
    print("\n  Testing create snapshot for non-existent deployment...")
    try:
        result = await tool.execute({
            "deployment_id": "non-existent-deploy-999",
            "name": "Test Invalid Snapshot"
        })
        print(f"    Response: {result}")
        print("  ✅ Create snapshot for non-existent deployment test completed")
    except Exception as e:
        print(f"    ❌ Create snapshot for non-existent deployment test failed: {e}")
        return False
    
    # Test 5: Missing required parameters
    print("\n  Testing missing required parameters...")
    try:
        result = await tool.execute({
            "name": "Test Without Source"
        })
        print(f"    Response: {result}")
        print("  ✅ Missing required parameters test completed")
    except Exception as e:
        print(f"    ❌ Missing required parameters test failed: {e}")
        return False
    
    # Clean up
    await client.disconnect()
    
    print("\n" + "="*60)
    print("📊 SYNTHESIS - Create Snapshot Test Results")
    print("="*60)
    print("✅ Tested scenarios:")
    print("   • Create snapshot for existing deployment")
    print("   • Create snapshot for existing branch")
    print("   • Create snapshot with description")
    print("   • Create snapshot for non-existent deployment")
    print("   • Handle missing required parameters")
    print(f"\n🔗 API Endpoint: {client.api_base_url}/snapshots")
    print(f"🔑 Authentication: {'✅ Token present' if client.access_token else '❌ No token'}")
    print("\n📝 Notes:")
    print("   • All tests completed successfully")
    print("   • Real API calls made to local server")
    print("   • HTTP session properly initialized and cleaned up")
    print("   • Various snapshot creation scenarios tested")
    print("="*60)
    
    print("\n✅ All create_snapshot real API tests completed!")
    return True

async def main():
    """Main test runner"""
    print("🚀 Starting create_snapshot real API tests...\n")
    
    try:
        success = await test_create_snapshot()
        return 0 if success else 1
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)