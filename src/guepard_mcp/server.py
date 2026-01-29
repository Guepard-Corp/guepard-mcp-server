"""
Main Guepard MCP Server - Complete API Implementation
Integrates all modules and provides a comprehensive MCP server for the Guepard platform.
"""

import os
import json
import sys
import asyncio
import logging
from typing import Dict, List, Optional, Set
from datetime import datetime
import traceback
from dotenv import load_dotenv

# Import all modules
from .utils.base import GuepardAPIClient
from .utils.config import ToolConfig, get_predefined_config, list_predefined_configs
from .auth.tools import AuthModule
from .deployments.tools import DeploymentsModule
from .branches.tools import BranchesModule
from .snapshots.tools import SnapshotsModule
from .nodes.tools import NodesModule
from .performance.tools import PerformanceModule
from .compute.tools import ComputeModule
from .users.tools import UsersModule
from .tokens.tools import TokensModule
from .f2_deployments.tools import F2DeploymentsModule
from .image_providers.tools import ImageProvidersModule
from .usage.tools import UsageModule
from .logs.tools import LogsModule
from .checkouts.tools import CheckoutsModule
from .shadows.tools import ShadowsModule
from .schema.tools import SchemaModule
from .subscriptions.tools import SubscriptionsModule

# Load environment variables from project root
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
env_path = os.path.join(project_root, '.env')
load_dotenv(env_path)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GuepardMCPServer:
    """Main Guepard MCP Server with complete API implementation"""
    
    def __init__(self):
        self.client = GuepardAPIClient()
        self.subscribed_deployments: Set[str] = set()
        
        # Initialize configuration
        self.config = ToolConfig()
        
        # Check for predefined configuration
        predefined_config_name = os.getenv("GUEPARD_CONFIG", "")
        if predefined_config_name:
            predefined_config = get_predefined_config(predefined_config_name)
            if predefined_config:
                logger.info(f"Using predefined configuration: {predefined_config_name}")
                logger.info(f"Description: {predefined_config['description']}")
                # Apply predefined configuration
                if "enabled_modules" in predefined_config:
                    os.environ["GUEPARD_ENABLED_MODULES"] = ",".join(predefined_config["enabled_modules"])
                if "enabled_tools" in predefined_config:
                    os.environ["GUEPARD_ENABLED_TOOLS"] = ",".join(predefined_config["enabled_tools"])
                if "disabled_tools" in predefined_config:
                    os.environ["GUEPARD_DISABLED_TOOLS"] = ",".join(predefined_config["disabled_tools"])
                # Reload configuration
                self.config = ToolConfig()
            else:
                logger.warning(f"Unknown predefined configuration: {predefined_config_name}")
        
        # Initialize all modules with configuration
        self.modules = {}
        module_classes = {
            "auth": AuthModule,
            "deployments": DeploymentsModule,
            "branches": BranchesModule,
            "snapshots": SnapshotsModule,
            "nodes": NodesModule,
            "performance": PerformanceModule,
            "compute": ComputeModule,
            "users": UsersModule,
            "tokens": TokensModule,
            "f2_deployments": F2DeploymentsModule,
            "image_providers": ImageProvidersModule,
            "usage": UsageModule,
            "logs": LogsModule,
            "checkouts": CheckoutsModule,
            "shadows": ShadowsModule,
            "schema": SchemaModule,
            "subscriptions": SubscriptionsModule
        }
        
        for module_name, module_class in module_classes.items():
            if self.config.is_module_enabled(module_name):
                # Special handling for modules that need server reference
                if module_name in ["subscriptions", "compute", "deployments"]:
                    self.modules[module_name] = module_class(self.client, self.config, self)
                else:
                    self.modules[module_name] = module_class(self.client, self.config)
                logger.info(f"Module '{module_name}' loaded with {len(self.modules[module_name].tools)} tools")
            else:
                logger.info(f"Module '{module_name}' disabled by configuration")
        
        # Collect enabled tools from all modules
        self.tools = {}
        for module_name, module in self.modules.items():
            for tool_name, tool in module.tools.items():
                if self.config.is_tool_enabled(tool_name):
                    self.tools[tool_name] = tool
        
        # Add configuration management tools
        self._add_configuration_tools()
        
        # Log configuration summary
        config_summary = self.config.get_configuration_summary()
        logger.info(f"Guepard MCP Server initialized with {len(self.tools)} enabled tools")
        logger.info(f"Configuration mode: {config_summary['configuration_mode']}")
        if config_summary['enabled_modules']:
            logger.info(f"Enabled modules: {', '.join(config_summary['enabled_modules'])}")
        if config_summary['disabled_tools']:
            logger.info(f"Disabled tools: {', '.join(config_summary['disabled_tools'])}")
        
        if not self.client.access_token:
            logger.error("ACCESS_TOKEN environment variable is required")
            sys.exit(1)
    
    def _add_configuration_tools(self):
        """Add configuration management tools"""
        from .utils.base import MCPTool
        
        class ListConfigurationsTool(MCPTool):
            def __init__(self, server):
                self.server = server
            
            def get_tool_definition(self) -> Dict:
                return {
                    "name": "list_configurations",
                    "description": "List available predefined configurations",
                    "inputSchema": {
                        "type": "object",
                        "properties": {}
                    }
                }
            
            async def execute(self, arguments: Dict) -> str:
                try:
                    configs = list_predefined_configs()
                    config_summary = self.server.config.get_configuration_summary()
                    
                    result = "📋 Available Predefined Configurations:\n\n"
                    for name, description in configs.items():
                        result += f"• **{name}**: {description}\n"
                    
                    result += f"\n⚙️ Current Configuration:\n"
                    result += f"• Mode: {config_summary['configuration_mode']}\n"
                    if config_summary['enabled_modules']:
                        result += f"• Enabled modules: {', '.join(config_summary['enabled_modules'])}\n"
                    if config_summary['enabled_tools']:
                        result += f"• Enabled tools: {', '.join(config_summary['enabled_tools'])}\n"
                    if config_summary['disabled_tools']:
                        result += f"• Disabled tools: {', '.join(config_summary['disabled_tools'])}\n"
                    
                    result += f"\n💡 To use a predefined configuration, set GUEPARD_CONFIG environment variable."
                    
                    return result
                except Exception as e:
                    return f"❌ Failed to list configurations: {str(e)}"
        
        class GetConfigurationTool(MCPTool):
            def __init__(self, server):
                self.server = server
            
            def get_tool_definition(self) -> Dict:
                return {
                    "name": "get_configuration",
                    "description": "Get current server configuration",
                    "inputSchema": {
                        "type": "object",
                        "properties": {}
                    }
                }
            
            async def execute(self, arguments: Dict) -> str:
                try:
                    config_summary = self.server.config.get_configuration_summary()
                    
                    result = "⚙️ Current Server Configuration:\n\n"
                    result += f"• **Mode**: {config_summary['configuration_mode']}\n"
                    result += f"• **Total Tools**: {len(self.server.tools)}\n"
                    result += f"• **Active Modules**: {len(self.server.modules)}\n"
                    
                    if config_summary['enabled_modules']:
                        result += f"• **Enabled Modules**: {', '.join(config_summary['enabled_modules'])}\n"
                    
                    if config_summary['enabled_tools']:
                        result += f"• **Enabled Tools**: {', '.join(config_summary['enabled_tools'])}\n"
                    
                    if config_summary['disabled_tools']:
                        result += f"• **Disabled Tools**: {', '.join(config_summary['disabled_tools'])}\n"
                    
                    result += f"\n📋 Active Modules:\n"
                    for module_name, module in self.server.modules.items():
                        enabled_tools = [name for name, tool in module.tools.items() if self.server.config.is_tool_enabled(name)]
                        result += f"• **{module_name}**: {len(enabled_tools)}/{len(module.tools)} tools enabled\n"
                    
                    return result
                except Exception as e:
                    return f"❌ Failed to get configuration: {str(e)}"
        
        # Add configuration tools only if they're enabled
        if self.config.is_tool_enabled("list_configurations"):
            self.tools["list_configurations"] = ListConfigurationsTool(self)
        if self.config.is_tool_enabled("get_configuration"):
            self.tools["get_configuration"] = GetConfigurationTool(self)
    
    async def connect(self):
        """Initialize HTTP session"""
        await self.client.connect()
    
    async def disconnect(self):
        """Close HTTP session"""
        await self.client.disconnect()
    
    async def call_tool(self, tool_name: str, arguments: Dict) -> str:
        """Call a specific tool with arguments"""
        if tool_name in self.tools:
            return await self.tools[tool_name].execute(arguments)
        else:
            return f"Unknown tool: {tool_name}"
    
    async def handle_request(self, request: Dict) -> Dict:
        """Handle incoming MCP requests"""
        method = request.get("method")
        request_id = request.get("id")
        
        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {"listChanged": False}
                    },
                    "serverInfo": {
                        "name": "guepard-complete",
                        "version": "1.5.0"
                    }
                }
            }
        
        elif method == "notifications/initialized":
            # Handle the initialized notification - no response needed
            return None
        
        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "tools": [tool.get_tool_definition() for tool in self.tools.values()]
                }
            }
        
        elif method == "tools/call":
            params = request.get("params", {})
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            result = await self.call_tool(tool_name, arguments)
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": result
                        }
                    ]
                }
            }
        
        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }
    
    async def run(self):
        """Run the MCP server"""
        logger.info("Starting Guepard MCP server with complete API integration...")
        
        # Initialize HTTP session
        await self.connect()
        
        try:
            while True:
                # Read from stdin
                line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
                if not line:
                    break
                
                try:
                    request = json.loads(line.strip())
                    response = await self.handle_request(request)
                    if response is not None:  # Only print response if it's not None (notifications return None)
                        print(json.dumps(response), flush=True)
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON: {line}")
                except Exception as e:
                    logger.error(f"Error handling request: {e}")
                    print(json.dumps({
                        "jsonrpc": "2.0",
                        "id": request.get("id") if 'request' in locals() else None,
                        "error": {
                            "code": -32603,
                            "message": str(e)
                        }
                    }), flush=True)
        
        except KeyboardInterrupt:
            logger.info("Shutdown requested.")
        except Exception as e:
            logger.error(f"Server error: {e}")
        finally:
            await self.disconnect()


async def main():
    """Main entry point"""
    server = GuepardMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
