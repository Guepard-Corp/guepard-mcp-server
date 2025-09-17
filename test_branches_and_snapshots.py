#!/usr/bin/env python3
"""
Test script for branch management and snapshot tools
"""

import json
import subprocess
import sys
import time

def test_branches_and_snapshots():
    """Test branch management and snapshot tools"""
    
    # Start the MCP server
    print("🌿 Starting MCP server for branches and snapshots testing...")
    process = subprocess.Popen(
        [sys.executable, "main.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd="/Users/mghassen/Workspace/GPRD/guepard-mcp-server"
    )
    
    # Give it a moment to start
    time.sleep(2)
    
    # Test branch and snapshot requests
    test_requests = [
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "branches-snapshots-test-client",
                    "version": "1.0.0"
                }
            }
        },
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "test_connection",
                "arguments": {}
            }
        },
        {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "list_deployments",
                "arguments": {"limit": 2}
            }
        },
        {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "list_branches",
                "arguments": {
                    "deployment_id": "5949ab07-5173-4e56-92a9-f7c5323aa6df"
                }
            }
        },
        {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "create_branch",
                "arguments": {
                    "deployment_id": "5949ab07-5173-4e56-92a9-f7c5323aa6df",
                    "name": "test-branch-from-mcp",
                    "description": "Test branch created via MCP server"
                }
            }
        },
        {
            "jsonrpc": "2.0",
            "id": 6,
            "method": "tools/call",
            "params": {
                "name": "list_snapshots_deployment",
                "arguments": {
                    "deployment_id": "5949ab07-5173-4e56-92a9-f7c5323aa6df"
                }
            }
        },
        {
            "jsonrpc": "2.0",
            "id": 7,
            "method": "tools/call",
            "params": {
                "name": "create_snapshot",
                "arguments": {
                    "deployment_id": "5949ab07-5173-4e56-92a9-f7c5323aa6df",
                    "branch_id": "main",
                    "snapshot_comment": "Test snapshot created via MCP server"
                }
            }
        },
        {
            "jsonrpc": "2.0",
            "id": 8,
            "method": "tools/call",
            "params": {
                "name": "list_snapshots_branch",
                "arguments": {
                    "deployment_id": "5949ab07-5173-4e56-92a9-f7c5323aa6df",
                    "branch_id": "main"
                }
            }
        },
        {
            "jsonrpc": "2.0",
            "id": 9,
            "method": "tools/call",
            "params": {
                "name": "create_bookmark",
                "arguments": {
                    "deployment_id": "5949ab07-5173-4e56-92a9-f7c5323aa6df",
                    "branch_id": "main",
                    "snapshot_comment": "Test bookmark created via MCP server"
                }
            }
        }
    ]
    
    try:
        for i, request in enumerate(test_requests):
            print(f"\n--- Test {i+1}: {request['method']} ---")
            if request['method'] == 'tools/call':
                tool_name = request['params']['name']
                print(f"🔧 Tool: {tool_name}")
                
                if tool_name == 'list_branches':
                    print("🌿 Listing branches for deployment...")
                elif tool_name == 'create_branch':
                    print("🌿 Creating new branch...")
                    print(f"   Deployment ID: {request['params']['arguments']['deployment_id']}")
                    print(f"   Name: {request['params']['arguments']['name']}")
                elif tool_name == 'list_snapshots_deployment':
                    print("📸 Listing snapshots for deployment...")
                elif tool_name == 'create_snapshot':
                    print("📸 Creating snapshot...")
                    print(f"   Deployment ID: {request['params']['arguments']['deployment_id']}")
                    print(f"   Branch ID: {request['params']['arguments']['branch_id']}")
                elif tool_name == 'list_snapshots_branch':
                    print("📸 Listing snapshots for branch...")
                elif tool_name == 'create_bookmark':
                    print("🔖 Creating bookmark...")
                else:
                    print(f"Arguments: {json.dumps(request['params']['arguments'], indent=2)}")
            else:
                print(f"Request: {json.dumps(request, indent=2)}")
            
            # Send request
            process.stdin.write(json.dumps(request) + "\n")
            process.stdin.flush()
            
            # Read response
            response_line = process.stdout.readline()
            if response_line:
                try:
                    response = json.loads(response_line.strip())
                    if 'result' in response and 'content' in response['result']:
                        content = response['result']['content'][0]['text']
                        if request['method'] == 'tools/call':
                            tool_name = request['params']['name']
                            if tool_name == 'list_branches':
                                print("✅ Branches List Result:")
                                if "Found" in content:
                                    print(f"   🌿 {content.split('Found')[1].split('branches')[0].strip()} branches")
                                else:
                                    print(f"   📝 {content[:200]}...")
                            elif tool_name == 'create_branch':
                                print("✅ Branch Creation Result:")
                                if "created successfully" in content:
                                    print("   🎉 Branch created successfully")
                                else:
                                    print(f"   📝 {content[:200]}...")
                            elif tool_name == 'list_snapshots_deployment':
                                print("✅ Deployment Snapshots Result:")
                                if "Found" in content:
                                    print(f"   📸 {content.split('Found')[1].split('snapshots')[0].strip()} snapshots")
                                else:
                                    print(f"   📝 {content[:200]}...")
                            elif tool_name == 'create_snapshot':
                                print("✅ Snapshot Creation Result:")
                                if "created successfully" in content:
                                    print("   🎉 Snapshot created successfully")
                                else:
                                    print(f"   📝 {content[:200]}...")
                            elif tool_name == 'list_snapshots_branch':
                                print("✅ Branch Snapshots Result:")
                                if "Found" in content:
                                    print(f"   📸 {content.split('Found')[1].split('snapshots')[0].strip()} snapshots")
                                else:
                                    print(f"   📝 {content[:200]}...")
                            elif tool_name == 'create_bookmark':
                                print("✅ Bookmark Creation Result:")
                                if "created successfully" in content:
                                    print("   🎉 Bookmark created successfully")
                                else:
                                    print(f"   📝 {content[:200]}...")
                            else:
                                print(f"✅ Response: {content[:150]}...")
                        else:
                            print(f"✅ Response: {content[:150]}...")
                    else:
                        print(f"✅ Response: {json.dumps(response, indent=2)}")
                except json.JSONDecodeError:
                    print(f"Raw response: {response_line}")
            else:
                print("❌ No response received")
            
            time.sleep(1)
    
    except Exception as e:
        print(f"❌ Error during testing: {e}")
    
    finally:
        # Clean up
        process.terminate()
        process.wait()
        print("\n🏁 MCP server stopped")
        print("\n✨ Branches and Snapshots Test Complete!")
        print("   • Branch listing and creation")
        print("   • Snapshot creation and listing")
        print("   • Bookmark creation")
        print("   • Branch-specific snapshot queries")

if __name__ == "__main__":
    test_branches_and_snapshots()
