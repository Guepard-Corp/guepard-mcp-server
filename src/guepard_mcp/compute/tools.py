"""
Compute MCP Tools for Guepard Platform
"""

from typing import Dict, Any
from ..utils.base import MCPTool, MCPModule, GuepardAPIClient, format_success_response, format_error_response


class GetComputeStatusTool(MCPTool):
    """Tool for getting compute status"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "get_compute_status",
            "description": "Get compute status",
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


class StartComputeTool(MCPTool):
    """Tool for starting compute"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "start_compute",
            "description": "Start compute for a specific deployment",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "deployment_id": {
                        "type": "string",
                        "description": "Deployment ID"
                    },
                    "notify": {
                        "type": "boolean",
                        "description": "Send notification when operation completes",
                        "default": True
                    }
                },
                "required": ["deployment_id"]
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        deployment_id = arguments.get("deployment_id")
        notify = arguments.get("notify", True)
        
        result = await self.client._make_api_call("GET", f"/deploy/{deployment_id}/start")
        
        if result.get("error"):
            return format_error_response(
                "Failed to start compute", 
                result.get("message", "Unknown error")
            )
        
        status = "Compute started successfully"
        if notify:
            status += " (notifications enabled)"
        
        return format_success_response(
            status,
            {
                "deployment_id": deployment_id,
                "notify": notify,
                "full_response": result
            }
        )


class StopComputeTool(MCPTool):
    """Tool for stopping compute"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "stop_compute",
            "description": "Stop compute for a specific deployment",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "deployment_id": {
                        "type": "string",
                        "description": "Deployment ID"
                    },
                    "notify": {
                        "type": "boolean",
                        "description": "Send notification when operation completes",
                        "default": True
                    }
                },
                "required": ["deployment_id"]
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        deployment_id = arguments.get("deployment_id")
        notify = arguments.get("notify", True)
        
        result = await self.client._make_api_call("GET", f"/deploy/{deployment_id}/stop")
        
        if result.get("error"):
            return format_error_response(
                "Failed to stop compute", 
                result.get("message", "Unknown error")
            )
        
        status = "Compute stopped successfully"
        if notify:
            status += " (notifications enabled)"
        
        return format_success_response(
            status,
            {
                "deployment_id": deployment_id,
                "notify": notify,
                "full_response": result
            }
        )


class GetDeploymentStatusTool(MCPTool):
    """Tool for getting deployment status"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "get_deployment_status",
            "description": "Get deployment status",
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
        
        result = await self.client._make_api_call("GET", f"/deploy/{deployment_id}/status")
        
        if result.get("error"):
            return format_error_response(
                "Failed to get deployment status", 
                result.get("message", "Unknown error")
            )
        
        return format_success_response(
            f"Deployment status retrieved for {deployment_id}",
            result
        )


class GetDeploymentLogsTool(MCPTool):
    """Tool for getting deployment logs"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "get_deployment_logs",
            "description": "Get deployment logs",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "deployment_id": {
                        "type": "string",
                        "description": "Deployment ID"
                    },
                    "lines": {
                        "type": "integer",
                        "description": "Number of log lines to retrieve",
                        "default": 100
                    }
                },
                "required": ["deployment_id"]
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        deployment_id = arguments.get("deployment_id")
        lines = arguments.get("lines", 100)
        
        params = {"lines": lines} if lines else {}
        
        result = await self.client._make_api_call(
            "GET", 
            f"/deploy/{deployment_id}/logs", 
            params=params
        )
        
        if result.get("error"):
            return format_error_response(
                "Failed to get deployment logs", 
                result.get("message", "Unknown error")
            )
        
        return format_success_response(
            f"Deployment logs retrieved for {deployment_id}",
            result
        )


class GetDeploymentMetricsTool(MCPTool):
    """Tool for getting deployment metrics"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "get_deployment_metrics",
            "description": "Get deployment metrics",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "deployment_id": {
                        "type": "string",
                        "description": "Deployment ID"
                    },
                    "time_range": {
                        "type": "string",
                        "description": "Time range for metrics",
                        "enum": ["1h", "6h", "24h", "7d"],
                        "default": "1h"
                    }
                },
                "required": ["deployment_id"]
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        deployment_id = arguments.get("deployment_id")
        time_range = arguments.get("time_range", "1h")
        
        params = {"time_range": time_range}
        
        result = await self.client._make_api_call(
            "GET", 
            f"/deploy/{deployment_id}/metrics", 
            params=params
        )
        
        if result.get("error"):
            return format_error_response(
                "Failed to get deployment metrics", 
                result.get("message", "Unknown error")
            )
        
        return format_success_response(
            f"Deployment metrics retrieved for {deployment_id}",
            {
                "time_range": time_range,
                "metrics": result
            }
        )


class ComputeModule(MCPModule):
    """Compute module containing all compute-related tools"""
    
    def _initialize_tools(self):
        self.tools = {
            "get_compute_status": GetComputeStatusTool(self.client),
            "start_compute": StartComputeTool(self.client),
            "stop_compute": StopComputeTool(self.client),
            "get_deployment_status": GetDeploymentStatusTool(self.client),
            "get_deployment_logs": GetDeploymentLogsTool(self.client),
            "get_deployment_metrics": GetDeploymentMetricsTool(self.client)
        }
