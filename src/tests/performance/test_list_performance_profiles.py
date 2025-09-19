#!/usr/bin/env python3
"""
Real test for ListPerformanceProfilesTool
Tests the list_performance_profiles functionality with real API calls
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from guepard_mcp.performance.tools import ListPerformanceProfilesTool
from guepard_mcp.utils.base import GuepardAPIClient

async def test_list_performance_profiles():
    """Test list_performance_profiles tool with real API calls"""
    print("🧪 Testing list_performance_profiles tool with real API calls...")
    
    # Create tool instance
    client = GuepardAPIClient()
    tool = ListPerformanceProfilesTool(client)
    
    # Check if we have credentials
    if not client.access_token:
        print("❌ No ACCESS_TOKEN found in environment variables")
        print("   Please set ACCESS_TOKEN in your .env file")
        return False
    
    print(f"   Using API: {client.api_base_url}")
    print(f"   Token: {client.access_token[:10]}...")
    
    # Initialize HTTP session
    await client.connect()
    
    # Test 1: List all performance profiles
    print("\n  Testing list all performance profiles...")
    try:
        result = await tool.execute({})
        print(f"    Response: {result}")
        print("  ✅ List all profiles test completed")
    except Exception as e:
        print(f"    ❌ List all profiles test failed: {e}")
        return False
    
    # Test 2: List profiles with database provider filter
    print("\n  Testing list profiles with database provider filter...")
    try:
        result = await tool.execute({
            "database_provider": "PostgreSQL"
        })
        print(f"    Response: {result}")
        print("  ✅ Database provider filter test completed")
    except Exception as e:
        print(f"    ❌ Database provider filter test failed: {e}")
        return False
    
    # Test 3: List profiles with database version filter
    print("\n  Testing list profiles with database version filter...")
    try:
        result = await tool.execute({
            "database_version": "17"
        })
        print(f"    Response: {result}")
        print("  ✅ Database version filter test completed")
    except Exception as e:
        print(f"    ❌ Database version filter test failed: {e}")
        return False
    
    # Test 4: List profiles with both filters
    print("\n  Testing list profiles with both filters...")
    try:
        result = await tool.execute({
            "database_provider": "PostgreSQL",
            "database_version": "18"
        })
        print(f"    Response: {result}")
        print("  ✅ Both filters test completed")
    except Exception as e:
        print(f"    ❌ Both filters test failed: {e}")
        return False
    
    # Clean up
    await client.disconnect()
    
    print("\n" + "="*60)
    print("📊 SYNTHESIS - List Performance Profiles Test Results")
    print("="*60)
    print("✅ Tested scenarios:")
    print("   • List all performance profiles")
    print("   • List profiles with database provider filter")
    print("   • List profiles with database version filter")
    print("   • List profiles with both filters")
    print(f"\n🔗 API Endpoint: {client.api_base_url}/performance/profiles")
    print(f"🔑 Authentication: {'✅ Token present' if client.access_token else '❌ No token'}")
    print("\n📝 Notes:")
    print("   • All tests completed successfully")
    print("   • Real API calls made to local server")
    print("   • HTTP session properly initialized and cleaned up")
    print("   • Filtering capabilities tested")
    print("="*60)
    
    print("\n✅ All list_performance_profiles real API tests completed!")
    return True

async def main():
    """Main test runner"""
    print("🚀 Starting list_performance_profiles real API tests...\n")
    
    try:
        success = await test_list_performance_profiles()
        return 0 if success else 1
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)