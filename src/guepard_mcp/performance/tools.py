"""
Performance MCP Tools for Guepard Platform
"""

from typing import Dict, Any
from ..utils.base import MCPTool, MCPModule, GuepardAPIClient, format_success_response, format_error_response


class ListPerformanceProfilesTool(MCPTool):
    """Tool for listing all available performance profiles"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "list_performance_profiles",
            "description": "Get all available performance profiles",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        result = await self.client._make_api_call("GET", "/performance")
        
        # Check if result is an error response (dict with error key)
        if isinstance(result, dict) and result.get("error"):
            return format_error_response(
                "Failed to get performance profiles", 
                result.get("message", "Unknown error")
            )
        
        # Handle successful response (list of profiles)
        if isinstance(result, list):
            count = len(result)
            return format_success_response(f"Found {count} performance profiles", result)
        else:
            return format_success_response("Performance profiles retrieved successfully", result)


class CreatePerformanceProfileTool(MCPTool):
    """Tool for creating a new performance profile"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "create_performance_profile",
            "description": "Create a new performance profile",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "label_name": {
                        "type": "string",
                        "description": "Profile label name"
                    },
                    "description_text": {
                        "type": "string",
                        "description": "Profile description"
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
                    "min_cpu": {
                        "type": "integer",
                        "description": "Minimum CPU cores"
                    },
                    "min_memory": {
                        "type": "integer",
                        "description": "Minimum memory in MB"
                    },
                    "config_flags": {
                        "type": "object",
                        "description": "Database configuration flags (e.g., max_connections, shared_buffers, work_mem)"
                    }
                },
                "required": ["label_name", "description_text", "min_cpu", "min_memory"]
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        data = {
            "label_name": arguments.get("label_name"),
            "description_text": arguments.get("description_text"),
            "database_provider": arguments.get("database_provider", "PostgreSQL"),
            "database_version": arguments.get("database_version", "17"),
            "min_cpu": arguments.get("min_cpu"),
            "min_memory": arguments.get("min_memory")
        }
        
        # Add optional config_flags if provided
        if arguments.get("config_flags"):
            data["config_flags"] = arguments.get("config_flags")
        
        result = await self.client._make_api_call("POST", "/performance", data=data)
        
        if result.get("error"):
            return format_error_response(
                "Failed to create performance profile", 
                result.get("message", "Unknown error")
            )
        
        profile_id = result.get("id", "Unknown")
        profile_name = result.get("label_name", "Unknown")
        
        return format_success_response(
            f"Performance profile '{profile_name}' created successfully",
            {
                "profile_id": profile_id,
                "profile_name": profile_name,
                "database_provider": arguments.get("database_provider", "PostgreSQL"),
                "database_version": arguments.get("database_version", "17"),
                "min_cpu": arguments.get("min_cpu"),
                "min_memory": arguments.get("min_memory"),
                "full_response": result
            }
        )


class UpdatePerformanceProfileTool(MCPTool):
    """Tool for updating an existing performance profile"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "update_performance_profile",
            "description": "Update an existing performance profile",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "profile_id": {
                        "type": "string",
                        "description": "Performance profile ID"
                    },
                    "label_name": {
                        "type": "string",
                        "description": "Updated profile label name"
                    },
                    "description_text": {
                        "type": "string",
                        "description": "Updated profile description"
                    },
                    "min_cpu": {
                        "type": "integer",
                        "description": "Updated minimum CPU cores"
                    },
                    "min_memory": {
                        "type": "integer",
                        "description": "Updated minimum memory in MB"
                    },
                    "config_flags": {
                        "type": "object",
                        "description": "Updated database configuration flags"
                    }
                },
                "required": ["profile_id"]
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        profile_id = arguments.get("profile_id")
        
        data = {}
        if arguments.get("label_name"):
            data["label_name"] = arguments.get("label_name")
        if arguments.get("description_text"):
            data["description_text"] = arguments.get("description_text")
        if arguments.get("min_cpu"):
            data["min_cpu"] = arguments.get("min_cpu")
        if arguments.get("min_memory"):
            data["min_memory"] = arguments.get("min_memory")
        if arguments.get("config_flags"):
            data["config_flags"] = arguments.get("config_flags")
        
        result = await self.client._make_api_call("PUT", f"/performance/{profile_id}", data=data)
        
        if result.get("error"):
            return format_error_response(
                "Failed to update performance profile", 
                result.get("message", "Unknown error")
            )
        
        return format_success_response(
            f"Performance profile {profile_id} updated successfully",
            result
        )


class ApplyPerformanceProfileTool(MCPTool):
    """Tool for applying a performance profile to a deployment"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "apply_performance_profile",
            "description": "Apply a performance profile to a deployment",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "deployment_id": {
                        "type": "string",
                        "description": "Deployment ID"
                    },
                    "performance_profile_id": {
                        "type": "string",
                        "description": "Performance profile ID to apply"
                    }
                },
                "required": ["deployment_id", "performance_profile_id"]
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        deployment_id = arguments.get("deployment_id")
        performance_profile_id = arguments.get("performance_profile_id")
        
        result = await self.client._make_api_call(
            "POST", 
            f"/deploy/{deployment_id}/performance/{performance_profile_id}"
        )
        
        if result.get("error"):
            return format_error_response(
                "Failed to apply performance profile", 
                result.get("message", "Unknown error")
            )
        
        return format_success_response(
            f"Performance profile {performance_profile_id} applied to deployment {deployment_id}",
            {
                "deployment_id": deployment_id,
                "performance_profile_id": performance_profile_id,
                "applied_date": result.get("applied_date", "Unknown"),
                "restart_required": result.get("restart_required", False),
                "full_response": result
            }
        )


class PerformanceModule(MCPModule):
    """Performance module containing all performance-related tools"""
    
    def _initialize_tools(self):
        self.tools = {
            "list_performance_profiles": ListPerformanceProfilesTool(self.client),
            "create_performance_profile": CreatePerformanceProfileTool(self.client),
            "update_performance_profile": UpdatePerformanceProfileTool(self.client),
            "apply_performance_profile": ApplyPerformanceProfileTool(self.client)
        }
