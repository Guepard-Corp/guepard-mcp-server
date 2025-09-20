#!/usr/bin/env python3
"""
Auto-Subscription Demo for Guepard MCP Tools
Demonstrates how agents automatically subscribe to deployments when using tools
"""

import asyncio
import sys
import os
from unittest.mock import Mock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from guepard_mcp.deployments.enhanced_tools import (
    EnhancedCreateDeploymentTool,
    EnhancedGetDeploymentTool,
    SubscriptionManagementTool
)
from guepard_mcp.utils.base import GuepardAPIClient

class AutoSubscriptionDemo:
    """Demo class showing automatic subscription functionality"""
    
    def __init__(self):
        print("🚀 Auto-Subscription Demo for Guepard MCP Tools")
        print("=" * 60)
        
        # Create mock server for subscription tracking
        self.mock_server = Mock()
        self.mock_server.subscribed_deployments = set()
        self.mock_server.tools = {}
        self.mock_server.modules = {}
        self.mock_server.config = Mock()
        
        # Initialize client
        self.client = GuepardAPIClient()
        
        # Initialize enhanced tools
        self.create_tool = EnhancedCreateDeploymentTool(self.client, None, self.mock_server)
        self.get_tool = EnhancedGetDeploymentTool(self.client, None, self.mock_server)
        self.manage_tool = SubscriptionManagementTool(self.client, None, self.mock_server)

    async def demo_1_create_deployment_with_auto_subscription(self):
        """Demo 1: Create deployment with automatic subscription"""
        print("\n📦 DEMO 1: Creating Deployment with Auto-Subscription")
        print("-" * 50)
        
        try:
            # Create a deployment
            result = await self.create_tool.execute({
                "repository_name": "my-awesome-app",
                "name": "Production Database",
                "database_provider": "PostgreSQL",
                "auto_subscribe": True
            })
            
            print(f"Result: {result}")
            print(f"Subscriptions: {list(self.mock_server.subscribed_deployments)}")
            
            print("✅ Demo 1 completed - Deployment created and auto-subscribed!")
            return True
            
        except Exception as e:
            print(f"❌ Demo 1 failed: {e}")
            return False

    async def demo_2_get_deployment_with_auto_subscription(self):
        """Demo 2: Get deployment with automatic subscription"""
        print("\n🔍 DEMO 2: Getting Deployment with Auto-Subscription")
        print("-" * 50)
        
        try:
            # Get a deployment (this will also auto-subscribe)
            result = await self.get_tool.execute({
                "repository_name": "my-awesome-app",
                "auto_subscribe": True
            })
            
            print(f"Result: {result}")
            print(f"Subscriptions: {list(self.mock_server.subscribed_deployments)}")
            
            print("✅ Demo 2 completed - Deployment retrieved and auto-subscribed!")
            return True
            
        except Exception as e:
            print(f"❌ Demo 2 failed: {e}")
            return False

    async def demo_3_subscription_management(self):
        """Demo 3: Subscription management"""
        print("\n⚙️ DEMO 3: Subscription Management")
        print("-" * 50)
        
        try:
            # Check subscription status
            print("Checking subscription status...")
            status_result = await self.manage_tool.execute({"action": "status"})
            print(f"Status: {status_result}")
            
            # Disable auto-subscription for create_deployment
            print("\nDisabling auto-subscription for create_deployment...")
            config_result = await self.manage_tool.execute({
                "action": "configure",
                "tool_name": "create_deployment",
                "enabled": False
            })
            print(f"Config: {config_result}")
            
            # Try creating another deployment (should not auto-subscribe)
            print("\nCreating deployment with auto-subscription disabled...")
            create_result = await self.create_tool.execute({
                "repository_name": "another-app",
                "name": "Test Database"
            })
            print(f"Create result: {create_result}")
            print(f"Subscriptions: {list(self.mock_server.subscribed_deployments)}")
            
            # Re-enable auto-subscription
            print("\nRe-enabling auto-subscription...")
            enable_result = await self.manage_tool.execute({
                "action": "enable",
                "enabled": True
            })
            print(f"Enable: {enable_result}")
            
            print("✅ Demo 3 completed - Subscription management working!")
            return True
            
        except Exception as e:
            print(f"❌ Demo 3 failed: {e}")
            return False

    async def demo_4_agent_workflow_simulation(self):
        """Demo 4: Simulate agent workflow with automatic subscriptions"""
        print("\n🤖 DEMO 4: Agent Workflow Simulation")
        print("-" * 50)
        
        try:
            print("Simulating agent workflow...")
            print("1. Agent creates a deployment...")
            
            # Step 1: Create deployment
            create_result = await self.create_tool.execute({
                "repository_name": "ecommerce-backend",
                "name": "E-commerce Database",
                "database_provider": "PostgreSQL",
                "auto_subscribe": True
            })
            print(f"   Create result: {create_result}")
            print(f"   Subscriptions after create: {list(self.mock_server.subscribed_deployments)}")
            
            print("\n2. Agent gets deployment details...")
            
            # Step 2: Get deployment
            get_result = await self.get_tool.execute({
                "repository_name": "ecommerce-backend",
                "auto_subscribe": True
            })
            print(f"   Get result: {get_result}")
            print(f"   Subscriptions after get: {list(self.mock_server.subscribed_deployments)}")
            
            print("\n3. Agent checks subscription status...")
            
            # Step 3: Check subscriptions
            status_result = await self.manage_tool.execute({"action": "status"})
            print(f"   Status: {status_result}")
            
            print("\n4. Agent creates another deployment...")
            
            # Step 4: Create another deployment
            create2_result = await self.create_tool.execute({
                "repository_name": "ecommerce-frontend",
                "name": "Frontend Database",
                "database_provider": "PostgreSQL",
                "auto_subscribe": True
            })
            print(f"   Create 2 result: {create2_result}")
            print(f"   Final subscriptions: {list(self.mock_server.subscribed_deployments)}")
            
            print("✅ Demo 4 completed - Agent workflow with auto-subscriptions working!")
            return True
            
        except Exception as e:
            print(f"❌ Demo 4 failed: {e}")
            return False

    async def demo_5_subscription_control(self):
        """Demo 5: Advanced subscription control"""
        print("\n🎛️ DEMO 5: Advanced Subscription Control")
        print("-" * 50)
        
        try:
            print("Testing advanced subscription control...")
            
            # Clear all subscriptions
            print("\n1. Clearing all subscriptions...")
            clear_result = await self.manage_tool.execute({"action": "clear_all"})
            print(f"   Clear result: {clear_result}")
            print(f"   Subscriptions after clear: {list(self.mock_server.subscribed_deployments)}")
            
            # Create a deployment
            print("\n2. Creating deployment...")
            create_result = await self.create_tool.execute({
                "repository_name": "test-app",
                "name": "Test Database"
            })
            print(f"   Create result: {create_result}")
            print(f"   Subscriptions after create: {list(self.mock_server.subscribed_deployments)}")
            
            # Unsubscribe from specific deployment
            if self.mock_server.subscribed_deployments:
                deployment_id = list(self.mock_server.subscribed_deployments)[0]
                print(f"\n3. Unsubscribing from deployment {deployment_id}...")
                unsubscribe_result = await self.manage_tool.execute({
                    "action": "unsubscribe",
                    "deployment_id": deployment_id
                })
                print(f"   Unsubscribe result: {unsubscribe_result}")
                print(f"   Subscriptions after unsubscribe: {list(self.mock_server.subscribed_deployments)}")
            
            print("✅ Demo 5 completed - Advanced subscription control working!")
            return True
            
        except Exception as e:
            print(f"❌ Demo 5 failed: {e}")
            return False

    async def run_all_demos(self):
        """Run all demos"""
        print("🎯 Running All Auto-Subscription Demos")
        print("=" * 60)
        
        demos = [
            ("Create Deployment with Auto-Subscription", self.demo_1_create_deployment_with_auto_subscription),
            ("Get Deployment with Auto-Subscription", self.demo_2_get_deployment_with_auto_subscription),
            ("Subscription Management", self.demo_3_subscription_management),
            ("Agent Workflow Simulation", self.demo_4_agent_workflow_simulation),
            ("Advanced Subscription Control", self.demo_5_subscription_control)
        ]
        
        passed = 0
        total = len(demos)
        
        for demo_name, demo_func in demos:
            try:
                if await demo_func():
                    passed += 1
            except Exception as e:
                print(f"❌ {demo_name} failed with exception: {e}")
        
        print(f"\n📊 DEMO RESULTS: {passed}/{total} demos passed")
        
        if passed == total:
            print("🎉 All auto-subscription demos passed!")
        else:
            print("⚠️  Some demos failed")
        
        return passed == total

async def main():
    """Main demo runner"""
    demo = AutoSubscriptionDemo()
    success = await demo.run_all_demos()
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
