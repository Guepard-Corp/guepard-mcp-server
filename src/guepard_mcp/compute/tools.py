"""
Compute MCP Tools for Guepard Platform
"""

from typing import Dict, Any
from ..utils.base import MCPTool, MCPModule, GuepardAPIClient, format_success_response, format_error_response


class StartComputeTool(MCPTool):
    """Tool for starting compute resources for a deployment"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "start_compute",
            "description": "Start compute resources for a deployment",
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
        
        result = await self.client._make_api_call("GET", f"/deploy/{deployment_id}/start")
        
        if result.get("error"):
            return format_error_response(
                "Failed to start compute", 
                result.get("message", "Unknown error")
            )
        
        return format_success_response(
            f"Compute resources started for deployment {deployment_id}",
            result
        )


class StopComputeTool(MCPTool):
    """Tool for stopping compute resources for a deployment"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "stop_compute",
            "description": "Stop compute resources for a deployment",
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
        
        result = await self.client._make_api_call("GET", f"/deploy/{deployment_id}/stop")
        
        if result.get("error"):
            return format_error_response(
                "Failed to stop compute", 
                result.get("message", "Unknown error")
            )
        
        return format_success_response(
            f"Compute resources stopped for deployment {deployment_id}",
            result
        )


class ComputeModule(MCPModule):
    """Compute module containing all compute-related tools"""
    
    def _initialize_tools(self):
        self.tools = {
            "start_compute": StartComputeTool(self.client),
            "stop_compute": StopComputeTool(self.client)
        }