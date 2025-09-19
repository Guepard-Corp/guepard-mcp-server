#!/usr/bin/env python3
"""
Test for TestConnectionTool
Tests the test_connection functionality
"""

import asyncio
import sys
import os
from unittest.mock import Mock, AsyncMock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from tests.base_test import BaseToolTest
from guepard_mcp.subscriptions.tools import TestConnectionTool
from guepard_mcp.utils.base import GuepardAPIClient

class TestConnectionTest:
    """Test class for TestConnectionTool with server dependency"""
    
    def __init__(self):
        # Create mock server for connection testing
        self.mock_server = Mock()
        self.mock_server.subscribed_deployments = set()
        self.mock_server.tools = {"tool1": "test", "tool2": "test"}
        self.mock_server.modules = {"module1": "test", "module2": "test"}
        self.mock_server.config = Mock()
        self.mock_server.config.get_configuration_summary.return_value = {
            'configuration_mode': 'default'
        }
        
        # Initialize with server dependency
        self.client = GuepardAPIClient()
        self.tool = TestConnectionTool(self.client, None, self.mock_server)
        self.tool_name = "test_connection"

    async def test_connection_success(self):
        """Test successful connection with real API"""
        print("🧪 Testing test_connection successful execution...")
        
        try:
            # Initialize client connection for real API calls
            await self.client.connect()
            
            print(f"   📥 INPUT: {{}} (no parameters)")
            print(f"   🔗 API URL: {self.client.api_base_url}")
            print(f"   🔑 Token: {self.client.access_token[:20]}...")
            
            # Test connection with real API
            result = await self.tool.execute({})
            
            print(f"   📤 OUTPUT: {result}")
            
            # Verify success response
            assert "connected successfully" in result
            assert "Available Tools" in result
            assert "Modules" in result
            assert "API URL" in result
            assert "Token" in result
            assert "Configuration" in result
            
            print("✅ Test connection success test passed!")
            return True
            
        except Exception as e:
            print(f"❌ Test connection success test failed: {e}")
            return False

    async def test_connection_failure(self):
        """Test connection failure with invalid credentials"""
        print("🧪 Testing test_connection failure...")
        
        try:
            # Create a client with invalid credentials to test failure
            from guepard_mcp.utils.base import GuepardAPIClient
            invalid_client = GuepardAPIClient()
            invalid_client.access_token = "invalid-token-12345"
            invalid_client.api_base_url = "http://invalid-url:9999"
            
            # Create tool with invalid client
            from guepard_mcp.subscriptions.tools import TestConnectionTool
            failure_tool = TestConnectionTool(invalid_client, None, self.mock_server)
            
            print(f"   📥 INPUT: {{}} (no parameters)")
            print(f"   🔗 API URL: {invalid_client.api_base_url}")
            print(f"   🔑 Token: {invalid_client.access_token}")
            
            # Test connection with invalid credentials
            result = await failure_tool.execute({})
            
            print(f"   📤 OUTPUT: {result}")
            
            # Verify error response
            assert "Connection test failed" in result or "Connection failed" in result
            
            print("✅ Test connection failure test passed!")
            return True
            
        except Exception as e:
            print(f"❌ Test connection failure test failed: {e}")
            return False

    async def test_connection_exception(self):
        """Test connection with exception"""
        print("🧪 Testing test_connection with exception...")
        
        try:
            # Mock exception during API call
            with AsyncMock() as mock_client:
                mock_client._make_api_call.side_effect = Exception("Network error")
                self.tool.client = mock_client
                
                # Test connection
                result = await self.tool.execute({})
                
                # Verify error response
                assert "Connection test failed" in result
                assert "Network error" in result
            
            print("✅ Test connection exception test passed!")
            return True
            
        except Exception as e:
            print(f"❌ Test connection exception test failed: {e}")
            return False

    async def test_connection_with_server_info(self):
        """Test connection with server information using real data"""
        print("🧪 Testing test_connection with server information...")
        
        try:
            # Initialize client connection for real API calls
            await self.client.connect()
            
            print(f"   📥 INPUT: {{}} (no parameters)")
            print(f"   🔗 API URL: {self.client.api_base_url}")
            print(f"   🔑 Token: {self.client.access_token[:20]}...")
            print(f"   📊 Server tools: {len(self.mock_server.tools)}")
            print(f"   📊 Server modules: {len(self.mock_server.modules)}")
            
            # Test connection with real API
            result = await self.tool.execute({})
            
            print(f"   📤 OUTPUT: {result}")
            
            # Verify server info is included
            assert "Available Tools" in result
            assert "Modules" in result
            assert "Configuration" in result
            
            print("✅ Test connection server info test passed!")
            return True
            
        except Exception as e:
            print(f"❌ Test connection server info test failed: {e}")
            return False

    async def test_connection_empty_tools_modules(self):
        """Test connection with empty tools and modules using real data"""
        print("🧪 Testing test_connection with empty tools/modules...")
        
        try:
            # Initialize client connection for real API calls
            await self.client.connect()
            
            # Create a new server with empty tools and modules
            from unittest.mock import Mock
            empty_server = Mock()
            empty_server.subscribed_deployments = set()
            empty_server.tools = {}
            empty_server.modules = {}
            empty_server.config = Mock()
            empty_server.config.get_configuration_summary.return_value = {
                'configuration_mode': 'default'
            }
            
            # Create tool with empty server
            from guepard_mcp.subscriptions.tools import TestConnectionTool
            empty_tool = TestConnectionTool(self.client, None, empty_server)
            
            print(f"   📥 INPUT: {{}} (no parameters)")
            print(f"   🔗 API URL: {self.client.api_base_url}")
            print(f"   🔑 Token: {self.client.access_token[:20]}...")
            print(f"   📊 Server tools: {len(empty_server.tools)}")
            print(f"   📊 Server modules: {len(empty_server.modules)}")
            
            # Test connection with empty server
            result = await empty_tool.execute({})
            
            print(f"   📤 OUTPUT: {result}")
            
            # Verify response handles empty collections
            assert "Available Tools: 0" in result
            assert "Modules: " in result  # Empty modules list
            
            print("✅ Test connection empty collections test passed!")
            return True
            
        except Exception as e:
            print(f"❌ Test connection empty collections test failed: {e}")
            return False

    async def test_tool_definition(self) -> bool:
        """Test tool definition structure"""
        print(f"🧪 Testing {self.tool_name} tool definition...")
        
        try:
            definition = self.tool.get_tool_definition()
            
            # Verify required fields
            assert definition["name"] == "test_connection"
            assert "description" in definition
            assert "inputSchema" in definition
            assert definition["inputSchema"]["type"] == "object"
            assert definition["inputSchema"]["properties"] == {}
            
            print(f"✅ {self.tool_name} tool definition test passed!")
            return True
            
        except Exception as e:
            print(f"❌ {self.tool_name} tool definition test failed: {e}")
            return False

    async def run_all_tests(self) -> bool:
        """Run all tests for test_connection tool"""
        print(f"🚀 Starting {self.tool_name} tests...\n")
        
        tests = [
            self.test_tool_definition,
            self.test_connection_success,
            self.test_connection_failure,
            self.test_connection_exception,
            self.test_connection_with_server_info,
            self.test_connection_empty_tools_modules
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
    """Main test runner for TestConnectionTool"""
    
    # Create and run tests
    tester = TestConnectionTest()
    success = await tester.run_all_tests()
    
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
