#!/usr/bin/env python3
"""
Guepard MCP Server - Complete API Implementation
Main entry point for the comprehensive Guepard MCP server.
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from guepard_mcp.server import main

if __name__ == "__main__":
    asyncio.run(main())
