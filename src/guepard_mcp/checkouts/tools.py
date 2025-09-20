"""
Checkouts MCP Tools for Guepard Platform
"""

from typing import Dict, Any
from ..utils.base import MCPTool, MCPModule, GuepardAPIClient, format_success_response, format_error_response


class CheckoutBranchTool(MCPTool):
    """Tool for checking out to a specific branch with snapshot"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "checkout_branch",
            "description": "Checkout to a specific branch with snapshot",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "deployment_id": {
                        "type": "string",
                        "description": "Deployment ID"
                    },
                    "branch_id": {
                        "type": "string",
                        "description": "Branch ID"
                    },
                    "snapshot_id": {
                        "type": "string",
                        "description": "Snapshot ID to checkout to"
                    }
                },
                "required": ["deployment_id", "branch_id", "snapshot_id"]
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        deployment_id = arguments.get("deployment_id")
        branch_id = arguments.get("branch_id")
        snapshot_id = arguments.get("snapshot_id")
        
        data = {"snapshot_id": snapshot_id}
        
        result = await self.client._make_api_call(
            "POST", 
            f"/deploy/{deployment_id}/{branch_id}/checkout", 
            data=data
        )
        
        if result.get("error"):
            return format_error_response(
                "Failed to checkout branch", 
                result.get("message", "Unknown error")
            )
        
        return format_success_response(
            f"Branch {branch_id} checked out successfully to snapshot {snapshot_id}",
            result
        )


class CheckoutSnapshotTool(MCPTool):
    """Tool for checking out to a specific snapshot"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "checkout_snapshot",
            "description": "Checkout to a specific snapshot",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "deployment_id": {
                        "type": "string",
                        "description": "Deployment ID"
                    },
                    "branch_id": {
                        "type": "string",
                        "description": "Parent branch ID"
                    },
                    "snapshot_id": {
                        "type": "string",
                        "description": "Snapshot ID to create branch from"
                    },
                    "branch_name": {
                        "type": "string",
                        "description": "Name for the new branch"
                    },
                    "is_ephemeral": {
                        "type": "boolean",
                        "description": "Whether the branch is ephemeral",
                        "default": True
                    }
                },
                "required": ["deployment_id", "branch_id", "snapshot_id"]
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        deployment_id = arguments.get("deployment_id")
        branch_id = arguments.get("branch_id")
        snapshot_id = arguments.get("snapshot_id")
        discard_changes = arguments.get("discard_changes", "true")
        checkout = arguments.get("checkout", True)
        ephemeral = arguments.get("ephemeral", True)
        performance_profile_name = arguments.get("performance_profile_name", "querying")
        
        data = {
            "discard_changes": discard_changes,
            "checkout": checkout,
            "ephemeral": ephemeral,
            "performance_profile_name": performance_profile_name,
            "snapshot_id": snapshot_id
        }
        
        result = await self.client._make_api_call(
            "POST", 
            f"/deploy/{deployment_id}/{branch_id}/checkout", 
            data=data
        )
        
        if result.get("error"):
            return format_error_response(
                "Failed to checkout snapshot", 
                result.get("message", "Unknown error")
            )
        
        return format_success_response(
            f"Successfully checked out to snapshot {snapshot_id}",
            result
        )


class CheckoutsModule(MCPModule):
    """Checkouts module containing all checkout-related tools"""
    
    def _initialize_tools(self):
        self.tools = {
            "checkout_branch": CheckoutBranchTool(self.client),
            "checkout_snapshot": CheckoutSnapshotTool(self.client)
        }
