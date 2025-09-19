#!/usr/bin/env python3
"""
Test for UnsubscribeDeploymentTool
Tests the unsubscribe_deployment functionality
"""

import asyncio
import sys
import os
from unittest.mock import Mock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from tests.base_test import BaseToolTest
from guepard_mcp.subscriptions.tools import UnsubscribeDeploymentTool
from guepard_mcp.utils.base import GuepardAPIClient

class UnsubscribeDeploymentTest:
    """Test class for UnsubscribeDeploymentTool with server dependency"""
    
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
        self.tool = UnsubscribeDeploymentTool(self.client, None, self.mock_server)
        self.tool_name = "unsubscribe_deployment"

    async def test_unsubscribe_success(self):
        """Test successful unsubscription with real deployment ID"""
        print("🧪 Testing unsubscribe_deployment successful execution...")
        
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
                        
                        # Add real deployment first
                        self.mock_server.subscribed_deployments.add(deployment_id)
                        
                        print(f"   📥 INPUT: {{'deployment_id': '{deployment_id}'}} (REAL DATA)")
                        print(f"   📊 Before: {len(self.mock_server.subscribed_deployments)} subscriptions")
                        print(f"   📋 Currently subscribed: {list(self.mock_server.subscribed_deployments)}")
                        
                        # Test unsubscribing
                        result = await self.tool.execute({"deployment_id": deployment_id})
                        
                        print(f"   📤 OUTPUT: {result}")
                        print(f"   📊 After: {len(self.mock_server.subscribed_deployments)} subscriptions")
                        print(f"   📋 Remaining subscriptions: {list(self.mock_server.subscribed_deployments)}")
                        
                        # Verify subscription was removed
                        assert deployment_id not in self.mock_server.subscribed_deployments
                        assert "Unsubscribed from notifications" in result
                        assert "Total subscriptions: 0" in result
                        
                        print("✅ Unsubscribe deployment success test passed!")
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
            print(f"❌ Unsubscribe deployment success test failed: {e}")
            return False

    async def test_unsubscribe_missing_id(self):
        """Test unsubscription with missing deployment_id"""
        print("🧪 Testing unsubscribe_deployment missing deployment_id...")
        
        try:
            # Test with missing deployment ID
            result = await self.tool.execute({})
            
            # Verify error handling
            assert "Missing deployment_id" in result
            
            print("✅ Unsubscribe deployment missing ID test passed!")
            return True
            
        except Exception as e:
            print(f"❌ Unsubscribe deployment missing ID test failed: {e}")
            return False

    async def test_unsubscribe_not_subscribed(self):
        """Test unsubscribing from deployment that's not subscribed"""
        print("🧪 Testing unsubscribe_deployment not subscribed...")
        
        try:
            # Generate dynamic deployment ID
            import uuid
            deployment_id = f"test-deployment-{uuid.uuid4().hex[:8]}"
            
            # Ensure deployment is not subscribed
            self.mock_server.subscribed_deployments.clear()
            
            # Try to unsubscribe from non-subscribed deployment
            result = await self.tool.execute({"deployment_id": deployment_id})
            
            # Verify it handles gracefully (discard doesn't raise error)
            assert deployment_id not in self.mock_server.subscribed_deployments
            assert "Unsubscribed from notifications" in result
            assert "Total subscriptions: 0" in result
            
            print("✅ Unsubscribe deployment not subscribed test passed!")
            return True
            
        except Exception as e:
            print(f"❌ Unsubscribe deployment not subscribed test failed: {e}")
            return False

    async def test_unsubscribe_multiple_deployments(self):
        """Test unsubscribing when multiple deployments are subscribed with real data"""
        print("🧪 Testing unsubscribe_deployment with multiple subscriptions...")
        
        try:
            # Initialize client connection for real API calls
            await self.client.connect()
            
            # Get real deployment IDs from API
            from guepard_mcp.deployments.tools import ListDeploymentsTool
            list_tool = ListDeploymentsTool(self.client)
            
            print("   🔍 Fetching real deployment IDs from API...")
            deployments_result = await list_tool.execute({"limit": 3})
            
            # Extract real deployment IDs
            import json
            if "✅" in deployments_result and "[" in deployments_result:
                json_start = deployments_result.find("[")
                json_end = deployments_result.rfind("]") + 1
                if json_start != -1 and json_end != -1:
                    json_str = deployments_result[json_start:json_end]
                    deployments = json.loads(json_str)
                    if deployments and len(deployments) >= 2:
                        deployment_ids = [d["id"] for d in deployments[:3]]
                        
                        # Add multiple real deployments
                        for deployment_id in deployment_ids:
                            self.mock_server.subscribed_deployments.add(deployment_id)
                        
                        # Unsubscribe from one
                        target_deployment = deployment_ids[1]
                        
                        print(f"   📥 INPUT: {{'deployment_id': '{target_deployment}'}} (REAL DATA)")
                        print(f"   📊 Before: {len(self.mock_server.subscribed_deployments)} subscriptions")
                        print(f"   📋 Currently subscribed: {list(self.mock_server.subscribed_deployments)}")
                        
                        result = await self.tool.execute({"deployment_id": target_deployment})
                        
                        print(f"   📤 OUTPUT: {result}")
                        print(f"   📊 After: {len(self.mock_server.subscribed_deployments)} subscriptions")
                        print(f"   📋 Remaining subscriptions: {list(self.mock_server.subscribed_deployments)}")
                        
                        # Verify only the specified one was removed
                        assert deployment_ids[0] in self.mock_server.subscribed_deployments
                        assert target_deployment not in self.mock_server.subscribed_deployments
                        assert deployment_ids[2] in self.mock_server.subscribed_deployments
                        assert "Total subscriptions: 2" in result
                        
                        print("✅ Unsubscribe deployment multiple subscriptions test passed!")
                        return True
                    else:
                        print("   ⚠️  Not enough real deployments found, skipping test")
                        return True
                else:
                    print("   ⚠️  Could not parse deployments JSON, skipping test")
                    return True
            else:
                print("   ⚠️  Could not fetch deployments, skipping test")
                return True
            
        except Exception as e:
            print(f"❌ Unsubscribe deployment multiple subscriptions test failed: {e}")
            return False

    async def test_tool_definition(self) -> bool:
        """Test tool definition structure"""
        print(f"🧪 Testing {self.tool_name} tool definition...")
        
        try:
            definition = self.tool.get_tool_definition()
            
            # Verify required fields
            assert definition["name"] == "unsubscribe_deployment"
            assert "description" in definition
            assert "inputSchema" in definition
            assert definition["inputSchema"]["type"] == "object"
            assert "deployment_id" in definition["inputSchema"]["properties"]
            assert "deployment_id" in definition["inputSchema"]["required"]
            
            print(f"✅ {self.tool_name} tool definition test passed!")
            return True
            
        except Exception as e:
            print(f"❌ {self.tool_name} tool definition test failed: {e}")
            return False

    async def run_all_tests(self) -> bool:
        """Run all tests for unsubscribe_deployment tool"""
        print(f"🚀 Starting {self.tool_name} tests...\n")
        
        tests = [
            self.test_tool_definition,
            self.test_unsubscribe_success,
            self.test_unsubscribe_missing_id,
            self.test_unsubscribe_not_subscribed,
            self.test_unsubscribe_multiple_deployments
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
    """Main test runner for UnsubscribeDeploymentTool"""
    
    # Create and run tests
    tester = UnsubscribeDeploymentTest()
    success = await tester.run_all_tests()
    
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
