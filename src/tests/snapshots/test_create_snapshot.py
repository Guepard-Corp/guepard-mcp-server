#!/usr/bin/env python3
"""
Simple test for CreateSnapshotTool
Gets deployment, gets branch, creates snapshot
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from guepard_mcp.snapshots.tools import CreateSnapshotTool
from guepard_mcp.utils.base import GuepardAPIClient
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from test_utils import get_real_deployment_id, get_first_branch_id

async def test_create_snapshot():
    """Simple test: get deployment, get branch, create snapshot"""
    print("🧪 Testing create_snapshot tool...")
    
    # Create client and tool
    client = GuepardAPIClient()
    tool = CreateSnapshotTool(client)
    
    # Check credentials
    if not client.access_token:
        print("❌ No ACCESS_TOKEN found")
        return False
    
    print(f"   API: {client.api_base_url}")
    print(f"   Token: {client.access_token[:10]}...")
    
    # Initialize session
    await client.connect()
    
    try:
        # 1. Get deployment
        print("\n1. Getting deployment...")
        deployment_id = await get_real_deployment_id(client)
        print(f"   ✅ Got deployment: {deployment_id}")
        
        # 2. Get branch
        print("\n2. Getting branch...")
        branch_id = await get_first_branch_id(client, deployment_id)
        print(f"   ✅ Got branch: {branch_id}")
        
        # 3. Create snapshot
        print("\n3. Creating snapshot...")
        result = await tool.execute({
            "deployment_id": deployment_id,
            "branch_id": branch_id,
            "snapshot_comment": "Test snapshot created by automated test"
        })
        print(f"   ✅ Snapshot created: {result}")
        
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return False
    finally:
        await client.disconnect()
    
    print("\n✅ Test completed successfully!")
    return True

async def main():
    """Main test runner"""
    print("🚀 Starting simple create_snapshot test...\n")
    
    try:
        success = await test_create_snapshot()
        return 0 if success else 1
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)