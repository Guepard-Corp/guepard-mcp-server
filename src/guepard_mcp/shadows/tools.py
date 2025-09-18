"""
Shadows MCP Tools for Guepard Platform
"""

from typing import Dict, Any
from ..utils.base import MCPTool, MCPModule, GuepardAPIClient, format_success_response, format_error_response


class ListShadowsForDeploymentTool(MCPTool):
    """Tool for listing shadow deployments for a specific deployment"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "list_shadows_for_deployment",
            "description": "List shadow deployments for a specific deployment",
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
        
        result = await self.client._make_api_call("GET", f"/deploy/{deployment_id}/shadow")
        
        if result.get("error"):
            return format_error_response(
                "Failed to get shadows for deployment", 
                result.get("message", "Unknown error")
            )
        
        if isinstance(result, dict) and "shadows" in result:
            count = len(result["shadows"])
            return format_success_response(f"Found {count} shadows for deployment {deployment_id}", result)
        else:
            return format_success_response(f"Shadows retrieved for deployment {deployment_id}", result)


class ListAllShadowsTool(MCPTool):
    """Tool for listing all shadow deployments"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "list_all_shadows",
            "description": "List all shadow deployments",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        result = await self.client._make_api_call("GET", "/shadows")
        
        if result.get("error"):
            return format_error_response(
                "Failed to get all shadows", 
                result.get("message", "Unknown error")
            )
        
        if isinstance(result, list):
            count = len(result)
            return format_success_response(f"Found {count} shadows", result)
        else:
            return format_success_response("All shadows retrieved successfully", result)


class CreateShadowTool(MCPTool):
    """Tool for creating a new shadow deployment"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "create_shadow",
            "description": "Create a new shadow deployment",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "deployment_id": {
                        "type": "string",
                        "description": "Deployment ID"
                    },
                    "name": {
                        "type": "string",
                        "description": "Shadow name"
                    },
                    "description": {
                        "type": "string",
                        "description": "Shadow description"
                    },
                    "snapshot_id": {
                        "type": "string",
                        "description": "Snapshot ID to create shadow from"
                    },
                    "branch_id": {
                        "type": "string",
                        "description": "Branch ID to create shadow from"
                    }
                },
                "required": ["deployment_id", "name", "snapshot_id"]
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        deployment_id = arguments.get("deployment_id")
        name = arguments.get("name")
        description = arguments.get("description")
        snapshot_id = arguments.get("snapshot_id")
        branch_id = arguments.get("branch_id")
        
        data = {
            "name": name,
            "snapshot_id": snapshot_id
        }
        
        if description:
            data["description"] = description
        if branch_id:
            data["branch_id"] = branch_id
        
        result = await self.client._make_api_call("POST", f"/deploy/{deployment_id}/shadow", data=data)
        
        if result.get("error"):
            return format_error_response(
                "Failed to create shadow", 
                result.get("message", "Unknown error")
            )
        
        return format_success_response(
            f"Shadow '{name}' created successfully",
            result
        )


class ShadowsModule(MCPModule):
    """Shadows module containing all shadow-related tools"""
    
    def _initialize_tools(self):
        self.tools = {
            "list_shadows_for_deployment": ListShadowsForDeploymentTool(self.client),
            "list_all_shadows": ListAllShadowsTool(self.client),
            "create_shadow": CreateShadowTool(self.client)
        }
