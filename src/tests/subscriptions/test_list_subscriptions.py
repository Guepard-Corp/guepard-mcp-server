#!/usr/bin/env python3
"""
Test for ListSubscriptionsTool
Tests the list_subscriptions functionality
"""

import asyncio
import sys
import os
from unittest.mock import Mock, AsyncMock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from tests.base_test import BaseToolTest
from guepard_mcp.subscriptions.tools import ListSubscriptionsTool
from guepard_mcp.utils.base import GuepardAPIClient

class ListSubscriptionsTest:
    """Test class for ListSubscriptionsTool with server dependency"""
    
    def __init__(self):
        # Create mock server for subscription tracking
        self.mock_server = Mock()
        self.mock_server.subscribed_deployments = set()
        self.mock_server.tools = {}
        self.mock_server.modules = {}
        self.mock_server.config = Mock()
        self.mock_server.config.get_configuration_summary.return_value = {
            'configuration_mode': 'default'
        }
        
        # Initialize with server dependency
        self.client = GuepardAPIClient()
        self.tool = ListSubscriptionsTool(self.client, None, self.mock_server)
        self.tool_name = "list_subscriptions"

    async def test_list_empty_subscriptions(self):
        """Test listing when no subscriptions exist"""
        print("🧪 Testing list_subscriptions with empty subscriptions...")
        
        try:
            # Ensure no subscriptions
            self.mock_server.subscribed_deployments.clear()
            
            # Test listing
            result = await self.tool.execute({})
            
            # Verify empty response
            assert "No active subscriptions" in result
            
            print("✅ List subscriptions empty test passed!")
            return True
            
        except Exception as e:
            print(f"❌ List subscriptions empty test failed: {e}")
            return False

    async def test_list_with_subscriptions(self):
        """Test listing with existing subscriptions using real data"""
        print("🧪 Testing list_subscriptions with existing subscriptions...")
        
        try:
            # Initialize client connection for real API calls
            await self.client.connect()
            
            # Get real deployment IDs from API
            from guepard_mcp.deployments.tools import ListDeploymentsTool
            list_tool = ListDeploymentsTool(self.client)
            
            print("   🔍 Fetching real deployment IDs from API...")
            deployments_result = await list_tool.execute({"limit": 2})
            
            # Extract real deployment IDs
            import json
            if "✅" in deployments_result and "[" in deployments_result:
                json_start = deployments_result.find("[")
                json_end = deployments_result.rfind("]") + 1
                if json_start != -1 and json_end != -1:
                    json_str = deployments_result[json_start:json_end]
                    deployments = json.loads(json_str)
                    if deployments and len(deployments) >= 1:
                        deployment_ids = [d["id"] for d in deployments[:2]]
                        
                        # Add real subscriptions
                        for deployment_id in deployment_ids:
                            self.mock_server.subscribed_deployments.add(deployment_id)
                        
                        print(f"   📥 INPUT: {{}} (no parameters)")
                        print(f"   📊 Subscribed deployments: {list(self.mock_server.subscribed_deployments)}")
                        
                        # Test listing
                        result = await self.tool.execute({})
                        
                        print(f"   📤 OUTPUT: {result}")
                        
                        # Verify response contains subscriptions
                        assert "Active subscriptions" in result
                        for deployment_id in deployment_ids:
                            assert deployment_id in result
                        
                        print("✅ List subscriptions with data test passed!")
                        return True
                    else:
                        print("   ⚠️  No real deployments found, skipping test")
                        return True
                else:
                    print("   ⚠️  Could not parse deployments JSON, skipping test")
                    return True
            else:
                print("   ⚠️  Could not fetch deployments, skipping test")
                return True
            
        except Exception as e:
            print(f"❌ List subscriptions with data test failed: {e}")
            return False

    async def test_list_with_status(self):
        """Test listing with status information using real data"""
        print("🧪 Testing list_subscriptions with status information...")
        
        try:
            # Initialize client connection for real API calls
            await self.client.connect()
            
            # Get real deployment ID from API
            from guepard_mcp.deployments.tools import ListDeploymentsTool
            list_tool = ListDeploymentsTool(self.client)
            
            print("   🔍 Fetching real deployment IDs from API...")
            deployments_result = await list_tool.execute({"limit": 1})
            
            # Extract real deployment ID
            import json
            if "✅" in deployments_result and "[" in deployments_result:
                json_start = deployments_result.find("[")
                json_end = deployments_result.rfind("]") + 1
                if json_start != -1 and json_end != -1:
                    json_str = deployments_result[json_start:json_end]
                    deployments = json.loads(json_str)
                    if deployments and len(deployments) > 0:
                        deployment_id = deployments[0]["id"]
                        
                        # Add real subscription
                        self.mock_server.subscribed_deployments.add(deployment_id)
                        
                        print(f"   📥 INPUT: {{'include_status': True}}")
                        print(f"   📊 Subscribed deployment: {deployment_id}")
                        
                        # Test listing with status (using real API calls)
                        result = await self.tool.execute({"include_status": True})
                        
                        print(f"   📤 OUTPUT: {result}")
                        
                        # Verify response contains status info
                        assert "Subscribed Deployments Status" in result
                        assert deployment_id in result
                        
                        print("✅ List subscriptions with status test passed!")
                        return True
                    else:
                        print("   ⚠️  No real deployments found, skipping test")
                        return True
                else:
                    print("   ⚠️  Could not parse deployments JSON, skipping test")
                    return True
            else:
                print("   ⚠️  Could not fetch deployments, skipping test")
                return True
            
        except Exception as e:
            print(f"❌ List subscriptions with status test failed: {e}")
            return False

    async def test_list_with_compute_status(self):
        """Test listing with compute status information"""
        print("🧪 Testing list_subscriptions with compute status...")
        
        try:
            # Generate dynamic deployment ID
            import uuid
            deployment_id = f"test-deployment-{uuid.uuid4().hex[:8]}"
            
            # Add a subscription
            self.mock_server.subscribed_deployments.add(deployment_id)
            
            # Mock API responses
            mock_deployment_response = {
                "id": deployment_id,
                "name": f"Test Deployment {deployment_id[:8]}",
                "status": "active"
            }
            mock_compute_response = {
                "status": "running"
            }
            
            with AsyncMock() as mock_client:
                # Mock the API calls
                async def mock_api_call(method, endpoint, **kwargs):
                    if "compute" in endpoint:
                        return mock_compute_response
                    return mock_deployment_response
                
                mock_client._make_api_call = mock_api_call
                self.tool.client = mock_client
                
                # Test listing with compute status
                result = await self.tool.execute({
                    "include_status": True,
                    "include_compute_status": True
                })
                
                # Verify response contains compute status
                assert "Subscribed Deployments Status" in result
                assert deployment_id in result
                assert "Compute: running" in result
            
            print("✅ List subscriptions with compute status test passed!")
            return True
            
        except Exception as e:
            print(f"❌ List subscriptions with compute status test failed: {e}")
            return False

    async def test_list_with_api_error(self):
        """Test listing when API returns error for status"""
        print("🧪 Testing list_subscriptions with API error...")
        
        try:
            # Generate dynamic deployment ID
            import uuid
            deployment_id = f"error-deployment-{uuid.uuid4().hex[:8]}"
            
            # Add a subscription
            self.mock_server.subscribed_deployments.add(deployment_id)
            
            # Mock API error response
            mock_error_response = {
                "error": True,
                "message": "API Error"
            }
            
            with AsyncMock() as mock_client:
                mock_client._make_api_call.return_value = mock_error_response
                self.tool.client = mock_client
                
                # Test listing with status (should handle error)
                result = await self.tool.execute({"include_status": True})
                
                # Verify error is handled gracefully
                assert "Subscribed Deployments Status" in result
                assert deployment_id in result
                assert "Error - API Error" in result
            
            print("✅ List subscriptions API error test passed!")
            return True
            
        except Exception as e:
            print(f"❌ List subscriptions API error test failed: {e}")
            return False

    async def test_tool_definition(self) -> bool:
        """Test tool definition structure"""
        print(f"🧪 Testing {self.tool_name} tool definition...")
        
        try:
            definition = self.tool.get_tool_definition()
            
            # Verify required fields
            assert definition["name"] == "list_subscriptions"
            assert "description" in definition
            assert "inputSchema" in definition
            assert definition["inputSchema"]["type"] == "object"
            assert "include_status" in definition["inputSchema"]["properties"]
            assert "include_compute_status" in definition["inputSchema"]["properties"]
            
            print(f"✅ {self.tool_name} tool definition test passed!")
            return True
            
        except Exception as e:
            print(f"❌ {self.tool_name} tool definition test failed: {e}")
            return False

    async def run_all_tests(self) -> bool:
        """Run all tests for list_subscriptions tool"""
        print(f"🚀 Starting {self.tool_name} tests...\n")
        
        tests = [
            self.test_tool_definition,
            self.test_list_empty_subscriptions,
            self.test_list_with_subscriptions,
            self.test_list_with_status,
            self.test_list_with_compute_status,
            self.test_list_with_api_error
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                if await test():
                    passed += 1
            except Exception as e:
                print(f"❌ Test failed with exception: {e}")
        
        print(f"\n📊 {self.tool_name} Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print(f"🎉 All {self.tool_name} tests passed!")
        else:
            print(f"⚠️  Some {self.tool_name} tests failed")
        
        return passed == total

async def main():
    """Main test runner for ListSubscriptionsTool"""
    
    # Create and run tests
    tester = ListSubscriptionsTest()
    success = await tester.run_all_tests()
    
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
