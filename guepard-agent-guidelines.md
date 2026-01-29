# Guepard MCP Server - AI Agent Guidelines

## Overview

Streamlined guidelines for AI agents using the Guepard MCP Server v1. Focus on essential workflows without overwhelming users with questions.

## Core Workflow

### 🔗 Setup (Do Automatically)
```bash
# Always start with connection test
test_connection()

# Subscribe to deployment for monitoring
subscribe_deployment(deployment_id="your_deployment_id")
```

### 📊 Database Changes (Ask Only When Critical)

**Only ask for snapshots when:**
- User mentions "important changes" or "production data"
- Making schema modifications
- User explicitly asks for safety measures

**Create snapshot automatically:**
```bash
create_snapshot(
    deployment_id="your_deployment_id",
    branch_id="your_branch_id", 
    snapshot_comment="Before [brief description]"
)
```

### 🌿 Branches (Ask Only for Major Work)

**Only ask about branches when:**
- User mentions "experimenting" or "testing"
- Multiple related changes planned
- User asks about "safe development"

### 💻 Compute Management (Handle Automatically)

**Check and manage compute automatically:**
```bash
# Check status
get_compute(deployment_id="your_deployment_id")

# Start if stopped and user needs to work
start_compute(deployment_id="your_deployment_id")

# Stop after operations to save costs (ask briefly)
stop_compute(deployment_id="your_deployment_id")
```

### 🔄 Checkout Operations

**When switching between snapshots or branches:**
```bash
# Checkout to specific snapshot
checkout_snapshot(
    deployment_id="your_deployment_id",
    snapshot_id="target_snapshot_id"
)

# Or checkout to branch
checkout_branch(
    deployment_id="your_deployment_id",
    branch_id="target_branch_id",
    snapshot_id="target_snapshot_id"
)
```

## Specific Scenarios

### 📝 Database Writing Operations

**For regular database writes:**
1. **Do automatically**: Create snapshot with comment "Before write operation"
2. **Perform the write**
3. **Inform user**: "✅ Write completed. Snapshot created for safety."

**Only ask if user mentions:**
- "This is important data"
- "Production database"
- "Critical changes"

### 🏗️ Schema Updates

**For schema changes:**
1. **Do automatically**: Create snapshot "Before schema changes"
2. **Ask only**: "Should I create a development branch for these schema changes?"
3. **Apply changes**
4. **Inform**: "✅ Schema updated. Snapshot created."

### 🚀 New Deployment Creation

**Streamlined process:**
1. **Show options**: List performance profiles and image providers
2. **Ask**: "What database type and name?" (one question)
3. **Create deployment**
4. **Subscribe automatically**

### 📈 Monitoring (Do Silently)

**Background monitoring:**
- Check deployment status automatically
- Report only if issues found
- Manage compute resources silently

## User Interaction Patterns

### 🤔 Ask Only When:

- **User mentions "experimenting" or "testing"** → Ask about development branch
- **User says "important" or "production"** → Ask about extra snapshots
- **Multiple related changes** → Ask about development branch
- **Compute costs concern** → Ask about stopping compute

### 📋 Inform User About:

- **✅ Completed operations** with brief status
- **⚠️ Issues found** during monitoring
- **💰 Compute status** only if stopped/expensive
- **📸 Snapshots created** automatically

### 🚫 Don't Ask About:

- Regular snapshots (do automatically)
- Basic compute management (handle silently)
- Standard monitoring (do in background)
- Routine deployment operations

## Error Handling

### 🚨 When Errors Occur:

1. **Test connection** to verify API connectivity
2. **Check deployment status** to ensure it's active
3. **Verify compute status** - may need to start compute
4. **Check subscription status** - may need to resubscribe
5. **Report error clearly** with suggested next steps

### 🔧 Common Error Scenarios:

**"Deployment not found"**
- List all deployments to find correct ID
- Ask user to confirm deployment name/ID

**"Compute not running"**
- Check compute status
- Ask if user wants to start compute

**"Connection failed"**
- Test connection
- Check ACCESS_TOKEN validity
- Verify network connectivity

## Best Practices Summary

### ✅ Do Automatically:
- Test connection and subscribe to deployments
- Create snapshots for database writes and schema changes
- Manage compute resources (start when needed, stop to save costs)
- Monitor deployment status in background
- Report completion with brief status updates

### ❌ Don't Ask About:
- Regular snapshots (just create them)
- Basic compute management (handle silently)
- Standard monitoring (do in background)
- Routine operations

### 🤔 Ask Only When:
- User mentions "experimenting/testing" → development branch
- User says "important/production" → extra safety measures
- Multiple related changes → development branch
- Compute cost concerns → stopping resources

## Example Conversation Flow

```
User: "I want to add a new table to my database"

Agent: "I'll add the new table. Let me create a snapshot first for safety, then I'll proceed with the schema changes."

[Agent performs: test_connection(), create_snapshot(), applies schema changes]

Agent: "✅ New table added successfully. Snapshot created before changes for safety."
```

**Only ask about branches if user mentions experimenting:**
```
User: "I want to experiment with different table structures"

Agent: "I'll help you experiment with table structures. Should I create a development branch for this work so you can test safely?"

[If yes, create branch and proceed]
```

## Available Tools Reference

### Connection & Testing
- `test_connection()` - Always start here

### Deployments  
- `list_deployments()` - See all deployments
- `get_deployment(deployment_id)` - Get specific deployment details
- `create_deployment(repository_name, ...)` - Create new deployment

### Compute Management
- `get_compute(deployment_id)` - Check compute status
- `start_compute(deployment_id)` - Start compute resources  
- `stop_compute(deployment_id)` - Stop compute resources

### Snapshots
- `list_snapshots_deployment(deployment_id)` - List deployment snapshots
- `list_snapshots_branch(deployment_id, branch_id)` - List branch snapshots
- `create_snapshot(deployment_id, branch_id, snapshot_comment)` - Create snapshot

### Branches
- `list_branches(deployment_id)` - List deployment branches
- `create_branch_from_snapshot(deployment_id, branch_id, snapshot_id, branch_name)` - Create branch

### Checkouts
- `checkout_branch(deployment_id, branch_id, snapshot_id)` - Switch to branch
- `checkout_snapshot(deployment_id, snapshot_id)` - Switch to snapshot

### Performance & Providers
- `list_performance_profiles()` - See available performance options
- `list_image_providers()` - See available database providers

### Subscriptions
- `subscribe_deployment(deployment_id)` - Subscribe to deployment
- `unsubscribe_deployment(deployment_id)` - Unsubscribe from deployment
- `list_subscriptions()` - See all subscriptions
- `manage_subscriptions(action, ...)` - Manage subscription settings

---

**Remember**: Always prioritize user safety, ask before making changes, and maintain proper database management workflows!
