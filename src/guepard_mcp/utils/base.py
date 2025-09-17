"""
Base classes and utilities for Guepard MCP Server
"""

import os
import json
import logging
import aiohttp
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class GuepardAPIClient:
    """Base API client for Guepard platform"""
    
    def __init__(self):
        self.access_token = os.getenv("ACCESS_TOKEN", "")
        self.api_base_url = os.getenv("GUEPARD_API_URL", "https://api.guepard.run")
        self.auth_api_url = os.getenv("GUEPARD_AUTH_API", "https://auth.guepard.run")
        self.supabase_anon_key = os.getenv("SUPABASE_ANON_KEY", "")
        self.session: Optional[aiohttp.ClientSession] = None
        
        if not self.access_token:
            logger.warning("ACCESS_TOKEN not found in environment variables")
    
    async def connect(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession(
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.access_token}"
            }
        )
        logger.info("HTTP session initialized")
    
    async def disconnect(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
            logger.info("HTTP session closed")
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for Supabase auth calls"""
        return {
            "Content-Type": "application/json",
            "apikey": self.supabase_anon_key,
            "Authorization": f"Bearer {self.access_token}"
        }
    
    async def _make_api_call(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None, 
        params: Optional[Dict] = None,
        use_auth_api: bool = False
    ) -> Dict:
        """Make API call to Guepard platform"""
        base_url = self.auth_api_url if use_auth_api else self.api_base_url
        url = f"{base_url}{endpoint}"
        
        headers = self._get_auth_headers() if use_auth_api else {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token}"
        }
        
        try:
            async with self.session.request(method, url, json=data, params=params, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    return {
                        "error": True,
                        "status_code": response.status,
                        "message": error_text
                    }
        except Exception as e:
            return {
                "error": True,
                "message": f"API call failed: {str(e)}"
            }


class MCPTool(ABC):
    """Abstract base class for MCP tools"""
    
    def __init__(self, client: GuepardAPIClient):
        self.client = client
    
    @abstractmethod
    def get_tool_definition(self) -> Dict[str, Any]:
        """Return the tool definition for MCP"""
        pass
    
    @abstractmethod
    async def execute(self, arguments: Dict[str, Any]) -> str:
        """Execute the tool with given arguments"""
        pass


class MCPModule(ABC):
    """Abstract base class for MCP modules (groups of related tools)"""
    
    def __init__(self, client: GuepardAPIClient, config=None):
        self.client = client
        self.config = config
        self.tools: Dict[str, MCPTool] = {}
        self._initialize_tools()
    
    @abstractmethod
    def _initialize_tools(self):
        """Initialize all tools for this module"""
        pass
    
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Get all tool definitions for this module"""
        return [tool.get_tool_definition() for tool in self.tools.values()]
    
    def get_enabled_tool_definitions(self) -> List[Dict[str, Any]]:
        """Get enabled tool definitions for this module"""
        if not self.config:
            return self.get_tool_definitions()
        
        enabled_tools = []
        for tool_name, tool in self.tools.items():
            if self.config.is_tool_enabled(tool_name):
                enabled_tools.append(tool.get_tool_definition())
        
        return enabled_tools
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Call a specific tool in this module"""
        if tool_name in self.tools:
            return await self.tools[tool_name].execute(arguments)
        else:
            return f"Unknown tool: {tool_name}"


def format_success_response(message: str, data: Optional[Dict] = None) -> str:
    """Format a success response"""
    response = f"✅ {message}"
    if data:
        response += f"\n{json.dumps(data, indent=2)}"
    return response


def format_error_response(message: str, error: Optional[str] = None) -> str:
    """Format an error response"""
    response = f"❌ {message}"
    if error:
        response += f"\nError: {error}"
    return response
