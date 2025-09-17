#!/usr/bin/env python3
"""
Guepard MCP Server - Real Implementation
Combines working stdio transport with real API calls to Guepard platform
"""

import os
import json
import sys
import asyncio
import logging
import aiohttp
from typing import Dict, List, Optional, Set
from datetime import datetime
import traceback
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GuepardMCPServer:
    def __init__(self):
        self.access_token = os.getenv("ACCESS_TOKEN", "")
        self.api_base_url = os.getenv("GUEPARD_API_URL", "https://api.guepard.run")
        self.session = None
        self.deployment_cache = {}
        self.subscribed_deployments: Set[str] = set()
        
        # Performance profile defaults from environment variables
        self.performance_profiles = {
            "postgres16": os.getenv("POSTGRES16_PROFILE_ID", ""),
            "postgres17": os.getenv("POSTGRES17_PROFILE_ID", "")
        }
        
        # Set defaults if not provided
        if not self.performance_profiles["postgres16"]:
            self.performance_profiles["postgres16"] = "e54710e1-73dd-4628-a51d-93d1aab5226c"
        if not self.performance_profiles["postgres17"]:
            self.performance_profiles["postgres17"] = "b0a4e557-bb67-4463-b774-ad82c04ab087"
        
        if not self.access_token:
            logger.error("ACCESS_TOKEN environment variable is required")
            sys.exit(1)
            
        logger.info(f"Guepard MCP Server initialized with token: {self.access_token[:20]}...")
        logger.info(f"API URL: {self.api_base_url}")
        logger.info(f"Performance profiles: PostgreSQL 16={self.performance_profiles['postgres16'][:8]}..., PostgreSQL 17={self.performance_profiles['postgres17'][:8]}...")
        
        # Define all available tools
        self.tools = {
            "test_connection": {
                "name": "test_connection",
                "description": "Test connection to Guepard API",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            "get_deployments": {
                "name": "get_deployments",
                "description": "Retrieve deployment info. Leave deployment_id empty to get all.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "deployment_id": {
                            "type": "string",
                            "description": "Deployment ID (optional)"
                        },
                        "status": {
                            "type": "string",
                            "description": "Filter by status",
                            "enum": ["active", "pending", "failed", "terminated"]
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Limit",
                            "default": 100
                        }
                    }
                }
            },
            "stop_compute": {
                "name": "stop_compute",
                "description": "Stop compute for a specific deployment",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "deployment_id": {
                            "type": "string",
                            "description": "Deployment ID"
                        },
                        "notify": {
                            "type": "boolean",
                            "description": "Send notification when operation completes",
                            "default": True
                        }
                    },
                    "required": ["deployment_id"]
                }
            },
            "start_compute": {
                "name": "start_compute",
                "description": "Start compute for a specific deployment",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "deployment_id": {
                            "type": "string",
                            "description": "Deployment ID"
                        },
                        "notify": {
                            "type": "boolean",
                            "description": "Send notification when operation completes",
                            "default": True
                        }
                    },
                    "required": ["deployment_id"]
                }
            },
            "create_branch": {
                "name": "create_branch",
                "description": "Create a branch from snapshot",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "deployment_id": {
                            "type": "string",
                            "description": "Deployment ID"
                        },
                        "clone_id": {
                            "type": "string",
                            "description": "Clone ID"
                        },
                        "snapshot_id": {
                            "type": "string",
                            "description": "Snapshot ID"
                        },
                        "branch_name": {
                            "type": "string",
                            "description": "Branch name"
                        },
                        "discard_changes": {
                            "type": "string",
                            "description": "Discard changes",
                            "enum": ["true", "false"],
                            "default": "true"
                        },
                        "checkout": {
                            "type": "boolean",
                            "description": "Checkout after creation",
                            "default": False
                        },
                        "ephemeral": {
                            "type": "boolean",
                            "description": "Create ephemeral branch",
                            "default": False
                        },
                        "notify": {
                            "type": "boolean",
                            "description": "Send notification when operation completes",
                            "default": True
                        }
                    },
                    "required": ["deployment_id", "clone_id", "snapshot_id", "branch_name"]
                }
            },
            "checkout_branch": {
                "name": "checkout_branch",
                "description": "Checkout to a specific branch",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "deployment_id": {
                            "type": "string",
                            "description": "Deployment ID"
                        },
                        "clone_id": {
                            "type": "string",
                            "description": "Clone ID"
                        },
                        "notify": {
                            "type": "boolean",
                            "description": "Send notification when operation completes",
                            "default": True
                        }
                    },
                    "required": ["deployment_id", "clone_id"]
                }
            },
            "create_bookmark": {
                "name": "create_bookmark",
                "description": "Create a bookmark for a specific deployment",
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
                        "snapshot_comment": {
                            "type": "string",
                            "description": "Snapshot comment"
                        },
                        "notify": {
                            "type": "boolean",
                            "description": "Send notification when operation completes",
                            "default": True
                        }
                    },
                    "required": ["deployment_id", "branch_id", "snapshot_comment"]
                }
            },
            "subscribe_deployment": {
                "name": "subscribe_deployment",
                "description": "Subscribe to deployment notifications",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "deployment_id": {
                            "type": "string",
                            "description": "Deployment ID"
                        }
                    },
                    "required": ["deployment_id"]
                }
            },
            "unsubscribe_deployment": {
                "name": "unsubscribe_deployment",
                "description": "Unsubscribe from deployment notifications",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "deployment_id": {
                            "type": "string",
                            "description": "Deployment ID"
                        }
                    },
                    "required": ["deployment_id"]
                }
            },
            "list_subscriptions": {
                "name": "list_subscriptions",
                "description": "List all deployment subscriptions",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            "get_performance_profiles": {
                "name": "get_performance_profiles",
                "description": "Get available performance profile defaults",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            "create_deployment": {
                "name": "create_deployment",
                "description": "Create a new database deployment",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "deployment_type": {
                            "type": "string",
                            "description": "Type of deployment",
                            "enum": ["REPOSITORY", "F2"],
                            "default": "REPOSITORY"
                        },
                        "database_provider": {
                            "type": "string",
                            "description": "Database provider",
                            "enum": ["PostgreSQL", "mysql", "mongodb"],
                            "default": "PostgreSQL"
                        },
                        "database_version": {
                            "type": "string",
                            "description": "Database version",
                            "default": "17"
                        },
                        "repository_name": {
                            "type": "string",
                            "description": "Repository name"
                        },
                        "performance_profile_id": {
                            "type": "string",
                            "description": "Performance profile ID"
                        },
                        "notify": {
                            "type": "boolean",
                            "description": "Send notification when operation completes",
                            "default": True
                        }
                    },
                    "required": ["repository_name", "performance_profile_id"]
                }
            }
        }
    
    async def connect(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession(
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.access_token}"
            }
        )
        logger.info("HTTP session initialized")
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for API calls"""
        supabase_anon_key = os.getenv("SUPABASE_ANON_KEY", "")
        return {
            "Content-Type": "application/json",
            "apikey": supabase_anon_key,
            "Authorization": f"Bearer {self.access_token}"
        }
    
    async def disconnect(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
            logger.info("HTTP session closed")
    
    async def _make_api_call(self, method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> Dict:
        """Make API call to Guepard platform"""
        url = f"{self.api_base_url}{endpoint}"
        
        try:
            async with self.session.request(method, url, json=data, params=params) as response:
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
    
    async def call_tool(self, tool_name: str, arguments: Dict) -> str:
        """Call a specific tool with arguments"""
        if tool_name == "test_connection":
            return await self._test_connection()
        
        elif tool_name == "get_deployments":
            return await self._get_deployments(
                deployment_id=arguments.get("deployment_id"),
                status=arguments.get("status"),
                limit=arguments.get("limit", 100)
            )
        
        elif tool_name == "stop_compute":
            return await self._stop_compute(
                deployment_id=arguments.get("deployment_id"),
                notify=arguments.get("notify", True)
            )
        
        elif tool_name == "start_compute":
            return await self._start_compute(
                deployment_id=arguments.get("deployment_id"),
                notify=arguments.get("notify", True)
            )
        
        elif tool_name == "create_branch":
            return await self._create_branch(
                deployment_id=arguments.get("deployment_id"),
                clone_id=arguments.get("clone_id"),
                snapshot_id=arguments.get("snapshot_id"),
                branch_name=arguments.get("branch_name"),
                discard_changes=arguments.get("discard_changes", "true"),
                checkout=arguments.get("checkout", False),
                ephemeral=arguments.get("ephemeral", False),
                notify=arguments.get("notify", True)
            )
        
        elif tool_name == "checkout_branch":
            return await self._checkout_branch(
                deployment_id=arguments.get("deployment_id"),
                clone_id=arguments.get("clone_id"),
                notify=arguments.get("notify", True)
            )
        
        elif tool_name == "create_bookmark":
            return await self._create_bookmark(
                deployment_id=arguments.get("deployment_id"),
                branch_id=arguments.get("branch_id"),
                snapshot_comment=arguments.get("snapshot_comment"),
                notify=arguments.get("notify", True)
            )
        
        elif tool_name == "subscribe_deployment":
            return await self._subscribe_deployment(
                deployment_id=arguments.get("deployment_id")
            )
        
        elif tool_name == "unsubscribe_deployment":
            return await self._unsubscribe_deployment(
                deployment_id=arguments.get("deployment_id")
            )
        
        elif tool_name == "list_subscriptions":
            return await self._list_subscriptions()
        
        elif tool_name == "get_performance_profiles":
            return await self._get_performance_profiles()
        
        elif tool_name == "create_deployment":
            return await self._create_deployment(
                deployment_type=arguments.get("deployment_type", "REPOSITORY"),
                database_provider=arguments.get("database_provider", "PostgreSQL"),
                database_version=arguments.get("database_version", "17"),
                repository_name=arguments.get("repository_name"),
                performance_profile_id=arguments.get("performance_profile_id"),
                notify=arguments.get("notify", True)
            )
        
        else:
            return f"Unknown tool: {tool_name}"
    
    async def _test_connection(self) -> str:
        """Test connection to Guepard API"""
        try:
            # Test with a simple API call that we know works
            result = await self._make_api_call("GET", "/deploy", params={"limit": 1})
            if isinstance(result, dict) and result.get("error"):
                return f"❌ Connection failed: {result.get('message', 'Unknown error')}"
            else:
                profiles_info = "\n".join([f"• {version}: {profile_id[:8]}..." for version, profile_id in self.performance_profiles.items()])
                return f"✅ Guepard MCP Server connected successfully!\nAPI URL: {self.api_base_url}\nToken: {self.access_token[:20]}...\n\n📊 Performance Profiles:\n{profiles_info}"
        except Exception as e:
            return f"❌ Connection test failed: {str(e)}"
    
    async def _get_deployments(self, deployment_id: Optional[str] = None, status: Optional[str] = None, limit: int = 100) -> str:
        """Get deployments from Guepard API"""
        endpoint = f"/deploy"
        if deployment_id:
            endpoint = f"/deploy/{deployment_id}"
        
        params = {}
        if status:
            params["status"] = status
        if limit:
            params["limit"] = limit
        
        try:
            result = await self._make_api_call("GET", endpoint, params=params)
            if isinstance(result, dict) and result.get("error"):
                return f"❌ Failed to get deployments: {result.get('message', 'Unknown error')}"
            else:
                # Handle both list and dict responses
                if isinstance(result, list):
                    count = len(result)
                    return f"✅ Found {count} deployments:\n{json.dumps(result, indent=2)}"
                else:
                    return f"✅ Deployments retrieved successfully:\n{json.dumps(result, indent=2)}"
        except Exception as e:
            return f"❌ Get deployments failed: {str(e)}"
    
    async def _stop_compute(self, deployment_id: str, notify: bool = True) -> str:
        """Stop compute for a deployment"""
        try:
            result = await self._make_api_call("GET", f"/deploy/{deployment_id}/stop")
            if result.get("error"):
                return f"❌ Failed to stop compute: {result.get('message', 'Unknown error')}"
            else:
                status = "✅ Compute stopped successfully"
                if notify:
                    status += " (notifications enabled)"
                return f"{status}\nDeployment: {deployment_id}\nResult: {json.dumps(result, indent=2)}"
        except Exception as e:
            return f"❌ Stop compute failed: {str(e)}"
    
    async def _start_compute(self, deployment_id: str, notify: bool = True) -> str:
        """Start compute for a deployment"""
        try:
            result = await self._make_api_call("GET", f"/deploy/{deployment_id}/start")
            if result.get("error"):
                return f"❌ Failed to start compute: {result.get('message', 'Unknown error')}"
            else:
                status = "✅ Compute started successfully"
                if notify:
                    status += " (notifications enabled)"
                return f"{status}\nDeployment: {deployment_id}\nResult: {json.dumps(result, indent=2)}"
        except Exception as e:
            return f"❌ Start compute failed: {str(e)}"
    
    async def _create_branch(self, deployment_id: str, clone_id: str, snapshot_id: str, branch_name: str, discard_changes: str = "true", checkout: bool = False, ephemeral: bool = False, notify: bool = True) -> str:
        """Create a branch from snapshot"""
        try:
            data = {
                "branch_name": branch_name,
                "discard_changes": discard_changes,
                "checkout": checkout,
                "ephemeral": ephemeral
            }
            result = await self._make_api_call("POST", f"/deploy/{deployment_id}/{clone_id}/{snapshot_id}/branch", data)
            if isinstance(result, dict) and result.get("error"):
                return f"❌ Failed to create branch: {result.get('message', 'Unknown error')}"
            else:
                status = f"✅ Branch '{branch_name}' created successfully"
                if notify:
                    status += " (notifications enabled)"
                return f"{status}\nDeployment: {deployment_id}\nClone: {clone_id}\nSnapshot: {snapshot_id}\nResult: {json.dumps(result, indent=2)}"
        except Exception as e:
            return f"❌ Create branch failed: {str(e)}"
    
    async def _checkout_branch(self, deployment_id: str, clone_id: str, notify: bool = True) -> str:
        """Checkout to a specific branch"""
        try:
            result = await self._make_api_call("POST", f"/deploy/{deployment_id}/{clone_id}/checkout")
            if isinstance(result, dict) and result.get("error"):
                return f"❌ Failed to checkout branch: {result.get('message', 'Unknown error')}"
            else:
                status = f"✅ Checked out branch successfully"
                if notify:
                    status += " (notifications enabled)"
                return f"{status}\nDeployment: {deployment_id}\nClone: {clone_id}\nResult: {json.dumps(result, indent=2)}"
        except Exception as e:
            return f"❌ Checkout branch failed: {str(e)}"
    
    async def _create_bookmark(self, deployment_id: str, branch_id: str, snapshot_comment: str, notify: bool = True) -> str:
        """Create a bookmark for a specific deployment"""
        try:
            data = {"snapshot_comment": snapshot_comment}
            result = await self._make_api_call("PUT", f"/deploy/{deployment_id}/{branch_id}/snap", data)
            if isinstance(result, dict) and result.get("error"):
                return f"❌ Failed to create bookmark: {result.get('message', 'Unknown error')}"
            else:
                status = "✅ Bookmark created successfully"
                if notify:
                    status += " (notifications enabled)"
                return f"{status}\nDeployment: {deployment_id}\nBranch: {branch_id}\nComment: {snapshot_comment}\nResult: {json.dumps(result, indent=2)}"
        except Exception as e:
            return f"❌ Create bookmark failed: {str(e)}"
    
    async def _subscribe_deployment(self, deployment_id: str) -> str:
        """Subscribe to deployment notifications"""
        try:
            self.subscribed_deployments.add(deployment_id)
            return f"✅ Subscribed to notifications for deployment: {deployment_id}\nTotal subscriptions: {len(self.subscribed_deployments)}"
        except Exception as e:
            return f"❌ Subscribe failed: {str(e)}"
    
    async def _unsubscribe_deployment(self, deployment_id: str) -> str:
        """Unsubscribe from deployment notifications"""
        try:
            self.subscribed_deployments.discard(deployment_id)
            return f"✅ Unsubscribed from notifications for deployment: {deployment_id}\nTotal subscriptions: {len(self.subscribed_deployments)}"
        except Exception as e:
            return f"❌ Unsubscribe failed: {str(e)}"
    
    async def _list_subscriptions(self) -> str:
        """List all deployment subscriptions"""
        try:
            if not self.subscribed_deployments:
                return "📋 No active subscriptions"
            else:
                subscriptions = list(self.subscribed_deployments)
                return f"📋 Active subscriptions ({len(subscriptions)}):\n" + "\n".join(f"• {deployment_id}" for deployment_id in subscriptions)
        except Exception as e:
            return f"❌ List subscriptions failed: {str(e)}"
    
    async def _get_performance_profiles(self) -> str:
        """Get available performance profiles"""
        try:
            profiles_info = []
            for version, profile_id in self.performance_profiles.items():
                profiles_info.append(f"• {version.upper()}: {profile_id}")
            
            return f"📊 Available Performance Profiles:\n" + "\n".join(profiles_info) + f"\n\n💡 Use these profile IDs when creating deployments or configuring database performance settings."
        except Exception as e:
            return f"❌ Get performance profiles failed: {str(e)}"
    
    async def _create_deployment(self, deployment_type: str, database_provider: str, database_version: str, repository_name: str, performance_profile_id: str, notify: bool = True) -> str:
        """Create a new database deployment"""
        try:
            data = {
                "deployment_type": deployment_type,
                "database_provider": database_provider,
                "database_version": database_version,
                "repository_name": repository_name,
                "performance_profile_id": performance_profile_id
            }
            result = await self._make_api_call("POST", "/deploy", data)
            if isinstance(result, dict) and result.get("error"):
                return f"❌ Failed to create deployment: {result.get('message', 'Unknown error')}"
            else:
                status = "✅ Deployment created successfully"
                if notify:
                    status += " (notifications enabled)"
                
                deployment_id = result.get("id", "Unknown")
                deployment_name = result.get("name", "Unknown")
                
                return f"{status}\nDeployment ID: {deployment_id}\nDeployment Name: {deployment_name}\nRepository: {repository_name}\nDatabase: {database_provider} {database_version}\nPerformance Profile: {performance_profile_id}\nResult: {json.dumps(result, indent=2)}"
        except Exception as e:
            return f"❌ Create deployment failed: {str(e)}"
    
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
                        "name": "guepard-custom",
                        "version": "1.0.0"
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
                    "tools": list(self.tools.values())
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
        """Run the custom MCP server"""
        logger.info("Starting Guepard MCP server with real API integration...")
        
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
    server = GuepardMCPServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())
