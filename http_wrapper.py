#!/usr/bin/env python3
"""
HTTP Wrapper for Guepard MCP Server
Converts HTTP requests to MCP protocol and back
"""

import asyncio
import json
import os
import sys
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import subprocess
import tempfile

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

app = FastAPI(title="Guepard MCP HTTP Wrapper", version="1.0.0")

class MCPRequest(BaseModel):
    method: str
    params: dict = {}
    id: int = 1

class MCPResponse(BaseModel):
    jsonrpc: str = "2.0"
    id: int
    result: dict = None
    error: dict = None

@app.get("/")
async def root():
    return {
        "message": "Guepard MCP Server HTTP Wrapper",
        "version": "1.0.0",
        "status": "running"
    }

@app.post("/mcp")
async def mcp_endpoint(mcp_req: MCPRequest, request: Request):
    """Handle MCP requests via HTTP"""
    try:
        # Extract access token priority: Authorization header > x-access-token header > body params.token
        auth_header = request.headers.get("authorization") or request.headers.get("Authorization")
        x_access_token = request.headers.get("x-access-token") or request.headers.get("X-Access-Token")
        body_token = None
        try:
            body_json = await request.json()
            body_token = (
                body_json.get("params", {}).get("token")
                if isinstance(body_json, dict)
                else None
            )
        except Exception:
            body_token = None

        token: str = ""
        if auth_header and auth_header.lower().startswith("bearer "):
            token = auth_header.split(" ", 1)[1].strip()
        elif x_access_token:
            token = x_access_token.strip()
        elif body_token:
            token = str(body_token).strip()

        if not token:
            raise HTTPException(status_code=401, detail="ACCESS_TOKEN missing. Provide via Authorization: Bearer <token>, X-Access-Token header, or params.token in body.")

        # Create MCP request
        mcp_request = {
            "jsonrpc": "2.0",
            "id": mcp_req.id,
            "method": mcp_req.method,
            "params": mcp_req.params
        }
        
        # Run MCP server with the request
        result = await run_mcp_request(mcp_request, token)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def run_mcp_request(request: dict, access_token: str):
    """Run a single MCP request"""
    try:
        # Create temporary file for input
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump(request, f)
            input_file = f.name
        
        # Prepare environment per request (isolate token)
        env = os.environ.copy()
        env["ACCESS_TOKEN"] = access_token

        # Optional overrides via request.params for flexibility
        params = request.get("params", {}) if isinstance(request, dict) else {}
        if isinstance(params, dict):
            if params.get("GUEPARD_API_URL"):
                env["GUEPARD_API_URL"] = str(params["GUEPARD_API_URL"]).strip()
            if params.get("GUEPARD_AUTH_API"):
                env["GUEPARD_AUTH_API"] = str(params["GUEPARD_AUTH_API"]).strip()
            if params.get("SUPABASE_ANON_KEY"):
                env["SUPABASE_ANON_KEY"] = str(params["SUPABASE_ANON_KEY"]).strip()

        # Run the MCP server
        process = await asyncio.create_subprocess_exec(
            'python', 'main.py',
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd='/app',
            env=env
        )
        
        # Send the request
        stdout, stderr = await process.communicate(
            input=json.dumps(request).encode()
        )
        
        # Clean up
        os.unlink(input_file)
        
        if process.returncode != 0:
            raise Exception(f"MCP server error: {stderr.decode()}")
        
        # Parse response
        response = json.loads(stdout.decode())
        return response
        
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": request.get("id", 1),
            "error": {
                "code": -32603,
                "message": str(e)
            }
        }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "guepard-mcp-http-wrapper"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=80)


