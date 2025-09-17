#!/usr/bin/env python3
"""
Test script to check deployments using the Guepard MCP Server
"""

import asyncio
import os
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the server class directly
exec(open('guepard-mcp-server.py').read())

async def test_deployments():
    """Test the get_deployments functionality"""
    print("🚀 Testing Guepard MCP Server - Get Deployments")
    print("=" * 50)
    
    # Check if ACCESS_TOKEN is set
    if not os.getenv("ACCESS_TOKEN"):
        print("❌ ERROR: ACCESS_TOKEN environment variable is required")
        print("Please set your Guepard access token:")
        print("export ACCESS_TOKEN='your_token_here'")
        return
    
    # Initialize the server
    server = GuepardMCPServer()
    
    try:
        # Connect to the API
        await server.connect()
        print("✅ Connected to Guepard API")
        
        # Test connection first
        print("\n🔍 Testing connection...")
        connection_result = await server._test_connection()
        print(connection_result)
        
        # Get all deployments
        print("\n📊 Getting all deployments...")
        deployments_result = await server._get_deployments()
        print(deployments_result)
        
        # Get deployments with limit
        print("\n📊 Getting deployments (limit 10)...")
        deployments_limited = await server._get_deployments(limit=10)
        print(deployments_limited)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Disconnect
        await server.disconnect()
        print("\n✅ Disconnected from API")

if __name__ == "__main__":
    asyncio.run(test_deployments())
