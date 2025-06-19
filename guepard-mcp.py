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

from mcp.types import ServerNotification, LoggingMessageNotification
from mcp.shared.context import RequestContext
import mcp.server.lowlevel.server as lowlevel_server

from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.requests import Request
from starlette.responses import Response
import uvicorn
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()


class GuepardDeploymentServer:
    def __init__(self):
        self.server = Server("guepard-deployment-server")
        self.session = None
        self.access_token = os.getenv("access_token")
        print(f"Access token: {self.access_token}")

        self.supabase_url = "https://zvcpnahtojfbbetnlshj.supabase.co/auth/v1/token?grant_type=password"
        self.api_base_url = "https://api.dev.guepard.run"
        self.api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp2Y3BuYWh0b2pmYmJldG5sc2hqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDU2Mjg5MjgsImV4cCI6MjA2MTIwNDkyOH0.d-yl_231Wht[...]"

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
                            "datacenter": {
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
                            "datacenter",
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
                    name="get_branches",
                    description="Get branches for a specific deployment",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "deployment_id": {"type": "string"}
                        },
                        "required": ["deployment_id"]
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
                ),
                types.Tool(
                    name="checkout_bookmark",
                    description="Checkout to a specific bookmark",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "deployment_id": {"type": "string"},
                            "branch_id": {"type": "string"},
                            "snapshot_id": {"type": "string"},
                            "discard_changes": true,
                            "checkout": true,
                            "ephemeral": true
                        },
                        "required": ["deployment_id", "branch_id", "snapshot_comment"]
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
                    deployment_id = result.get("id")
                    name = result.get("name")
                    fqdn = result.get("fqdn")
                    port = result.get("port")
                    username = result.get("database_username")
                    password = result.get("database_password")
                    async def wait_until_created_and_notify(deployment_id):
                        max_retries = 30  
                        for _ in range(max_retries):
                            await asyncio.sleep(5)
                            deployment = await self._get_deployments(deployment_id=deployment_id)
                            if deployment and isinstance(deployment, dict):
                                if deployment.get("status") == "CREATED":  
                                    await self._send_deployment_created_notification(deployment_id,name, fqdn, port, username, password)
                                    logger.info(f"Deployment {deployment_id} is created and notification sent.")
                                    break
                        else:
                            print(f"[Timeout] Deployment {deployment_id} did not reach 'created' status.")

                    asyncio.create_task(wait_until_created_and_notify(deployment_id))

                    return [types.TextContent(type="text", text=json.dumps(result))]

                elif name == "create_branch":
                    result = await self._create_branch(**arguments)
                elif name == "create_snapshot":
                    result = await self._create_snapshot(**arguments)
                elif name == "get_branches":
                    result = await self._get_branches(**arguments)
                elif name == "start_compute":
                    result = await self._start_compute(**arguments)
                    asyncio.create_task(self._send_compute_started_notification("Compute started"))
                    return [types.TextContent(type="text", text=json.dumps({}))]
                elif name == "stop_compute":
                    result = await self._stop_compute(**arguments)
                    asyncio.create_task(self._send_compute_started_notification("Compute started"))
                    return [types.TextContent(type="text", text=json.dumps({}))]
                elif name == "checkout_branch":
                    result = await self._checkout_branch(**arguments)
                elif name == "checkout_bookmark":
                    result = await self._checkout_bookmark(**arguments)
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
    async def _checkout_bookmark(self, **kwargs) -> dict:
        deployment_id = kwargs["deployment_id"]
        branch_id = kwargs["branch_id"]
        snapshot_id = kwargs["snapshot_id"]
        discard_changes = kwargs.get("discard_changes", "true")
        checkout = kwargs.get("checkout", True)
        ephemeral = kwargs.get("ephemeral", True)

        url = f"{self.api_base_url}/deploy/{deployment_id}/{branch_id}/{snapshot_id}/branch"
        payload = {
            "discard_changes": discard_changes,
            "checkout": checkout,
            "ephemeral": ephemeral
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
        try:
            logger.info(f"Fetching deployment from URL: {url}")
            async with self.session.get(url, headers=self._get_auth_headers(), params=params) as response:
                if response.status == 404:
                    logger.warning(f"Deployment not found: {deployment_id}")
                    return []
                response.raise_for_status()
                data = await response.json()
                logger.info(f"API Response: {json.dumps(data, indent=2)}")
                return data
        except aiohttp.ClientError as e:
            logger.error(f"Network error while fetching deployment: {str(e)}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in _get_deployments: {str(e)}")
            return []

    async def other(self, deployment_id: str) -> dict:
        url = f"{self.api_base_url}/deploy/{deployment_id}/start"
        async with self.session.get(url, headers=self._get_auth_headers()) as response:
            text = await response.text()
            if response.status >= 400:
                try:
                    error_msg = json.loads(text).get('message', text)
                except json.JSONDecodeError:
                    error_msg = text
                raise Exception(f"API Error {response.status}: {error_msg}")
            data = json.loads(text)
            
            try:
                session = lowlevel_server.request_ctx.get().session
                notification = ServerNotification(
                    method="computeStarted",
                    params={
                        "deployment_id": deployment_id,
                        "status": data.get("status", "started"),
                    }
                )
                await session.send_notification(notification)
                logger.info(f"Sent computeStarted notification for deployment_id={deployment_id}")
            except Exception as e:
                logger.warning(f"Failed to send computeStarted notification: {e}")

            return data

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
            "datacenter": "us-west-aws",
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
    async def _send_compute_started_notification(self, deployment_id: str):
        try:
            import mcp.server.lowlevel.server as lowlevel_server
            session = lowlevel_server.request_ctx.get().session
            notification = LoggingMessageNotification(
            method="notifications/message",
            params={
                "level": "info",
                "data": f"Compute started for deployment_id={deployment_id}"
            }
)

            await session.send_notification(notification)
            logger.info(f"Sent computeStarted notification for deployment_id={deployment_id}")
        except Exception as e:
            logger.warning(f"Failed to send computeStarted notification: {e}")
    async def _send_deployment_created_notification(self, deployment_id, name, fqdn, port, username, password):
        try:
            import mcp.server.lowlevel.server as lowlevel_server
            session = lowlevel_server.request_ctx.get().session
            
            
            message = f"""Deployment is ready!
Name: {name}
Host: {fqdn}
Port: {port}
Username: {username}
Password: {password}
Connection string: postgresql://{username}:{password}@{fqdn}:{port}"""

            notification = LoggingMessageNotification(
                method="notifications/message",
                params={
                    "level": "info",
                    "data": message
                }
            )

            await session.send_notification(notification)
            logger.info(f"Sent deployment created notification for deployment_id={deployment_id}")
        except Exception as e:
            logger.warning(f"Failed to send deployment created notification: {e}")
    

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
            return {}
    async def _get_branches(self, **kwargs) -> dict:
        deployment_id = kwargs["deployment_id"]
        url = f"{self.api_base_url}/deploy/{deployment_id}/branch"
        async with self.session.get(url, headers=self._get_auth_headers()) as response:
            text = await response.text()
            if response.status >= 400:
                try:
                    error_msg = json.loads(text).get('message', text)
                except json.JSONDecodeError:
                    error_msg = text
                raise Exception(f"API Error {response.status}: {error_msg}")
            return json.loads(text)
    
    async def _check_deployment_status(self, deployment_id: str) -> str:
        """
        Check the status of a deployment.
        Returns the current status or None if deployment not found.
        """
        try:
            deployments = await self._get_deployments(deployment_id=deployment_id)
            if deployments and isinstance(deployments, list) and len(deployments) > 0:
                deployment = deployments[0]
                status = deployment.get("status")
                logger.info(f"Deployment {deployment_id} status: {status}")
                return status, deployment
            else:
                logger.warning(f"No deployment found with ID {deployment_id}")
                return None, None
        except Exception as e:
            logger.error(f"Error checking deployment status: {str(e)}")
            return None, None

#global
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
    
    sse_transport = SseServerTransport("/messages/")
    
    async def handle_sse(request: Request):
        """Handle SSE connections"""
        try:
            if mcp_app is None:
                await setup_server()
            
            async with sse_transport.connect_sse(
                request.scope, request.receive, request._send
            ) as streams:
                await mcp_app.server.run(
                    streams[0], 
                    streams[1], 
                    mcp_app.server.create_initialization_options()
                )
        except Exception as e:
            logger.error(f"SSE handler error: {e}")
            logger.error(traceback.format_exc())
        finally:
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

    routes = [
        Route("/sse", endpoint=handle_sse, methods=["GET"]),
        Route("/health", endpoint=handle_health, methods=["GET"]),
        Route("/info", endpoint=handle_info, methods=["GET"]),
        Mount("/messages/", app=sse_transport.handle_post_message),
    ]

    app = Starlette(routes=routes)
    
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
        app = create_sse_app(args.host, args.port)
        
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