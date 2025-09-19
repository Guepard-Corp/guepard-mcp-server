"""
Deployments MCP Tools for Guepard Platform
"""

from typing import Dict, Any, Optional, List
from ..utils.base import MCPTool, MCPModule, GuepardAPIClient, format_success_response, format_error_response


class ListDeploymentsTool(MCPTool):
    """Tool for listing deployments"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "list_deployments",
            "description": "Get all deployments for the authenticated user",
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
        elif isinstance(result, dict):
            # Handle case where API returns a dict with deployments data
            return format_success_response("Deployments retrieved successfully", result)
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
                        "description": "Database version (will auto-match with performance profile if not specified)",
                    },
                    "deployment_type": {
                        "type": "string",
                        "description": "Type of deployment (REPOSITORY, F2, etc.). Auto-selects based on context: F2 for replicas/clones/parent deployments, REPOSITORY for new repositories.",
                        "enum": ["REPOSITORY", "F2"]
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
                        "description": "Performance profile ID. Use 'list_performance_profiles' tool to get available profile IDs, or leave empty to auto-select a default profile."
                    }
                },
                "required": ["repository_name"]
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        # Auto-select image provider, performance profile and database version if not provided
        performance_profile_id = arguments.get("performance_profile_id")
        selected_profile_version = None
        selected_database_provider = None
        
        if not performance_profile_id:
            try:
                # Step 1: Get available image providers
                from ..image_providers.tools import ImageProvidersModule
                image_providers_module = ImageProvidersModule(self.client)
                image_providers_result = await image_providers_module.call_tool("list_image_providers", {})
                
                # Parse image providers
                import json
                if "Found" in image_providers_result and "image providers" in image_providers_result:
                    json_start = image_providers_result.find('[')
                    if json_start != -1:
                        json_str = image_providers_result[json_start:]
                        image_providers = json.loads(json_str)
                        if not image_providers or len(image_providers) == 0:
                            return format_error_response(
                                "No image providers available", 
                                "Please contact support or specify a valid performance_profile_id"
                            )
                    else:
                        return format_error_response(
                            "Failed to parse image providers", 
                            "Please specify a valid performance_profile_id"
                        )
                else:
                    return format_error_response(
                        "Failed to get image providers", 
                        "Please specify a valid performance_profile_id"
                    )
                
                # Step 2: Get performance profiles
                from ..performance.tools import PerformanceModule
                performance_module = PerformanceModule(self.client)
                profiles_result = await performance_module.call_tool("list_performance_profiles", {})
                
                # Parse performance profiles
                if "Found" in profiles_result and "performance profiles" in profiles_result:
                    json_start = profiles_result.find('[')
                    if json_start != -1:
                        json_str = profiles_result[json_start:]
                        profiles = json.loads(json_str)
                        if profiles and len(profiles) > 0:
                            # Find a profile that matches available image providers
                            # Look for default profile first, then any profile that matches available providers
                            available_providers = [ip.get("catalog", {}).get("database_provider", "").lower() for ip in image_providers]
                            
                            # Try to find a default profile that matches available providers
                            default_profile = None
                            for profile in profiles:
                                if profile.get("is_default", False):
                                    provider = profile.get("database_provider", "").lower()
                                    if provider in available_providers:
                                        default_profile = profile
                                        break
                            
                            # If no default matches, use first profile that matches
                            if not default_profile:
                                for profile in profiles:
                                    provider = profile.get("database_provider", "").lower()
                                    if provider in available_providers:
                                        default_profile = profile
                                        break
                            
                            # If still no match, use first profile
                            if not default_profile:
                                default_profile = profiles[0]
                            
                            performance_profile_id = default_profile["id"]
                            selected_profile_version = default_profile.get("database_version", "17")
                            selected_database_provider = default_profile.get("database_provider", "PostgreSQL")
                        else:
                            return format_error_response(
                                "No performance profiles available", 
                                "Please create a performance profile first or specify a valid performance_profile_id"
                            )
                    else:
                        return format_error_response(
                            "Failed to parse performance profiles", 
                            "Please specify a valid performance_profile_id"
                        )
                else:
                    return format_error_response(
                        "Failed to get performance profiles", 
                        "Please specify a valid performance_profile_id"
                    )
            except Exception as e:
                return format_error_response(
                    "Failed to auto-select configuration", 
                    f"Please specify valid parameters. Error: {str(e)}"
                )
        
        # Auto-select database version if not provided
        database_version = arguments.get("database_version")
        if not database_version and selected_profile_version:
            database_version = selected_profile_version
        elif not database_version:
            database_version = "17"  # Fallback default
        
        # Auto-select database provider if not provided
        database_provider = arguments.get("database_provider")
        if not database_provider and selected_database_provider:
            database_provider = selected_database_provider
        elif not database_provider:
            database_provider = "PostgreSQL"  # Fallback default
        
        # Auto-select deployment type if not provided
        deployment_type = arguments.get("deployment_type")
        if not deployment_type:
            # Smart deployment type selection based on context
            repository_name = arguments.get("repository_name", "").lower()
            deployment_parent = arguments.get("deployment_parent")
            snapshot_parent = arguments.get("snapshot_parent")
            
            # Determine deployment type based on context clues
            if deployment_parent or snapshot_parent:
                # If there's a parent deployment or snapshot, likely a clone/replica
                deployment_type = "F2"
            elif any(keyword in repository_name for keyword in ["replica", "clone", "copy", "backup", "f2"]):
                # If repository name suggests it's a replica or F2 type
                deployment_type = "F2"
            elif any(keyword in repository_name for keyword in ["main", "master", "primary", "prod", "production"]):
                # If repository name suggests it's a main/production repo
                deployment_type = "REPOSITORY"
            else:
                # Default to REPOSITORY for new repositories
                deployment_type = "REPOSITORY"
        
        data = {
            "name": arguments.get("name"),
            "repository_name": arguments.get("repository_name"),
            "database_provider": database_provider,
            "database_version": database_version,
            "deployment_type": deployment_type,
            "performance_profile_id": performance_profile_id
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
            "description": "Get detailed information about a specific deployment",
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
    """Tool for updating deployment configuration"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "update_deployment",
            "description": "Update deployment configuration",
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
                    },
                    "performance_profile_id": {
                        "type": "string",
                        "description": "Updated performance profile ID"
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
        if arguments.get("performance_profile_id"):
            data["performance_profile_id"] = arguments.get("performance_profile_id")
        
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
            "description": "Delete a deployment and all associated resources",
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


class UpdateDeploymentEventsTool(MCPTool):
    """Tool for updating deployment events and status"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "update_deployment_events",
            "description": "Update deployment events and status",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "deployment_id": {
                        "type": "string",
                        "description": "Deployment ID"
                    },
                    "events": {
                        "type": "array",
                        "description": "List of events to update",
                        "items": {
                            "type": "object",
                            "properties": {
                                "type": {
                                    "type": "string",
                                    "description": "Event type (e.g., deployment_updated, status_changed)"
                                },
                                "timestamp": {
                                    "type": "string",
                                    "description": "Event timestamp in ISO format"
                                },
                                "data": {
                                    "type": "object",
                                    "description": "Event data payload"
                                }
                            },
                            "required": ["type", "timestamp"]
                        }
                    }
                },
                "required": ["deployment_id", "events"]
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        deployment_id = arguments.get("deployment_id")
        events = arguments.get("events", [])
        
        data = {
            "events": events
        }
        
        result = await self.client._make_api_call("PUT", f"/deploy/{deployment_id}/events", data=data)
        
        if result.get("error"):
            return format_error_response(
                "Failed to update deployment events", 
                result.get("message", "Unknown error")
            )
        
        return format_success_response(
            f"Deployment events updated successfully for {deployment_id}",
            result
        )


class GetDeploymentStatusTool(MCPTool):
    """Tool for getting current status of a deployment"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "get_deployment_status",
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


class DeploymentsModule(MCPModule):
    """Deployments module containing all deployment-related tools"""
    
    def _initialize_tools(self):
        self.tools = {
            "list_deployments": ListDeploymentsTool(self.client),
            "create_deployment": CreateDeploymentTool(self.client),
            "get_deployment": GetDeploymentTool(self.client),
            "update_deployment": UpdateDeploymentTool(self.client),
            "delete_deployment": DeleteDeploymentTool(self.client),
            "update_deployment_events": UpdateDeploymentEventsTool(self.client),
            "get_deployment_status": GetDeploymentStatusTool(self.client)
        }
