# Auto-Subscription Guide for Guepard MCP Tools

This guide explains how to set up and use automatic subscription functionality in your Guepard MCP tools.

## 🎯 **What is Auto-Subscription?**

Auto-subscription automatically subscribes agents to deployment notifications when they use certain tools. This means when an agent creates a deployment or starts compute, it will automatically be subscribed to monitor that deployment.

## ✅ **Current Auto-Subscription Support**

### **Already Working:**
- `create_deployment` - Auto-subscribes when creating deployments
- `get_deployment` - Auto-subscribes when retrieving deployment details  
- `start_compute` - Auto-subscribes when starting compute resources

### **Enhanced Tools Available:**
- `EnhancedCreateDeploymentTool` - Advanced auto-subscription with configuration
- `EnhancedGetDeploymentTool` - Advanced auto-subscription with configuration
- `SubscriptionManagementTool` - Manage subscription settings

## 🚀 **How to Use Auto-Subscription**

### **1. Basic Usage (Already Working)**

When you use these tools, they automatically subscribe:

```python
# Create deployment - automatically subscribes
result = await create_deployment_tool.execute({
    "repository_name": "my-app",
    "name": "Production DB"
})
# Result includes: "📌 Automatically subscribed to deployment deployment-123"

# Get deployment - automatically subscribes  
result = await get_deployment_tool.execute({
    "deployment_id": "deployment-123"
})
# Result includes: "📌 Automatically subscribed to deployment deployment-123"

# Start compute - automatically subscribes
result = await start_compute_tool.execute({
    "deployment_id": "deployment-123"
})
# Result includes: "📌 Automatically subscribed to deployment deployment-123"
```

### **2. Enhanced Usage with Configuration**

```python
# Create deployment with subscription control
result = await enhanced_create_tool.execute({
    "repository_name": "my-app",
    "name": "Production DB",
    "auto_subscribe": True  # Explicitly enable (default)
})

# Get deployment with subscription control
result = await enhanced_get_tool.execute({
    "deployment_id": "deployment-123",
    "auto_subscribe": False  # Disable for this call
})
```

### **3. Subscription Management**

```python
# Check subscription status
status = await manage_subscriptions_tool.execute({
    "action": "status"
})

# Disable auto-subscription globally
await manage_subscriptions_tool.execute({
    "action": "disable"
})

# Configure specific tool
await manage_subscriptions_tool.execute({
    "action": "configure",
    "tool_name": "create_deployment",
    "enabled": False
})

# Unsubscribe from specific deployment
await manage_subscriptions_tool.execute({
    "action": "unsubscribe",
    "deployment_id": "deployment-123"
})

# Clear all subscriptions
await manage_subscriptions_tool.execute({
    "action": "clear_all"
})
```

## ⚙️ **Configuration Options**

### **Environment Variables**

Add to your `.env` file:

```bash
# Enable/disable auto-subscription globally
GUEPARD_AUTO_SUBSCRIBE=true

# Configure which tools auto-subscribe
GUEPARD_AUTO_SUBSCRIBE_TOOLS=create_deployment,get_deployment,start_compute,checkout_branch
```

### **Programmatic Configuration**

```python
# Configure subscription manager
subscription_manager.configure_auto_subscription(
    enabled=True,
    actions={
        'create_deployment': True,
        'get_deployment': True,
        'start_compute': True,
        'checkout_branch': False,
        'create_snapshot': True
    }
)
```

## 🔧 **Integration with Your Agent**

### **1. Update Your Server Configuration**

In your `server.py`, ensure the subscription module is enabled:

```python
# In server initialization
module_classes = {
    "subscriptions": SubscriptionsModule,
    "deployments": DeploymentsModule,  # Uses auto-subscription
    "compute": ComputeModule,          # Uses auto-subscription
    # ... other modules
}
```

### **2. Agent Workflow Example**

```python
async def agent_create_and_monitor_deployment():
    """Example agent workflow with auto-subscription"""
    
    # 1. Create deployment (auto-subscribes)
    create_result = await create_deployment_tool.execute({
        "repository_name": "my-app",
        "name": "Production Database"
    })
    
    # 2. Start compute (auto-subscribes)
    start_result = await start_compute_tool.execute({
        "deployment_id": "deployment-123"
    })
    
    # 3. Check what we're subscribed to
    subscriptions = await list_subscriptions_tool.execute({
        "include_status": True
    })
    
    # 4. Monitor deployment status
    status = await get_deployment_tool.execute({
        "deployment_id": "deployment-123"
    })
    
    return {
        "deployment_created": create_result,
        "compute_started": start_result,
        "subscriptions": subscriptions,
        "status": status
    }
```

## 📊 **Monitoring Subscriptions**

### **List Current Subscriptions**

```python
# Basic list
subscriptions = await list_subscriptions_tool.execute({})

# With status information
subscriptions_with_status = await list_subscriptions_tool.execute({
    "include_status": True,
    "include_compute_status": True
})
```

### **Subscription Status**

```python
# Get detailed subscription info
info = await manage_subscriptions_tool.execute({
    "action": "status"
})
# Returns: enabled status, subscription count, deployment IDs, tool configurations
```

## 🎮 **Demo and Testing**

Run the demo to see auto-subscription in action:

```bash
cd /Users/mghassen/Workspace/GPRD/guepard-mcp-server
source venv/bin/activate
python3 demo_auto_subscription.py
```

## 🔄 **Workflow Examples**

### **Development Workflow**

```python
# 1. Create development deployment
dev_result = await create_deployment_tool.execute({
    "repository_name": "my-app-dev",
    "name": "Development Database"
})
# Auto-subscribes to dev deployment

# 2. Create production deployment  
prod_result = await create_deployment_tool.execute({
    "repository_name": "my-app-prod", 
    "name": "Production Database"
})
# Auto-subscribes to prod deployment

# 3. Check all subscriptions
all_subscriptions = await list_subscriptions_tool.execute({
    "include_status": True
})
# Shows both dev and prod deployments
```

### **Monitoring Workflow**

```python
# 1. Get deployment details (auto-subscribes)
deployment = await get_deployment_tool.execute({
    "repository_name": "critical-app"
})

# 2. Start compute (auto-subscribes)
compute = await start_compute_tool.execute({
    "deployment_id": "deployment-456"
})

# 3. Monitor all subscribed deployments
monitoring = await list_subscriptions_tool.execute({
    "include_status": True,
    "include_compute_status": True
})
```

## 🛠️ **Troubleshooting**

### **Auto-Subscription Not Working**

1. Check if subscription module is enabled
2. Verify server reference is passed to tools
3. Check subscription configuration
4. Look for error messages in logs

### **Too Many Subscriptions**

1. Use `manage_subscriptions` tool to clear old subscriptions
2. Configure specific tools to not auto-subscribe
3. Regularly clean up unused subscriptions

### **Subscription Management**

1. Use `list_subscriptions` to see current subscriptions
2. Use `unsubscribe_deployment` to remove specific subscriptions
3. Use `clear_all` to remove all subscriptions

## 📈 **Benefits**

- **Automatic Monitoring**: Agents automatically monitor deployments they create
- **No Manual Setup**: No need to remember to subscribe after creating deployments
- **Configurable**: Can be enabled/disabled per tool or globally
- **Transparent**: Clear feedback when subscriptions are created
- **Manageable**: Easy to view and manage all subscriptions

This auto-subscription system makes it much easier for agents to monitor the deployments they create and manage, providing better visibility and control over your Guepard infrastructure.
