#!/usr/bin/env python3
"""
Test utilities for Guepard MCP Server tests
"""

import json
from guepard_mcp.deployments.tools import ListDeploymentsTool
from guepard_mcp.utils.base import GuepardAPIClient


async def get_real_deployment_id(client: GuepardAPIClient, limit: int = 5) -> str:
    """
    Get a real deployment ID from the API dynamically, preferring CREATED status over INIT
    
    Args:
        client: GuepardAPIClient instance
        limit: Maximum number of deployments to fetch
        
    Returns:
        str: Real deployment ID
        
    Raises:
        Exception: If no deployments found or API call fails
    """
    list_tool = ListDeploymentsTool(client)
    
    print(f"    📋 Fetching real deployment IDs from API...")
    deployments_result = await list_tool.execute({"limit": limit})
    print(f"    Deployments result: {deployments_result}")
    
    # Extract deployment IDs from the result
    if "✅" in deployments_result and "[" in deployments_result:
        # Extract JSON part from the response
        json_start = deployments_result.find("[")
        json_end = deployments_result.rfind("]") + 1
        if json_start != -1 and json_end != -1:
            json_str = deployments_result[json_start:json_end]
            deployments = json.loads(json_str)
            if deployments and len(deployments) > 0:
                # Prefer CREATED status over INIT status
                created_deployments = [d for d in deployments if d.get("status") == "CREATED"]
                if created_deployments:
                    real_deployment_id = created_deployments[0]["id"]
                    print(f"    Using CREATED deployment ID: {real_deployment_id}")
                else:
                    real_deployment_id = deployments[0]["id"]
                    print(f"    Using deployment ID (status: {deployments[0].get('status', 'Unknown')}): {real_deployment_id}")
                return real_deployment_id
            else:
                raise Exception("No deployments found")
        else:
            raise Exception("Could not parse deployments JSON")
    else:
        raise Exception("Could not fetch deployments")


def get_fake_deployment_id() -> str:
    """
    Get a fake deployment ID for testing error cases
    
    Returns:
        str: Fake deployment ID that doesn't exist
    """
    return "99999999-9999-9999-9999-999999999999"


async def get_first_branch_id(client: GuepardAPIClient, deployment_id: str) -> str:
    """
    Get the first branch ID from a deployment
    
    Args:
        client: GuepardAPIClient instance
        deployment_id: Deployment ID to get branches from
        
    Returns:
        str: First branch ID
        
    Raises:
        Exception: If no branches found or API call fails
    """
    from guepard_mcp.branches.tools import ListBranchesTool
    
    list_tool = ListBranchesTool(client)
    
    print(f"    📋 Fetching branches for deployment {deployment_id}...")
    branches_result = await list_tool.execute({"deployment_id": deployment_id})
    print(f"    Branches result: {branches_result}")
    
    # Extract branch IDs from the result
    if "✅" in branches_result and "[" in branches_result:
        # Extract JSON part from the response
        json_start = branches_result.find("[")
        json_end = branches_result.rfind("]") + 1
        if json_start != -1 and json_end != -1:
            json_str = branches_result[json_start:json_end]
            branches = json.loads(json_str)
            if branches and len(branches) > 0:
                first_branch_id = branches[0]["id"]
                print(f"    Using first branch ID: {first_branch_id}")
                return first_branch_id
            else:
                raise Exception("No branches found for this deployment")
        else:
            raise Exception("Could not parse branches JSON")
    else:
        raise Exception("Could not fetch branches")


async def get_first_snapshot_id(client: GuepardAPIClient, deployment_id: str, branch_id: str) -> str:
    """
    Get the first snapshot ID from a branch
    
    Args:
        client: GuepardAPIClient instance
        deployment_id: Deployment ID
        branch_id: Branch ID to get snapshots from
        
    Returns:
        str: First snapshot ID
        
    Raises:
        Exception: If no snapshots found or API call fails
    """
    from guepard_mcp.snapshots.tools import ListSnapshotsForBranchTool
    
    list_tool = ListSnapshotsForBranchTool(client)
    
    print(f"    📋 Fetching snapshots for deployment {deployment_id}, branch {branch_id}...")
    snapshots_result = await list_tool.execute({
        "deployment_id": deployment_id,
        "branch_id": branch_id
    })
    print(f"    Snapshots result: {snapshots_result}")
    
    # Extract snapshot IDs from the result
    if "✅" in snapshots_result and "[" in snapshots_result:
        # Extract JSON part from the response
        json_start = snapshots_result.find("[")
        json_end = snapshots_result.rfind("]") + 1
        if json_start != -1 and json_end != -1:
            json_str = snapshots_result[json_start:json_end]
            snapshots = json.loads(json_str)
            if snapshots and len(snapshots) > 0:
                first_snapshot_id = snapshots[0]["id"]
                print(f"    Using first snapshot ID: {first_snapshot_id}")
                return first_snapshot_id
            else:
                raise Exception("No snapshots found for this branch")
        else:
            raise Exception("Could not parse snapshots JSON")
    else:
        raise Exception("Could not fetch snapshots")


async def get_deployment_with_multiple_branches(client: GuepardAPIClient, min_branches: int = 2) -> tuple[str, list[dict]]:
    """
    Get a deployment ID that has multiple branches
    
    Args:
        client: GuepardAPIClient instance
        min_branches: Minimum number of branches required
        
    Returns:
        tuple: (deployment_id, list of branches)
        
    Raises:
        Exception: If no deployment with multiple branches found
    """
    from guepard_mcp.branches.tools import ListBranchesTool
    
    list_tool = ListBranchesTool(client)
    
    print(f"    📋 Searching for deployment with at least {min_branches} branches...")
    
    # Get all deployments first
    deployments_result = await get_real_deployment_id(client, limit=10)
    if isinstance(deployments_result, str):
        # If get_real_deployment_id returns a string, we need to get deployments differently
        from guepard_mcp.deployments.tools import ListDeploymentsTool
        deployments_tool = ListDeploymentsTool(client)
        deployments_result = await deployments_tool.execute({"limit": 10})
    
    # Extract deployment IDs from the result
    if "✅" in str(deployments_result) and "[" in str(deployments_result):
        # Extract JSON part from the response
        deployments_str = str(deployments_result)
        json_start = deployments_str.find("[")
        json_end = deployments_str.rfind("]") + 1
        if json_start != -1 and json_end != -1:
            json_str = deployments_str[json_start:json_end]
            deployments = json.loads(json_str)
            
            # Check each deployment for multiple branches
            for deployment in deployments:
                deployment_id = deployment["id"]
                print(f"    Checking deployment {deployment_id}...")
                
                branches_result = await list_tool.execute({"deployment_id": deployment_id})
                
                if "✅" in branches_result and "[" in branches_result:
                    # Extract JSON part from the response
                    json_start = branches_result.find("[")
                    json_end = branches_result.rfind("]") + 1
                    if json_start != -1 and json_end != -1:
                        json_str = branches_result[json_start:json_end]
                        branches = json.loads(json_str)
                        
                        if len(branches) >= min_branches:
                            print(f"    ✅ Found deployment {deployment_id} with {len(branches)} branches")
                            return deployment_id, branches
            
            raise Exception(f"No deployment found with at least {min_branches} branches")
        else:
            raise Exception("Could not parse deployments JSON")
    else:
        raise Exception("Could not fetch deployments")


async def get_current_branch_info(client: GuepardAPIClient, deployment_id: str) -> dict:
    """
    Get information about the current branch state for a deployment
    
    Args:
        client: GuepardAPIClient instance
        deployment_id: Deployment ID to check
        
    Returns:
        dict: Current branch information including current branch ID and snapshot
        
    Raises:
        Exception: If unable to get current branch info
    """
    from guepard_mcp.deployments.tools import GetDeploymentTool
    
    get_tool = GetDeploymentTool(client)
    
    print(f"    📋 Getting current branch info for deployment {deployment_id}...")
    deployment_result = await get_tool.execute({"deployment_id": deployment_id})
    print(f"    Deployment result: {deployment_result}")
    
    # Extract current branch info from the result
    if "✅" in deployment_result and "{" in deployment_result:
        # Extract JSON part from the response
        json_start = deployment_result.find("{")
        json_end = deployment_result.rfind("}") + 1
        if json_start != -1 and json_end != -1:
            json_str = deployment_result[json_start:json_end]
            deployment_data = json.loads(json_str)
            
            current_branch_id = deployment_data.get("current_branch_id")
            current_snapshot_id = deployment_data.get("current_snapshot_id")
            
            if current_branch_id:
                print(f"    ✅ Current branch ID: {current_branch_id}")
                print(f"    ✅ Current snapshot ID: {current_snapshot_id}")
                return {
                    "current_branch_id": current_branch_id,
                    "current_snapshot_id": current_snapshot_id,
                    "deployment_data": deployment_data
                }
            else:
                raise Exception("No current branch found for this deployment")
        else:
            raise Exception("Could not parse deployment JSON")
    else:
        raise Exception("Could not fetch deployment info")
