#!/usr/bin/env python3
"""
Real test for ListDeploymentsTool
Tests the list_deployments functionality with real API calls
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from guepard_mcp.deployments.tools import ListDeploymentsTool
from guepard_mcp.utils.base import GuepardAPIClient

async def test_list_deployments():
    """Test list_deployments tool with real API calls"""
    print("🧪 Testing list_deployments tool with real API calls...")
    
    # Create tool instance
    client = GuepardAPIClient()
    tool = ListDeploymentsTool(client)
    
    # Check if we have credentials
    if not client.access_token:
        print("❌ No ACCESS_TOKEN found in environment variables")
        print("   Please set ACCESS_TOKEN in your .env file")
        return False
    
    print(f"   Using API: {client.api_base_url}")
    print(f"   Token: {client.access_token[:10]}...")
    
    # Initialize HTTP session
    await client.connect()
    
    # Test 1: Basic list
    print("\n  Testing basic list...")
    try:
        result = await tool.execute({})
        print(f"    Response: {result}")
        print("  ✅ Basic list test completed")
    except Exception as e:
        print(f"    ❌ Basic list test failed: {e}")
        return False
    
    # Test 2: With status filter
    print("\n  Testing with status filter...")
    try:
        result = await tool.execute({"status": "running"})
        print(f"    Response: {result}")
        print("  ✅ Status filter test completed")
    except Exception as e:
        print(f"    ❌ Status filter test failed: {e}")
        return False
    
    # Test 3: With custom limit
    print("\n  Testing with custom limit...")
    try:
        result = await tool.execute({"limit": 5})
        print(f"    Response: {result}")
        print("  ✅ Custom limit test completed")
    except Exception as e:
        print(f"    ❌ Custom limit test failed: {e}")
        return False
    
    # Test 4: With both status and limit
    print("\n  Testing with status and limit...")
    try:
        result = await tool.execute({"status": "active", "limit": 3})
        print(f"    Response: {result}")
        print("  ✅ Status and limit test completed")
    except Exception as e:
        print(f"    ❌ Status and limit test failed: {e}")
        return False
    
    # Clean up
    await client.disconnect()
    
    print("\n" + "="*60)
    print("📊 SYNTHESIS - List Deployments Test Results")
    print("="*60)
    print("✅ Tested scenarios:")
    print("   • Basic list deployment call")
    print("   • List with status filter (running)")
    print("   • List with custom limit (5)")
    print("   • List with both status and limit filters")
    print(f"\n🔗 API Endpoint: {client.api_base_url}/deploy")
    print(f"🔑 Authentication: {'✅ Token present' if client.access_token else '❌ No token'}")
    print("\n📝 Notes:")
    print("   • All tests completed successfully")
    print("   • Real API calls made to local server")
    print("   • HTTP session properly initialized and cleaned up")
    print("="*60)
    
    print("\n✅ All list_deployments real API tests completed!")
    return True

async def main():
    """Main test runner"""
    print("🚀 Starting list_deployments real API tests...\n")
    
    try:
        success = await test_list_deployments()
        return 0 if success else 1
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)