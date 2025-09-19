#!/usr/bin/env python3
"""
Test subscription management module
Tests the SubscriptionsModule functionality
"""

import asyncio
import sys
import os
from unittest.mock import Mock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from tests.base_test import ModuleTestRunner
from guepard_mcp.subscriptions.tools import SubscriptionsModule
from guepard_mcp.utils.base import GuepardAPIClient

async def test_subscriptions_module():
    """Test subscriptions module initialization and functionality"""
    print("🧪 Testing SubscriptionsModule...")
    
    try:
        # Create mock server
        mock_server = Mock()
        mock_server.subscribed_deployments = set()
        mock_server.tools = {}
        mock_server.modules = {}
        mock_server.config = Mock()
        mock_server.config.get_configuration_summary.return_value = {
            'configuration_mode': 'default'
        }
        
        # Create module
        client = GuepardAPIClient()
        module = SubscriptionsModule(client, None, mock_server)
        
        # Test module initialization
        assert "subscribe_deployment" in module.tools
        assert "unsubscribe_deployment" in module.tools
        assert "list_subscriptions" in module.tools
        assert "test_connection" in module.tools
        
        # Test tool types
        from guepard_mcp.subscriptions.tools import (
            SubscribeDeploymentTool,
            UnsubscribeDeploymentTool,
            ListSubscriptionsTool,
            TestConnectionTool
        )
        
        assert isinstance(module.tools["subscribe_deployment"], SubscribeDeploymentTool)
        assert isinstance(module.tools["unsubscribe_deployment"], UnsubscribeDeploymentTool)
        assert isinstance(module.tools["list_subscriptions"], ListSubscriptionsTool)
        assert isinstance(module.tools["test_connection"], TestConnectionTool)
        
        print("✅ SubscriptionsModule test passed!")
        return True
        
    except Exception as e:
        print(f"❌ SubscriptionsModule test failed: {e}")
        return False

async def main():
    """Main test runner for subscriptions module"""
    print("🚀 Starting subscriptions module tests...\n")
    
    # Test module initialization
    success = await test_subscriptions_module()
    
    if success:
        print("\n🎉 All subscriptions module tests passed!")
    else:
        print("\n⚠️  Some subscriptions module tests failed")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
