"""
Usage & Resources MCP Tools for Guepard Platform
"""

from typing import Dict, Any
from ..utils.base import MCPTool, MCPModule, GuepardAPIClient, format_success_response, format_error_response


class GetUsageStatisticsTool(MCPTool):
    """Tool for getting usage statistics for the authenticated user"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "get_usage_statistics",
            "description": "Get usage statistics for the authenticated user",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        result = await self.client._make_api_call("GET", "/usage")
        
        if result.get("error"):
            return format_error_response(
                "Failed to get usage statistics", 
                result.get("message", "Unknown error")
            )
        
        return format_success_response("Usage statistics retrieved successfully", result)


class UpdateResourcesTool(MCPTool):
    """Tool for updating resource quotas and limits"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "update_resources",
            "description": "Update resource quotas and limits",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "max_deployments": {
                        "type": "integer",
                        "description": "Maximum number of deployments allowed"
                    },
                    "max_cpu": {
                        "type": "integer",
                        "description": "Maximum CPU cores allowed"
                    },
                    "max_memory_gb": {
                        "type": "integer",
                        "description": "Maximum memory in GB allowed"
                    },
                    "max_storage_gb": {
                        "type": "integer",
                        "description": "Maximum storage in GB allowed"
                    }
                }
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        data = {k: v for k, v in arguments.items() if v is not None}
        
        result = await self.client._make_api_call("PUT", "/usage", data=data)
        
        if result.get("error"):
            return format_error_response(
                "Failed to update resources", 
                result.get("message", "Unknown error")
            )
        
        return format_success_response("Resources updated successfully", result)


class UsageModule(MCPModule):
    """Usage module containing all usage and resource-related tools"""
    
    def _initialize_tools(self):
        self.tools = {
            "get_usage_statistics": GetUsageStatisticsTool(self.client),
            "update_resources": UpdateResourcesTool(self.client)
        }
