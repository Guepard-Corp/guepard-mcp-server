"""
Auto-Subscribe MCP Tool Base Class
Provides automatic subscription functionality for Guepard MCP tools
"""

from typing import Dict, Any, Optional
from .base import MCPTool, format_success_response, format_error_response
from .subscription_manager import SubscriptionManager

class AutoSubscribeMCPTool(MCPTool):
    """Base class for MCP tools that support automatic subscription"""
    
    def __init__(self, client, config=None, server=None):
        super().__init__(client)
        self.config = config
        self.server = server
        self.subscription_manager = SubscriptionManager(server)
    
    def auto_subscribe_to_deployment(self, deployment_id: str, tool_name: str, context: Dict[str, Any] = None) -> tuple[bool, str]:
        """
        Automatically subscribe to a deployment if auto-subscription is enabled
        
        Returns:
            tuple: (success: bool, message: str)
        """
        if not self.subscription_manager.is_auto_subscribe_enabled(tool_name):
            return False, ""
        
        success = self.subscription_manager.subscribe_to_deployment(deployment_id, tool_name, context)
        
        if success:
            total_subscriptions = len(self.server.subscribed_deployments) if self.server else 0
            message = self.subscription_manager.get_subscription_message(
                deployment_id, tool_name, total_subscriptions
            )
            return True, message
        else:
            return False, ""
    
    def enhance_response_with_subscription(self, response: str, deployment_id: str, tool_name: str, context: Dict[str, Any] = None) -> str:
        """
        Enhance a response message with subscription information
        
        Args:
            response: Original response message
            deployment_id: Deployment ID to potentially subscribe to
            tool_name: Name of the tool being used
            context: Additional context information
            
        Returns:
            Enhanced response message
        """
        success, subscription_message = self.auto_subscribe_to_deployment(deployment_id, tool_name, context)
        
        if success:
            return response + subscription_message
        
        return response
    
    def get_subscription_info(self) -> Dict[str, Any]:
        """Get current subscription information"""
        return self.subscription_manager.get_subscription_info()
    
    def configure_auto_subscription(self, enabled: bool = None, actions: Dict[str, bool] = None):
        """Configure auto-subscription behavior"""
        self.subscription_manager.configure_auto_subscription(enabled, actions)
