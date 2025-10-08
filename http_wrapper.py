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
from supabase import create_client, Client
from typing import Optional, Dict, Any

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Supabase configuration
SUPABASE_URL = "https://zvcpnahtojfbbetnlshj.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp2Y3BuYWh0b2pmYmJldG5sc2hqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDU2Mjg5MjgsImV4cCI6MjA2MTIwNDkyOH0.d-yl_231WhtTsnfuxTDvEtW35wyXMtro5M7Xu3vuGQ4"

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

app = FastAPI(title="Guepard MCP HTTP Wrapper", version="1.0.0")

class MCPRequest(BaseModel):
    method: str
    params: dict = {}
    id: int = 1

class MCPResponse(BaseModel):
    jsonrpc: str = "2.0"
    id: int
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None

async def validate_supabase_token(token: str) -> Optional[Dict[str, Any]]:
    """Validate Supabase access token and return user info"""
    try:
        # Quick validation - check if token looks like a Supabase token
        if not token or len(token) < 50:
            return None
            
        # Set the auth token for this request with timeout
        supabase.auth.set_session(token, "")
        
        # Get user info with timeout protection
        import asyncio
        try:
            # Use asyncio.wait_for to add timeout
            user = await asyncio.wait_for(
                asyncio.to_thread(supabase.auth.get_user), 
                timeout=5.0
            )
        except asyncio.TimeoutError:
            print("Supabase token validation timeout")
            return None
        
        if user and user.user:
            return {
                "user_id": user.user.id,
                "email": user.user.email,
                "auth_type": "supabase"
            }
        return None
    except Exception as e:
        print(f"Supabase token validation failed: {e}")
        return None

def is_guepard_token(token: str) -> bool:
    """Check if token looks like a Guepard JWT token"""
    try:
        # Guepard tokens are JWTs with specific structure
        parts = token.split('.')
        if len(parts) != 3:
            return False
        
        # Decode header to check if it's a Guepard token
        import base64
        import json
        
        # Add padding if needed
        header = parts[0]
        header += '=' * (4 - len(header) % 4)
        header_data = json.loads(base64.urlsafe_b64decode(header))
        
        # Check if it has Guepard-specific claims or structure
        return True  # Assume it's Guepard if it's a valid JWT
    except Exception:
        return False

@app.get("/")
async def root():
    return {
        "message": "Guepard MCP Server HTTP Wrapper",
        "version": "1.0.0",
        "status": "running"
    }

@app.post("/mcp")
async def mcp_endpoint(mcp_req: MCPRequest, request: Request):
    """Handle MCP requests via HTTP with dual authentication support"""
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

        # Determine authentication type and validate
        auth_info = None
        final_token = token
        
        # Try Supabase authentication first
        supabase_user = await validate_supabase_token(token)
        if supabase_user:
            auth_info = supabase_user
            print(f"✅ Supabase authentication successful for user: {supabase_user['email']}")
        else:
            # Fallback to Guepard token (existing functionality)
            if is_guepard_token(token):
                auth_info = {"auth_type": "guepard", "token": token}
                print(f"✅ Guepard token authentication")
            else:
                # Try as Guepard token anyway (for backward compatibility)
                auth_info = {"auth_type": "guepard", "token": token}
                print(f"⚠️ Unknown token type, treating as Guepard token")

        if not auth_info:
            raise HTTPException(status_code=403, detail="Invalid token. Token must be either a valid Supabase access token or Guepard token.")

        # Create MCP request
        mcp_request = {
            "jsonrpc": "2.0",
            "id": mcp_req.id,
            "method": mcp_req.method,
            "params": mcp_req.params
        }
        
        # Run MCP server with the request
        result = await run_mcp_request(mcp_request, final_token, auth_info)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def run_mcp_request(request: dict, access_token: str, auth_info: Dict[str, Any]):
    """Run a single MCP request with authentication context"""
    try:
        # Prepare environment per request (isolate token)
        env = os.environ.copy()
        env["ACCESS_TOKEN"] = access_token
        
        # Add authentication context to environment
        if auth_info.get("auth_type") == "supabase":
            env["AUTH_TYPE"] = "supabase"
            env["SUPABASE_USER_ID"] = auth_info.get("user_id", "")
            env["SUPABASE_USER_EMAIL"] = auth_info.get("email", "")
        else:
            env["AUTH_TYPE"] = "guepard"

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
        
        if process.returncode != 0:
            error_message = stderr.decode().strip()
            # Attempt to parse stderr as JSON if it looks like an MCP error response
            try:
                error_json = json.loads(error_message)
                if "error" in error_json:
                    return error_json
            except json.JSONDecodeError:
                pass  # Not a JSON error, proceed with generic error
            
            return {
                "jsonrpc": "2.0",
                "id": request.get("id", 1),
                "error": {
                    "code": -32603,
                    "message": f"MCP server error: {error_message}"
                }
            }
        
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


