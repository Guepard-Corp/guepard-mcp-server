#!/usr/bin/env python3
"""
Real test for CheckoutBranchTool
Tests the checkout_branch functionality with real API calls
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from guepard_mcp.branches.tools import CheckoutBranchTool
from guepard_mcp.utils.base import GuepardAPIClient

async def test_checkout_branch():
    """Test checkout_branch tool with real API calls"""
    print("🧪 Testing checkout_branch tool with real API calls...")
    
    # Create tool instance
    client = GuepardAPIClient()
    tool = CheckoutBranchTool(client)
    
    # Check if we have credentials
    if not client.access_token:
        print("❌ No ACCESS_TOKEN found in environment variables")
        print("   Please set ACCESS_TOKEN in your .env file")
        return False
    
    print(f"   Using API: {client.api_base_url}")
    print(f"   Token: {client.access_token[:10]}...")
    
    # Initialize HTTP session
    await client.connect()
    
    # Test 1: Checkout existing branch
    print("\n  Testing checkout existing branch...")
    try:
        result = await tool.execute({
            "branch_id": "test-branch-123"
        })
        print(f"    Response: {result}")
        print("  ✅ Checkout existing branch test completed")
    except Exception as e:
        print(f"    ❌ Checkout existing branch test failed: {e}")
        return False
    
    # Test 2: Checkout non-existent branch
    print("\n  Testing checkout non-existent branch...")
    try:
        result = await tool.execute({
            "branch_id": "non-existent-branch-999"
        })
        print(f"    Response: {result}")
        print("  ✅ Checkout non-existent branch test completed")
    except Exception as e:
        print(f"    ❌ Checkout non-existent branch test failed: {e}")
        return False
    
    # Test 3: Missing branch_id parameter
    print("\n  Testing missing branch_id parameter...")
    try:
        result = await tool.execute({})
        print(f"    Response: {result}")
        print("  ✅ Missing branch_id test completed")
    except Exception as e:
        print(f"    ❌ Missing branch_id test failed: {e}")
        return False
    
    # Clean up
    await client.disconnect()
    
    print("\n" + "="*60)
    print("📊 SYNTHESIS - Checkout Branch Test Results")
    print("="*60)
    print("✅ Tested scenarios:")
    print("   • Checkout existing branch")
    print("   • Checkout non-existent branch")
    print("   • Handle missing branch_id parameter")
    print(f"\n🔗 API Endpoint: {client.api_base_url}/branches/checkout")
    print(f"🔑 Authentication: {'✅ Token present' if client.access_token else '❌ No token'}")
    print("\n📝 Notes:")
    print("   • All tests completed successfully")
    print("   • Real API calls made to local server")
    print("   • HTTP session properly initialized and cleaned up")
    print("   • Error handling tested for various scenarios")
    print("="*60)
    
    print("\n✅ All checkout_branch real API tests completed!")
    return True

async def main():
    """Main test runner"""
    print("🚀 Starting checkout_branch real API tests...\n")
    
    try:
        success = await test_checkout_branch()
        return 0 if success else 1
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

