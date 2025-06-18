import os
import json
import sys
import argparse
import logging
import aiohttp
from typing import Dict, List, Optional, Union
import traceback
from mcp import server as mcp_server

from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.models import InitializationOptions
import mcp.types as types
import mcp.server.stdio
from mcp.server.sse import SseServerTransport

# Web server imports
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.requests import Request
from starlette.responses import Response
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()


class GuepardDeploymentServer:
    def __init__(self):
        self.server = Server("guepard-deployment-server")
        self.session = None
        self.access_token = os.getenv("access_token")
        print(f"Access token: {self.access_token}")

        # Load environment variables
        self.supabase_url = "https://zvcpnahtojfbbetnlshj.supabase.co/auth/v1/token?grant_type=password"
        self.api_base_url = "https://api.dev.guepard.run"
        self.api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp2Y3BuYWh0b2pmYmJldG5sc2hqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDU2Mjg5MjgsImV4cCI6MjA2MTIwNDkyOH0.d-yl_231WhtTsnfuxTDvEtW35wyXMtro5M7Xu3vuGQ4"

        # Validate credentials
        if not self.api_key:
            raise ValueError("Missing SUPABASE_API_KEY in environment.")

        self._setup_handlers()

    async def connect(self):
        self.session = aiohttp.ClientSession()
        logger.info("Session started.")

    async def disconnect(self):
        if self.session:
            await self.session.close()
            logger.info("Session disconnected.")

    def _get_auth_headers(self) -> Dict[str, str]:
        return {
            "Content-Type": "application/json",
            "apikey": self.api_key,
            "Authorization": f"Bearer {self.access_token}"
        }

    def _setup_handlers(self):

        @self.server.list_tools()
        async def list_tools() -> List[types.Tool]:
            return [
                types.Tool(
                    name="get_deployments",
                    description="Retrieve deployment info. Leave deployment_id empty to get all.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "deployment_id": {"type": "string", "description": "Deployment ID (optional)"},
                            "status": {"type": "string", "description": "Filter by status", "enum": ["active", "pending", "failed", "terminated"]},
                            "limit": {"type": "integer", "description": "Limit", "default": 100}
                        }
                    }
                ),
                types.Tool(
                    name="stop_compute",
                    description="Stop compute for a specific deployment",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "deployment_id": {"type": "string", "description": "Deployment ID"}
                        }
                    }
                ),
                types.Tool(
                    name="start_compute",
                    description="Start compute for a specific deployment",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "deployment_id": {"type": "string", "description": "Deployment ID"},
                        }
                    }
                ),
                types.Tool(
                    name="create_branch",
                    description="Create a branch from snapshot",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "deployment_id": {"type": "string"},
                            "clone_id": {"type": "string"},
                            "snapshot_id": {"type": "string"},
                            "branch_name": {"type": "string"},
                            "discard_changes": {"type": "string", "enum": ["true", "false"]},
                            "checkout": {"type": "boolean"},
                            "ephemeral": {"type": "boolean"}
                        },
                        "required": ["deployment_id", "clone_id", "snapshot_id", "branch_name"]
                    }
                ),
                types.Tool(
                    name="create_deployment",
                    description="Create a new database deployment",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "deployment_type": {
                                "type": "string",
                                "enum": ["REPOSITORY", "F2"],
                                "default": "REPOSITORY"
                            },
                            "database_provider": {
                                "type": "string",
                                "enum": ["PostgreSQL", "mysql", "mongodb"],
                                "default": "PostgreSQL"
                            },
                            "database_version": {
                                "type": "string",
                                "default": "16"
                            },
                            "data_center": {
                                "type": "string",
                                "default": "us-west-aws"
                            },
                            "region": {
                                "type": "string",
                                "default": "us"
                            },
                            "instance_type": {
                                "type": "string",
                                "enum": ["free", "small", "medium", "large", "xlarge"],
                                "default": "free"
                            },
                            "repository_name": {
                                "type": "string",
                                "default": "Guepard-API-Postgres"
                            },
                            "database_username": {
                                "type": "string",
                                "default": "postgres"
                            },
                            "performance_profile_id": {
                                "type": "string",
                                "default": "f8bdcb24-d9f1-4cc8-8e65-0f7edff74ada"
                            }
                        },
                        "required": [
                            "deployment_type",
                            "database_provider",
                            "database_version",
                            "data_center",
                            "region",
                            "instance_type",
                            "repository_name",
                            "database_username",
                            "performance_profile_id"
                        ]
                    }
                ),
                types.Tool(
                    name="create_bookmark",
                    description="Create a bookmark for a specific deployment",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "deployment_id": {"type": "string"},
                            "branch_id": {"type": "string"},
                            "snapshot_comment": {"type": "string"}
                        },
                        "required": ["deployment_id", "branch_id", "snapshot_comment"]
                    }
                ),
                types.Tool(
                    name="checkout_branch",
                    description="Checkout to a specific branch",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "deployment_id": {"type": "string"},
                            "clone_id": {"type": "string"},
                        },
                        "required": ["deployment_id", "clone_id"]
                    }
                )
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict):
            if not self.access_token:
                return [types.TextContent(type="text", text=json.dumps({"error": "Not authenticated"}))]

            try:
                if name == "get_deployments":
                    result = await self._get_deployments(**arguments)
                elif name == "create_deployment":
                    result = await self._create_deployment(**arguments)
                elif name == "create_branch":
                    result = await self._create_branch(**arguments)
                elif name == "create_snapshot":
                    result = await self._create_snapshot(**arguments)
                elif name == "start_compute":
                    result = await self._start_compute(**arguments)
                elif name == "stop_compute":
                    result = await self._stop_compute(**arguments)
                elif name == "checkout_branch":
                    result = await self._checkout_branch(**arguments)
                else:
                    return [types.TextContent(type="text", text=f"Unknown tool: {name}")]

                json_str = json.dumps(result, indent=2)
                chunk_size = 512
                content_chunks = []
                for i in range(0, len(json_str), chunk_size):
                    content_chunks.append(types.TextContent(type="text", text=json_str[i:i+chunk_size]))
                
                return content_chunks

            except Exception as e:
                logger.error(f"Tool '{name}' failed: {str(e)}")
                error_json = json.dumps({"error": str(e)})
                return [types.TextContent(type="text", text=error_json)]

    async def _checkout_branch(self, **kwargs) -> dict:
        deployment_id = kwargs["deployment_id"]
        clone_id = kwargs["clone_id"]
        url = f"{self.api_base_url}/deploy/{deployment_id}/{clone_id}/checkout"
        async with self.session.post(url, headers=self._get_auth_headers()) as response:
            text = await response.text()
            if response.status >= 400:
                try:
                    error_msg = json.loads(text).get('message', text)
                except json.JSONDecodeError:
                    error_msg = text
                raise Exception(f"API Error {response.status}: {error_msg}")
            return json.loads(text)

    async def _get_deployments(self, deployment_id=None, status=None, limit=100) -> Union[Dict, List[Dict]]:
        endpoint = f"/deploy/{deployment_id}" if deployment_id else "/deploy"
        params = {"status": status, "limit": max(1, min(limit, 1000))} if status else {"limit": max(1, min(limit, 1000))}
        url = f"{self.api_base_url}{endpoint}"
        async with self.session.get(url, headers=self._get_auth_headers(), params=params) as response:
            response.raise_for_status()
            return await response.json()

    async def _start_compute(self, deployment_id: str) -> dict:
        url = f"{self.api_base_url}/deploy/{deployment_id}/start"
        async with self.session.get(url, headers=self._get_auth_headers()) as response:
            text = await response.text()
            if response.status >= 400:
                try:
                    error_msg = json.loads(text).get('message', text)
                except json.JSONDecodeError:
                    error_msg = text
                raise Exception(f"API Error {response.status}: {error_msg}")
            return json.loads(text)

    async def _stop_compute(self, deployment_id: str) -> dict:
        url = f"{self.api_base_url}/deploy/{deployment_id}/stop"
        async with self.session.get(url, headers=self._get_auth_headers()) as response:
            text = await response.text()
            if response.status >= 400:
                try:
                    error_msg = json.loads(text).get('message', text)
                except json.JSONDecodeError:
                    error_msg = text
                raise Exception(f"API Error {response.status}: {error_msg}")
            return json.loads(text)

    async def _create_branch(self, **kwargs) -> dict:
        url = f"{self.api_base_url}/deploy/{kwargs['deployment_id']}/{kwargs['clone_id']}/{kwargs['snapshot_id']}/branch"
        payload = {
            "branch_name": kwargs["branch_name"],
            "discard_changes": kwargs.get("discard_changes", "true"),
            "checkout": kwargs.get("checkout", False),
            "ephemeral": kwargs.get("ephemeral", False)
        }
        async with self.session.post(url, headers=self._get_auth_headers(), json=payload) as response:
            text = await response.text()
            if response.status >= 400:
                try:
                    error_msg = json.loads(text).get('message', text)
                except json.JSONDecodeError:
                    error_msg = text
                raise Exception(f"API Error {response.status}: {error_msg}")
            return json.loads(text)

    async def _create_deployment(self, **kwargs) -> dict:
        url = f"{self.api_base_url}/deploy"
        defaults = {
            "database_provider": "PostgreSQL",
            "database_version": "16",
            "region": "us",
            "data_center": "us-west-aws",
            "instance_type": "free",
            "repository_name": "Guepard-API-Postgres",
            "database_username": "postgres",
            "deployment_type": "REPOSITORY",
            "performance_profile_id": "f8bdcb24-d9f1-4cc8-8e65-0f7edff74ada"
        }
        payload = {k: kwargs.get(k, v) for k, v in defaults.items()}
        async with self.session.post(url, headers=self._get_auth_headers(), json=payload) as response:
            text = await response.text()
            if response.status >= 400:
                try:
                    error_msg = json.loads(text).get('message', text)
                except json.JSONDecodeError:
                    error_msg = text
                raise Exception(f"API Error {response.status}: {error_msg}")
            return json.loads(text)

    async def _create_bookmark(self, **kwargs) -> dict:
        deployment_id = kwargs["deployment_id"]
        branch_id = kwargs["branch_id"]
        payload = {
            "snapshot_comment": kwargs["snapshot_comment"]
        }

        url = f"{self.api_base_url}/deploy/{deployment_id}/{branch_id}/snap"

        async with self.session.put(url, headers=self._get_auth_headers(), json=payload) as response:
            text = await response.text()
            if response.status >= 400:
                try:
                    error_msg = json.loads(text).get("message", text)
                except json.JSONDecodeError:
                    error_msg = text
                raise Exception(f"API Error {response.status}: {error_msg}")
            return json.loads(text)


# Global server instance
mcp_app = None


async def setup_server():
    """Initialize the MCP server and connect session"""
    global mcp_app
    mcp_app = GuepardDeploymentServer()
    await mcp_app.connect()
    return mcp_app


async def cleanup_server():
    """Cleanup the MCP server session"""
    global mcp_app
    if mcp_app:
        await mcp_app.disconnect()


def create_sse_app(host: str = "127.0.0.1", port: int = 8000) -> Starlette:
    """Create a Starlette app with SSE transport"""
    
    # Create SSE transport with message endpoint
    sse_transport = SseServerTransport("/messages/")
    
    async def handle_sse(request: Request):
        """Handle SSE connections"""
        try:
            # Initialize server if not already done
            if mcp_app is None:
                await setup_server()
            
            async with sse_transport.connect_sse(
                request.scope, request.receive, request._send
            ) as streams:
                # Run the MCP server with the SSE streams
                await mcp_app.server.run(
                    streams[0], 
                    streams[1], 
                    mcp_app.server.create_initialization_options()
                )
        except Exception as e:
            logger.error(f"SSE handler error: {e}")
            logger.error(traceback.format_exc())
        finally:
            # Return empty response to avoid NoneType error
            return Response()

    async def handle_health(request: Request):
        """Health check endpoint"""
        return Response("OK", status_code=200)

    async def handle_info(request: Request):
        """Server info endpoint"""
        info = {
            "name": "guepard-deployment-server",
            "version": "1.0.0",
            "description": "Guepard Deployment MCP Server with SSE support",
            "endpoints": {
                "sse": f"http://{host}:{port}/sse",
                "messages": f"http://{host}:{port}/messages/",
                "health": f"http://{host}:{port}/health",
                "info": f"http://{host}:{port}/info"
            }
        }
        return Response(
            json.dumps(info, indent=2), 
            media_type="application/json"
        )

    # Create Starlette routes
    routes = [
        Route("/sse", endpoint=handle_sse, methods=["GET"]),
        Route("/health", endpoint=handle_health, methods=["GET"]),
        Route("/info", endpoint=handle_info, methods=["GET"]),
        Mount("/messages/", app=sse_transport.handle_post_message),
    ]

    # Create Starlette app
    app = Starlette(routes=routes)
    
    # Add startup and shutdown event handlers
    @app.on_event("startup")
    async def startup_event():
        await setup_server()
        logger.info(f"MCP Server started with SSE transport on http://{host}:{port}")
        logger.info(f"SSE endpoint: http://{host}:{port}/sse")
        logger.info(f"Health check: http://{host}:{port}/health")
        logger.info(f"Server info: http://{host}:{port}/info")

    @app.on_event("shutdown")
    async def shutdown_event():
        await cleanup_server()
        logger.info("MCP Server shutdown")

    return app


async def run_stdio():
    """Run the server with stdio transport (original functionality)"""
    server = GuepardDeploymentServer()

    try:
        await server.connect()
        logger.info("Guepard MCP Server is running with stdio...")
        async with mcp_server.stdio.stdio_server() as (read_stream, write_stream):
            await server.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="guepard-deployment-server",
                    server_version="1.0.0",
                    capabilities={"tools": {}, "resources": {}, "prompts": {}}
                )
            )
    except KeyboardInterrupt:
        logger.info("Shutdown requested.")
    except Exception as e:
        logger.error(f"Server error: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)
    finally:
        await server.disconnect()


async def main():
    parser = argparse.ArgumentParser(description="Guepard Deployment MCP Server")
    parser.add_argument("--transport", choices=["stdio", "sse"], default="stdio",
                      help="Transport method to use (default: stdio)")
    parser.add_argument("--host", default="127.0.0.1",
                      help="Host to bind to when using SSE transport (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000,
                      help="Port to bind to when using SSE transport (default: 8000)")
    
    args = parser.parse_args()

    if args.transport == "stdio":
        await run_stdio()
    elif args.transport == "sse":
        # Create and run the SSE app
        app = create_sse_app(args.host, args.port)
        
        # Use uvicorn to run the Starlette app
        config = uvicorn.Config(
            app, 
            host=args.host, 
            port=args.port,
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())