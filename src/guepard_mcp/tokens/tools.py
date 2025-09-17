"""
Tokens MCP Tools for Guepard Platform
"""

from typing import Dict, Any
from ..utils.base import MCPTool, MCPModule, GuepardAPIClient, format_success_response, format_error_response


class ListTokensTool(MCPTool):
    """Tool for listing all tokens"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "list_tokens",
            "description": "Get all tokens",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        result = await self.client._make_api_call("GET", "/tokens")
        
        if result.get("error"):
            return format_error_response(
                "Failed to get tokens", 
                result.get("message", "Unknown error")
            )
        
        if isinstance(result, list):
            count = len(result)
            return format_success_response(f"Found {count} tokens", result)
        else:
            return format_success_response("Tokens retrieved successfully", result)


class GenerateTokenTool(MCPTool):
    """Tool for generating a new token"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "generate_token",
            "description": "Generate new token",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Token name"
                    },
                    "expires_in": {
                        "type": "integer",
                        "description": "Token expiration time in seconds",
                        "default": 86400
                    }
                },
                "required": ["name"]
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        name = arguments.get("name")
        expires_in = arguments.get("expires_in", 86400)
        
        data = {
            "name": name,
            "expires_in": expires_in
        }
        
        result = await self.client._make_api_call("POST", "/tokens", data=data)
        
        if result.get("error"):
            return format_error_response(
                "Failed to generate token", 
                result.get("message", "Unknown error")
            )
        
        token_id = result.get("id", "Unknown")
        token_value = result.get("token", "")
        
        return format_success_response(
            f"Token '{name}' generated successfully",
            {
                "token_id": token_id,
                "token_name": name,
                "expires_in": expires_in,
                "token_value": token_value[:20] + "..." if token_value else "Not provided",
                "full_response": result
            }
        )


class RevokeTokenTool(MCPTool):
    """Tool for revoking a token"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "revoke_token",
            "description": "Revoke token",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "token_id": {
                        "type": "string",
                        "description": "Token ID"
                    }
                },
                "required": ["token_id"]
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        token_id = arguments.get("token_id")
        
        result = await self.client._make_api_call("DELETE", f"/tokens/{token_id}")
        
        if result.get("error"):
            return format_error_response(
                "Failed to revoke token", 
                result.get("message", "Unknown error")
            )
        
        return format_success_response(
            f"Token {token_id} revoked successfully",
            result
        )


class TokensModule(MCPModule):
    """Tokens module containing all token-related tools"""
    
    def _initialize_tools(self):
        self.tools = {
            "list_tokens": ListTokensTool(self.client),
            "generate_token": GenerateTokenTool(self.client),
            "revoke_token": RevokeTokenTool(self.client)
        }
