import os
import json
import sys
import argparse
import logging
import aiohttp
from typing import Dict, List, Optional, Union, Set
import traceback
import asyncio
from datetime import datetime
from mcp import server as mcp_server
from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware

from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.models import InitializationOptions
import mcp.types as types
import mcp.server.stdio
from mcp.server.sse import SseServerTransport
from mcp.server.lowlevel.server import NotificationOptions

from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.requests import Request
from starlette.responses import Response
import uvicorn

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

access_token = os.getenv("ACCESS_TOKEN")

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        token = request.headers.get("Authorization")
        if not token or token != f"Bearer {ACCESS_TOKEN}":
            return JSONResponse({"error": "Unauthorized"}, status_code=401)
        return await call_next(request)
app = FastAPI()

app.add_middleware(AuthMiddleware)
class GuepardDeploymentServer:
    access_token = os.getenv("ACCESS_TOKEN")
    def __init__(self):
        self.server = Server("guepard-deployment-server")
        self.session = None
        self.server_session = None   
        self.access_token = access_token
        self.monitoring_enabled = True
        self.monitoring_task = None
        self.deployment_cache = {} 
        self.subscribed_deployments: Set[str] = set() 
        
        print(f"Access token: {self.access_token}")

        self.supabase_url = "https://zvcpnahtojfbbetnlshj.supabase.co/auth/v1/token?grant_type=password"
        self.api_base_url = "https://api.dev.guepard.run"
        self.api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp2Y3BuYWh0b2pmYmJldG5sc2hqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDU2Mjg5MjgsImV4cCI6MjA2MTIwNDkyOH0.d-yl_231WhtTsnfuxTDvEtW35wyXMtro5M7Xu3vuGQ4"

        if not self.api_key:
            raise ValueError("Missing SUPABASE_API_KEY in environment.")

        self._setup_handlers()

    def set_server_session(self, server_session):
        """Set the server session for sending notifications"""
        self.server_session = server_session
        
    async def start_monitoring(self, interval: int = 30):
        """Start background monitoring for deployment status changes"""
        if self.monitoring_task is None or self.monitoring_task.done():
            self.monitoring_task = asyncio.create_task(self._monitoring_loop(interval))
            logger.info(f"Started deployment monitoring with {interval}s interval")

    async def stop_monitoring(self):
        """Stop background monitoring"""
        if self.monitoring_task and not self.monitoring_task.done():
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
            logger.info("Stopped deployment monitoring")

    async def _monitoring_loop(self, interval: int):
        """Background task to monitor deployment status changes"""
        while self.monitoring_enabled:
            try:
                if self.subscribed_deployments:
                    await self._check_deployment_changes()
                await asyncio.sleep(interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(interval)

    async def _check_deployment_changes(self):
        """Check for deployment status changes and send notifications"""
        if not self.server_session:
            return
            
        for deployment_id in self.subscribed_deployments.copy():
            try:
                current_state = await self._get_deployments(deployment_id=deployment_id)
                if isinstance(current_state, dict):
                    old_state = self.deployment_cache.get(deployment_id)
                    
                    if old_state:
                        if old_state.get('status') != current_state.get('status'):
                            await self._notify_status_change(deployment_id, old_state.get('status'), current_state.get('status'))
                        
                        if old_state.get('compute_status') != current_state.get('compute_status'):
                            await self._notify_compute_change(deployment_id, current_state.get('compute_status'))
                    
                    self.deployment_cache[deployment_id] = current_state
                    
            except Exception as e:
                logger.error(f"Error checking deployment {deployment_id}: {e}")

    async def _notify_status_change(self, deployment_id: str, old_status: str, new_status: str):
        """Send notification when deployment status changes"""
        if not self.server_session:
            return
            
        try:
            message = f"Deployment {deployment_id} status changed from {old_status} to {new_status}"
            await self.server_session.send_log_message(
                level=types.LoggingLevel.INFO,
                data={
                    "event_type": "status_change",
                    "deployment_id": deployment_id,
                    "old_status": old_status,
                    "new_status": new_status,
                    "timestamp": datetime.now().isoformat(),
                    "message": message
                },
                logger="guepard-deployment-monitor"
            )
            logger.info(f"Sent status change notification: {message}")
        except Exception as e:
            logger.error(f"Failed to send status change notification: {e}")

    async def _notify_compute_change(self, deployment_id: str, compute_status: str):
        """Send notification when compute status changes"""
        if not self.server_session:
            return
            
        try:
            message = f"Deployment {deployment_id} compute status: {compute_status}"
            await self.server_session.send_log_message(
                level=types.LoggingLevel.INFO,
                data={
                    "event_type": "compute_change",
                    "deployment_id": deployment_id,
                    "compute_status": compute_status,
                    "timestamp": datetime.now().isoformat(),
                    "message": message
                },
                logger="guepard-compute-monitor"
            )
            logger.info(f"Sent compute change notification: {message}")
        except Exception as e:
            logger.error(f"Failed to send compute change notification: {e}")

    async def _notify_operation_result(self, operation: str, deployment_id: str, success: bool, details: dict = None):
        """Send notification for operation results"""
        if not self.server_session:
            return
            
        try:
            status = "success" if success else "failed"
            message = f"Operation '{operation}' {status} for deployment {deployment_id}"
            
            data = {
                "event_type": "operation_result",
                "operation": operation,
                "deployment_id": deployment_id,
                "success": success,
                "timestamp": datetime.now().isoformat(),
                "message": message
            }
            
            if details:
                data["details"] = details
                
            level = types.LoggingLevel.INFO if success else types.LoggingLevel.ERROR
            
            await self.server_session.send_log_message(
                level=level,
                data=data,
                logger="guepard-operations"
            )
            logger.info(f"Sent operation result notification: {message}")
        except Exception as e:
            logger.error(f"Failed to send operation result notification: {e}")

    async def _notify_progress(self, operation: str, deployment_id: str, progress: float, message: str = None):
        """Send progress notification for long-running operations"""
        if not self.server_session:
            return
            
        try:
            progress_token = f"{operation}_{deployment_id}"
            await self.server_session.send_progress_notification(
                progress_token=progress_token,
                progress=progress,
                total=100.0,
                message=message or f"{operation} in progress for {deployment_id}"
            )
            logger.debug(f"Sent progress notification: {operation} {progress}% for {deployment_id}")
        except Exception as e:
            logger.error(f"Failed to send progress notification: {e}")

    def subscribe_deployment(self, deployment_id: str):
        """Subscribe to notifications for a specific deployment"""
        self.subscribed_deployments.add(deployment_id)
        logger.info(f"Subscribed to notifications for deployment {deployment_id}")

    def unsubscribe_deployment(self, deployment_id: str):
        """Unsubscribe from notifications for a specific deployment"""
        self.subscribed_deployments.discard(deployment_id)
        if deployment_id in self.deployment_cache:
            del self.deployment_cache[deployment_id]
        logger.info(f"Unsubscribed from notifications for deployment {deployment_id}")

    async def connect(self):
        self.session = aiohttp.ClientSession()
        logger.info("Session started.")

    async def disconnect(self):
        if self.session:
            await self.session.close()
            logger.info("Session disconnected.")
        await self.stop_monitoring()
        self.server_session = None

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
                            "deployment_id": {"type": "string", "description": "Deployment ID"},
                            "notify": {"type": "boolean", "description": "Send notification when operation completes", "default": True}
                        },
                        "required": ["deployment_id"]
                    }
                ),
                types.Tool(
                    name="start_compute",
                    description="Start compute for a specific deployment",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "deployment_id": {"type": "string", "description": "Deployment ID"},
                            "notify": {"type": "boolean", "description": "Send notification when operation completes", "default": True}
                        },
                        "required": ["deployment_id"]
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
                            "ephemeral": {"type": "boolean"},
                            "notify": {"type": "boolean", "description": "Send notification when operation completes", "default": True}
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
                            },
                            "notify": {"type": "boolean", "description": "Send notification when operation completes", "default": True},
                            "monitor": {"type": "boolean", "description": "Monitor deployment for status changes", "default": False}
                        },
                        "required": [
                            "deployment_type",
                            "database_provider",
                            "database_version",
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
                            "snapshot_comment": {"type": "string"},
                            "notify": {"type": "boolean", "description": "Send notification when operation completes", "default": True}
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
                            "notify": {"type": "boolean", "description": "Send notification when operation completes", "default": True}
                        },
                        "required": ["deployment_id", "clone_id"]
                    }
                ),
                types.Tool(
                    name="subscribe_deployment",
                    description="Subscribe to notifications for a deployment",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "deployment_id": {"type": "string", "description": "Deployment ID to monitor"}
                        },
                        "required": ["deployment_id"]
                    }
                ),
                types.Tool(
                    name="unsubscribe_deployment", 
                    description="Unsubscribe from notifications for a deployment",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "deployment_id": {"type": "string", "description": "Deployment ID to stop monitoring"}
                        },
                        "required": ["deployment_id"]
                    }
                ),
                types.Tool(
                    name="list_subscriptions",
                    description="List all deployment subscriptions",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                types.Tool(
                    name="start_monitoring",
                    description="Start background monitoring with custom interval",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "interval": {"type": "integer", "description": "Monitoring interval in seconds", "default": 30, "minimum": 10}
                        }
                    }
                ),
                types.Tool(
                    name="stop_monitoring",
                    description="Stop background monitoring",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                )
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict):
            if not self.access_token:
                return [types.TextContent(type="text", text=json.dumps({"error": "Not authenticated"}))]

            try:
                notify = arguments.get("notify", True)
                
                if name == "get_deployments":
                    result = await self._get_deployments(**arguments)
                elif name == "create_deployment":
                    result = await self._create_deployment(**arguments)
                    if notify and "id" in result:
                        await self._notify_operation_result("create_deployment", result["id"], True, result)
                        if arguments.get("monitor", False):
                            self.subscribe_deployment(result["id"])
                elif name == "create_branch":
                    deployment_id = arguments["deployment_id"]
                    result = await self._create_branch(**arguments)
                    if notify:
                        await self._notify_operation_result("create_branch", deployment_id, True, result)
                elif name == "create_snapshot":
                    deployment_id = arguments["deployment_id"]
                    result = await self._create_snapshot(**arguments)
                    if notify:
                        await self._notify_operation_result("create_snapshot", deployment_id, True, result)
                elif name == "start_compute":
                    deployment_id = arguments["deployment_id"]
                    await self._notify_progress("start_compute", deployment_id, 0, "Starting compute...")
                    result = await self._start_compute(deployment_id)
                    if notify:
                        await self._notify_operation_result("start_compute", deployment_id, True, result)
                    await self._notify_progress("start_compute", deployment_id, 100, "Compute started successfully")
                elif name == "stop_compute":
                    deployment_id = arguments["deployment_id"]
                    await self._notify_progress("stop_compute", deployment_id, 0, "Stopping compute...")
                    result = await self._stop_compute(deployment_id)
                    if notify:
                        await self._notify_operation_result("stop_compute", deployment_id, True, result)
                    await self._notify_progress("stop_compute", deployment_id, 100, "Compute stopped successfully")
                elif name == "checkout_branch":
                    deployment_id = arguments["deployment_id"]
                    result = await self._checkout_branch(**arguments)
                    if notify:
                        await self._notify_operation_result("checkout_branch", deployment_id, True, result)
                elif name == "create_bookmark":
                    deployment_id = arguments["deployment_id"]
                    result = await self._create_bookmark(**arguments)
                    if notify:
                        await self._notify_operation_result("create_bookmark", deployment_id, True, result)
                elif name == "subscribe_deployment":
                    deployment_id = arguments["deployment_id"]
                    self.subscribe_deployment(deployment_id)
                    try:
                        initial_state = await self._get_deployments(deployment_id=deployment_id)
                        if isinstance(initial_state, dict):
                            self.deployment_cache[deployment_id] = initial_state
                    except Exception as e:
                        logger.warning(f"Could not get initial state for {deployment_id}: {e}")
                    result = {"message": f"Subscribed to notifications for deployment {deployment_id}", "deployment_id": deployment_id}
                elif name == "unsubscribe_deployment":
                    deployment_id = arguments["deployment_id"]
                    self.unsubscribe_deployment(deployment_id)
                    result = {"message": f"Unsubscribed from notifications for deployment {deployment_id}", "deployment_id": deployment_id}
                elif name == "list_subscriptions":
                    result = {
                        "subscribed_deployments": list(self.subscribed_deployments),
                        "monitoring_enabled": self.monitoring_enabled,
                        "monitoring_active": self.monitoring_task is not None and not self.monitoring_task.done() if self.monitoring_task else False
                    }
                elif name == "start_monitoring":
                    interval = arguments.get("interval", 30)
                    await self.start_monitoring(interval)
                    result = {"message": f"Started monitoring with {interval}s interval", "interval": interval}
                elif name == "stop_monitoring":
                    await self.stop_monitoring()
                    result = {"message": "Stopped monitoring"}
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
                
                if "deployment_id" in arguments:
                    await self._notify_operation_result(name, arguments["deployment_id"], False, {"error": str(e)})
                
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
                init_options = mcp_app.server.create_initialization_options(
                    notification_options=NotificationOptions(
                        resources_changed=True,
                        tools_changed=True,
                        prompts_changed=False
                    )
                )
                
                from mcp.server.session import ServerSession
                from mcp.shared.context import RequestContext
                from contextlib import AsyncExitStack
                import anyio
                
                async with AsyncExitStack() as stack:
                    session = await stack.enter_async_context(
                        ServerSession(
                            streams[0],
                            streams[1], 
                            init_options,
                            stateless=False,
                        )
                    )
                    
                    mcp_app.set_server_session(session)
                    
                    if mcp_app.subscribed_deployments:
                        await mcp_app.start_monitoring()
                    
                    async with anyio.create_task_group() as tg:
                        async for message in session.incoming_messages:
                            logger.debug("Received message: %s", message)
                            tg.start_soon(
                                mcp_app.server._handle_message,
                                message,
                                session,
                                {},  
                                False,  
                            )
                            
        except Exception as e:
            logger.error(f"SSE handler error: {e}")
            logger.error(traceback.format_exc())
        finally:
            if mcp_app:
                mcp_app.set_server_session(None)
                await mcp_app.stop_monitoring()
            return Response()

    async def handle_health(request: Request):
        """Health check endpoint"""
        return Response("OK", status_code=200)

    async def handle_info(request: Request):
        """Server info endpoint"""
        info = {
            "name": "guepard-deployment-server",
            "version": "1.0.0",
            "description": "Guepard Deployment MCP Server with SSE support and notifications",
            "endpoints": {
                "sse": f"http://{host}:{port}/sse",
                "messages": f"http://{host}:{port}/messages/",
                "health": f"http://{host}:{port}/health",
                "info": f"http://{host}:{port}/info"
            },
            "capabilities": {
                "notifications": {
                    "status_changes": "Notifies when deployment status changes",
                    "compute_events": "Notifies when compute starts/stops",
                    "operation_progress": "Shows progress for long-running operations",
                    "operation_results": "Notifies when operations complete"
                },
                "monitoring": {
                    "background_monitoring": "Can monitor deployments for changes",
                    "subscription_based": "Subscribe to specific deployments",
                    "configurable_interval": "Adjustable monitoring frequency"
                }
            },
            "tools": {
                "deployment_management": ["get_deployments", "create_deployment"],
                "compute_management": ["start_compute", "stop_compute"],
                "branch_management": ["create_branch", "checkout_branch"],
                "bookmark_management": ["create_bookmark"],
                "notification_management": ["subscribe_deployment", "unsubscribe_deployment", "list_subscriptions"],
                "monitoring_management": ["start_monitoring", "stop_monitoring"]
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
        logger.info("Notification capabilities enabled:")
        logger.info("  - Deployment status changes")
        logger.info("  - Compute start/stop events")
        logger.info("  - Operation progress updates")
        logger.info("  - Operation completion results")

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
    parser = argparse.ArgumentParser(
        description="Guepard Deployment MCP Server with notification support",
        epilog="""
Notification Features:
  - Real-time deployment status changes
  - Compute start/stop notifications  
  - Operation progress updates
  - Background monitoring with subscriptions
  
  Run with stdio transport
  python guepard-mcp.py --transport stdio
  
  Run with SSE transport (enables notifications)
  python guepard-mcp.py --transport sse --host 0.0.0.0 --port 8000
        """
    )
    parser.add_argument("--transport", choices=["stdio", "sse"], default="stdio",
                      help="Transport method to use (default: sse)")
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