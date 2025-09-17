"""
Nodes MCP Tools for Guepard Platform
"""

from typing import Dict, Any
from ..utils.base import MCPTool, MCPModule, GuepardAPIClient, format_success_response, format_error_response


class ListNodesTool(MCPTool):
    """Tool for listing all nodes"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "list_nodes",
            "description": "Get all nodes",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        result = await self.client._make_api_call("GET", "/deploy/nodes")
        
        if result.get("error"):
            return format_error_response(
                "Failed to get nodes", 
                result.get("message", "Unknown error")
            )
        
        if isinstance(result, list):
            count = len(result)
            return format_success_response(f"Found {count} nodes", result)
        else:
            return format_success_response("Nodes retrieved successfully", result)


class CreateNodeTool(MCPTool):
    """Tool for creating a new node"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "create_node",
            "description": "Create a new node",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "label_name": {
                        "type": "string",
                        "description": "Node label name"
                    },
                    "node_type": {
                        "type": "string",
                        "description": "Node type"
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
                        "description": "Hosting provider"
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
                        "description": "Storage size in GB"
                    },
                    "created_by": {
                        "type": "string",
                        "description": "User ID who created the node"
                    }
                },
                "required": ["label_name", "node_type", "memory", "cpu", "storage"]
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        data = {
            "label_name": arguments.get("label_name"),
            "node_type": arguments.get("node_type"),
            "node_pool": arguments.get("node_pool", "default"),
            "memory": arguments.get("memory"),
            "cpu": arguments.get("cpu"),
            "storage": arguments.get("storage")
        }
        
        # Add optional fields if provided
        if arguments.get("datacenter"):
            data["datacenter"] = arguments.get("datacenter")
        if arguments.get("region"):
            data["region"] = arguments.get("region")
        if arguments.get("hosting_provider"):
            data["hosting_provider"] = arguments.get("hosting_provider")
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
                "node_type": arguments.get("node_type"),
                "memory": arguments.get("memory"),
                "cpu": arguments.get("cpu"),
                "storage": arguments.get("storage"),
                "full_response": result
            }
        )


class GetNodeTool(MCPTool):
    """Tool for getting node details"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "get_node",
            "description": "Get node details",
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
            "create_node": CreateNodeTool(self.client),
            "get_node": GetNodeTool(self.client)
        }
