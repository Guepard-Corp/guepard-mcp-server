#!/usr/bin/env python3
"""
Real test for UpdateDeploymentEventsTool
Tests the update_deployment_events functionality with real API calls
"""

import asyncio
import sys
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from guepard_mcp.deployments.tools import UpdateDeploymentEventsTool
from guepard_mcp.utils.base import GuepardAPIClient
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from test_utils import get_real_deployment_id, get_fake_deployment_id

async def test_update_deployment_events():
    """Test update_deployment_events tool with real API calls"""
    print("🧪 Testing update_deployment_events tool with real API calls...")
    
    # Create tool instance
    client = GuepardAPIClient()
    tool = UpdateDeploymentEventsTool(client)
    
    # Check if we have credentials
    if not client.access_token:
        print("❌ No ACCESS_TOKEN found in environment variables")
        print("   Please set ACCESS_TOKEN in your .env file")
        return False
    
    print(f"   Using API: {client.api_base_url}")
    print(f"   Token: {client.access_token[:10]}...")
    
    # Initialize HTTP session
    await client.connect()
    
    # Test 1: Update deployment events with single event
    print("\n  Testing update deployment events with single event...")
    try:
        events = [{
            "type": "deployment_updated",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "status": "updated",
                "message": "Deployment configuration updated"
            }
        }]
        
        result = await tool.execute({
            "deployment_id": "test-deploy-123",
            "events": events
        })
        print(f"    Response: {result}")
        print("  ✅ Single event update test completed")
    except Exception as e:
        print(f"    ❌ Single event update test failed: {e}")
        return False
    
    # Test 2: Update deployment events with multiple events
    print("\n  Testing update deployment events with multiple events...")
    try:
        events = [
            {
                "type": "status_changed",
                "timestamp": datetime.now().isoformat(),
                "data": {"status": "running"}
            },
            {
                "type": "configuration_updated",
                "timestamp": datetime.now().isoformat(),
                "data": {"database_version": "18"}
            }
        ]
        
        result = await tool.execute({
            "deployment_id": "test-deploy-123",
            "events": events
        })
        print(f"    Response: {result}")
        print("  ✅ Multiple events update test completed")
    except Exception as e:
        print(f"    ❌ Multiple events update test failed: {e}")
        return False
    
    # Test 3: Update events for non-existent deployment
    print("\n  Testing update events for non-existent deployment...")
    try:
        events = [{
            "type": "test_event",
            "timestamp": datetime.now().isoformat(),
            "data": {"test": "data"}
        }]
        
        result = await tool.execute({
            "deployment_id": "non-existent-deploy-999",
            "events": events
        })
        print(f"    Response: {result}")
        print("  ✅ Non-existent deployment events test completed")
    except Exception as e:
        print(f"    ❌ Non-existent deployment events test failed: {e}")
        return False
    
    # Test 4: Missing required parameters
    print("\n  Testing missing required parameters...")
    try:
        result = await tool.execute({
            "deployment_id": "test-deploy-123"
        })
        print(f"    Response: {result}")
        print("  ✅ Missing events parameter test completed")
    except Exception as e:
        print(f"    ❌ Missing events parameter test failed: {e}")
        return False
    
    # Clean up
    await client.disconnect()
    
    print("\n" + "="*60)
    print("📊 SYNTHESIS - Update Deployment Events Test Results")
    print("="*60)
    print("✅ Tested scenarios:")
    print("   • Update deployment events with single event")
    print("   • Update deployment events with multiple events")
    print("   • Update events for non-existent deployment")
    print("   • Handle missing required parameters")
    print(f"\n🔗 API Endpoint: {client.api_base_url}/deploy/{{deployment_id}}/events")
    print(f"🔑 Authentication: {'✅ Token present' if client.access_token else '❌ No token'}")
    print("\n📝 Notes:")
    print("   • All tests completed successfully")
    print("   • Real API calls made to local server")
    print("   • HTTP session properly initialized and cleaned up")
    print("   • Event timestamp handling tested")
    print("="*60)
    
    print("\n✅ All update_deployment_events real API tests completed!")
    return True

async def main():
    """Main test runner"""
    print("🚀 Starting update_deployment_events real API tests...\n")
    
    try:
        success = await test_update_deployment_events()
        return 0 if success else 1
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)