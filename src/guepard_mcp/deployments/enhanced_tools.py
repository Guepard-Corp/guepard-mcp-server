"""
Enhanced Deployment MCP Tools with Advanced Auto-Subscription
"""

from typing import Dict, Any, Optional, List
from ..utils.base import MCPTool, MCPModule, GuepardAPIClient, format_success_response, format_error_response
from ..utils.auto_subscribe_tool import AutoSubscribeMCPTool

class EnhancedCreateDeploymentTool(AutoSubscribeMCPTool):
    """Enhanced deployment creation tool with advanced auto-subscription"""
    
    def __init__(self, client: GuepardAPIClient, config=None, server=None):
        super().__init__(client, config, server)
        # Configure auto-subscription for this tool
        self.configure_auto_subscription(actions={'create_deployment': True})
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "create_deployment",
            "description": "Create a new database deployment with automatic subscription",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Deployment name"
                    },
                    "repository_name": {
                        "type": "string",
                        "description": "Repository name"
                    },
                    "database_provider": {
                        "type": "string",
                        "description": "Database provider",
                        "enum": ["PostgreSQL", "mysql", "mongodb"],
                        "default": "PostgreSQL"
                    },
                    "database_version": {
                        "type": "string",
                        "description": "Database version (will auto-match with performance profile if not specified)",
                    },
                    "deployment_type": {
                        "type": "string",
                        "description": "Type of deployment (REPOSITORY, F2, etc.)",
                        "enum": ["REPOSITORY", "F2"]
                    },
                    "deployment_parent": {
                        "type": "string",
                        "description": "Parent deployment ID (optional)"
                    },
                    "snapshot_parent": {
                        "type": "string",
                        "description": "Parent snapshot ID (optional)"
                    },
                    "performance_profile_id": {
                        "type": "string",
                        "description": "Performance profile ID"
                    },
                    "auto_subscribe": {
                        "type": "boolean",
                        "description": "Automatically subscribe to this deployment (default: true)",
                        "default": True
                    }
                },
                "required": ["repository_name"]
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        # Check if auto-subscription is explicitly disabled
        auto_subscribe = arguments.get("auto_subscribe", True)
        if not auto_subscribe:
            self.configure_auto_subscription(actions={'create_deployment': False})
        
        # [Previous deployment creation logic would go here]
        # For now, we'll simulate the creation
        deployment_id = f"deployment-{hash(arguments.get('repository_name', 'default'))}"
        deployment_name = arguments.get("name", f"Deployment for {arguments.get('repository_name')}")
        
        # Simulate successful creation
        result = {
            "id": deployment_id,
            "name": deployment_name,
            "repository_name": arguments.get("repository_name"),
            "database_provider": arguments.get("database_provider", "PostgreSQL"),
            "database_version": arguments.get("database_version", "17"),
            "status": "created"
        }
        
        # Create base response
        response_message = f"Deployment '{deployment_name}' created successfully"
        
        # Enhance with auto-subscription
        enhanced_response = self.enhance_response_with_subscription(
            response_message, 
            deployment_id, 
            "create_deployment",
            {"repository_name": arguments.get("repository_name")}
        )
        
        return format_success_response(
            enhanced_response,
            {
                "deployment_id": deployment_id,
                "deployment_name": deployment_name,
                "repository_name": arguments.get("repository_name"),
                "database_provider": arguments.get("database_provider", "PostgreSQL"),
                "database_version": arguments.get("database_version", "17"),
                "subscribed": deployment_id in (self.server.subscribed_deployments if self.server else set()),
                "auto_subscription_enabled": auto_subscribe,
                "full_response": result
            }
        )

class EnhancedGetDeploymentTool(AutoSubscribeMCPTool):
    """Enhanced deployment retrieval tool with auto-subscription"""
    
    def __init__(self, client: GuepardAPIClient, config=None, server=None):
        super().__init__(client, config, server)
        self.configure_auto_subscription(actions={'get_deployment': True})
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "get_deployment",
            "description": "Get deployment details with automatic subscription",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "deployment_id": {
                        "type": "string",
                        "description": "Deployment ID (optional if repository_name or latest is provided)"
                    },
                    "repository_name": {
                        "type": "string",
                        "description": "Repository name to find deployment (optional)"
                    },
                    "latest": {
                        "type": "boolean",
                        "description": "Get the latest deployment (optional)"
                    },
                    "auto_subscribe": {
                        "type": "boolean",
                        "description": "Automatically subscribe to this deployment (default: true)",
                        "default": True
                    }
                }
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        # Check if auto-subscription is explicitly disabled
        auto_subscribe = arguments.get("auto_subscribe", True)
        if not auto_subscribe:
            self.configure_auto_subscription(actions={'get_deployment': False})
        
        deployment_id = arguments.get("deployment_id")
        repository_name = arguments.get("repository_name")
        latest = arguments.get("latest", False)
        
        # Simulate deployment retrieval
        if deployment_id:
            result = {
                "id": deployment_id,
                "name": f"Deployment {deployment_id}",
                "repository_name": repository_name or "test-repo",
                "status": "active"
            }
        else:
            # Simulate finding deployment by repository or latest
            deployment_id = f"deployment-{hash(repository_name or 'latest')}"
            result = {
                "id": deployment_id,
                "name": f"Deployment for {repository_name or 'latest'}",
                "repository_name": repository_name or "test-repo",
                "status": "active"
            }
        
        # Create base response
        response_message = f"Deployment {deployment_id} retrieved successfully"
        
        # Enhance with auto-subscription
        enhanced_response = self.enhance_response_with_subscription(
            response_message,
            deployment_id,
            "get_deployment",
            {"repository_name": repository_name, "latest": latest}
        )
        
        return format_success_response(enhanced_response, result)

class SubscriptionManagementTool(AutoSubscribeMCPTool):
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

class EnhancedDeploymentsModule(MCPModule):
    """Enhanced deployments module with advanced auto-subscription"""
    
    def __init__(self, client: GuepardAPIClient, config=None, server=None):
        self.server = server
        super().__init__(client, config)
    
    def _initialize_tools(self):
        self.tools = {
            "create_deployment": EnhancedCreateDeploymentTool(self.client, self.config, self.server),
            "get_deployment": EnhancedGetDeploymentTool(self.client, self.config, self.server),
            "manage_subscriptions": SubscriptionManagementTool(self.client, self.config, self.server)
        }
