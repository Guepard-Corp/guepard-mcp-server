"""
Database Users MCP Tools for Guepard Platform
"""

from typing import Dict, Any, List
from ..utils.base import MCPTool, MCPModule, GuepardAPIClient, format_success_response, format_error_response


class ListDatabaseUsersTool(MCPTool):
    """Tool for listing database users for a deployment"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "list_database_users",
            "description": "Get database users for deployment",
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
        
        result = await self.client._make_api_call("GET", f"/deploy/{deployment_id}/users")
        
        if result.get("error"):
            return format_error_response(
                "Failed to get database users", 
                result.get("message", "Unknown error")
            )
        
        if isinstance(result, list):
            count = len(result)
            return format_success_response(f"Found {count} database users for deployment {deployment_id}", result)
        else:
            return format_success_response(f"Database users retrieved for deployment {deployment_id}", result)


class BatchCreateDatabaseUsersTool(MCPTool):
    """Tool for creating multiple database users at once"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "batch_create_database_users",
            "description": "Create multiple database users at once",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "deployment_id": {
                        "type": "string",
                        "description": "Deployment ID"
                    },
                    "users": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "username": {
                                    "type": "string",
                                    "description": "Database username"
                                },
                                "password": {
                                    "type": "string",
                                    "description": "Database password"
                                },
                                "privileges": {
                                    "type": "array",
                                    "items": {
                                        "type": "string",
                                        "enum": ["SELECT", "INSERT", "UPDATE", "DELETE", "CREATE", "DROP", "ALTER", "INDEX", "REFERENCES"]
                                    },
                                    "description": "List of privileges to grant"
                                }
                            },
                            "required": ["username", "password"]
                        },
                        "description": "List of users to create"
                    }
                },
                "required": ["deployment_id", "users"]
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        deployment_id = arguments.get("deployment_id")
        users = arguments.get("users")
        
        data = {"users": users}
        
        result = await self.client._make_api_call("POST", f"/deploy/{deployment_id}/users", data=data)
        
        if result.get("error"):
            return format_error_response(
                "Failed to create database users", 
                result.get("message", "Unknown error")
            )
        
        return format_success_response(
            f"Batch created {len(users)} database users for deployment {deployment_id}",
            result
        )


class CreateDatabaseUserTool(MCPTool):
    """Tool for creating a single database user"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "create_database_user",
            "description": "Create a new database user",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "deployment_id": {
                        "type": "string",
                        "description": "Deployment ID"
                    },
                    "username": {
                        "type": "string",
                        "description": "Database username"
                    },
                    "password": {
                        "type": "string",
                        "description": "Database password"
                    },
                    "privileges": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["SELECT", "INSERT", "UPDATE", "DELETE", "CREATE", "DROP", "ALTER", "INDEX", "REFERENCES"]
                        },
                        "description": "List of privileges to grant"
                    }
                },
                "required": ["deployment_id", "username", "password"]
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        deployment_id = arguments.get("deployment_id")
        username = arguments.get("username")
        password = arguments.get("password")
        privileges = arguments.get("privileges", ["SELECT", "INSERT", "UPDATE"])
        
        data = {
            "username": username,
            "password": password,
            "privileges": privileges
        }
        
        result = await self.client._make_api_call("POST", f"/deploy/{deployment_id}/user", data=data)
        
        if result.get("error"):
            return format_error_response(
                "Failed to create database user", 
                result.get("message", "Unknown error")
            )
        
        return format_success_response(
            f"Database user '{username}' created successfully",
            result
        )


class UpdateDatabaseUserTool(MCPTool):
    """Tool for updating a database user"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "update_database_user",
            "description": "Update database user",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "deployment_id": {
                        "type": "string",
                        "description": "Deployment ID"
                    },
                    "username": {
                        "type": "string",
                        "description": "Database username"
                    },
                    "password": {
                        "type": "string",
                        "description": "New database password"
                    }
                },
                "required": ["deployment_id", "username"]
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        deployment_id = arguments.get("deployment_id")
        username = arguments.get("username")
        password = arguments.get("password")
        
        data = {"username": username}
        if password:
            data["password"] = password
        
        result = await self.client._make_api_call("PUT", f"/deploy/{deployment_id}/user", data=data)
        
        if result.get("error"):
            return format_error_response(
                "Failed to update database user", 
                result.get("message", "Unknown error")
            )
        
        return format_success_response(
            f"Database user '{username}' updated successfully",
            result
        )


class DeleteDatabaseUserTool(MCPTool):
    """Tool for deleting a database user"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "delete_database_user",
            "description": "Delete database user",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "deployment_id": {
                        "type": "string",
                        "description": "Deployment ID"
                    },
                    "username": {
                        "type": "string",
                        "description": "Database username"
                    }
                },
                "required": ["deployment_id", "username"]
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        deployment_id = arguments.get("deployment_id")
        username = arguments.get("username")
        
        data = {"username": username}
        
        result = await self.client._make_api_call("DELETE", f"/deploy/{deployment_id}/user", data=data)
        
        if result.get("error"):
            return format_error_response(
                "Failed to delete database user", 
                result.get("message", "Unknown error")
            )
        
        return format_success_response(
            f"Database user '{username}' deleted successfully",
            result
        )


class GrantPrivilegesTool(MCPTool):
    """Tool for granting privileges to a database user"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "grant_privileges",
            "description": "Grant privileges to database user",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "deployment_id": {
                        "type": "string",
                        "description": "Deployment ID"
                    },
                    "username": {
                        "type": "string",
                        "description": "Database username"
                    },
                    "privileges": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["SELECT", "INSERT", "UPDATE", "DELETE", "CREATE", "DROP", "ALTER", "INDEX", "REFERENCES"]
                        },
                        "description": "List of privileges to grant"
                    }
                },
                "required": ["deployment_id", "username", "privileges"]
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        deployment_id = arguments.get("deployment_id")
        username = arguments.get("username")
        privileges = arguments.get("privileges")
        
        data = {
            "username": username,
            "privileges": privileges
        }
        
        result = await self.client._make_api_call("POST", f"/deploy/{deployment_id}/user/grant-privs", data=data)
        
        if result.get("error"):
            return format_error_response(
                "Failed to grant privileges", 
                result.get("message", "Unknown error")
            )
        
        return format_success_response(
            f"Privileges granted to user '{username}'",
            {
                "deployment_id": deployment_id,
                "username": username,
                "privileges": privileges,
                "full_response": result
            }
        )


class RevokePrivilegesTool(MCPTool):
    """Tool for revoking privileges from a database user"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "revoke_privileges",
            "description": "Revoke privileges from database user",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "deployment_id": {
                        "type": "string",
                        "description": "Deployment ID"
                    },
                    "username": {
                        "type": "string",
                        "description": "Database username"
                    },
                    "privileges": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["SELECT", "INSERT", "UPDATE", "DELETE", "CREATE", "DROP", "ALTER", "INDEX", "REFERENCES"]
                        },
                        "description": "List of privileges to revoke"
                    }
                },
                "required": ["deployment_id", "username", "privileges"]
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        deployment_id = arguments.get("deployment_id")
        username = arguments.get("username")
        privileges = arguments.get("privileges")
        
        data = {
            "username": username,
            "privileges": privileges
        }
        
        result = await self.client._make_api_call("POST", f"/deploy/{deployment_id}/user/revoke-privs", data=data)
        
        if result.get("error"):
            return format_error_response(
                "Failed to revoke privileges", 
                result.get("message", "Unknown error")
            )
        
        return format_success_response(
            f"Privileges revoked from user '{username}'",
            {
                "deployment_id": deployment_id,
                "username": username,
                "privileges": privileges,
                "full_response": result
            }
        )


class ListUserPrivilegesTool(MCPTool):
    """Tool for listing privileges for a database user"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "list_user_privileges",
            "description": "List privileges for database user",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "deployment_id": {
                        "type": "string",
                        "description": "Deployment ID"
                    },
                    "username": {
                        "type": "string",
                        "description": "Database username"
                    }
                },
                "required": ["deployment_id", "username"]
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        deployment_id = arguments.get("deployment_id")
        username = arguments.get("username")
        
        data = {"username": username}
        
        result = await self.client._make_api_call("GET", f"/deploy/{deployment_id}/user/privs", data=data)
        
        if result.get("error"):
            return format_error_response(
                "Failed to list user privileges", 
                result.get("message", "Unknown error")
            )
        
        return format_success_response(
            f"Privileges for user '{username}'",
            {
                "deployment_id": deployment_id,
                "username": username,
                "privileges": result
            }
        )


class UsersModule(MCPModule):
    """Users module containing all database user-related tools"""
    
    def _initialize_tools(self):
        self.tools = {
            "list_database_users": ListDatabaseUsersTool(self.client),
            "batch_create_database_users": BatchCreateDatabaseUsersTool(self.client),
            "create_database_user": CreateDatabaseUserTool(self.client),
            "update_database_user": UpdateDatabaseUserTool(self.client),
            "delete_database_user": DeleteDatabaseUserTool(self.client),
            "grant_privileges": GrantPrivilegesTool(self.client),
            "revoke_privileges": RevokePrivilegesTool(self.client),
            "list_user_privileges": ListUserPrivilegesTool(self.client)
        }
