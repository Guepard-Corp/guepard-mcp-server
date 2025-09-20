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


class CheckoutSnapshotTool(MCPTool):
    """Tool for checking out to a random snapshot from a deployment's branches"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "checkout_snapshot",
            "description": "Get a deployment, randomly select one of its branches, randomly select one of its snapshots, then checkout to that snapshot",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "deployment_id": {
                        "type": "string",
                        "description": "Deployment ID"
                    },
                    "discard_changes": {
                        "type": "string",
                        "description": "Whether to discard changes",
                        "default": "true"
                    },
                    "checkout": {
                        "type": "boolean",
                        "description": "Whether to perform checkout",
                        "default": True
                    },
                    "ephemeral": {
                        "type": "boolean",
                        "description": "Whether the checkout is ephemeral",
                        "default": True
                    },
                    "performance_profile_name": {
                        "type": "string",
                        "description": "Performance profile name",
                        "default": "querying"
                    }
                },
                "required": []
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        import json
        import random
        
        deployment_id = arguments.get("deployment_id")
        discard_changes = arguments.get("discard_changes", "true")
        checkout = arguments.get("checkout", True)
        ephemeral = arguments.get("ephemeral", True)
        performance_profile_name = arguments.get("performance_profile_name", "querying")
        
        try:
            # Step 0: If no deployment_id provided, get a random deployment
            if not deployment_id:
                from ..deployments.tools import ListDeploymentsTool
                deployments_tool = ListDeploymentsTool(self.client)
                deployments_result = await deployments_tool.execute({})
                
                if "✅" not in deployments_result or "[" not in deployments_result:
                    return format_error_response(
                        "Failed to get deployments", 
                        "Could not fetch deployments"
                    )
                
                # Parse deployments JSON
                json_start = deployments_result.find("[")
                json_end = deployments_result.rfind("]") + 1
                if json_start == -1 or json_end == -1:
                    return format_error_response(
                        "Failed to parse deployments", 
                        "Could not parse deployments JSON response"
                    )
                
                json_str = deployments_result[json_start:json_end]
                deployments = json.loads(json_str)
                
                if len(deployments) == 0:
                    return format_error_response(
                        "No deployments found", 
                        "No deployments available"
                    )
                
                # Filter for CREATED deployments and randomly select one
                created_deployments = [d for d in deployments if d.get("status") == "CREATED"]
                if not created_deployments:
                    created_deployments = deployments  # Fall back to all deployments
                
                random_deployment = random.choice(created_deployments)
                deployment_id = random_deployment["id"]
            
            # Step 1: Get branches for the deployment
            from ..branches.tools import ListBranchesTool
            branches_tool = ListBranchesTool(self.client)
            branches_result = await branches_tool.execute({
                "deployment_id": deployment_id
            })
            
            if "✅" not in branches_result or "[" not in branches_result:
                return format_error_response(
                    "Failed to get branches", 
                    "Could not fetch branches for deployment"
                )
            
            # Parse branches JSON
            json_start = branches_result.find("[")
            json_end = branches_result.rfind("]") + 1
            if json_start == -1 or json_end == -1:
                return format_error_response(
                    "Failed to parse branches", 
                    "Could not parse branches JSON response"
                )
            
            json_str = branches_result[json_start:json_end]
            branches = json.loads(json_str)
            
            if len(branches) == 0:
                return format_error_response(
                    "No branches found", 
                    f"No branches found for deployment {deployment_id}"
                )
            
            # Step 2: Randomly select a branch (avoid the currently checked out one if possible)
            # Try to find a branch that's not currently checked out
            available_branches = [b for b in branches if b.get("job_status") != "ACTIVE"]
            if not available_branches:
                available_branches = branches  # Fall back to all branches if all are active
            
            random_branch = random.choice(available_branches)
            branch_id = random_branch["id"]
            
            # Step 3: Get snapshots for the selected branch
            from ..snapshots.tools import ListSnapshotsForBranchTool
            snapshots_tool = ListSnapshotsForBranchTool(self.client)
            snapshots_result = await snapshots_tool.execute({
                "deployment_id": deployment_id,
                "branch_id": branch_id
            })
            
            if "✅" not in snapshots_result or "[" not in snapshots_result:
                return format_error_response(
                    "Failed to get snapshots", 
                    f"Could not fetch snapshots for branch {branch_id}"
                )
            
            # Parse snapshots JSON
            json_start = snapshots_result.find("[")
            json_end = snapshots_result.rfind("]") + 1
            if json_start == -1 or json_end == -1:
                return format_error_response(
                    "Failed to parse snapshots", 
                    "Could not parse snapshots JSON response"
                )
            
            json_str = snapshots_result[json_start:json_end]
            snapshots = json.loads(json_str)
            
            if len(snapshots) == 0:
                return format_error_response(
                    "No snapshots found", 
                    f"No snapshots found for branch {branch_id}"
                )
            
            # Step 4: Randomly select a snapshot (avoid the currently checked out one if possible)
            # Try to find a snapshot that's not currently checked out
            current_snapshot_id = random_branch.get("snapshot_id")
            available_snapshots = [s for s in snapshots if s.get("id") != current_snapshot_id]
            if not available_snapshots:
                available_snapshots = snapshots  # Fall back to all snapshots if current is the only one
            
            random_snapshot = random.choice(available_snapshots)
            snapshot_id = random_snapshot["id"]
            
            # Step 5: Checkout the branch to the selected snapshot
            data = {
                "discard_changes": discard_changes,
                "checkout": checkout,
                "ephemeral": ephemeral,
                "performance_profile_name": performance_profile_name,
                "snapshot_id": snapshot_id
            }
            
            # Debug: Log the API call details
            print(f"🔍 API Call Debug:")
            print(f"   URL: /deploy/{deployment_id}/{branch_id}/{snapshot_id}/branch")
            print(f"   Data: {data}")
            print(f"   Branch: {random_branch.get('branch_name', 'unknown')} (ID: {branch_id})")
            print(f"   Snapshot: {random_snapshot.get('name', 'unknown')} (ID: {snapshot_id})")
            
            result = await self.client._make_api_call(
                "POST", 
                f"/deploy/{deployment_id}/{branch_id}/{snapshot_id}/branch", 
                data=data
            )
            
            # Check if it's an error or just a message about already being checked out
            if result.get("error"):
                return format_error_response(
                    "Failed to checkout snapshot", 
                    result.get("message", "Unknown error")
                )
            
            # Check if the response indicates the workspace is already checked out
            # The message might be in the body field if it's a 400 response
            message = result.get("message", "")
            body = result.get("body", "")
            
            # Parse body if it's a JSON string
            if body and isinstance(body, str):
                try:
                    import json
                    body_data = json.loads(body)
                    message = body_data.get("message", message)
                except:
                    pass
            
            if "already checked out" in message.lower():
                return format_success_response(
                    f"Workspace is already checked out to branch {branch_id} with snapshot {snapshot_id}",
                    {
                        "deployment_id": deployment_id,
                        "selected_branch": random_branch,
                        "selected_snapshot": random_snapshot,
                        "checkout_result": result,
                        "status": "already_checked_out"
                    }
                )
            
            return format_success_response(
                f"Successfully checked out to snapshot {snapshot_id} from branch {branch_id}",
                {
                    "deployment_id": deployment_id,
                    "selected_branch": random_branch,
                    "selected_snapshot": random_snapshot,
                    "checkout_result": result
                }
            )
            
        except Exception as e:
            return format_error_response(
                "Failed to checkout snapshot", 
                str(e)
            )


class CheckoutsModule(MCPModule):
    """Checkouts module containing all checkout-related tools"""
    
    def _initialize_tools(self):
        self.tools = {
            "checkout_branch": CheckoutBranchTool(self.client),
            "checkout_snapshot": CheckoutSnapshotTool(self.client)
        }
