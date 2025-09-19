#!/usr/bin/env python3
"""
Test for ListSubscriptionsTool
Tests the list_subscriptions functionality
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from tests.base_test import BaseToolTest
from guepard_mcp.server.tools import ListSubscriptionsTool

async def main():
    """Main test runner for ListSubscriptionsTool"""
    
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
    tester = BaseToolTest(ListSubscriptionsTool, "list_subscriptions", test_cases)
    success = await tester.run_all_tests()
    
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
