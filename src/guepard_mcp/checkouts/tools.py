"""
Checkouts MCP Tools for Guepard Platform
"""

from typing import Dict, Any
from ..utils.base import MCPTool, MCPModule, GuepardAPIClient, format_success_response, format_error_response


class CheckoutBranchTool(MCPTool):
    """Tool for checking out to a specific branch with snapshot"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "checkout_branch",
            "description": "Checkout to a specific branch with snapshot",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "deployment_id": {
                        "type": "string",
                        "description": "Deployment ID"
                    },
                    "branch_id": {
                        "type": "string",
                        "description": "Branch ID"
                    },
                    "snapshot_id": {
                        "type": "string",
                        "description": "Snapshot ID to checkout to"
                    }
                },
                "required": ["deployment_id", "branch_id", "snapshot_id"]
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        deployment_id = arguments.get("deployment_id")
        branch_id = arguments.get("branch_id")
        snapshot_id = arguments.get("snapshot_id")
        
        data = {"snapshot_id": snapshot_id}
        
        result = await self.client._make_api_call(
            "POST", 
            f"/deploy/{deployment_id}/{branch_id}/checkout", 
            data=data
        )
        
        if result.get("error"):
            return format_error_response(
                "Failed to checkout branch", 
                result.get("message", "Unknown error")
            )
        
        return format_success_response(
            f"Branch {branch_id} checked out successfully to snapshot {snapshot_id}",
            result
        )


class CheckoutsModule(MCPModule):
    """Checkouts module containing all checkout-related tools"""
    
    def _initialize_tools(self):
        self.tools = {
            "checkout_branch": CheckoutBranchTool(self.client)
        }
