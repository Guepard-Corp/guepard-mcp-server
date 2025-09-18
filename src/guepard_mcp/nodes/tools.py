"""
Nodes MCP Tools for Guepard Platform
"""

from typing import Dict, Any
from ..utils.base import MCPTool, MCPModule, GuepardAPIClient, format_success_response, format_error_response


class ListNodesTool(MCPTool):
    """Tool for listing all available compute nodes"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "list_nodes",
            "description": "Get all available compute nodes",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        result = await self.client._make_api_call("GET", "/deploy/nodes")
        
        # Check if result is an error response (dict with error key)
        if isinstance(result, dict) and result.get("error"):
            return format_error_response(
                "Failed to get nodes", 
                result.get("message", "Unknown error")
            )
        
        # Handle successful response (list of nodes)
        if isinstance(result, list):
            count = len(result)
            return format_success_response(f"Found {count} nodes", result)
        else:
            return format_success_response("Nodes retrieved successfully", result)


class ListAccessibleNodesTool(MCPTool):
    """Tool for listing nodes accessible to the authenticated user"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "list_accessible_nodes",
            "description": "Get nodes accessible to the authenticated user",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        result = await self.client._make_api_call("GET", "/deploy/accessible-nodes")
        
        # Check if result is an error response (dict with error key)
        if isinstance(result, dict) and result.get("error"):
            return format_error_response(
                "Failed to get accessible nodes", 
                result.get("message", "Unknown error")
            )
        
        # Handle successful response (list of nodes)
        if isinstance(result, list):
            count = len(result)
            return format_success_response(f"Found {count} accessible nodes", result)
        else:
            return format_success_response("Accessible nodes retrieved successfully", result)


class CreateNodeTool(MCPTool):
    """Tool for creating a new compute node"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "create_node",
            "description": "Create a new compute node",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "label_name": {
                        "type": "string",
                        "description": "Node label name"
                    },
                    "node_type": {
                        "type": "string",
                        "description": "Node type",
                        "enum": ["compute", "storage"],
                        "default": "compute"
                    },
                    "node_pool": {
                        "type": "string",
                        "description": "Node pool",
                        "default": "default"
                    },
                    "datacenter": {
                        "type": "string",
                        "description": "Datacenter"
                    },
                    "region": {
                        "type": "string",
                        "description": "Region"
                    },
                    "hosting_provider": {
                        "type": "string",
                        "description": "Hosting provider",
                        "enum": ["aws", "gcp", "azure"],
                        "default": "aws"
                    },
                    "memory": {
                        "type": "integer",
                        "description": "Memory in MB"
                    },
                    "cpu": {
                        "type": "integer",
                        "description": "CPU cores"
                    },
                    "storage": {
                        "type": "integer",
                        "description": "Storage in GB"
                    },
                    "created_by": {
                        "type": "string",
                        "description": "User ID who created the node"
                    }
                },
                "required": ["label_name", "node_type", "datacenter", "region", "hosting_provider", "memory", "cpu", "storage"]
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        data = {
            "label_name": arguments.get("label_name"),
            "node_type": arguments.get("node_type", "compute"),
            "node_pool": arguments.get("node_pool", "default"),
            "datacenter": arguments.get("datacenter"),
            "region": arguments.get("region"),
            "hosting_provider": arguments.get("hosting_provider", "aws"),
            "memory": arguments.get("memory"),
            "cpu": arguments.get("cpu"),
            "storage": arguments.get("storage")
        }
        
        # Add optional created_by if provided
        if arguments.get("created_by"):
            data["created_by"] = arguments.get("created_by")
        
        result = await self.client._make_api_call("POST", "/deploy/node", data=data)
        
        if result.get("error"):
            return format_error_response(
                "Failed to create node", 
                result.get("message", "Unknown error")
            )
        
        node_id = result.get("id", "Unknown")
        node_name = result.get("label_name", "Unknown")
        
        return format_success_response(
            f"Node '{node_name}' created successfully",
            {
                "node_id": node_id,
                "node_name": node_name,
                "node_type": arguments.get("node_type", "compute"),
                "status": result.get("status", "Unknown"),
                "datacenter": arguments.get("datacenter"),
                "region": arguments.get("region"),
                "hosting_provider": arguments.get("hosting_provider", "aws"),
                "full_response": result
            }
        )


class GetNodeTool(MCPTool):
    """Tool for getting detailed information about a specific node"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "get_node",
            "description": "Get detailed information about a specific node",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "node_id": {
                        "type": "string",
                        "description": "Node ID"
                    }
                },
                "required": ["node_id"]
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        node_id = arguments.get("node_id")
        
        result = await self.client._make_api_call("GET", f"/deploy/node/{node_id}")
        
        if result.get("error"):
            return format_error_response(
                "Failed to get node", 
                result.get("message", "Unknown error")
            )
        
        return format_success_response(
            f"Node {node_id} retrieved successfully",
            result
        )


class NodesModule(MCPModule):
    """Nodes module containing all node-related tools"""
    
    def _initialize_tools(self):
        self.tools = {
            "list_nodes": ListNodesTool(self.client),
            "list_accessible_nodes": ListAccessibleNodesTool(self.client),
            "create_node": CreateNodeTool(self.client),
            "get_node": GetNodeTool(self.client)
        }
