#!/usr/bin/env python3
"""
Test utilities for Guepard MCP Server tests
"""

import json
from guepard_mcp.deployments.tools import ListDeploymentsTool
from guepard_mcp.utils.base import GuepardAPIClient


async def get_real_deployment_id(client: GuepardAPIClient, limit: int = 5) -> str:
    """
    Get a real deployment ID from the API dynamically
    
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
                real_deployment_id = deployments[0]["id"]
                print(f"    Using real deployment ID: {real_deployment_id}")
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
