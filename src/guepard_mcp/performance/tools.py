"""
Performance Profiles MCP Tools for Guepard Platform
"""

import os
from typing import Dict, Any
from ..utils.base import MCPTool, MCPModule, GuepardAPIClient, format_success_response, format_error_response


class ListPerformanceProfilesTool(MCPTool):
    """Tool for listing all performance profiles"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "list_performance_profiles",
            "description": "Get all performance profiles",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        result = await self.client._make_api_call("GET", "/performance")
        
        if result.get("error"):
            return format_error_response(
                "Failed to get performance profiles", 
                result.get("message", "Unknown error")
            )
        
        if isinstance(result, list):
            count = len(result)
            return format_success_response(f"Found {count} performance profiles", result)
        else:
            return format_success_response("Performance profiles retrieved successfully", result)


class CreatePerformanceProfileTool(MCPTool):
    """Tool for creating a performance profile"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "create_performance_profile",
            "description": "Create performance profile",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "label_name": {
                        "type": "string",
                        "description": "Performance profile label name"
                    },
                    "description_text": {
                        "type": "string",
                        "description": "Description text"
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
                        "description": "Configuration flags as key-value pairs"
                    }
                },
                "required": ["label_name", "min_cpu", "min_memory"]
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        data = {
            "label_name": arguments.get("label_name"),
            "description_text": arguments.get("description_text", ""),
            "database_provider": arguments.get("database_provider", "PostgreSQL"),
            "database_version": arguments.get("database_version", "17"),
            "min_cpu": arguments.get("min_cpu"),
            "min_memory": arguments.get("min_memory")
        }
        
        # Add config flags if provided
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
    """Tool for updating a performance profile"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "update_performance_profile",
            "description": "Update performance profile",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "performance_profile_id": {
                        "type": "string",
                        "description": "Performance profile ID"
                    },
                    "label_name": {
                        "type": "string",
                        "description": "Updated label name"
                    },
                    "description_text": {
                        "type": "string",
                        "description": "Updated description text"
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
                        "description": "Updated configuration flags"
                    }
                },
                "required": ["performance_profile_id"]
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        performance_profile_id = arguments.get("performance_profile_id")
        
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
        
        result = await self.client._make_api_call(
            "PUT", 
            f"/performance/{performance_profile_id}", 
            data=data
        )
        
        if result.get("error"):
            return format_error_response(
                "Failed to update performance profile", 
                result.get("message", "Unknown error")
            )
        
        return format_success_response(
            f"Performance profile {performance_profile_id} updated successfully",
            result
        )


class GetPerformanceProfilesTool(MCPTool):
    """Tool for getting available performance profile defaults"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "get_performance_profiles",
            "description": "Get available performance profile defaults",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        # Get performance profiles from environment variables
        postgres16_profile = os.getenv("POSTGRES16_PROFILE_ID", "e54710e1-73dd-4628-a51d-93d1aab5226c")
        postgres17_profile = os.getenv("POSTGRES17_PROFILE_ID", "b0a4e557-bb67-4463-b774-ad82c04ab087")
        
        profiles_info = [
            f"• PostgreSQL 16: {postgres16_profile}",
            f"• PostgreSQL 17: {postgres17_profile}"
        ]
        
        return format_success_response(
            "Available Performance Profiles",
            {
                "profiles": {
                    "postgres16": postgres16_profile,
                    "postgres17": postgres17_profile
                },
                "description": "Use these profile IDs when creating deployments or configuring database performance settings."
            }
        )


class PerformanceModule(MCPModule):
    """Performance module containing all performance profile-related tools"""
    
    def _initialize_tools(self):
        self.tools = {
            "list_performance_profiles": ListPerformanceProfilesTool(self.client),
            "create_performance_profile": CreatePerformanceProfileTool(self.client),
            "update_performance_profile": UpdatePerformanceProfileTool(self.client),
            "get_performance_profiles": GetPerformanceProfilesTool(self.client)
        }
