#!/usr/bin/env python3
"""
Test script for the complete Guepard MCP Server implementation
"""

import sys
import os
import asyncio
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from guepard_mcp.server import GuepardMCPServer


async def test_server_initialization():
    """Test server initialization and tool loading"""
    print("🧪 Testing Guepard MCP Server initialization...")
    
    try:
        # Create server instance
        server = GuepardMCPServer()
        
        # Check modules
        print(f"✅ Modules loaded: {len(server.modules)}")
        for module_name, module in server.modules.items():
            tool_count = len(module.tools)
            print(f"   📦 {module_name}: {tool_count} tools")
        
        # Check total tools
        total_tools = len(server.tools)
        print(f"✅ Total tools available: {total_tools}")
        
        # List all tools
        print("\n📋 Available tools:")
        for tool_name, tool in server.tools.items():
            definition = tool.get_tool_definition()
            print(f"   🔧 {tool_name}: {definition.get('description', 'No description')}")
        
        # Test tool definitions
        print("\n🧪 Testing tool definitions...")
        for tool_name, tool in server.tools.items():
            definition = tool.get_tool_definition()
            assert 'name' in definition, f"Tool {tool_name} missing name"
            assert 'description' in definition, f"Tool {tool_name} missing description"
            assert 'inputSchema' in definition, f"Tool {tool_name} missing inputSchema"
        
        print("✅ All tool definitions are valid")
        
        return True
        
    except Exception as e:
        print(f"❌ Server initialization failed: {e}")
        return False


async def test_mcp_handlers():
    """Test MCP request handlers"""
    print("\n🧪 Testing MCP request handlers...")
    
    try:
        server = GuepardMCPServer()
        
        # Test initialize request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {}
        }
        
        response = await server.handle_request(init_request)
        assert response is not None, "Initialize response should not be None"
        assert response["jsonrpc"] == "2.0", "Response should be JSON-RPC 2.0"
        assert "result" in response, "Response should have result"
        assert response["result"]["serverInfo"]["name"] == "guepard-complete", "Server name should match"
        
        print("✅ Initialize handler works")
        
        # Test tools/list request
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        response = await server.handle_request(tools_request)
        assert response is not None, "Tools list response should not be None"
        assert "result" in response, "Response should have result"
        assert "tools" in response["result"], "Response should have tools"
        
        tools_count = len(response["result"]["tools"])
        print(f"✅ Tools list handler works ({tools_count} tools)")
        
        # Test unknown method
        unknown_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "unknown/method",
            "params": {}
        }
        
        response = await server.handle_request(unknown_request)
        assert response is not None, "Unknown method response should not be None"
        assert "error" in response, "Response should have error"
        assert response["error"]["code"] == -32601, "Error code should be -32601"
        
        print("✅ Unknown method handler works")
        
        return True
        
    except Exception as e:
        print(f"❌ MCP handlers test failed: {e}")
        return False


async def test_module_structure():
    """Test module structure and inheritance"""
    print("\n🧪 Testing module structure...")
    
    try:
        from guepard_mcp.utils.base import GuepardAPIClient, MCPTool, MCPModule
        
        # Test base classes
        client = GuepardAPIClient()
        assert hasattr(client, 'access_token'), "Client should have access_token"
        assert hasattr(client, 'api_base_url'), "Client should have api_base_url"
        assert hasattr(client, '_make_api_call'), "Client should have _make_api_call method"
        
        print("✅ Base client class works")
        
        # Test module imports
        from guepard_mcp.auth.tools import AuthModule
        from guepard_mcp.deployments.tools import DeploymentsModule
        from guepard_mcp.branches.tools import BranchesModule
        from guepard_mcp.snapshots.tools import SnapshotsModule
        from guepard_mcp.nodes.tools import NodesModule
        from guepard_mcp.performance.tools import PerformanceModule
        from guepard_mcp.compute.tools import ComputeModule
        from guepard_mcp.users.tools import UsersModule
        from guepard_mcp.tokens.tools import TokensModule
        
        print("✅ All modules import successfully")
        
        # Test module initialization
        auth_module = AuthModule(client)
        assert hasattr(auth_module, 'tools'), "Module should have tools"
        assert len(auth_module.tools) > 0, "Module should have tools"
        
        print("✅ Module initialization works")
        
        return True
        
    except Exception as e:
        print(f"❌ Module structure test failed: {e}")
        return False


async def main():
    """Run all tests"""
    print("🚀 Starting Guepard MCP Server Complete Implementation Tests\n")
    
    tests = [
        test_server_initialization,
        test_mcp_handlers,
        test_module_structure
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            result = await test()
            if result:
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Implementation is ready.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
