"""
Logs & Metrics MCP Tools for Guepard Platform
"""

from typing import Dict, Any
from ..utils.base import MCPTool, MCPModule, GuepardAPIClient, format_success_response, format_error_response


class GetDeploymentLogsTool(MCPTool):
    """Tool for getting deployment logs for monitoring and debugging"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "get_deployment_logs",
            "description": "Get deployment logs for monitoring and debugging",
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
                    },
                    "level": {
                        "type": "string",
                        "description": "Filter logs by level",
                        "enum": ["DEBUG", "INFO", "WARN", "ERROR", "FATAL"]
                    },
                    "component": {
                        "type": "string",
                        "description": "Filter logs by component"
                    }
                },
                "required": ["deployment_id"]
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        deployment_id = arguments.get("deployment_id")
        lines = arguments.get("lines", 100)
        level = arguments.get("level")
        component = arguments.get("component")
        
        params = {}
        if lines:
            params["lines"] = lines
        if level:
            params["level"] = level
        if component:
            params["component"] = component
        
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
    """Tool for getting deployment metrics and performance data"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "get_deployment_metrics",
            "description": "Get deployment metrics and performance data",
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
                        "enum": ["1h", "6h", "24h", "7d", "30d"],
                        "default": "1h"
                    },
                    "metric_type": {
                        "type": "string",
                        "description": "Type of metrics to retrieve",
                        "enum": ["cpu", "memory", "storage", "network", "all"],
                        "default": "all"
                    }
                },
                "required": ["deployment_id"]
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        deployment_id = arguments.get("deployment_id")
        time_range = arguments.get("time_range", "1h")
        metric_type = arguments.get("metric_type", "all")
        
        params = {
            "time_range": time_range,
            "metric_type": metric_type
        }
        
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
            result
        )


class LogsModule(MCPModule):
    """Logs module containing all logs and metrics-related tools"""
    
    def _initialize_tools(self):
        self.tools = {
            "get_deployment_logs": GetDeploymentLogsTool(self.client),
            "get_deployment_metrics": GetDeploymentMetricsTool(self.client)
        }
