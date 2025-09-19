"""
Snapshots MCP Tools for Guepard Platform
"""

from typing import Dict, Any
from ..utils.base import MCPTool, MCPModule, GuepardAPIClient, format_success_response, format_error_response


class ListSnapshotsForDeploymentTool(MCPTool):
    """Tool for listing snapshots for a deployment"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "list_snapshots_deployment",
            "description": "Get all snapshots for a deployment",
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
        
        if not deployment_id:
            return format_error_response("Missing required parameter", "deployment_id is required")
        
        result = await self.client._make_api_call("GET", f"/deploy/{deployment_id}/snap")
        
        # Check if result is an error response (dict with error key)
        if isinstance(result, dict) and result.get("error"):
            error_message = result.get("message", "Unknown error")
            status_code = result.get("status_code", "Unknown")
            
            # Provide more specific error information
            if "Database connection error" in error_message:
                return format_error_response(
                    "Database connection error - deployment may not be ready for snapshots", 
                    f"Status: {status_code}, Message: {error_message}. The deployment may need to be in a different status or the database may not be fully initialized."
                )
            else:
                return format_error_response(
                    "Failed to get snapshots", 
                    f"Status: {status_code}, Message: {error_message}"
                )
        
        if isinstance(result, list):
            count = len(result)
            return format_success_response(f"Found {count} snapshots for deployment {deployment_id}", result)
        else:
            return format_success_response(f"Snapshots retrieved for deployment {deployment_id}", result)


class ListSnapshotsForBranchTool(MCPTool):
    """Tool for listing snapshots for a specific branch"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "list_snapshots_branch",
            "description": "Get all snapshots for a specific branch",
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
        
        if not deployment_id:
            return format_error_response("Missing required parameter", "deployment_id is required")
        if not branch_id:
            return format_error_response("Missing required parameter", "branch_id is required")
        
        result = await self.client._make_api_call("GET", f"/deploy/{deployment_id}/{branch_id}/snap")
        
        # Check if result is an error response (dict with error key)
        if isinstance(result, dict) and result.get("error"):
            error_message = result.get("message", "Unknown error")
            status_code = result.get("status_code", "Unknown")
            
            # Provide more specific error information
            if "Database connection error" in error_message:
                return format_error_response(
                    "Database connection error - deployment may not be ready for snapshots", 
                    f"Status: {status_code}, Message: {error_message}. The deployment may need to be in a different status or the database may not be fully initialized."
                )
            else:
                return format_error_response(
                    "Failed to get snapshots", 
                    f"Status: {status_code}, Message: {error_message}"
                )
        
        if isinstance(result, list):
            count = len(result)
            return format_success_response(f"Found {count} snapshots for branch {branch_id}", result)
        else:
            return format_success_response(f"Snapshots retrieved for branch {branch_id}", result)


class CreateSnapshotTool(MCPTool):
    """Tool for creating a new snapshot of the current branch state"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "create_snapshot",
            "description": "Create a new snapshot of the current branch state",
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
                        "description": "Snapshot comment describing the snapshot"
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
        
        # Check if result is an error response (dict with error key)
        if isinstance(result, dict) and result.get("error"):
            error_message = result.get("message", "Unknown error")
            status_code = result.get("status_code", "Unknown")
            
            # Provide more specific error information
            if "Database connection error" in error_message:
                return format_error_response(
                    "Database connection error - deployment may not be ready for snapshots", 
                    f"Status: {status_code}, Message: {error_message}. The deployment may need to be in a different status or the database may not be fully initialized."
                )
            else:
                return format_error_response(
                    "Failed to create snapshot", 
                    f"Status: {status_code}, Message: {error_message}"
                )
        
        return format_success_response(
            f"Snapshot created successfully",
            {
                "snapshot_id": result.get("id", "Unknown"),
                "deployment_id": deployment_id,
                "branch_id": branch_id,
                "snapshot_comment": snapshot_comment,
                "status": result.get("status", "Unknown"),
                "size_bytes": result.get("size_bytes", 0),
                "full_response": result
            }
        )


class SnapshotsModule(MCPModule):
    """Snapshots module containing all snapshot-related tools"""
    
    def _initialize_tools(self):
        self.tools = {
            "list_snapshots_deployment": ListSnapshotsForDeploymentTool(self.client),
            "list_snapshots_branch": ListSnapshotsForBranchTool(self.client),
            "create_snapshot": CreateSnapshotTool(self.client)
        }
