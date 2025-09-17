#!/usr/bin/env python3
"""
Test script for the Guepard MCP Server configuration system
"""

import sys
import os
import asyncio
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from guepard_mcp.server import GuepardMCPServer
from guepard_mcp.utils.config import ToolConfig, get_predefined_config, list_predefined_configs


async def test_predefined_configurations():
    """Test predefined configurations"""
    print("🧪 Testing predefined configurations...")
    
    try:
        configs = list_predefined_configs()
        print(f"✅ Found {len(configs)} predefined configurations:")
        
        for name, description in configs.items():
            print(f"   📦 {name}: {description}")
        
        # Test each predefined configuration
        for config_name in configs.keys():
            config = get_predefined_config(config_name)
            assert config is not None, f"Configuration {config_name} should exist"
            assert "description" in config, f"Configuration {config_name} should have description"
            print(f"   ✅ Configuration '{config_name}' is valid")
        
        return True
        
    except Exception as e:
        print(f"❌ Predefined configurations test failed: {e}")
        return False


async def test_tool_config():
    """Test ToolConfig class"""
    print("\n🧪 Testing ToolConfig class...")
    
    try:
        # Test default configuration (all enabled)
        config = ToolConfig()
        assert config.is_module_enabled("deployments"), "Default config should enable deployments module"
        assert config.is_tool_enabled("test_connection"), "Default config should enable test_connection tool"
        
        print("✅ Default configuration works")
        
        # Test with environment variables
        os.environ["GUEPARD_ENABLED_MODULES"] = "deployments,compute"
        config = ToolConfig()
        assert config.is_module_enabled("deployments"), "Should enable deployments module"
        assert config.is_module_enabled("compute"), "Should enable compute module"
        assert not config.is_module_enabled("auth"), "Should not enable auth module"
        
        print("✅ Module-based configuration works")
        
        # Test with disabled tools
        os.environ["GUEPARD_DISABLED_TOOLS"] = "delete_deployment,delete_database_user"
        config = ToolConfig()
        assert not config.is_tool_enabled("delete_deployment"), "Should disable delete_deployment tool"
        assert not config.is_tool_enabled("delete_database_user"), "Should disable delete_database_user tool"
        assert config.is_tool_enabled("test_connection"), "Should still enable test_connection tool"
        
        print("✅ Tool-based configuration works")
        
        # Clean up environment
        for key in ["GUEPARD_ENABLED_MODULES", "GUEPARD_DISABLED_TOOLS"]:
            if key in os.environ:
                del os.environ[key]
        
        return True
        
    except Exception as e:
        print(f"❌ ToolConfig test failed: {e}")
        return False


async def test_server_with_configuration():
    """Test server with different configurations"""
    print("\n🧪 Testing server with different configurations...")
    
    try:
        # Test with minimal configuration
        os.environ["GUEPARD_CONFIG"] = "minimal"
        server = GuepardMCPServer()
        
        config_summary = server.config.get_configuration_summary()
        assert config_summary["configuration_mode"] == "selective", "Should be in selective mode"
        assert len(server.tools) < 50, "Minimal config should have fewer tools"
        
        print(f"✅ Minimal configuration: {len(server.tools)} tools enabled")
        
        # Test with read-only configuration
        os.environ["GUEPARD_CONFIG"] = "read_only"
        server = GuepardMCPServer()
        
        config_summary = server.config.get_configuration_summary()
        assert config_summary["configuration_mode"] == "selective", "Should be in selective mode"
        
        print(f"✅ Read-only configuration: {len(server.tools)} tools enabled")
        
        # Test with production configuration
        os.environ["GUEPARD_CONFIG"] = "production"
        server = GuepardMCPServer()
        
        config_summary = server.config.get_configuration_summary()
        assert config_summary["configuration_mode"] == "selective", "Should be in selective mode"
        
        print(f"✅ Production configuration: {len(server.tools)} tools enabled")
        
        # Clean up environment
        if "GUEPARD_CONFIG" in os.environ:
            del os.environ["GUEPARD_CONFIG"]
        
        return True
        
    except Exception as e:
        print(f"❌ Server configuration test failed: {e}")
        return False


async def test_configuration_tools():
    """Test configuration-related tools"""
    print("\n🧪 Testing configuration tools...")
    
    try:
        # Test with minimal configuration
        os.environ["GUEPARD_CONFIG"] = "minimal"
        server = GuepardMCPServer()
        
        # Test list_configurations tool
        if "list_configurations" in server.tools:
            result = await server.tools["list_configurations"].execute({})
            assert "Available Predefined Configurations" in result, "Should list configurations"
            print("✅ list_configurations tool works")
        
        # Test get_configuration tool
        if "get_configuration" in server.tools:
            result = await server.tools["get_configuration"].execute({})
            assert "Current Server Configuration" in result, "Should show current configuration"
            print("✅ get_configuration tool works")
        
        # Clean up environment
        if "GUEPARD_CONFIG" in os.environ:
            del os.environ["GUEPARD_CONFIG"]
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration tools test failed: {e}")
        return False


async def main():
    """Run all configuration tests"""
    print("🚀 Starting Guepard MCP Server Configuration Tests\n")
    
    tests = [
        test_predefined_configurations,
        test_tool_config,
        test_server_with_configuration,
        test_configuration_tools
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
    
    print(f"\n📊 Configuration Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All configuration tests passed! Tool activation system is ready.")
        return True
    else:
        print("⚠️  Some configuration tests failed. Please check the implementation.")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
