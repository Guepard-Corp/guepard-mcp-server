#!/usr/bin/env python3
"""
Test for ListF2DeploymentsTool
Tests the list_f2_deployments functionality
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from tests.base_test import BaseToolTest
from guepard_mcp.f2_deployments.tools import ListF2DeploymentsTool

async def main():
    """Main test runner for ListF2DeploymentsTool"""
    
    # Define test cases
    test_cases = [
        {
            "name": "basic_list",
            "arguments": {},
            "expected_api_call": None
        },
        {
            "name": "with_filters",
            "arguments": {"limit": 10},
            "expected_api_call": None
        }
    ]
    
    # Create and run tests
    tester = BaseToolTest(ListF2DeploymentsTool, "list_f2_deployments", test_cases)
    success = await tester.run_all_tests()
    
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
