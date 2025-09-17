"""
Branches MCP Tools for Guepard Platform
"""

from typing import Dict, Any
from ..utils.base import MCPTool, MCPModule, GuepardAPIClient, format_success_response, format_error_response


class ListBranchesTool(MCPTool):
    """Tool for listing branches for a deployment"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "list_branches",
            "description": "Get branches for deployment",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "deployment_id": {
                        "type": "string",
                        "description": "Deployment ID"
                    }
                },
                "required": ["deployment_id"]
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        deployment_id = arguments.get("deployment_id")
        
        result = await self.client._make_api_call("GET", f"/deploy/{deployment_id}/branch")
        
        # Check if result is an error response (dict with error key)
        if isinstance(result, dict) and result.get("error"):
            return format_error_response(
                "Failed to get branches", 
                result.get("message", "Unknown error")
            )
        
        if isinstance(result, list):
            count = len(result)
            return format_success_response(f"Found {count} branches for deployment {deployment_id}", result)
        else:
            return format_success_response(f"Branches retrieved for deployment {deployment_id}", result)


class CreateBranchTool(MCPTool):
    """Tool for creating a new branch"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "create_branch",
            "description": "Create a new branch from snapshot",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "deployment_id": {
                        "type": "string",
                        "description": "Deployment ID"
                    },
                    "branch_id": {
                        "type": "string",
                        "description": "Branch ID (clone ID)"
                    },
                    "snapshot_id": {
                        "type": "string",
                        "description": "Snapshot ID"
                    },
                    "branch_name": {
                        "type": "string",
                        "description": "Branch name"
                    },
                    "is_ephemeral": {
                        "type": "boolean",
                        "description": "Create ephemeral branch",
                        "default": False
                    }
                },
                "required": ["deployment_id", "branch_id", "snapshot_id", "branch_name"]
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        deployment_id = arguments.get("deployment_id")
        branch_id = arguments.get("branch_id")
        snapshot_id = arguments.get("snapshot_id")
        branch_name = arguments.get("branch_name")
        is_ephemeral = arguments.get("is_ephemeral", False)
        
        data = {
            "branch_name": branch_name,
            "is_ephemeral": is_ephemeral
        }
        
        result = await self.client._make_api_call(
            "POST", 
            f"/deploy/{deployment_id}/{branch_id}/{snapshot_id}/branch", 
            data=data
        )
        
        if result.get("error"):
            return format_error_response(
                "Failed to create branch", 
                result.get("message", "Unknown error")
            )
        
        return format_success_response(
            f"Branch '{branch_name}' created successfully",
            {
                "deployment_id": deployment_id,
                "branch_id": branch_id,
                "snapshot_id": snapshot_id,
                "branch_name": branch_name,
                "is_ephemeral": is_ephemeral,
                "full_response": result
            }
        )


class GetBranchTool(MCPTool):
    """Tool for getting branch details"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "get_branch",
            "description": "Get branch details",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "branch_id": {
                        "type": "string",
                        "description": "Branch ID"
                    }
                },
                "required": ["branch_id"]
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        branch_id = arguments.get("branch_id")
        
        result = await self.client._make_api_call("GET", f"/branches/{branch_id}")
        
        if result.get("error"):
            return format_error_response(
                "Failed to get branch", 
                result.get("message", "Unknown error")
            )
        
        return format_success_response(
            f"Branch {branch_id} retrieved successfully",
            result
        )


class UpdateBranchTool(MCPTool):
    """Tool for updating branch"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "update_branch",
            "description": "Update branch",
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
                    "label_name": {
                        "type": "string",
                        "description": "Updated branch label name"
                    },
                    "is_ephemeral": {
                        "type": "boolean",
                        "description": "Updated ephemeral status"
                    }
                },
                "required": ["deployment_id", "branch_id"]
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        deployment_id = arguments.get("deployment_id")
        branch_id = arguments.get("branch_id")
        
        data = {}
        if arguments.get("label_name"):
            data["label_name"] = arguments.get("label_name")
        if arguments.get("is_ephemeral") is not None:
            data["is_ephemeral"] = arguments.get("is_ephemeral")
        
        result = await self.client._make_api_call(
            "PUT", 
            f"/deploy/{deployment_id}/{branch_id}/branch", 
            data=data
        )
        
        if result.get("error"):
            return format_error_response(
                "Failed to update branch", 
                result.get("message", "Unknown error")
            )
        
        return format_success_response(
            f"Branch {branch_id} updated successfully",
            result
        )


class CheckoutBranchTool(MCPTool):
    """Tool for checking out to a specific snapshot"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "checkout_branch",
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
        
        data = {
            "snapshot_id": snapshot_id
        }
        
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
            f"Branch {branch_id} checked out to snapshot {snapshot_id}",
            {
                "deployment_id": deployment_id,
                "branch_id": branch_id,
                "snapshot_id": snapshot_id,
                "full_response": result
            }
        )


class BranchesModule(MCPModule):
    """Branches module containing all branch-related tools"""
    
    def _initialize_tools(self):
        self.tools = {
            "list_branches": ListBranchesTool(self.client),
            "create_branch": CreateBranchTool(self.client),
            "get_branch": GetBranchTool(self.client),
            "update_branch": UpdateBranchTool(self.client),
            "checkout_branch": CheckoutBranchTool(self.client)
        }
