#!/usr/bin/env python3
"""
Test for SubscribeDeploymentTool
Tests the subscribe_deployment functionality
"""

import asyncio
import sys
import os
from unittest.mock import Mock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from tests.base_test import BaseToolTest
from guepard_mcp.subscriptions.tools import SubscribeDeploymentTool
from guepard_mcp.utils.base import GuepardAPIClient

class SubscribeDeploymentTest:
    """Test class for SubscribeDeploymentTool with server dependency"""
    
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
        self.tool = SubscribeDeploymentTool(self.client, None, self.mock_server)
        self.tool_name = "subscribe_deployment"

    async def test_subscribe_success(self):
        """Test successful subscription with real deployment ID"""
        print("🧪 Testing subscribe_deployment successful execution...")
        
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
                        print(f"   📥 INPUT: {{'deployment_id': '{deployment_id}'}} (REAL DATA)")
                        print(f"   📊 Before: {len(self.mock_server.subscribed_deployments)} subscriptions")
                        
                        # Test with real deployment ID
                        result = await self.tool.execute({"deployment_id": deployment_id})
                        
                        print(f"   📤 OUTPUT: {result}")
                        print(f"   📊 After: {len(self.mock_server.subscribed_deployments)} subscriptions")
                        print(f"   📋 Subscribed deployments: {list(self.mock_server.subscribed_deployments)}")
                        
                        # Verify subscription was added
                        assert deployment_id in self.mock_server.subscribed_deployments
                        assert "Subscribed to notifications" in result
                        assert "Total subscriptions: 1" in result
                        
                        print("✅ Subscribe deployment success test passed!")
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
            print(f"❌ Subscribe deployment success test failed: {e}")
            return False

    async def test_subscribe_missing_id(self):
        """Test subscription with missing deployment_id"""
        print("🧪 Testing subscribe_deployment missing deployment_id...")
        
        try:
            # Clear any existing subscriptions
            self.mock_server.subscribed_deployments.clear()
            
            print(f"   📥 INPUT: {{}} (empty - missing deployment_id)")
            print(f"   📊 Before: {len(self.mock_server.subscribed_deployments)} subscriptions")
            
            # Test with missing deployment ID
            result = await self.tool.execute({})
            
            print(f"   📤 OUTPUT: {result}")
            print(f"   📊 After: {len(self.mock_server.subscribed_deployments)} subscriptions")
            
            # Verify error handling
            assert "Missing deployment_id" in result
            assert len(self.mock_server.subscribed_deployments) == 0
            
            print("✅ Subscribe deployment missing ID test passed!")
            return True
            
        except Exception as e:
            print(f"❌ Subscribe deployment missing ID test failed: {e}")
            return False

    async def test_subscribe_duplicate(self):
        """Test subscribing to already subscribed deployment with real data"""
        print("🧪 Testing subscribe_deployment duplicate subscription...")
        
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
                        
                        # Clear any existing subscriptions first
                        self.mock_server.subscribed_deployments.clear()
                        
                        # Add real deployment first
                        self.mock_server.subscribed_deployments.add(deployment_id)
                        
                        print(f"   📥 INPUT: {{'deployment_id': '{deployment_id}'}} (REAL DATA)")
                        print(f"   📊 Before: {len(self.mock_server.subscribed_deployments)} subscriptions")
                        print(f"   📋 Already subscribed: {deployment_id}")
                        
                        # Try to subscribe again
                        result = await self.tool.execute({"deployment_id": deployment_id})
                        
                        print(f"   📤 OUTPUT: {result}")
                        print(f"   📊 After: {len(self.mock_server.subscribed_deployments)} subscriptions")
                        print(f"   📋 Subscribed deployments: {list(self.mock_server.subscribed_deployments)}")
                        
                        # Verify it's still subscribed (set doesn't add duplicates)
                        assert deployment_id in self.mock_server.subscribed_deployments
                        assert "Subscribed to notifications" in result
                        assert "Total subscriptions: 1" in result
                        
                        print("✅ Subscribe deployment duplicate test passed!")
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
            print(f"❌ Subscribe deployment duplicate test failed: {e}")
            return False

    async def test_tool_definition(self) -> bool:
        """Test tool definition structure"""
        print(f"🧪 Testing {self.tool_name} tool definition...")
        
        try:
            definition = self.tool.get_tool_definition()
            
            # Verify required fields
            assert definition["name"] == "subscribe_deployment"
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
        """Run all tests for subscribe_deployment tool"""
        print(f"🚀 Starting {self.tool_name} tests...\n")
        
        tests = [
            self.test_tool_definition,
            self.test_subscribe_success,
            self.test_subscribe_missing_id,
            self.test_subscribe_duplicate
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
    """Main test runner for SubscribeDeploymentTool"""
    
    # Create and run tests
    tester = SubscribeDeploymentTest()
    success = await tester.run_all_tests()
    
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
