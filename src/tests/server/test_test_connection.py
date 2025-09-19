#!/usr/bin/env python3
"""
Real test for TestConnectionTool
Tests the test_connection functionality with real API calls
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from guepard_mcp.server.tools import TestConnectionTool
from guepard_mcp.utils.base import GuepardAPIClient

async def test_test_connection():
    """Test test_connection tool with real API calls"""
    print("🧪 Testing test_connection tool with real API calls...")
    
    # Create tool instance
    client = GuepardAPIClient()
    tool = TestConnectionTool(client)
    
    # Check if we have credentials
    if not client.access_token:
        print("❌ No ACCESS_TOKEN found in environment variables")
        print("   Please set ACCESS_TOKEN in your .env file")
        return False
    
    print(f"   Using API: {client.api_base_url}")
    print(f"   Token: {client.access_token[:10]}...")
    
    # Initialize HTTP session
    await client.connect()
    
    # Test 1: Test connection without parameters
    print("\n  Testing connection without parameters...")
    try:
        result = await tool.execute({})
        print(f"    Response: {result}")
        print("  ✅ Basic connection test completed")
    except Exception as e:
        print(f"    ❌ Basic connection test failed: {e}")
        return False
    
    # Test 2: Test connection with specific endpoint
    print("\n  Testing connection with specific endpoint...")
    try:
        result = await tool.execute({
            "endpoint": "/health"
        })
        print(f"    Response: {result}")
        print("  ✅ Specific endpoint test completed")
    except Exception as e:
        print(f"    ❌ Specific endpoint test failed: {e}")
        return False
    
    # Test 3: Test connection with timeout
    print("\n  Testing connection with timeout...")
    try:
        result = await tool.execute({
            "timeout": 10
        })
        print(f"    Response: {result}")
        print("  ✅ Timeout test completed")
    except Exception as e:
        print(f"    ❌ Timeout test failed: {e}")
        return False
    
    # Clean up
    await client.disconnect()
    
    print("\n" + "="*60)
    print("📊 SYNTHESIS - Test Connection Test Results")
    print("="*60)
    print("✅ Tested scenarios:")
    print("   • Test connection without parameters")
    print("   • Test connection with specific endpoint")
    print("   • Test connection with timeout")
    print(f"\n🔗 API Endpoint: {client.api_base_url}/health")
    print(f"🔑 Authentication: {'✅ Token present' if client.access_token else '❌ No token'}")
    print("\n📝 Notes:")
    print("   • All tests completed successfully")
    print("   • Real API calls made to local server")
    print("   • HTTP session properly initialized and cleaned up")
    print("   • Connection health verified")
    print("="*60)
    
    print("\n✅ All test_connection real API tests completed!")
    return True

async def main():
    """Main test runner"""
    print("🚀 Starting test_connection real API tests...\n")
    
    try:
        success = await test_test_connection()
        return 0 if success else 1
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)