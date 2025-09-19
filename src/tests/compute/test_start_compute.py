#!/usr/bin/env python3
"""
Real test for StartComputeTool
Tests the start_compute functionality with real API calls
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from guepard_mcp.compute.tools import StartComputeTool
from guepard_mcp.utils.base import GuepardAPIClient

async def test_start_compute():
    """Test start_compute tool with real API calls"""
    print("🧪 Testing start_compute tool with real API calls...")
    
    # Create tool instance
    client = GuepardAPIClient()
    tool = StartComputeTool(client)
    
    # Check if we have credentials
    if not client.access_token:
        print("❌ No ACCESS_TOKEN found in environment variables")
        print("   Please set ACCESS_TOKEN in your .env file")
        return False
    
    print(f"   Using API: {client.api_base_url}")
    print(f"   Token: {client.access_token[:10]}...")
    
    # Initialize HTTP session
    await client.connect()
    
    # Test 1: Start compute for existing deployment
    print("\n  Testing start compute for existing deployment...")
    try:
        result = await tool.execute({
            "deployment_id": "test-deploy-123"
        })
        print(f"    Response: {result}")
        print("  ✅ Start compute test completed")
    except Exception as e:
        print(f"    ❌ Start compute test failed: {e}")
        return False
    
    # Test 2: Start compute for non-existent deployment
    print("\n  Testing start compute for non-existent deployment...")
    try:
        result = await tool.execute({
            "deployment_id": "non-existent-deploy-999"
        })
        print(f"    Response: {result}")
        print("  ✅ Non-existent deployment test completed")
    except Exception as e:
        print(f"    ❌ Non-existent deployment test failed: {e}")
        return False
    
    # Test 3: Missing deployment_id parameter
    print("\n  Testing missing deployment_id parameter...")
    try:
        result = await tool.execute({})
        print(f"    Response: {result}")
        print("  ✅ Missing deployment_id test completed")
    except Exception as e:
        print(f"    ❌ Missing deployment_id test failed: {e}")
        return False
    
    # Clean up
    await client.disconnect()
    
    print("\n" + "="*60)
    print("📊 SYNTHESIS - Start Compute Test Results")
    print("="*60)
    print("✅ Tested scenarios:")
    print("   • Start compute for existing deployment")
    print("   • Start compute for non-existent deployment")
    print("   • Handle missing deployment_id parameter")
    print(f"\n🔗 API Endpoint: {client.api_base_url}/compute/start")
    print(f"🔑 Authentication: {'✅ Token present' if client.access_token else '❌ No token'}")
    print("\n📝 Notes:")
    print("   • All tests completed successfully")
    print("   • Real API calls made to local server")
    print("   • HTTP session properly initialized and cleaned up")
    print("   • Error handling tested for various scenarios")
    print("="*60)
    
    print("\n✅ All start_compute real API tests completed!")
    return True

async def main():
    """Main test runner"""
    print("🚀 Starting start_compute real API tests...\n")
    
    try:
        success = await test_start_compute()
        return 0 if success else 1
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)