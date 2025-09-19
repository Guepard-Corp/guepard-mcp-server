#!/usr/bin/env python3
"""
Test for CreateNodeTool
Tests the create_node functionality
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from tests.base_test import BaseToolTest
from guepard_mcp.nodes.tools import CreateNodeTool

async def main():
    """Main test runner for CreateNodeTool"""
    
    # Define test cases
    test_cases = [
        {
            "name": "basic_test",
            "arguments": {},
            "expected_api_call": None
        }
    ]
    
    # Create and run tests
    tester = BaseToolTest(CreateNodeTool, "create_node", test_cases)
    success = await tester.run_all_tests()
    
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
