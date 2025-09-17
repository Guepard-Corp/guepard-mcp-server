"""
Snapshots MCP Tools for Guepard Platform
"""

from typing import Dict, Any
from ..utils.base import MCPTool, MCPModule, GuepardAPIClient, format_success_response, format_error_response


class CreateSnapshotTool(MCPTool):
    """Tool for creating a snapshot"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "create_snapshot",
            "description": "Create a snapshot",
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
                    "snapshot_comment": {
                        "type": "string",
                        "description": "Snapshot comment"
                    }
                },
                "required": ["deployment_id", "branch_id", "snapshot_comment"]
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        deployment_id = arguments.get("deployment_id")
        branch_id = arguments.get("branch_id")
        snapshot_comment = arguments.get("snapshot_comment")
        
        data = {
            "snapshot_comment": snapshot_comment
        }
        
        result = await self.client._make_api_call(
            "POST", 
            f"/deploy/{deployment_id}/{branch_id}/snap", 
            data=data
        )
        
        if result.get("error"):
            return format_error_response(
                "Failed to create snapshot", 
                result.get("message", "Unknown error")
            )
        
        return format_success_response(
            f"Snapshot created successfully",
            {
                "deployment_id": deployment_id,
                "branch_id": branch_id,
                "snapshot_comment": snapshot_comment,
                "full_response": result
            }
        )


class ListSnapshotsForDeploymentTool(MCPTool):
    """Tool for listing snapshots for a deployment"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "list_snapshots_deployment",
            "description": "Get snapshots for deployment",
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
        
        result = await self.client._make_api_call("GET", f"/deploy/{deployment_id}/snap")
        
        if result.get("error"):
            return format_error_response(
                "Failed to get snapshots", 
                result.get("message", "Unknown error")
            )
        
        if isinstance(result, list):
            count = len(result)
            return format_success_response(f"Found {count} snapshots for deployment {deployment_id}", result)
        else:
            return format_success_response(f"Snapshots retrieved for deployment {deployment_id}", result)


class ListSnapshotsForBranchTool(MCPTool):
    """Tool for listing snapshots for a branch"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "list_snapshots_branch",
            "description": "Get snapshots for branch",
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
                    }
                },
                "required": ["deployment_id", "branch_id"]
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        deployment_id = arguments.get("deployment_id")
        branch_id = arguments.get("branch_id")
        
        result = await self.client._make_api_call("GET", f"/deploy/{deployment_id}/{branch_id}/snap")
        
        if result.get("error"):
            return format_error_response(
                "Failed to get snapshots", 
                result.get("message", "Unknown error")
            )
        
        if isinstance(result, list):
            count = len(result)
            return format_success_response(f"Found {count} snapshots for branch {branch_id}", result)
        else:
            return format_success_response(f"Snapshots retrieved for branch {branch_id}", result)


class CreateBookmarkTool(MCPTool):
    """Tool for creating a bookmark (snapshot with comment)"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "create_bookmark",
            "description": "Create a bookmark for a specific deployment",
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
                    "snapshot_comment": {
                        "type": "string",
                        "description": "Snapshot comment"
                    }
                },
                "required": ["deployment_id", "branch_id", "snapshot_comment"]
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        deployment_id = arguments.get("deployment_id")
        branch_id = arguments.get("branch_id")
        snapshot_comment = arguments.get("snapshot_comment")
        
        data = {
            "snapshot_comment": snapshot_comment
        }
        
        result = await self.client._make_api_call(
            "PUT", 
            f"/deploy/{deployment_id}/{branch_id}/snap", 
            data=data
        )
        
        if result.get("error"):
            return format_error_response(
                "Failed to create bookmark", 
                result.get("message", "Unknown error")
            )
        
        return format_success_response(
            f"Bookmark created successfully",
            {
                "deployment_id": deployment_id,
                "branch_id": branch_id,
                "snapshot_comment": snapshot_comment,
                "full_response": result
            }
        )


class SnapshotsModule(MCPModule):
    """Snapshots module containing all snapshot-related tools"""
    
    def _initialize_tools(self):
        self.tools = {
            "create_snapshot": CreateSnapshotTool(self.client),
            "list_snapshots_deployment": ListSnapshotsForDeploymentTool(self.client),
            "list_snapshots_branch": ListSnapshotsForBranchTool(self.client),
            "create_bookmark": CreateBookmarkTool(self.client)
        }
