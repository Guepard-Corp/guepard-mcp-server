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
                    "snapshot_id": {
                        "type": "string",
                        "description": "Snapshot ID to create shadow from"
                    },
                    "repository_name": {
                        "type": "string",
                        "description": "Repository name"
                    },
                    "branch_name": {
                        "type": "string",
                        "description": "Branch name"
                    },
                    "performance_profile_id": {
                        "type": "string",
                        "description": "Performance profile ID"
                    }
                },
                "required": ["deployment_id", "snapshot_id", "repository_name", "branch_name", "performance_profile_id"]
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        deployment_id = arguments.get("deployment_id")
        snapshot_id = arguments.get("snapshot_id")
        repository_name = arguments.get("repository_name")
        branch_name = arguments.get("branch_name")
        performance_profile_id = arguments.get("performance_profile_id")
        
        data = {
            "repository_name": repository_name,
            "branch_name": branch_name,
            "performance_profile_id": performance_profile_id
        }
        
        result = await self.client._make_api_call("POST", f"/deploy/{deployment_id}/snapshot/{snapshot_id}/shadow", data=data)
        
        if result.get("error"):
            return format_error_response(
                "Failed to create shadow", 
                result.get("message", "Unknown error")
            )
        
        return format_success_response(
            f"Shadow created successfully from snapshot {snapshot_id}",
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
