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
        
        # Auto-subscribe if requested and server is available
        if auto_subscribe and self.server:
            self.server.subscribed_deployments.add(deployment_id)
            response += f"\n📌 Automatically subscribed to deployment {deployment_id}"
            response += f"\n📋 Total subscriptions: {len(self.server.subscribed_deployments)}"
        
        return format_success_response(response, result)


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


class GetComputeStatusTool(MCPTool):
    """Tool for getting compute status for a deployment"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "get_compute_status",
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


class StartAllSubscribedComputeTool(MCPTool):
    """Tool for starting compute for all subscribed deployments"""
    
    def __init__(self, client: GuepardAPIClient, config=None, server=None):
        super().__init__(client)
        self.config = config
        self.server = server
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "start_all_subscribed_compute",
            "description": "Start compute for all subscribed deployments",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "filter_by_status": {
                        "type": "string",
                        "description": "Only start compute for deployments with this status",
                        "enum": ["active", "pending", "failed", "terminated"]
                    }
                }
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        if not self.server or not self.server.subscribed_deployments:
            return "📋 No subscribed deployments to start compute for"
        
        filter_status = arguments.get("filter_by_status")
        
        try:
            started_count = 0
            skipped_count = 0
            error_count = 0
            results = []
            
            for deployment_id in self.server.subscribed_deployments:
                try:
                    # Check deployment status if filter is specified
                    if filter_status:
                        deployment_result = await self.client._make_api_call("GET", f"/deploy/{deployment_id}")
                        if deployment_result.get("error"):
                            results.append(f"❌ {deployment_id}: Error checking status")
                            error_count += 1
                            continue
                        
                        if deployment_result.get("status") != filter_status:
                            results.append(f"⏭️ {deployment_id}: Skipped (status: {deployment_result.get('status')})")
                            skipped_count += 1
                            continue
                    
                    # Start compute
                    compute_result = await self.client._make_api_call("GET", f"/deploy/{deployment_id}/start")
                    if compute_result.get("error"):
                        results.append(f"❌ {deployment_id}: Compute start failed - {compute_result.get('message', 'Unknown error')}")
                        error_count += 1
                    else:
                        results.append(f"✅ {deployment_id}: Compute start initiated")
                        started_count += 1
                    
                except Exception as e:
                    results.append(f"❌ {deployment_id}: Error - {str(e)}")
                    error_count += 1
            
            summary = f"🚀 Bulk Compute Start Results:\n"
            summary += f"✅ Started: {started_count}\n"
            summary += f"⏭️ Skipped: {skipped_count}\n"
            summary += f"❌ Errors: {error_count}\n\n"
            summary += "Details:\n" + "\n".join(results)
            
            return summary
        except Exception as e:
            return format_error_response("Failed to start compute for subscribed deployments", str(e))


class ComputeModule(MCPModule):
    """Compute module containing all compute-related tools"""
    
    def __init__(self, client: GuepardAPIClient, config=None, server=None):
        self.server = server
        super().__init__(client, config)
    
    def _initialize_tools(self):
        self.tools = {
            "start_compute": StartComputeTool(self.client, self.config, self.server),
            "stop_compute": StopComputeTool(self.client),
            "get_compute_status": GetComputeStatusTool(self.client),
            "start_all_subscribed_compute": StartAllSubscribedComputeTool(self.client, self.config, self.server)
        }