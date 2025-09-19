#!/usr/bin/env python3
"""
Test for GetDeploymentMetricsTool
Tests the get_deployment_metrics functionality
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from tests.base_test import BaseToolTest
from guepard_mcp.logs.tools import GetDeploymentMetricsTool
from guepard_mcp.utils.base import GuepardAPIClient
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from test_utils import get_real_deployment_id, get_fake_deployment_id

async def main():
    """Main test runner for GetDeploymentMetricsTool"""
    
    # Define test cases
    test_cases = [
        {
            "name": "valid_deployment_id",
            "arguments": {"deployment_id": "deploy-123"},
            "expected_api_call": ("GET", "/deploy/deploy-123")
        }
    ]
    
    # Create and run tests
    tester = BaseToolTest(GetDeploymentMetricsTool, "get_deployment_metrics", test_cases)
    success = await tester.run_all_tests()
    
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
