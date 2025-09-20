"""
Schema Management MCP Tools for Guepard Platform
"""

from typing import Dict, Any
from ..utils.base import MCPTool, MCPModule, GuepardAPIClient, format_success_response, format_error_response


class ExtractSchemaTool(MCPTool):
    """Tool for extracting database schema from a branch"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "extract_schema",
            "description": "Extract database schema from a branch",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "deployment_id": {
                        "type": "string",
                        "description": "Deployment ID"
                    },
                    "branch_id": {
                        "type": "string",
                        "description": "Branch ID"
                    }
                },
                "required": ["deployment_id", "branch_id"]
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        deployment_id = arguments.get("deployment_id")
        branch_id = arguments.get("branch_id")
        
        result = await self.client._make_api_call(
            "GET", 
            f"/deploy/{deployment_id}/{branch_id}/extract-schema"
        )
        
        if result.get("error"):
            return format_error_response(
                "Failed to extract schema", 
                result.get("message", "Unknown error")
            )
        
        return format_success_response(
            f"Schema extracted from branch {branch_id}",
            result
        )


class UpdateSchemaTool(MCPTool):
    """Tool for updating database schema"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "update_schema",
            "description": "Update database schema",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "deployment_id": {
                        "type": "string",
                        "description": "Deployment ID"
                    },
                    "branch_id": {
                        "type": "string",
                        "description": "Branch ID"
                    },
                    "schema": {
                        "type": "object",
                        "description": "Schema definition to apply"
                    }
                },
                "required": ["deployment_id", "branch_id", "schema"]
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        deployment_id = arguments.get("deployment_id")
        branch_id = arguments.get("branch_id")
        schema = arguments.get("schema")
        
        data = {"schema": schema}
        
        result = await self.client._make_api_call(
            "PUT", 
            f"/deploy/{deployment_id}/{branch_id}/schema", 
            data=data
        )
        
        if result.get("error"):
            return format_error_response(
                "Failed to update schema", 
                result.get("message", "Unknown error")
            )
        
        return format_success_response(
            f"Schema updated for branch {branch_id}",
            result
        )


class GetSnapshotSchemaTool(MCPTool):
    """Tool for getting schema from a specific snapshot"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "get_snapshot_schema",
            "description": "Get schema from a specific snapshot",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "deployment_id": {
                        "type": "string",
                        "description": "Deployment ID"
                    },
                    "snapshot_id": {
                        "type": "string",
                        "description": "Snapshot ID"
                    }
                },
                "required": ["deployment_id", "snapshot_id"]
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        deployment_id = arguments.get("deployment_id")
        snapshot_id = arguments.get("snapshot_id")
        
        result = await self.client._make_api_call(
            "GET", 
            f"/deploy/{deployment_id}/snapshot/{snapshot_id}/schema"
        )
        
        if result.get("error"):
            return format_error_response(
                "Failed to get snapshot schema", 
                result.get("message", "Unknown error")
            )
        
        return format_success_response(
            f"Schema retrieved from snapshot {snapshot_id}",
            result
        )


class StoreGraphSchemaTool(MCPTool):
    """Tool for storing the graph schema of a deployment"""
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "store_graph_schema",
            "description": "Store the graph schema representing relationships and connections within a deployment",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "deployment_id": {
                        "type": "string",
                        "description": "Deployment ID"
                    },
                    "graph_schema": {
                        "type": "object",
                        "description": "Graph schema definition containing nodes, edges, and relationships",
                        "properties": {
                            "nodes": {
                                "type": "array",
                                "description": "List of nodes in the graph",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "id": {
                                            "type": "string",
                                            "description": "Unique node identifier"
                                        },
                                        "type": {
                                            "type": "string",
                                            "description": "Node type (e.g., table, view, function, index, constraint)"
                                        },
                                        "name": {
                                            "type": "string",
                                            "description": "Node name"
                                        },
                                        "properties": {
                                            "type": "object",
                                            "description": "Additional node properties"
                                        },
                                        "metadata": {
                                            "type": "object",
                                            "description": "Node metadata (schema, database, etc.)"
                                        }
                                    },
                                    "required": ["id", "type", "name"]
                                }
                            },
                            "edges": {
                                "type": "array",
                                "description": "List of relationships between nodes",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "id": {
                                            "type": "string",
                                            "description": "Unique edge identifier"
                                        },
                                        "source": {
                                            "type": "string",
                                            "description": "Source node ID"
                                        },
                                        "target": {
                                            "type": "string",
                                            "description": "Target node ID"
                                        },
                                        "type": {
                                            "type": "string",
                                            "description": "Relationship type (e.g., foreign_key, references, depends_on, contains)"
                                        },
                                        "properties": {
                                            "type": "object",
                                            "description": "Additional edge properties"
                                        },
                                        "metadata": {
                                            "type": "object",
                                            "description": "Edge metadata"
                                        }
                                    },
                                    "required": ["id", "source", "target", "type"]
                                }
                            },
                            "metadata": {
                                "type": "object",
                                "description": "Graph-level metadata",
                                "properties": {
                                    "version": {
                                        "type": "string",
                                        "description": "Schema version"
                                    },
                                    "created_at": {
                                        "type": "string",
                                        "description": "Creation timestamp"
                                    },
                                    "description": {
                                        "type": "string",
                                        "description": "Graph description"
                                    },
                                    "database_provider": {
                                        "type": "string",
                                        "description": "Database provider (PostgreSQL, MySQL, etc.)"
                                    },
                                    "database_version": {
                                        "type": "string",
                                        "description": "Database version"
                                    }
                                }
                            }
                        },
                        "required": ["nodes", "edges"]
                    },
                    "branch_id": {
                        "type": "string",
                        "description": "Branch ID (optional, defaults to main branch)"
                    },
                    "overwrite": {
                        "type": "boolean",
                        "description": "Whether to overwrite existing graph schema",
                        "default": False
                    }
                },
                "required": ["deployment_id", "graph_schema"]
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        deployment_id = arguments.get("deployment_id")
        graph_schema = arguments.get("graph_schema")
        branch_id = arguments.get("branch_id")
        overwrite = arguments.get("overwrite", False)
        
        # Validate graph schema structure
        if not isinstance(graph_schema, dict):
            return format_error_response(
                "Failed to store graph schema",
                "Graph schema must be a valid object"
            )
        
        if "nodes" not in graph_schema or "edges" not in graph_schema:
            return format_error_response(
                "Failed to store graph schema",
                "Graph schema must contain 'nodes' and 'edges' arrays"
            )
        
        if not isinstance(graph_schema["nodes"], list) or not isinstance(graph_schema["edges"], list):
            return format_error_response(
                "Failed to store graph schema",
                "Nodes and edges must be arrays"
            )
        
        # Prepare the data payload
        data = {
            "graph_schema": graph_schema,
            "overwrite": overwrite
        }
        
        # Add branch_id if provided
        if branch_id:
            data["branch_id"] = branch_id
        
        # Determine the API endpoint
        if branch_id:
            endpoint = f"/deploy/{deployment_id}/{branch_id}/graph-schema"
        else:
            endpoint = f"/deploy/{deployment_id}/graph-schema"
        
        result = await self.client._make_api_call(
            "POST", 
            endpoint, 
            data=data
        )
        
        if result.get("error"):
            return format_error_response(
                "Failed to store graph schema", 
                result.get("message", "Unknown error")
            )
        
        # Extract useful information from the result
        stored_at = result.get("stored_at", "Unknown")
        schema_id = result.get("schema_id", "Unknown")
        node_count = len(graph_schema.get("nodes", []))
        edge_count = len(graph_schema.get("edges", []))
        
        response_message = f"Graph schema stored successfully for deployment {deployment_id}"
        if branch_id:
            response_message += f" on branch {branch_id}"
        response_message += f"\n📊 Schema contains {node_count} nodes and {edge_count} relationships"
        response_message += f"\n🆔 Schema ID: {schema_id}"
        response_message += f"\n⏰ Stored at: {stored_at}"
        
        return format_success_response(
            response_message,
            {
                "schema_id": schema_id,
                "deployment_id": deployment_id,
                "branch_id": branch_id,
                "node_count": node_count,
                "edge_count": edge_count,
                "stored_at": stored_at,
                "overwrite": overwrite,
                "full_response": result
            }
        )


class SchemaModule(MCPModule):
    """Schema module containing all schema management-related tools"""
    
    def _initialize_tools(self):
        self.tools = {
            "extract_schema": ExtractSchemaTool(self.client),
            "update_schema": UpdateSchemaTool(self.client),
            "get_snapshot_schema": GetSnapshotSchemaTool(self.client),
            "store_graph_schema": StoreGraphSchemaTool(self.client)
        }
