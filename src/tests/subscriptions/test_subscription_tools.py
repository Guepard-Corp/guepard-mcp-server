"""
Test subscription management tools
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from src.guepard_mcp.subscriptions.tools import (
    SubscribeDeploymentTool,
    UnsubscribeDeploymentTool,
    ListSubscriptionsTool,
    TestConnectionTool,
    SubscriptionsModule
)


class TestSubscriptionTools:
    """Test subscription management tools"""
    
    @pytest.fixture
    def mock_client(self):
        """Mock API client"""
        client = Mock()
        client._make_api_call = AsyncMock()
        return client
    
    @pytest.fixture
    def mock_config(self):
        """Mock configuration"""
        config = Mock()
        return config
    
    @pytest.fixture
    def mock_server(self):
        """Mock server with subscription tracking"""
        server = Mock()
        server.subscribed_deployments = set()
        server.tools = {}
        server.modules = {}
        server.config = Mock()
        server.config.get_configuration_summary.return_value = {
            'configuration_mode': 'default'
        }
        return server
    
    def test_subscribe_deployment_tool_definition(self, mock_client, mock_config, mock_server):
        """Test subscribe deployment tool definition"""
        tool = SubscribeDeploymentTool(mock_client, mock_config, mock_server)
        definition = tool.get_tool_definition()
        
        assert definition["name"] == "subscribe_deployment"
        assert "deployment_id" in definition["inputSchema"]["properties"]
        assert "deployment_id" in definition["inputSchema"]["required"]
    
    @pytest.mark.asyncio
    async def test_subscribe_deployment_execute(self, mock_client, mock_config, mock_server):
        """Test subscribe deployment execution"""
        tool = SubscribeDeploymentTool(mock_client, mock_config, mock_server)
        
        result = await tool.execute({"deployment_id": "test-deployment-123"})
        
        assert "test-deployment-123" in mock_server.subscribed_deployments
        assert "Subscribed to notifications" in result
        assert "Total subscriptions: 1" in result
    
    @pytest.mark.asyncio
    async def test_subscribe_deployment_missing_id(self, mock_client, mock_config, mock_server):
        """Test subscribe deployment with missing deployment_id"""
        tool = SubscribeDeploymentTool(mock_client, mock_config, mock_server)
        
        result = await tool.execute({})
        
        assert "Missing deployment_id" in result
        assert len(mock_server.subscribed_deployments) == 0
    
    def test_unsubscribe_deployment_tool_definition(self, mock_client, mock_config, mock_server):
        """Test unsubscribe deployment tool definition"""
        tool = UnsubscribeDeploymentTool(mock_client, mock_config, mock_server)
        definition = tool.get_tool_definition()
        
        assert definition["name"] == "unsubscribe_deployment"
        assert "deployment_id" in definition["inputSchema"]["properties"]
        assert "deployment_id" in definition["inputSchema"]["required"]
    
    @pytest.mark.asyncio
    async def test_unsubscribe_deployment_execute(self, mock_client, mock_config, mock_server):
        """Test unsubscribe deployment execution"""
        tool = UnsubscribeDeploymentTool(mock_client, mock_config, mock_server)
        
        # Add a deployment first
        mock_server.subscribed_deployments.add("test-deployment-123")
        
        result = await tool.execute({"deployment_id": "test-deployment-123"})
        
        assert "test-deployment-123" not in mock_server.subscribed_deployments
        assert "Unsubscribed from notifications" in result
        assert "Total subscriptions: 0" in result
    
    def test_list_subscriptions_tool_definition(self, mock_client, mock_config, mock_server):
        """Test list subscriptions tool definition"""
        tool = ListSubscriptionsTool(mock_client, mock_config, mock_server)
        definition = tool.get_tool_definition()
        
        assert definition["name"] == "list_subscriptions"
        assert definition["inputSchema"]["properties"] == {}
    
    @pytest.mark.asyncio
    async def test_list_subscriptions_empty(self, mock_client, mock_config, mock_server):
        """Test list subscriptions when empty"""
        tool = ListSubscriptionsTool(mock_client, mock_config, mock_server)
        
        result = await tool.execute({})
        
        assert "No active subscriptions" in result
    
    @pytest.mark.asyncio
    async def test_list_subscriptions_with_data(self, mock_client, mock_config, mock_server):
        """Test list subscriptions with data"""
        tool = ListSubscriptionsTool(mock_client, mock_config, mock_server)
        
        # Add some deployments
        mock_server.subscribed_deployments.add("deployment-1")
        mock_server.subscribed_deployments.add("deployment-2")
        
        result = await tool.execute({})
        
        assert "Active subscriptions (2)" in result
        assert "deployment-1" in result
        assert "deployment-2" in result
    
    def test_test_connection_tool_definition(self, mock_client, mock_config, mock_server):
        """Test test connection tool definition"""
        tool = TestConnectionTool(mock_client, mock_config, mock_server)
        definition = tool.get_tool_definition()
        
        assert definition["name"] == "test_connection"
        assert definition["inputSchema"]["properties"] == {}
    
    @pytest.mark.asyncio
    async def test_test_connection_success(self, mock_client, mock_config, mock_server):
        """Test test connection success"""
        tool = TestConnectionTool(mock_client, mock_config, mock_server)
        
        # Mock successful API call
        mock_client._make_api_call.return_value = [{"id": "test-deployment"}]
        
        result = await tool.execute({})
        
        assert "connected successfully" in result
        assert "Available Tools" in result
        assert "Modules" in result
    
    @pytest.mark.asyncio
    async def test_test_connection_failure(self, mock_client, mock_config, mock_server):
        """Test test connection failure"""
        tool = TestConnectionTool(mock_client, mock_config, mock_server)
        
        # Mock failed API call
        mock_client._make_api_call.return_value = {"error": True, "message": "API Error"}
        
        result = await tool.execute({})
        
        assert "Connection failed" in result
        assert "API Error" in result
    
    def test_subscriptions_module_initialization(self, mock_client, mock_config, mock_server):
        """Test subscriptions module initialization"""
        module = SubscriptionsModule(mock_client, mock_config, mock_server)
        
        assert "subscribe_deployment" in module.tools
        assert "unsubscribe_deployment" in module.tools
        assert "list_subscriptions" in module.tools
        assert "test_connection" in module.tools
        
        assert isinstance(module.tools["subscribe_deployment"], SubscribeDeploymentTool)
        assert isinstance(module.tools["unsubscribe_deployment"], UnsubscribeDeploymentTool)
        assert isinstance(module.tools["list_subscriptions"], ListSubscriptionsTool)
        assert isinstance(module.tools["test_connection"], TestConnectionTool)
