"""
Subscription Management MCP Tools for Guepard Platform
"""

from typing import Dict, Any, Set
from ..utils.base import MCPTool, MCPModule, GuepardAPIClient, format_success_response, format_error_response
from ..utils.auto_subscribe_tool import AutoSubscribeMCPTool


class SubscribeDeploymentTool(MCPTool):
    """Tool for subscribing to deployment notifications"""
    
    def __init__(self, client: GuepardAPIClient, config, server):
        super().__init__(client)
        self.config = config
        self.server = server
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "subscribe_deployment",
            "description": "Subscribe to deployment notifications",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "deployment_id": {
                        "type": "string",
                        "description": "Deployment ID to subscribe to"
                    }
                },
                "required": ["deployment_id"]
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        deployment_id = arguments.get("deployment_id")
        
        if not deployment_id:
            return format_error_response("Missing deployment_id", "deployment_id is required")
        
        try:
            # Add to server's subscription set
            self.server.subscribed_deployments.add(deployment_id)
            
            return format_success_response(
                f"Subscribed to notifications for deployment: {deployment_id}",
                f"Total subscriptions: {len(self.server.subscribed_deployments)}"
            )
        except Exception as e:
            return format_error_response("Subscribe failed", str(e))


class UnsubscribeDeploymentTool(MCPTool):
    """Tool for unsubscribing from deployment notifications"""
    
    def __init__(self, client: GuepardAPIClient, config, server):
        super().__init__(client)
        self.config = config
        self.server = server
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "unsubscribe_deployment",
            "description": "Unsubscribe from deployment notifications",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "deployment_id": {
                        "type": "string",
                        "description": "Deployment ID to unsubscribe from"
                    }
                },
                "required": ["deployment_id"]
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        deployment_id = arguments.get("deployment_id")
        
        if not deployment_id:
            return format_error_response("Missing deployment_id", "deployment_id is required")
        
        try:
            # Remove from server's subscription set
            self.server.subscribed_deployments.discard(deployment_id)
            
            return format_success_response(
                f"Unsubscribed from notifications for deployment: {deployment_id}",
                f"Total subscriptions: {len(self.server.subscribed_deployments)}"
            )
        except Exception as e:
            return format_error_response("Unsubscribe failed", str(e))


class ListSubscriptionsTool(MCPTool):
    """Tool for listing all deployment subscriptions"""
    
    def __init__(self, client: GuepardAPIClient, config, server):
        super().__init__(client)
        self.config = config
        self.server = server
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "list_subscriptions",
            "description": "List all deployment subscriptions with optional status information",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "include_status": {
                        "type": "boolean",
                        "description": "Include deployment status information",
                        "default": False
                    },
                    "include_compute_status": {
                        "type": "boolean",
                        "description": "Include compute status information (requires include_status=true)",
                        "default": False
                    }
                }
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        include_status = arguments.get("include_status", False)
        include_compute_status = arguments.get("include_compute_status", False)
        
        try:
            if not self.server.subscribed_deployments:
                return "📋 No active subscriptions"
            
            subscriptions = list(self.server.subscribed_deployments)
            
            if not include_status:
                # Simple list
                subscription_list = "\n".join(f"• {deployment_id}" for deployment_id in subscriptions)
                return f"📋 Active subscriptions ({len(subscriptions)}):\n{subscription_list}"
            else:
                # Detailed list with status
                results = []
                for deployment_id in subscriptions:
                    try:
                        # Get deployment info
                        deployment_result = await self.client._make_api_call("GET", f"/deploy/{deployment_id}")
                        
                        if deployment_result.get("error"):
                            results.append(f"❌ {deployment_id}: Error - {deployment_result.get('message', 'Unknown error')}")
                        else:
                            status = deployment_result.get("status", "unknown")
                            name = deployment_result.get("name", "Unknown")
                            
                            result_line = f"✅ {deployment_id} ({name}): {status}"
                            
                            # Add compute status if requested
                            if include_compute_status:
                                compute_result = await self.client._make_api_call("GET", f"/deploy/{deployment_id}/compute")
                                if not compute_result.get("error"):
                                    compute_status = compute_result.get("status", "unknown")
                                    result_line += f" [Compute: {compute_status}]"
                            
                            results.append(result_line)
                    except Exception as e:
                        results.append(f"❌ {deployment_id}: Error - {str(e)}")
                
                return f"📊 Subscribed Deployments Status ({len(results)}):\n" + "\n".join(results)
        except Exception as e:
            return format_error_response("List subscriptions failed", str(e))


class ManageSubscriptionsTool(AutoSubscribeMCPTool):
    """Tool for managing subscription settings"""
    
    def __init__(self, client: GuepardAPIClient, config=None, server=None):
        super().__init__(client, config, server)
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "manage_subscriptions",
            "description": "Manage automatic subscription settings and view current subscriptions",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "description": "Action to perform",
                        "enum": ["status", "enable", "disable", "configure", "clear_all", "unsubscribe"]
                    },
                    "tool_name": {
                        "type": "string",
                        "description": "Tool name for configure/unsubscribe actions"
                    },
                    "deployment_id": {
                        "type": "string",
                        "description": "Deployment ID for unsubscribe action"
                    },
                    "enabled": {
                        "type": "boolean",
                        "description": "Enable/disable auto-subscription"
                    }
                },
                "required": ["action"]
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        action = arguments.get("action")
        
        if action == "status":
            info = self.get_subscription_info()
            return format_success_response(
                "Subscription status retrieved",
                info
            )
        
        elif action == "enable":
            enabled = arguments.get("enabled", True)
            self.configure_auto_subscription(enabled=enabled)
            return format_success_response(
                f"Auto-subscription {'enabled' if enabled else 'disabled'}",
                {"enabled": enabled}
            )
        
        elif action == "disable":
            self.configure_auto_subscription(enabled=False)
            return format_success_response(
                "Auto-subscription disabled",
                {"enabled": False}
            )
        
        elif action == "configure":
            tool_name = arguments.get("tool_name")
            enabled = arguments.get("enabled", True)
            
            if not tool_name:
                return format_error_response(
                    "Configuration failed",
                    "tool_name is required for configure action"
                )
            
            self.configure_auto_subscription(actions={tool_name: enabled})
            return format_success_response(
                f"Auto-subscription for {tool_name} {'enabled' if enabled else 'disabled'}",
                {"tool_name": tool_name, "enabled": enabled}
            )
        
        elif action == "clear_all":
            count = self.subscription_manager.clear_all_subscriptions()
            return format_success_response(
                f"Cleared {count} subscriptions",
                {"cleared_count": count}
            )
        
        elif action == "unsubscribe":
            deployment_id = arguments.get("deployment_id")
            
            if not deployment_id:
                return format_error_response(
                    "Unsubscribe failed",
                    "deployment_id is required for unsubscribe action"
                )
            
            success = self.subscription_manager.unsubscribe_from_deployment(deployment_id)
            if success:
                return format_success_response(
                    f"Unsubscribed from deployment {deployment_id}",
                    {"deployment_id": deployment_id, "success": True}
                )
            else:
                return format_error_response(
                    "Unsubscribe failed",
                    f"Could not unsubscribe from deployment {deployment_id}"
                )
        
        else:
            return format_error_response(
                "Invalid action",
                f"Unknown action: {action}"
            )


class TestConnectionTool(MCPTool):
    """Tool for testing connection to Guepard API"""
    
    def __init__(self, client: GuepardAPIClient, config, server):
        super().__init__(client)
        self.config = config
        self.server = server
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "test_connection",
            "description": "Test connection to Guepard API",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        try:
            # Test with a simple API call
            result = await self.client._make_api_call("GET", "/deploy", params={"limit": 1})
            if isinstance(result, dict) and result.get("error"):
                return format_error_response(
                    "Connection failed", 
                    result.get('message', 'Unknown error')
                )
            else:
                config_summary = self.server.config.get_configuration_summary()
                return format_success_response(
                    "Guepard MCP Server connected successfully!",
                    f"API URL: {self.client.api_base_url}\n"
                    f"Token: {self.client.access_token[:20]}...\n\n"
                    f"📊 Available Tools: {len(self.server.tools)}\n"
                    f"📋 Modules: {', '.join(self.server.modules.keys())}\n"
                    f"⚙️ Configuration: {config_summary['configuration_mode']}"
                )
        except Exception as e:
            return format_error_response("Connection test failed", str(e))






class SubscriptionsModule(MCPModule):
    """Subscription management module"""
    
    def __init__(self, client: GuepardAPIClient, config, server=None):
        self.server = server
        super().__init__(client, config)
    
    def _initialize_tools(self):
        """Initialize all tools for this module"""
        self.tools = {
            "subscribe_deployment": SubscribeDeploymentTool(self.client, self.config, self.server),
            "unsubscribe_deployment": UnsubscribeDeploymentTool(self.client, self.config, self.server),
            "list_subscriptions": ListSubscriptionsTool(self.client, self.config, self.server),
            "manage_subscriptions": ManageSubscriptionsTool(self.client, self.config, self.server),
            "test_connection": TestConnectionTool(self.client, self.config, self.server)
        }
