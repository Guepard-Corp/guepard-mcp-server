"""
F2 Deployments MCP Tools for Guepard Platform
"""

from typing import Dict, Any
from ..utils.base import MCPTool, MCPModule, GuepardAPIClient, format_success_response, format_error_response


class ListF2DeploymentsTool(MCPTool):
    """Tool for listing all F2 deployments"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "list_f2_deployments",
            "description": "Get all F2 deployments",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        result = await self.client._make_api_call("GET", "/deploy/f2")
        
        if result.get("error"):
            return format_error_response(
                "Failed to get F2 deployments", 
                result.get("message", "Unknown error")
            )
        
        if isinstance(result, list):
            count = len(result)
            return format_success_response(f"Found {count} F2 deployments", result)
        else:
            return format_success_response("F2 deployments retrieved successfully", result)


class F2DeploymentsModule(MCPModule):
    """F2 Deployments module containing all F2 deployment-related tools"""
    
    def _initialize_tools(self):
        self.tools = {
            "list_f2_deployments": ListF2DeploymentsTool(self.client)
        }
