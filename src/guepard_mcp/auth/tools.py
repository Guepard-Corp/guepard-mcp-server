"""
Authentication MCP Tools for Guepard Platform
"""

from typing import Dict, Any
from ..utils.base import MCPTool, MCPModule, GuepardAPIClient, format_success_response, format_error_response


class LoginTool(MCPTool):
    """Tool for logging in with Supabase authentication"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "login_supabase",
            "description": "Login with Supabase authentication",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "email": {
                        "type": "string",
                        "description": "User email address"
                    },
                    "password": {
                        "type": "string",
                        "description": "User password"
                    }
                },
                "required": ["email", "password"]
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        email = arguments.get("email")
        password = arguments.get("password")
        
        data = {
            "email": email,
            "password": password
        }
        
        result = await self.client._make_api_call(
            "POST", 
            "/auth/v1/token?grant_type=password", 
            data=data, 
            use_auth_api=True
        )
        
        if result.get("error"):
            return format_error_response(
                "Login failed", 
                result.get("message", "Unknown error")
            )
        
        # Extract tokens and user info
        access_token = result.get("access_token", "")
        refresh_token = result.get("refresh_token", "")
        user = result.get("user", {})
        
        return format_success_response(
            f"Login successful for {email}",
            {
                "access_token": access_token[:20] + "..." if access_token else "Not provided",
                "refresh_token": refresh_token[:20] + "..." if refresh_token else "Not provided",
                "user_id": user.get("id", "Unknown"),
                "user_email": user.get("email", "Unknown")
            }
        )


class RefreshTokenTool(MCPTool):
    """Tool for refreshing access token with Supabase"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "refresh_token_supabase",
            "description": "Refresh access token with Supabase",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "refresh_token": {
                        "type": "string",
                        "description": "Refresh token"
                    }
                },
                "required": ["refresh_token"]
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        refresh_token = arguments.get("refresh_token")
        
        data = {
            "refresh_token": refresh_token
        }
        
        result = await self.client._make_api_call(
            "POST", 
            "/auth/v1/token?grant_type=refresh_token", 
            data=data, 
            use_auth_api=True
        )
        
        if result.get("error"):
            return format_error_response(
                "Token refresh failed", 
                result.get("message", "Unknown error")
            )
        
        access_token = result.get("access_token", "")
        
        return format_success_response(
            "Token refreshed successfully",
            {
                "access_token": access_token[:20] + "..." if access_token else "Not provided",
                "expires_in": result.get("expires_in", "Unknown")
            }
        )


class LogoutTool(MCPTool):
    """Tool for logging out and invalidating tokens with Supabase"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "logout_supabase",
            "description": "Logout and invalidate tokens with Supabase",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "refresh_token": {
                        "type": "string",
                        "description": "Refresh token to invalidate"
                    }
                },
                "required": ["refresh_token"]
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        refresh_token = arguments.get("refresh_token")
        
        data = {
            "refresh_token": refresh_token
        }
        
        result = await self.client._make_api_call(
            "POST", 
            "/auth/v1/logout", 
            data=data, 
            use_auth_api=True
        )
        
        if result.get("error"):
            return format_error_response(
                "Logout failed", 
                result.get("message", "Unknown error")
            )
        
        return format_success_response("Logout successful - tokens invalidated")


class AuthModule(MCPModule):
    """Authentication module containing all auth-related tools"""
    
    def _initialize_tools(self):
        self.tools = {
            "login_supabase": LoginTool(self.client),
            "refresh_token_supabase": RefreshTokenTool(self.client),
            "logout_supabase": LogoutTool(self.client)
        }
