#!/usr/bin/env python3
"""
Guepard Deployment API MCP Server
"""

import os
import json
import sys
import argparse
import logging
import aiohttp
from typing import Dict, List, Optional, Union

from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.models import InitializationOptions
import mcp.types as types
import mcp.server.stdio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()


class GuepardDeploymentServer:
    def __init__(self):
        self.server = Server("guepard-deployment-server")
        self.session = None
        self.access_token = None

        # Load environment variables
        self.supabase_url = "https://zvcpnahtojfbbetnlshj.supabase.co/auth/v1/token?grant_type=password"
        self.api_base_url = "https://api.dev.guepard.run"
        self.api_key = os.getenv("SUPABASE_API_KEY")
        self.email = os.getenv("EMAIL_USER")
        self.password = os.getenv("PASSWORD_USER")

        # Validate credentials
        if not self.api_key:
            raise ValueError("Missing SUPABASE_API_KEY in environment.")
        if not self.email:
            raise ValueError("Missing EMAIL_USER in environment.")
        if not self.password:
            raise ValueError("Missing PASSWORD_USER in environment.")

        self._setup_handlers()

    async def connect(self):
        self.session = aiohttp.ClientSession()
        logger.info("Attempting to log in...")
        self.access_token = await self._login()
        if not self.access_token:
            raise Exception("Supabase authentication failed.")
        logger.info("Successfully authenticated with Supabase.")

    async def disconnect(self):
        if self.session:
            await self.session.close()
            logger.info("Session disconnected.")

    def _get_auth_headers(self) -> Dict[str, str]:
        if not self.access_token:
            raise Exception("Missing access token.")
        return {
            "Content-Type": "application/json",
            "apikey": self.api_key,
            "Authorization": f"Bearer {self.access_token}"
        }

    async def _login(self) -> Optional[str]:
        payload = {"email": self.email, "password": self.password}
        try:
            async with self.session.post(self.supabase_url, json=payload, headers={"Content-Type": "application/json", "apikey": self.api_key}) as response:
                response.raise_for_status()
                data = await response.json()
                return data.get("access_token")
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return None

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
                    name="start_compute",
                    description="Start compute for a specific deployment",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "deployment_id": {"type": "string", "description": "Deployment ID"},
                            "clone_id": {"type": "string", "description": "Clone ID"}
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
)
,
                types.Tool(
                    name="create_snapshot",
                    description="Create a snapshot for a specific deployment",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "deployment_id": {"type": "string"},
                            "clone_id": {"type": "string"},
                            "snapshot_comment": {"type": "string"}
                        },
                        "required": ["deployment_id", "clone_id", "snapshot_comment"]
                    }
                ),
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> List[types.TextContent]:
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
                else:
                    return [types.TextContent(type="text", text=f"Unknown tool: {name}")]
                return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
            except Exception as e:
                logger.error(f"Tool '{name}' failed: {str(e)}")
                return [types.TextContent(type="text", text=json.dumps({"error": str(e)}))]

    async def _get_deployments(self, deployment_id=None, status=None, limit=100) -> Union[Dict, List[Dict]]:
        endpoint = f"/deploy/{deployment_id}" if deployment_id else "/deploy"
        params = {"status": status, "limit": max(1, min(limit, 1000))} if status else {"limit": max(1, min(limit, 1000))}
        url = f"{self.api_base_url}{endpoint}"
        async with self.session.get(url, headers=self._get_auth_headers(), params=params) as response:
            response.raise_for_status()
            return await response.json()
    async def _start_compute(self, deployment_id: str, clone_id: str) -> dict:
        url = f"{self.api_base_url}/deploy/{deployment_id}/{clone_id}/start"
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

    async def _create_snapshot(self, **kwargs) -> dict:
        deployment_id = kwargs["deployment_id"]
        clone_id = kwargs["clone_id"]
        payload = {
            "snapshot_comment": kwargs["snapshot_comment"]
        }

        url = f"{self.api_base_url}/deploy/{deployment_id}/{clone_id}/snap"

        async with self.session.put(url, headers=self._get_auth_headers(), json=payload) as response:
            text = await response.text()
            if response.status >= 400:
                try:
                    error_msg = json.loads(text).get("message", text)
                except json.JSONDecodeError:
                    error_msg = text
                raise Exception(f"API Error {response.status}: {error_msg}")
            return json.loads(text)


async def main():
    parser = argparse.ArgumentParser(description="Guepard Deployment MCP Server")
    parser.parse_args()

    server = GuepardDeploymentServer()

    try:
        await server.connect()
        logger.info("Guepard MCP Server is running...")
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
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
        logger.info("Shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)
    finally:
        await server.disconnect()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
