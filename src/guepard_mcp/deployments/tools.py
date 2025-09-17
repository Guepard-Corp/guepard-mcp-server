"""
Deployments MCP Tools for Guepard Platform
"""

from typing import Dict, Any, Optional
from ..utils.base import MCPTool, MCPModule, GuepardAPIClient, format_success_response, format_error_response


class ListDeploymentsTool(MCPTool):
    """Tool for listing deployments"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "list_deployments",
            "description": "Get all deployments",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "description": "Filter by status",
                        "enum": ["active", "pending", "failed", "terminated"]
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Limit number of results",
                        "default": 100
                    }
                }
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        status = arguments.get("status")
        limit = arguments.get("limit", 100)
        
        params = {}
        if status:
            params["status"] = status
        if limit:
            params["limit"] = limit
        
        result = await self.client._make_api_call("GET", "/deploy", params=params)
        
        # Check if result is an error response (dict with error key)
        if isinstance(result, dict) and result.get("error"):
            return format_error_response(
                "Failed to get deployments", 
                result.get("message", "Unknown error")
            )
        
        # Handle successful response (list of deployments)
        if isinstance(result, list):
            count = len(result)
            return format_success_response(f"Found {count} deployments", result)
        else:
            return format_success_response("Deployments retrieved successfully", result)


class CreateDeploymentTool(MCPTool):
    """Tool for creating a new deployment"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "create_deployment",
            "description": "Create a new database deployment",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Deployment name"
                    },
                    "repository_name": {
                        "type": "string",
                        "description": "Repository name"
                    },
                    "database_provider": {
                        "type": "string",
                        "description": "Database provider",
                        "enum": ["PostgreSQL", "mysql", "mongodb"],
                        "default": "PostgreSQL"
                    },
                    "database_version": {
                        "type": "string",
                        "description": "Database version",
                        "default": "17"
                    },
                    "deployment_type": {
                        "type": "string",
                        "description": "Type of deployment",
                        "enum": ["REPOSITORY", "F2"],
                        "default": "REPOSITORY"
                    },
                    "deployment_parent": {
                        "type": "string",
                        "description": "Parent deployment ID (optional)"
                    },
                    "snapshot_parent": {
                        "type": "string",
                        "description": "Parent snapshot ID (optional)"
                    },
                    "performance_profile_id": {
                        "type": "string",
                        "description": "Performance profile ID. Use 'get_performance_profiles' tool to get available profile IDs."
                    }
                },
                "required": ["repository_name", "performance_profile_id"]
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        data = {
            "name": arguments.get("name"),
            "repository_name": arguments.get("repository_name"),
            "database_provider": arguments.get("database_provider", "PostgreSQL"),
            "database_version": arguments.get("database_version", "17"),
            "deployment_type": arguments.get("deployment_type", "REPOSITORY"),
            "performance_profile_id": arguments.get("performance_profile_id")
        }
        
        # Add optional fields if provided
        if arguments.get("deployment_parent"):
            data["deployment_parent"] = arguments.get("deployment_parent")
        if arguments.get("snapshot_parent"):
            data["snapshot_parent"] = arguments.get("snapshot_parent")
        
        result = await self.client._make_api_call("POST", "/deploy", data=data)
        
        if result.get("error"):
            return format_error_response(
                "Failed to create deployment", 
                result.get("message", "Unknown error")
            )
        
        deployment_id = result.get("id", "Unknown")
        deployment_name = result.get("name", "Unknown")
        
        return format_success_response(
            f"Deployment '{deployment_name}' created successfully",
            {
                "deployment_id": deployment_id,
                "deployment_name": deployment_name,
                "repository_name": arguments.get("repository_name"),
                "database_provider": arguments.get("database_provider", "PostgreSQL"),
                "database_version": arguments.get("database_version", "17"),
                "full_response": result
            }
        )


class GetDeploymentTool(MCPTool):
    """Tool for getting deployment details"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "get_deployment",
            "description": "Get deployment details",
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
                "Failed to get deployment", 
                result.get("message", "Unknown error")
            )
        
        return format_success_response(
            f"Deployment {deployment_id} retrieved successfully",
            result
        )


class UpdateDeploymentTool(MCPTool):
    """Tool for updating deployment"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "update_deployment",
            "description": "Update deployment",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "deployment_id": {
                        "type": "string",
                        "description": "Deployment ID"
                    },
                    "repository_name": {
                        "type": "string",
                        "description": "Updated repository name"
                    },
                    "name": {
                        "type": "string",
                        "description": "Updated deployment name"
                    },
                    "database_provider": {
                        "type": "string",
                        "description": "Updated database provider"
                    },
                    "database_version": {
                        "type": "string",
                        "description": "Updated database version"
                    }
                },
                "required": ["deployment_id"]
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        deployment_id = arguments.get("deployment_id")
        
        data = {}
        if arguments.get("repository_name"):
            data["repository_name"] = arguments.get("repository_name")
        if arguments.get("name"):
            data["name"] = arguments.get("name")
        if arguments.get("database_provider"):
            data["database_provider"] = arguments.get("database_provider")
        if arguments.get("database_version"):
            data["database_version"] = arguments.get("database_version")
        
        result = await self.client._make_api_call("PUT", f"/deploy/{deployment_id}", data=data)
        
        if result.get("error"):
            return format_error_response(
                "Failed to update deployment", 
                result.get("message", "Unknown error")
            )
        
        return format_success_response(
            f"Deployment {deployment_id} updated successfully",
            result
        )


class DeleteDeploymentTool(MCPTool):
    """Tool for deleting deployment"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "delete_deployment",
            "description": "Delete deployment",
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
        
        result = await self.client._make_api_call("DELETE", f"/deploy/{deployment_id}")
        
        if result.get("error"):
            return format_error_response(
                "Failed to delete deployment", 
                result.get("message", "Unknown error")
            )
        
        return format_success_response(
            f"Deployment {deployment_id} deleted successfully",
            result
        )


class DeploymentsModule(MCPModule):
    """Deployments module containing all deployment-related tools"""
    
    def _initialize_tools(self):
        self.tools = {
            "list_deployments": ListDeploymentsTool(self.client),
            "create_deployment": CreateDeploymentTool(self.client),
            "get_deployment": GetDeploymentTool(self.client),
            "update_deployment": UpdateDeploymentTool(self.client),
            "delete_deployment": DeleteDeploymentTool(self.client)
        }
