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
            "description": "Get all branches for a deployment",
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


class UpdateBranchTool(MCPTool):
    """Tool for updating branch configuration"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "update_branch",
            "description": "Update branch configuration",
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


class CreateBranchFromSnapshotTool(MCPTool):
    """Tool for creating a new branch from a specific snapshot"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "create_branch_from_snapshot",
            "description": "Create a new branch from a specific snapshot",
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
            f"Branch '{branch_name}' created successfully from snapshot {snapshot_id}",
            {
                "deployment_id": deployment_id,
                "branch_id": branch_id,
                "snapshot_id": snapshot_id,
                "branch_name": branch_name,
                "is_ephemeral": is_ephemeral,
                "full_response": result
            }
        )


class BranchesModule(MCPModule):
    """Branches module containing all branch-related tools"""
    
    def _initialize_tools(self):
        self.tools = {
            "list_branches": ListBranchesTool(self.client),
            "update_branch": UpdateBranchTool(self.client),
            "create_branch_from_snapshot": CreateBranchFromSnapshotTool(self.client)
        }
