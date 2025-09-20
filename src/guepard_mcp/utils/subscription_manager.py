"""
Subscription Manager for Guepard MCP Tools
Handles automatic subscription to deployments when using various tools
"""

from typing import Set, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class SubscriptionManager:
    """Manages automatic subscription behavior for Guepard MCP tools"""
    
    def __init__(self, server=None):
        self.server = server
        self.auto_subscribe_enabled = True
        self.subscription_actions = {
            'create_deployment': True,
            'get_deployment': True,
            'start_compute': True,
            'checkout_branch': True,
            'checkout_snapshot': True,
            'create_branch': True,
            'create_snapshot': True,
            'create_node': True,
            'create_f2_deployment': True
        }
    
    def is_auto_subscribe_enabled(self, tool_name: str) -> bool:
        """Check if auto-subscription is enabled for a specific tool"""
        if not self.auto_subscribe_enabled:
            return False
        return self.subscription_actions.get(tool_name, False)
    
    def subscribe_to_deployment(self, deployment_id: str, tool_name: str, context: Dict[str, Any] = None) -> bool:
        """Subscribe to a deployment and return success status"""
        if not self.server or not deployment_id or deployment_id == "Unknown":
            return False
        
        try:
            # Add to server's subscription set
            self.server.subscribed_deployments.add(deployment_id)
            
            # Log the subscription
            logger.info(f"Auto-subscribed to deployment {deployment_id} via {tool_name}")
            
            return True
        except Exception as e:
            logger.error(f"Failed to auto-subscribe to deployment {deployment_id}: {e}")
            return False
    
    def get_subscription_message(self, deployment_id: str, tool_name: str, total_subscriptions: int) -> str:
        """Get formatted subscription message"""
        return (
            f"\n📌 Automatically subscribed to deployment {deployment_id} (via {tool_name})"
            f"\n📋 Total subscriptions: {total_subscriptions}"
        )
    
    def get_subscription_info(self) -> Dict[str, Any]:
        """Get current subscription information"""
        if not self.server:
            return {"enabled": False, "subscriptions": 0, "deployments": []}
        
        return {
            "enabled": self.auto_subscribe_enabled,
            "subscriptions": len(self.server.subscribed_deployments),
            "deployments": list(self.server.subscribed_deployments),
            "actions": self.subscription_actions
        }
    
    def configure_auto_subscription(self, enabled: bool = None, actions: Dict[str, bool] = None):
        """Configure auto-subscription behavior"""
        if enabled is not None:
            self.auto_subscribe_enabled = enabled
        
        if actions:
            self.subscription_actions.update(actions)
        
        logger.info(f"Auto-subscription configured: enabled={self.auto_subscribe_enabled}, actions={self.subscription_actions}")
    
    def unsubscribe_from_deployment(self, deployment_id: str) -> bool:
        """Unsubscribe from a deployment"""
        if not self.server or not deployment_id:
            return False
        
        try:
            self.server.subscribed_deployments.discard(deployment_id)
            logger.info(f"Unsubscribed from deployment {deployment_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to unsubscribe from deployment {deployment_id}: {e}")
            return False
    
    def clear_all_subscriptions(self) -> int:
        """Clear all subscriptions and return count of cleared subscriptions"""
        if not self.server:
            return 0
        
        count = len(self.server.subscribed_deployments)
        self.server.subscribed_deployments.clear()
        logger.info(f"Cleared {count} subscriptions")
        return count
