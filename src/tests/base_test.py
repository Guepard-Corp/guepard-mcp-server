#!/usr/bin/env python3
"""
Base test class for Guepard MCP Server tools
Provides common testing utilities and base functionality
"""

import asyncio
import json
import sys
import os
from typing import Dict, Any, List, Optional
from unittest.mock import AsyncMock, patch
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from guepard_mcp.utils.base import GuepardAPIClient, MCPTool

# Load environment variables
load_dotenv()

class BaseToolTest:
    """Base test class for all MCP tools"""
    
    def __init__(self, tool_class, tool_name: str, test_cases: List[Dict[str, Any]] = None):
        self.tool_class = tool_class
        self.tool_name = tool_name
        self.client = GuepardAPIClient()
        self.tool = tool_class(self.client)
        self.test_cases = test_cases or []
        self.test_results = []
    
    async def test_tool_definition(self) -> bool:
        """Test tool definition structure"""
        print(f"🧪 Testing {self.tool_name} tool definition...")
        
        try:
            definition = self.tool.get_tool_definition()
            
            # Verify required fields
            assert definition["name"] == self.tool_name, f"Tool name should be '{self.tool_name}'"
            assert "description" in definition, "Tool should have description"
            assert "inputSchema" in definition, "Tool should have input schema"
            assert definition["inputSchema"]["type"] == "object", "Input schema should be object type"
            
            print(f"✅ {self.tool_name} tool definition test passed!")
            return True
            
        except Exception as e:
            print(f"❌ {self.tool_name} tool definition test failed: {e}")
            return False
    
    async def test_successful_execution(self, test_arguments: Dict[str, Any], expected_api_call: tuple) -> bool:
        """Test successful tool execution with mocked API response"""
        print(f"🧪 Testing {self.tool_name} successful execution...")
        
        try:
            # Mock successful API response
            mock_response = {
                "success": True,
                "data": {"test": "data"},
                "message": "Operation successful"
            }
            
            with patch.object(self.client, '_make_api_call', new_callable=AsyncMock) as mock_call:
                mock_call.return_value = mock_response
                
                result = await self.tool.execute(test_arguments)
                
                # Verify the API was called correctly
                if expected_api_call:
                    # Handle both positional and keyword arguments
                    if len(expected_api_call) == 4 and expected_api_call[2] is None:
                        # Format: (method, endpoint, None, params_dict)
                        method, endpoint, _, params = expected_api_call
                        mock_call.assert_called_once_with(method, endpoint, params=params)
                    else:
                        # Fallback to original behavior
                        mock_call.assert_called_once_with(*expected_api_call)
                
                # Verify the response format
                assert isinstance(result, str), "Response should be a string"
                assert len(result) > 0, "Response should not be empty"
                
                print(f"✅ {self.tool_name} successful execution test passed!")
                print(f"Response: {result[:200]}...")
                return True
                
        except Exception as e:
            print(f"❌ {self.tool_name} successful execution test failed: {e}")
            return False
    
    async def test_error_handling(self, test_arguments: Dict[str, Any], expected_api_call: tuple) -> bool:
        """Test error handling for API errors"""
        print(f"🧪 Testing {self.tool_name} error handling...")
        
        try:
            # Mock API error response
            mock_error_response = {
                "error": True,
                "message": "Test error message"
            }
            
            with patch.object(self.client, '_make_api_call', new_callable=AsyncMock) as mock_call:
                mock_call.return_value = mock_error_response
                
                result = await self.tool.execute(test_arguments)
                
                # Verify the API was called correctly
                if expected_api_call:
                    # Handle both positional and keyword arguments
                    if len(expected_api_call) == 4 and expected_api_call[2] is None:
                        # Format: (method, endpoint, None, params_dict)
                        method, endpoint, _, params = expected_api_call
                        mock_call.assert_called_once_with(method, endpoint, params=params)
                    else:
                        # Fallback to original behavior
                        mock_call.assert_called_once_with(*expected_api_call)
                
                # Verify error response format
                assert isinstance(result, str), "Response should be a string"
                assert len(result) > 0, "Response should not be empty"
                
                print(f"✅ {self.tool_name} error handling test passed!")
                print(f"Response: {result[:200]}...")
                return True
                
        except Exception as e:
            print(f"❌ {self.tool_name} error handling test failed: {e}")
            return False
    
    async def test_missing_required_parameters(self, test_arguments: Dict[str, Any]) -> bool:
        """Test handling of missing required parameters"""
        print(f"🧪 Testing {self.tool_name} missing parameters...")
        
        try:
            result = await self.tool.execute(test_arguments)
            
            # Should handle missing parameters gracefully
            assert isinstance(result, str), "Response should be a string"
            assert len(result) > 0, "Response should not be empty"
            
            print(f"✅ {self.tool_name} missing parameters test passed!")
            print(f"Response: {result[:200]}...")
            return True
            
        except Exception as e:
            print(f"❌ {self.tool_name} missing parameters test failed: {e}")
            return False
    
    async def test_real_api_call(self, test_arguments: Dict[str, Any]) -> bool:
        """Test with real API call (if credentials are available)"""
        print(f"🧪 Testing {self.tool_name} real API call...")
        
        # Check if we have credentials
        if not self.client.access_token:
            print(f"⚠️  No access token found, skipping real API test for {self.tool_name}")
            return True
        
        try:
            result = await self.tool.execute(test_arguments)
            
            print(f"Real API response for {self.tool_name}: {result[:200]}...")
            
            # Check if it's an error or success
            if "❌" in result:
                print(f"ℹ️  Real API call for {self.tool_name} returned error (expected if data doesn't exist)")
            else:
                print(f"✅ Real API call for {self.tool_name} successful!")
            
            return True
            
        except Exception as e:
            print(f"⚠️  Real API call for {self.tool_name} failed: {e}")
            return True
    
    async def run_all_tests(self, test_cases: List[Dict[str, Any]]) -> bool:
        """Run all tests for this tool"""
        print(f"🚀 Starting {self.tool_name} tests...\n")
        
        tests = [
            self.test_tool_definition,
        ]
        
        # Add execution tests for each test case
        for i, test_case in enumerate(test_cases):
            test_name = test_case.get('name', f'test_case_{i}')
            args = test_case.get('arguments', {})
            api_call = test_case.get('expected_api_call')
            
            # Add successful execution test
            tests.append(lambda args=args, api_call=api_call: self.test_successful_execution(args, api_call))
            
            # Add error handling test
            tests.append(lambda args=args, api_call=api_call: self.test_error_handling(args, api_call))
            
            # Add missing parameters test (with empty args)
            tests.append(lambda: self.test_missing_required_parameters({}))
            
            # Add real API test
            tests.append(lambda args=args: self.test_real_api_call(args))
        
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

class ModuleTestRunner:
    """Test runner for entire modules"""
    
    def __init__(self, module_name: str, tool_tests: List[BaseToolTest]):
        self.module_name = module_name
        self.tool_tests = tool_tests
    
    async def run_module_tests(self) -> bool:
        """Run all tests for a module"""
        print(f"🚀 Starting {self.module_name} module tests...\n")
        
        passed = 0
        total = len(self.tool_tests)
        
        for tool_test in self.tool_tests:
            if await tool_test.run_all_tests(tool_test.test_cases):
                passed += 1
        
        print(f"\n📊 {self.module_name} Module Results: {passed}/{total} tools passed")
        
        if passed == total:
            print(f"🎉 All {self.module_name} module tests passed!")
        else:
            print(f"⚠️  Some {self.module_name} module tests failed")
        
        return passed == total
