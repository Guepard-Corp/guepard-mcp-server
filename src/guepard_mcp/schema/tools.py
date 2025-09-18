"""
Schema Management MCP Tools for Guepard Platform
"""

from typing import Dict, Any
from ..utils.base import MCPTool, MCPModule, GuepardAPIClient, format_success_response, format_error_response


class ExtractSchemaTool(MCPTool):
    """Tool for extracting database schema from a branch"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "extract_schema",
            "description": "Extract database schema from a branch",
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
        
        result = await self.client._make_api_call(
            "GET", 
            f"/deploy/{deployment_id}/{branch_id}/extract-schema"
        )
        
        if result.get("error"):
            return format_error_response(
                "Failed to extract schema", 
                result.get("message", "Unknown error")
            )
        
        return format_success_response(
            f"Schema extracted from branch {branch_id}",
            result
        )


class UpdateSchemaTool(MCPTool):
    """Tool for updating database schema"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "update_schema",
            "description": "Update database schema",
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
                    "schema": {
                        "type": "object",
                        "description": "Schema definition to apply"
                    }
                },
                "required": ["deployment_id", "branch_id", "schema"]
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        deployment_id = arguments.get("deployment_id")
        branch_id = arguments.get("branch_id")
        schema = arguments.get("schema")
        
        data = {"schema": schema}
        
        result = await self.client._make_api_call(
            "PUT", 
            f"/deploy/{deployment_id}/{branch_id}/schema", 
            data=data
        )
        
        if result.get("error"):
            return format_error_response(
                "Failed to update schema", 
                result.get("message", "Unknown error")
            )
        
        return format_success_response(
            f"Schema updated for branch {branch_id}",
            result
        )


class GetSnapshotSchemaTool(MCPTool):
    """Tool for getting schema from a specific snapshot"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "get_snapshot_schema",
            "description": "Get schema from a specific snapshot",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "deployment_id": {
                        "type": "string",
                        "description": "Deployment ID"
                    },
                    "snapshot_id": {
                        "type": "string",
                        "description": "Snapshot ID"
                    }
                },
                "required": ["deployment_id", "snapshot_id"]
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        deployment_id = arguments.get("deployment_id")
        snapshot_id = arguments.get("snapshot_id")
        
        result = await self.client._make_api_call(
            "GET", 
            f"/deploy/{deployment_id}/snapshot/{snapshot_id}/schema"
        )
        
        if result.get("error"):
            return format_error_response(
                "Failed to get snapshot schema", 
                result.get("message", "Unknown error")
            )
        
        return format_success_response(
            f"Schema retrieved from snapshot {snapshot_id}",
            result
        )


class SchemaModule(MCPModule):
    """Schema module containing all schema management-related tools"""
    
    def _initialize_tools(self):
        self.tools = {
            "extract_schema": ExtractSchemaTool(self.client),
            "update_schema": UpdateSchemaTool(self.client),
            "get_snapshot_schema": GetSnapshotSchemaTool(self.client)
        }
