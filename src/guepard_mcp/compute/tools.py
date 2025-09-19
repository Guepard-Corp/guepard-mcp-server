"""
Compute MCP Tools for Guepard Platform
"""

from typing import Dict, Any
from ..utils.base import MCPTool, MCPModule, GuepardAPIClient, format_success_response, format_error_response


class StartComputeTool(MCPTool):
    """Tool for starting compute resources for a deployment"""
    
    def __init__(self, client: GuepardAPIClient, config=None, server=None):
        super().__init__(client)
        self.config = config
        self.server = server
    
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
                    },
                    "auto_subscribe": {
                        "type": "boolean",
                        "description": "Automatically subscribe to this deployment",
                        "default": False
                    }
                },
                "required": ["deployment_id"]
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        deployment_id = arguments.get("deployment_id")
        auto_subscribe = arguments.get("auto_subscribe", False)
        
        result = await self.client._make_api_call("GET", f"/deploy/{deployment_id}/start")
        
        if result.get("error"):
            return format_error_response(
                "Failed to start compute", 
                result.get("message", "Unknown error")
            )
        
        response = f"✅ Compute resources started for deployment {deployment_id}"
        
        # Always auto-subscribe when starting compute (unless explicitly disabled)
        if self.server and deployment_id:
            self.server.subscribed_deployments.add(deployment_id)
            response += f"\n📌 Automatically subscribed to deployment {deployment_id}"
            response += f"\n📋 Total subscriptions: {len(self.server.subscribed_deployments)}"
        
        return format_success_response(response, result)


class StopComputeTool(MCPTool):
    """Tool for stopping compute resources for a deployment"""
    
    def __init__(self, client: GuepardAPIClient, config=None, server=None):
        super().__init__(client)
        self.config = config
        self.server = server
    
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
        
        response = f"✅ Compute resources stopped for deployment {deployment_id}"
        
        # Auto-subscribe when stopping compute to track the deployment
        if self.server and deployment_id:
            self.server.subscribed_deployments.add(deployment_id)
            response += f"\n📌 Automatically subscribed to deployment {deployment_id}"
            response += f"\n📋 Total subscriptions: {len(self.server.subscribed_deployments)}"
        
        return format_success_response(response, result)


class GetComputeTool(MCPTool):
    """Tool for getting compute status for a deployment"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "get_compute",
            "description": "Get compute status for a deployment",
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
        
        result = await self.client._make_api_call("GET", f"/deploy/{deployment_id}/compute")
        
        if result.get("error"):
            return format_error_response(
                "Failed to get compute status", 
                result.get("message", "Unknown error")
            )
        
        return format_success_response(
            f"Compute status retrieved for deployment {deployment_id}",
            result
        )


class GetComputeStatusTool(MCPTool):
    """Tool for getting current status of a deployment"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "get_compute_status",
            "description": "Get current status of a deployment",
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
        
        result = await self.client._make_api_call("GET", f"/deploy/{deployment_id}")
        
        if result.get("error"):
            return format_error_response(
                "Failed to get deployment status", 
                result.get("message", "Unknown error")
            )
        
        # Extract status information from the deployment data
        status = result.get("status", "Unknown")
        deployment_name = result.get("name", "Unknown")
        
        return format_success_response(
            f"Deployment status for {deployment_name} ({deployment_id}): {status}",
            {
                "deployment_id": deployment_id,
                "deployment_name": deployment_name,
                "status": status,
                "full_deployment_data": result
            }
        )


class ComputeModule(MCPModule):
    """Compute module containing all compute-related tools"""
    
    def __init__(self, client: GuepardAPIClient, config=None, server=None):
        self.server = server
        super().__init__(client, config)
    
    def _initialize_tools(self):
        self.tools = {
            "start_compute": StartComputeTool(self.client, self.config, self.server),
            "stop_compute": StopComputeTool(self.client, self.config, self.server),
            "get_compute": GetComputeTool(self.client),
            "get_compute_status": GetComputeStatusTool(self.client)
        }