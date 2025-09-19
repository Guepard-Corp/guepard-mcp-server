#!/usr/bin/env python3
"""
Real test for GetPerformanceProfilesTool
Tests the get_performance_profiles functionality with real API calls
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from guepard_mcp.performance.tools import GetPerformanceProfilesTool
from guepard_mcp.utils.base import GuepardAPIClient

async def test_get_performance_profiles():
    """Test get_performance_profiles tool with real API calls"""
    print("🧪 Testing get_performance_profiles tool with real API calls...")
    
    # Create tool instance
    client = GuepardAPIClient()
    tool = GetPerformanceProfilesTool(client)
    
    # Check if we have credentials
    if not client.access_token:
        print("❌ No ACCESS_TOKEN found in environment variables")
        print("   Please set ACCESS_TOKEN in your .env file")
        return False
    
    print(f"   Using API: {client.api_base_url}")
    print(f"   Token: {client.access_token[:10]}...")
    
    # Initialize HTTP session
    await client.connect()
    
    # Test 1: Get performance profile by ID
    print("\n  Testing get performance profile by ID...")
    try:
        result = await tool.execute({
            "profile_id": "test-profile-123"
        })
        print(f"    Response: {result}")
        print("  ✅ Get profile by ID test completed")
    except Exception as e:
        print(f"    ❌ Get profile by ID test failed: {e}")
        return False
    
    # Test 2: Get performance profile by name
    print("\n  Testing get performance profile by name...")
    try:
        result = await tool.execute({
            "name": "test-profile"
        })
        print(f"    Response: {result}")
        print("  ✅ Get profile by name test completed")
    except Exception as e:
        print(f"    ❌ Get profile by name test failed: {e}")
        return False
    
    # Test 3: Get performance profile by database provider
    print("\n  Testing get performance profile by database provider...")
    try:
        result = await tool.execute({
            "database_provider": "PostgreSQL"
        })
        print(f"    Response: {result}")
        print("  ✅ Get profile by database provider test completed")
    except Exception as e:
        print(f"    ❌ Get profile by database provider test failed: {e}")
        return False
    
    # Test 4: Get performance profile for non-existent ID
    print("\n  Testing get performance profile for non-existent ID...")
    try:
        result = await tool.execute({
            "profile_id": "non-existent-profile-999"
        })
        print(f"    Response: {result}")
        print("  ✅ Get non-existent profile test completed")
    except Exception as e:
        print(f"    ❌ Get non-existent profile test failed: {e}")
        return False
    
    # Test 5: Missing parameters
    print("\n  Testing missing parameters...")
    try:
        result = await tool.execute({})
        print(f"    Response: {result}")
        print("  ✅ Missing parameters test completed")
    except Exception as e:
        print(f"    ❌ Missing parameters test failed: {e}")
        return False
    
    # Clean up
    await client.disconnect()
    
    print("\n" + "="*60)
    print("📊 SYNTHESIS - Get Performance Profiles Test Results")
    print("="*60)
    print("✅ Tested scenarios:")
    print("   • Get performance profile by ID")
    print("   • Get performance profile by name")
    print("   • Get performance profile by database provider")
    print("   • Get performance profile for non-existent ID")
    print("   • Handle missing parameters")
    print(f"\n🔗 API Endpoint: {client.api_base_url}/performance/profiles")
    print(f"🔑 Authentication: {'✅ Token present' if client.access_token else '❌ No token'}")
    print("\n📝 Notes:")
    print("   • All tests completed successfully")
    print("   • Real API calls made to local server")
    print("   • HTTP session properly initialized and cleaned up")
    print("   • Various search criteria tested")
    print("="*60)
    
    print("\n✅ All get_performance_profiles real API tests completed!")
    return True

async def main():
    """Main test runner"""
    print("🚀 Starting get_performance_profiles real API tests...\n")
    
    try:
        success = await test_get_performance_profiles()
        return 0 if success else 1
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
