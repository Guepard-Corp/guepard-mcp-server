"""
Authentication MCP Tools for Guepard Platform
"""

from typing import Dict, Any
from ..utils.base import MCPTool, MCPModule, GuepardAPIClient, format_success_response, format_error_response


# 3rd Party Authentication Tools
class StartLoginTool(MCPTool):
    """Tool for starting 3rd party authentication process"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "start_login",
            "description": "Start the login process with a third-party provider",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "provider": {
                        "type": "string",
                        "description": "Authentication provider",
                        "enum": ["supabase"],
                        "default": "supabase"
                    },
                    "redirect_url": {
                        "type": "string",
                        "description": "Redirect URL after authentication"
                    }
                },
                "required": ["redirect_url"]
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        provider = arguments.get("provider", "supabase")
        redirect_url = arguments.get("redirect_url")
        
        data = {
            "provider": provider,
            "redirect_url": redirect_url
        }
        
        result = await self.client._make_api_call("POST", "/start-login", data=data)
        
        if result.get("error"):
            return format_error_response(
                "Failed to start login", 
                result.get("message", "Unknown error")
            )
        
        return format_success_response(
            "Login process started successfully",
            {
                "login_url": result.get("login_url", ""),
                "state": result.get("state", ""),
                "expires_in": result.get("expires_in", 600)
            }
        )


class ResumeLoginTool(MCPTool):
    """Tool for resuming login with authorization code"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "resume_login",
            "description": "Resume the login process with authorization code",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "state": {
                        "type": "string",
                        "description": "State parameter from start-login response"
                    },
                    "code": {
                        "type": "string",
                        "description": "Authorization code from provider"
                    }
                },
                "required": ["state", "code"]
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        state = arguments.get("state")
        code = arguments.get("code")
        
        data = {
            "state": state,
            "code": code
        }
        
        result = await self.client._make_api_call("POST", "/resume-login", data=data)
        
        if result.get("error"):
            return format_error_response(
                "Failed to resume login", 
                result.get("message", "Unknown error")
            )
        
        return format_success_response(
            "Login resumed successfully",
            {
                "session_id": result.get("session_id", ""),
                "user_id": result.get("user_id", ""),
                "expires_in": result.get("expires_in", 3600),
                "next_step": result.get("next_step", "")
            }
        )


class VerifySessionTool(MCPTool):
    """Tool for verifying session and getting access token"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "verify_session",
            "description": "Verify the current session and get access token",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Session ID from resume-login response"
                    }
                },
                "required": ["session_id"]
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        session_id = arguments.get("session_id")
        
        data = {
            "session_id": session_id
        }
        
        result = await self.client._make_api_call("POST", "/verify-session", data=data)
        
        if result.get("error"):
            return format_error_response(
                "Failed to verify session", 
                result.get("message", "Unknown error")
            )
        
        return format_success_response(
            "Session verified successfully",
            {
                "access_token": result.get("access_token", "")[:20] + "..." if result.get("access_token") else "",
                "refresh_token": result.get("refresh_token", "")[:20] + "..." if result.get("refresh_token") else "",
                "expires_in": result.get("expires_in", 3600),
                "user": result.get("user", {})
            }
        )


class EndLoginTool(MCPTool):
    """Tool for ending login process"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "end_login",
            "description": "End the login process",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Session ID to end"
                    }
                },
                "required": ["session_id"]
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        session_id = arguments.get("session_id")
        
        data = {
            "session_id": session_id
        }
        
        result = await self.client._make_api_call("POST", "/end-login", data=data)
        
        if result.get("error"):
            return format_error_response(
                "Failed to end login", 
                result.get("message", "Unknown error")
            )
        
        return format_success_response("Login process ended successfully")


# Supabase Authentication Tools
class LoginSupabaseTool(MCPTool):
    """Tool for logging in with Supabase authentication"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "login_supabase",
            "description": "Login with Supabase authentication to get access and refresh tokens",
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
                "expires_in": result.get("expires_in", 3600),
                "token_type": result.get("token_type", "bearer"),
                "user_id": user.get("id", "Unknown"),
                "user_email": user.get("email", "Unknown")
            }
        )


class RefreshTokenSupabaseTool(MCPTool):
    """Tool for refreshing access token with Supabase"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "refresh_token_supabase",
            "description": "Refresh access token using refresh token",
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


class LogoutSupabaseTool(MCPTool):
    """Tool for logging out and invalidating tokens with Supabase"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "logout_supabase",
            "description": "Logout and invalidate tokens",
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
            # 3rd Party Authentication
            "start_login": StartLoginTool(self.client),
            "resume_login": ResumeLoginTool(self.client),
            "verify_session": VerifySessionTool(self.client),
            "end_login": EndLoginTool(self.client),
            # Supabase Authentication
            "login_supabase": LoginSupabaseTool(self.client),
            "refresh_token_supabase": RefreshTokenSupabaseTool(self.client),
            "logout_supabase": LogoutSupabaseTool(self.client)
        }
