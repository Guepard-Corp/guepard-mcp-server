#!/usr/bin/env python3
"""
Test for CheckoutBranchTool
Tests the checkout_branch functionality
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from tests.base_test import BaseToolTest
from guepard_mcp.checkouts.tools import CheckoutBranchTool

async def main():
    """Main test runner for CheckoutBranchTool"""
    
    # Define test cases
    test_cases = [
        {
            "name": "basic_checkout",
            "arguments": {
                "deployment_id": "deploy-123",
                "branch_id": "branch-123"
            },
            "expected_api_call": None
        }
    ]
    
    # Create and run tests
    tester = BaseToolTest(CheckoutBranchTool, "checkout_branch", test_cases)
    success = await tester.run_all_tests()
    
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
