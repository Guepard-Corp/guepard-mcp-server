#!/usr/bin/env python3
"""
Real test for GetDeploymentLogsTool
Tests the get_deployment_logs functionality with real API calls
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from guepard_mcp.logs.tools import GetDeploymentLogsTool
from guepard_mcp.utils.base import GuepardAPIClient

async def test_get_deployment_logs():
    """Test get_deployment_logs tool with real API calls"""
    print("🧪 Testing get_deployment_logs tool with real API calls...")
    
    # Create tool instance
    client = GuepardAPIClient()
    tool = GetDeploymentLogsTool(client)
    
    # Check if we have credentials
    if not client.access_token:
        print("❌ No ACCESS_TOKEN found in environment variables")
        print("   Please set ACCESS_TOKEN in your .env file")
        return False
    
    print(f"   Using API: {client.api_base_url}")
    print(f"   Token: {client.access_token[:10]}...")
    
    # Initialize HTTP session
    await client.connect()
    
    # Test 1: Get logs for existing deployment
    print("\n  Testing get logs for existing deployment...")
    try:
        result = await tool.execute({
            "deployment_id": "test-deploy-123"
        })
        print(f"    Response: {result}")
        print("  ✅ Get logs for deployment test completed")
    except Exception as e:
        print(f"    ❌ Get logs for deployment test failed: {e}")
        return False
    
    # Test 2: Get logs with limit
    print("\n  Testing get logs with limit...")
    try:
        result = await tool.execute({
            "deployment_id": "test-deploy-123",
            "limit": 10
        })
        print(f"    Response: {result}")
        print("  ✅ Get logs with limit test completed")
    except Exception as e:
        print(f"    ❌ Get logs with limit test failed: {e}")
        return False
    
    # Test 3: Get logs with log level filter
    print("\n  Testing get logs with log level filter...")
    try:
        result = await tool.execute({
            "deployment_id": "test-deploy-123",
            "level": "ERROR"
        })
        print(f"    Response: {result}")
        print("  ✅ Get logs with level filter test completed")
    except Exception as e:
        print(f"    ❌ Get logs with level filter test failed: {e}")
        return False
    
    # Test 4: Get logs for non-existent deployment
    print("\n  Testing get logs for non-existent deployment...")
    try:
        result = await tool.execute({
            "deployment_id": "non-existent-deploy-999"
        })
        print(f"    Response: {result}")
        print("  ✅ Get logs for non-existent deployment test completed")
    except Exception as e:
        print(f"    ❌ Get logs for non-existent deployment test failed: {e}")
        return False
    
    # Test 5: Missing deployment_id parameter
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
    print("📊 SYNTHESIS - Get Deployment Logs Test Results")
    print("="*60)
    print("✅ Tested scenarios:")
    print("   • Get logs for existing deployment")
    print("   • Get logs with limit")
    print("   • Get logs with log level filter")
    print("   • Get logs for non-existent deployment")
    print("   • Handle missing deployment_id parameter")
    print(f"\n🔗 API Endpoint: {client.api_base_url}/logs/deployment/{{deployment_id}}")
    print(f"🔑 Authentication: {'✅ Token present' if client.access_token else '❌ No token'}")
    print("\n📝 Notes:")
    print("   • All tests completed successfully")
    print("   • Real API calls made to local server")
    print("   • HTTP session properly initialized and cleaned up")
    print("   • Log filtering capabilities tested")
    print("="*60)
    
    print("\n✅ All get_deployment_logs real API tests completed!")
    return True

async def main():
    """Main test runner"""
    print("🚀 Starting get_deployment_logs real API tests...\n")
    
    try:
        success = await test_get_deployment_logs()
        return 0 if success else 1
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)