"""
Test cases for StoreGraphSchemaTool
"""

import pytest
import json
from unittest.mock import AsyncMock, patch
from src.guepard_mcp.schema.tools import StoreGraphSchemaTool
from src.guepard_mcp.utils.base import GuepardAPIClient


class TestStoreGraphSchemaTool:
    """Test cases for StoreGraphSchemaTool"""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock API client"""
        client = AsyncMock(spec=GuepardAPIClient)
        return client
    
    @pytest.fixture
    def tool(self, mock_client):
        """Create a StoreGraphSchemaTool instance"""
        return StoreGraphSchemaTool(mock_client)
    
    @pytest.fixture
    def sample_graph_schema(self):
        """Sample graph schema for testing"""
        return {
            "nodes": [
                {
                    "id": "table_users",
                    "type": "table",
                    "name": "users",
                    "properties": {
                        "columns": ["id", "username", "email"],
                        "primary_key": "id"
                    },
                    "metadata": {
                        "schema": "public",
                        "database": "myapp"
                    }
                },
                {
                    "id": "table_orders",
                    "type": "table",
                    "name": "orders",
                    "properties": {
                        "columns": ["id", "user_id", "total", "created_at"],
                        "primary_key": "id"
                    },
                    "metadata": {
                        "schema": "public",
                        "database": "myapp"
                    }
                },
                {
                    "id": "index_users_email",
                    "type": "index",
                    "name": "idx_users_email",
                    "properties": {
                        "columns": ["email"],
                        "unique": True
                    },
                    "metadata": {
                        "schema": "public"
                    }
                }
            ],
            "edges": [
                {
                    "id": "fk_orders_user_id",
                    "source": "table_orders",
                    "target": "table_users",
                    "type": "foreign_key",
                    "properties": {
                        "column": "user_id",
                        "referenced_column": "id"
                    },
                    "metadata": {
                        "constraint_name": "fk_orders_user_id"
                    }
                },
                {
                    "id": "index_on_table",
                    "source": "index_users_email",
                    "target": "table_users",
                    "type": "contains",
                    "properties": {
                        "indexed_columns": ["email"]
                    }
                }
            ],
            "metadata": {
                "version": "1.0",
                "created_at": "2024-01-20T18:30:00Z",
                "description": "User and orders relationship graph",
                "database_provider": "PostgreSQL",
                "database_version": "17"
            }
        }
    
    def test_tool_definition(self, tool):
        """Test tool definition structure"""
        definition = tool.get_tool_definition()
        
        assert definition["name"] == "store_graph_schema"
        assert "Store the graph schema representing relationships" in definition["description"]
        
        # Check input schema structure
        input_schema = definition["inputSchema"]
        assert input_schema["type"] == "object"
        assert "deployment_id" in input_schema["properties"]
        assert "graph_schema" in input_schema["properties"]
        assert "branch_id" in input_schema["properties"]
        assert "overwrite" in input_schema["properties"]
        
        # Check required fields
        assert "deployment_id" in input_schema["required"]
        assert "graph_schema" in input_schema["required"]
        
        # Check graph_schema structure
        graph_schema_props = input_schema["properties"]["graph_schema"]["properties"]
        assert "nodes" in graph_schema_props
        assert "edges" in graph_schema_props
        assert "metadata" in graph_schema_props
    
    @pytest.mark.asyncio
    async def test_successful_store_without_branch(self, tool, mock_client, sample_graph_schema):
        """Test successful graph schema storage without branch"""
        # Mock API response
        mock_response = {
            "schema_id": "graph_schema_123",
            "stored_at": "2024-01-20T19:30:00Z",
            "deployment_id": "deploy_456",
            "node_count": 3,
            "edge_count": 2
        }
        mock_client._make_api_call.return_value = mock_response
        
        # Execute tool
        arguments = {
            "deployment_id": "deploy_456",
            "graph_schema": sample_graph_schema
        }
        
        result = await tool.execute(arguments)
        
        # Verify API call
        mock_client._make_api_call.assert_called_once_with(
            "POST",
            "/deploy/deploy_456/graph-schema",
            data={
                "graph_schema": sample_graph_schema,
                "overwrite": False
            }
        )
        
        # Verify response
        assert "Graph schema stored successfully" in result
        assert "deploy_456" in result
        assert "3 nodes and 2 relationships" in result
        assert "graph_schema_123" in result
    
    @pytest.mark.asyncio
    async def test_successful_store_with_branch(self, tool, mock_client, sample_graph_schema):
        """Test successful graph schema storage with branch"""
        # Mock API response
        mock_response = {
            "schema_id": "graph_schema_789",
            "stored_at": "2024-01-20T19:30:00Z",
            "deployment_id": "deploy_456",
            "branch_id": "branch_123",
            "node_count": 3,
            "edge_count": 2
        }
        mock_client._make_api_call.return_value = mock_response
        
        # Execute tool
        arguments = {
            "deployment_id": "deploy_456",
            "graph_schema": sample_graph_schema,
            "branch_id": "branch_123",
            "overwrite": True
        }
        
        result = await tool.execute(arguments)
        
        # Verify API call
        mock_client._make_api_call.assert_called_once_with(
            "POST",
            "/deploy/deploy_456/branch_123/graph-schema",
            data={
                "graph_schema": sample_graph_schema,
                "overwrite": True,
                "branch_id": "branch_123"
            }
        )
        
        # Verify response
        assert "Graph schema stored successfully" in result
        assert "deploy_456" in result
        assert "branch_123" in result
        assert "3 nodes and 2 relationships" in result
    
    @pytest.mark.asyncio
    async def test_invalid_graph_schema_not_dict(self, tool, mock_client):
        """Test error handling for invalid graph schema (not a dict)"""
        arguments = {
            "deployment_id": "deploy_456",
            "graph_schema": "invalid_schema"
        }
        
        result = await tool.execute(arguments)
        
        # Verify error response
        assert "Failed to store graph schema" in result
        assert "Graph schema must be a valid object" in result
        
        # Verify no API call was made
        mock_client._make_api_call.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_invalid_graph_schema_missing_nodes(self, tool, mock_client):
        """Test error handling for graph schema missing nodes"""
        arguments = {
            "deployment_id": "deploy_456",
            "graph_schema": {
                "edges": []
            }
        }
        
        result = await tool.execute(arguments)
        
        # Verify error response
        assert "Failed to store graph schema" in result
        assert "Graph schema must contain 'nodes' and 'edges' arrays" in result
        
        # Verify no API call was made
        mock_client._make_api_call.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_invalid_graph_schema_missing_edges(self, tool, mock_client):
        """Test error handling for graph schema missing edges"""
        arguments = {
            "deployment_id": "deploy_456",
            "graph_schema": {
                "nodes": []
            }
        }
        
        result = await tool.execute(arguments)
        
        # Verify error response
        assert "Failed to store graph schema" in result
        assert "Graph schema must contain 'nodes' and 'edges' arrays" in result
        
        # Verify no API call was made
        mock_client._make_api_call.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_invalid_graph_schema_nodes_not_array(self, tool, mock_client):
        """Test error handling for nodes not being an array"""
        arguments = {
            "deployment_id": "deploy_456",
            "graph_schema": {
                "nodes": "not_an_array",
                "edges": []
            }
        }
        
        result = await tool.execute(arguments)
        
        # Verify error response
        assert "Failed to store graph schema" in result
        assert "Nodes and edges must be arrays" in result
        
        # Verify no API call was made
        mock_client._make_api_call.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_api_error_response(self, tool, mock_client, sample_graph_schema):
        """Test handling of API error response"""
        # Mock API error response
        mock_response = {
            "error": True,
            "message": "Deployment not found"
        }
        mock_client._make_api_call.return_value = mock_response
        
        # Execute tool
        arguments = {
            "deployment_id": "deploy_456",
            "graph_schema": sample_graph_schema
        }
        
        result = await tool.execute(arguments)
        
        # Verify error response
        assert "Failed to store graph schema" in result
        assert "Deployment not found" in result
    
    @pytest.mark.asyncio
    async def test_minimal_graph_schema(self, tool, mock_client):
        """Test storing minimal valid graph schema"""
        # Mock API response
        mock_response = {
            "schema_id": "graph_schema_minimal",
            "stored_at": "2024-01-20T19:30:00Z",
            "deployment_id": "deploy_456",
            "node_count": 0,
            "edge_count": 0
        }
        mock_client._make_api_call.return_value = mock_response
        
        # Minimal valid graph schema
        minimal_schema = {
            "nodes": [],
            "edges": []
        }
        
        # Execute tool
        arguments = {
            "deployment_id": "deploy_456",
            "graph_schema": minimal_schema
        }
        
        result = await tool.execute(arguments)
        
        # Verify API call
        mock_client._make_api_call.assert_called_once_with(
            "POST",
            "/deploy/deploy_456/graph-schema",
            data={
                "graph_schema": minimal_schema,
                "overwrite": False
            }
        )
        
        # Verify response
        assert "Graph schema stored successfully" in result
        assert "0 nodes and 0 relationships" in result
    
    @pytest.mark.asyncio
    async def test_complex_graph_schema(self, tool, mock_client):
        """Test storing complex graph schema with multiple node and edge types"""
        complex_schema = {
            "nodes": [
                {
                    "id": "table_customers",
                    "type": "table",
                    "name": "customers",
                    "properties": {"columns": ["id", "name", "email"]},
                    "metadata": {"schema": "public"}
                },
                {
                    "id": "table_products",
                    "type": "table",
                    "name": "products",
                    "properties": {"columns": ["id", "name", "price"]},
                    "metadata": {"schema": "public"}
                },
                {
                    "id": "view_customer_orders",
                    "type": "view",
                    "name": "customer_orders",
                    "properties": {"query": "SELECT * FROM customers c JOIN orders o ON c.id = o.customer_id"},
                    "metadata": {"schema": "public"}
                },
                {
                    "id": "function_calculate_total",
                    "type": "function",
                    "name": "calculate_total",
                    "properties": {"parameters": ["order_id"], "return_type": "decimal"},
                    "metadata": {"schema": "public"}
                }
            ],
            "edges": [
                {
                    "id": "fk_orders_customer",
                    "source": "table_orders",
                    "target": "table_customers",
                    "type": "foreign_key",
                    "properties": {"column": "customer_id", "referenced_column": "id"}
                },
                {
                    "id": "view_depends_customers",
                    "source": "view_customer_orders",
                    "target": "table_customers",
                    "type": "depends_on",
                    "properties": {"dependency_type": "read"}
                },
                {
                    "id": "function_uses_orders",
                    "source": "function_calculate_total",
                    "target": "table_orders",
                    "type": "references",
                    "properties": {"usage_type": "read"}
                }
            ],
            "metadata": {
                "version": "2.0",
                "description": "E-commerce database graph",
                "database_provider": "PostgreSQL",
                "database_version": "17"
            }
        }
        
        # Mock API response
        mock_response = {
            "schema_id": "graph_schema_complex",
            "stored_at": "2024-01-20T19:30:00Z",
            "deployment_id": "deploy_789",
            "node_count": 4,
            "edge_count": 3
        }
        mock_client._make_api_call.return_value = mock_response
        
        # Execute tool
        arguments = {
            "deployment_id": "deploy_789",
            "graph_schema": complex_schema,
            "overwrite": True
        }
        
        result = await tool.execute(arguments)
        
        # Verify API call
        mock_client._make_api_call.assert_called_once_with(
            "POST",
            "/deploy/deploy_789/graph-schema",
            data={
                "graph_schema": complex_schema,
                "overwrite": True
            }
        )
        
        # Verify response
        assert "Graph schema stored successfully" in result
        assert "4 nodes and 3 relationships" in result
        assert "graph_schema_complex" in result
