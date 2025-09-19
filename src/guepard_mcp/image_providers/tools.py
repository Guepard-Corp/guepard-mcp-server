"""
Image Providers MCP Tools for Guepard Platform
"""

from typing import Dict, Any
from ..utils.base import MCPTool, MCPModule, GuepardAPIClient, format_success_response, format_error_response


class ListImageProvidersTool(MCPTool):
    """Tool for listing all available database image providers"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "list_image_providers",
            "description": "Get all available database image providers",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        result = await self.client._make_api_call("GET", "/image-providers")
        
        # Check if result is an error response (dict with error key)
        if isinstance(result, dict) and result.get("error"):
            return format_error_response(
                "Failed to get image providers", 
                result.get("message", "Unknown error")
            )
        
        # Handle successful response (list of image providers)
        if isinstance(result, list):
            count = len(result)
            return format_success_response(f"Found {count} image providers", result)
        elif isinstance(result, dict):
            # Handle case where API returns a dict with image providers data
            return format_success_response("Image providers retrieved successfully", result)
        else:
            return format_success_response("Image providers retrieved successfully", result)


class ImageProvidersModule(MCPModule):
    """Image Providers module containing all image provider-related tools"""
    
    def _initialize_tools(self):
        self.tools = {
            "list_image_providers": ListImageProvidersTool(self.client)
        }
