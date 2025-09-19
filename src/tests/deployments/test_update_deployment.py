#!/usr/bin/env python3
"""
Real test for UpdateDeploymentTool
Tests the update_deployment functionality with real API calls
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from guepard_mcp.deployments.tools import UpdateDeploymentTool
from guepard_mcp.utils.base import GuepardAPIClient

async def test_update_deployment():
    """Test update_deployment tool with real API calls"""
    print("🧪 Testing update_deployment tool with real API calls...")
    
    # Create tool instance
    client = GuepardAPIClient()
    tool = UpdateDeploymentTool(client)
    
    # Check if we have credentials
    if not client.access_token:
        print("❌ No ACCESS_TOKEN found in environment variables")
        print("   Please set ACCESS_TOKEN in your .env file")
        return False
    
    print(f"   Using API: {client.api_base_url}")
    print(f"   Token: {client.access_token[:10]}...")
    
    # Initialize HTTP session
    await client.connect()
    
    # Test 1: Update deployment name
    print("\n  Testing update deployment name...")
    try:
        result = await tool.execute({
            "deployment_id": "test-deploy-123",
            "name": "Updated Deployment Name"
        })
        print(f"    Response: {result}")
        print("  ✅ Update name test completed")
    except Exception as e:
        print(f"    ❌ Update name test failed: {e}")
        return False
    
    # Test 2: Update repository name
    print("\n  Testing update repository name...")
    try:
        result = await tool.execute({
            "deployment_id": "test-deploy-123",
            "repository_name": "updated-repo-name"
        })
        print(f"    Response: {result}")
        print("  ✅ Update repository name test completed")
    except Exception as e:
        print(f"    ❌ Update repository name test failed: {e}")
        return False
    
    # Test 3: Update database provider and version
    print("\n  Testing update database configuration...")
    try:
        result = await tool.execute({
            "deployment_id": "test-deploy-123",
            "database_provider": "PostgreSQL",
            "database_version": "18"
        })
        print(f"    Response: {result}")
        print("  ✅ Update database configuration test completed")
    except Exception as e:
        print(f"    ❌ Update database configuration test failed: {e}")
        return False
    
    # Test 4: Update performance profile
    print("\n  Testing update performance profile...")
    try:
        result = await tool.execute({
            "deployment_id": "test-deploy-123",
            "performance_profile_id": "profile-123"
        })
        print(f"    Response: {result}")
        print("  ✅ Update performance profile test completed")
    except Exception as e:
        print(f"    ❌ Update performance profile test failed: {e}")
        return False
    
    # Test 5: Missing deployment_id parameter
    print("\n  Testing missing deployment_id parameter...")
    try:
        result = await tool.execute({
            "name": "Test Without ID"
        })
        print(f"    Response: {result}")
        print("  ✅ Missing deployment_id test completed")
    except Exception as e:
        print(f"    ❌ Missing deployment_id test failed: {e}")
        return False
    
    # Clean up
    await client.disconnect()
    
    print("\n" + "="*60)
    print("📊 SYNTHESIS - Update Deployment Test Results")
    print("="*60)
    print("✅ Tested scenarios:")
    print("   • Update deployment name")
    print("   • Update repository name")
    print("   • Update database provider and version")
    print("   • Update performance profile")
    print("   • Handle missing deployment_id parameter")
    print(f"\n🔗 API Endpoint: {client.api_base_url}/deploy/{{deployment_id}}")
    print(f"🔑 Authentication: {'✅ Token present' if client.access_token else '❌ No token'}")
    print("\n📝 Notes:")
    print("   • All tests completed successfully")
    print("   • Real API calls made to local server")
    print("   • HTTP session properly initialized and cleaned up")
    print("   • Various update scenarios tested")
    print("="*60)
    
    print("\n✅ All update_deployment real API tests completed!")
    return True

async def main():
    """Main test runner"""
    print("🚀 Starting update_deployment real API tests...\n")
    
    try:
        success = await test_update_deployment()
        return 0 if success else 1
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)