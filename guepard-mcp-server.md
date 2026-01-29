# Guepard MCP Server Specification (v1 Configuration)

## Overview

The Guepard MCP Server v1 is a streamlined Model Context Protocol (MCP) server that provides AI agents and users with essential access to the Guepard database management platform. The v1 configuration focuses on core deployment management, compute operations, and basic database lifecycle management.

## Quick Start

### Docker Usage (Recommended)

```bash
# Pull the latest image
docker pull mghassen/guepard-mcp-server:1.4.0

# Run with your access token
docker run --rm -i -e ACCESS_TOKEN="your_guepard_token" mghassen/guepard-mcp-server:1.4.0
```

### Cursor Integration

Add to your `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "guepard": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-e", "ACCESS_TOKEN=your_guepard_token", "mghassen/guepard-mcp-server:1.4.0"],
      "env": {}
    }
  }
}
```

## Configuration

### Environment Variables

**Required:**
- `ACCESS_TOKEN`: Your Guepard platform access token

**Optional:**
- `GUEPARD_API_URL`: API base URL (default: https://api.guepard.run)
- `GUEPARD_AUTH_API`: Auth API URL (default: https://auth.guepard.run)
- `SUPABASE_ANON_KEY`: Supabase anonymous key for authentication

**Tool Configuration:**
- `GUEPARD_CONFIG`: Set to "v1" for essential deployment management tools
- `GUEPARD_ENABLED_MODULES`: Comma-separated list of modules to enable
- `GUEPARD_ENABLED_TOOLS`: Comma-separated list of specific tools to enable
- `GUEPARD_DISABLED_TOOLS`: Comma-separated list of tools to disable
- `GUEPARD_DISABLED_MODULES`: Comma-separated list of modules to disable

### v1 Configuration

The v1 configuration provides essential deployment management tools only:

**Enabled Modules:**
- `deployments` - Core deployment management
- `compute` - Compute resource management
- `performance` - Performance profile access
- `image_providers` - Database image providers
- `checkouts` - Branch and snapshot checkout operations
- `snapshots` - Snapshot management
- `branches` - Branch management
- `subscriptions` - Deployment subscription management

**Available Tools (25 total):**
- Connection testing
- Deployment lifecycle management
- Compute resource control
- Snapshot and branch operations
- Performance profile access
- Image provider information
- Subscription management

### Complete v1 Tool List

**Connection & Testing:**
- `test_connection` - Test API connectivity

**Deployments:**
- `list_deployments` - List all deployments
- `get_deployment` - Get deployment details
- `create_deployment` - Create new deployment

**Compute Management:**
- `get_compute` - Get compute status
- `start_compute` - Start compute resources
- `stop_compute` - Stop compute resources

**Snapshots:**
- `list_snapshots_deployment` - List deployment snapshots
- `list_snapshots_branch` - List branch snapshots
- `create_snapshot` - Create new snapshot

**Branches:**
- `list_branches` - List deployment branches
- `create_branch_from_snapshot` - Create branch from snapshot

**Checkouts:**
- `checkout_branch` - Checkout to branch
- `checkout_snapshot` - Checkout to snapshot

**Performance:**
- `list_performance_profiles` - List available profiles

**Image Providers:**
- `list_image_providers` - List database providers

**Subscriptions:**
- `subscribe_deployment` - Subscribe to notifications
- `unsubscribe_deployment` - Unsubscribe from notifications
- `list_subscriptions` - List all subscriptions
- `manage_subscriptions` - Manage subscription settings

## Available Tools (v1 Configuration)

### 🔗 Connection Testing

#### `test_connection`
Test connection to Guepard API.

**Parameters:**
- `random_string` (required): Dummy parameter for no-parameter tools

**Example Usage:**
```bash
# Test connection
docker run --rm -i -e ACCESS_TOKEN="your_token" mghassen/guepard-mcp-server:1.4.0
# In Cursor: "Test my Guepard connection"
```

### 🚀 Deployments Module (`deployments`)

#### `list_deployments`
Get all deployments for the authenticated user.

**Parameters:**
- `status` (optional): Filter by status ("active", "pending", "failed", "terminated")
- `limit` (optional): Limit number of results (default: 100)

#### `create_deployment`
Create a new database deployment.

**Parameters:**
- `repository_name` (required): Repository name
- `performance_profile_id` (optional): Performance profile ID
- `database_provider` (optional): Database provider ("PostgreSQL", "mysql", "mongodb")
- `database_version` (optional): Database version
- `name` (optional): Deployment name
- `auto_subscribe` (optional): Automatically subscribe to deployment (default: true)

#### `get_deployment`
Get detailed information about a specific deployment.

**Parameters:**
- `deployment_id` (optional): Deployment ID
- `repository_name` (optional): Repository name to find deployment
- `latest` (optional): Get the latest deployment
- `auto_subscribe` (optional): Automatically subscribe to deployment (default: true)

#### `update_deployment`
Update deployment settings.

**Parameters:**
- `deployment_id` (required): Deployment ID
- `name` (optional): New deployment name
- `performance_profile_id` (optional): New performance profile ID

#### `delete_deployment`
Delete a deployment.

**Parameters:**
- `deployment_id` (required): Deployment ID

### 🌿 Branches Module (`branches`)

#### `list_branches`
Get all branches for a deployment.

**Parameters:**
- `deployment_id` (required): Deployment ID

#### `create_branch_from_snapshot`
Create a new branch from a specific snapshot.

**Parameters:**
- `deployment_id` (required): Deployment ID
- `branch_id` (required): Branch ID (clone ID)
- `snapshot_id` (required): Snapshot ID
- `branch_name` (required): Branch name
- `is_ephemeral` (optional): Create ephemeral branch (default: false)

#### `update_branch`
Update branch settings.

**Parameters:**
- `deployment_id` (required): Deployment ID
- `branch_id` (required): Branch ID
- `branch_name` (optional): New branch name
- `is_ephemeral` (optional): Ephemeral status

### 📸 Snapshots Module (`snapshots`)

#### `list_snapshots_deployment`
Get all snapshots for a deployment.

**Parameters:**
- `deployment_id` (required): Deployment ID

#### `list_snapshots_branch`
Get all snapshots for a specific branch.

**Parameters:**
- `deployment_id` (required): Deployment ID
- `branch_id` (required): Branch ID

#### `create_snapshot`
Create a new snapshot of the current branch state.

**Parameters:**
- `deployment_id` (required): Deployment ID
- `branch_id` (required): Branch ID
- `snapshot_comment` (required): Snapshot comment describing the snapshot

### 🔄 Checkouts Module (`checkouts`)

#### `checkout_branch`
Checkout to a specific branch with snapshot.

**Parameters:**
- `deployment_id` (required): Deployment ID
- `branch_id` (required): Branch ID
- `snapshot_id` (required): Snapshot ID to checkout to

#### `checkout_snapshot`
Get a deployment, randomly select one of its branches, randomly select one of its snapshots, then checkout to that snapshot.

**Parameters:**
- `deployment_id` (required): Deployment ID
- `checkout` (optional): Whether to perform checkout (default: true)
- `discard_changes` (optional): Whether to discard changes (default: "true")
- `ephemeral` (optional): Whether the checkout is ephemeral (default: true)
- `performance_profile_name` (optional): Performance profile name (default: "querying")

### 💻 Compute Module (`compute`)

#### `get_compute`
Get compute status for a deployment.

**Parameters:**
- `deployment_id` (required): Deployment ID

#### `start_compute`
Start compute resources for a deployment.

**Parameters:**
- `deployment_id` (required): Deployment ID
- `auto_subscribe` (optional): Automatically subscribe to deployment (default: false)

#### `stop_compute`
Stop compute resources for a deployment.

**Parameters:**
- `deployment_id` (required): Deployment ID

### ⚡ Performance Module (`performance`)

#### `list_performance_profiles`
Get all available performance profiles.

**Parameters:**
- `random_string` (required): Dummy parameter for no-parameter tools

### 🖼️ Image Providers Module (`image_providers`)

#### `list_image_providers`
Get all available database image providers.

**Parameters:**
- `random_string` (required): Dummy parameter for no-parameter tools

**Example Usage:**
```bash
# In Cursor: "List all available database image providers"
```

### 📡 Subscriptions Module (`subscriptions`)

#### `subscribe_deployment`
Subscribe to deployment notifications.

**Parameters:**
- `deployment_id` (required): Deployment ID to subscribe to

#### `unsubscribe_deployment`
Unsubscribe from deployment notifications.

**Parameters:**
- `deployment_id` (required): Deployment ID to unsubscribe from

#### `list_subscriptions`
List all deployment subscriptions with optional status information.

**Parameters:**
- `include_status` (optional): Include deployment status information (default: false)
- `include_compute_status` (optional): Include compute status information (requires include_status=true) (default: false)

#### `manage_subscriptions`
Manage automatic subscription settings and view current subscriptions.

**Parameters:**
- `action` (required): Action to perform ("status", "enable", "disable", "configure", "clear_all", "unsubscribe")
- `enabled` (optional): Enable/disable auto-subscription
- `tool_name` (optional): Tool name for configure/unsubscribe actions
- `deployment_id` (optional): Deployment ID for unsubscribe action

#### `test_connection`
Test connection to Guepard API.

**Parameters:**
- `random_string` (required): Dummy parameter for no-parameter tools

## Usage Examples

### Basic Deployment Management

```bash
# Test connection
docker run --rm -i -e ACCESS_TOKEN="your_token" mghassen/guepard-mcp-server:1.4.0

# List all deployments
# In Cursor: "List all my deployments"

# Create a new deployment
# In Cursor: "Create a new PostgreSQL deployment named 'my-db'"

# Start compute for a deployment
# In Cursor: "Start compute for deployment xyz"
```

### Advanced Operations

```bash
# Create branch from snapshot
# In Cursor: "Create a new branch 'feature-branch' from snapshot abc123"

# Create snapshot
# In Cursor: "Create a snapshot with comment 'Before major changes'"

# Checkout to specific snapshot
# In Cursor: "Checkout to snapshot xyz789"
```

### Monitoring and Observability

```bash
# Get deployment status
# In Cursor: "Get status for deployment abc123"

# List subscriptions
# In Cursor: "Show all my deployment subscriptions"

# Subscribe to deployment notifications
# In Cursor: "Subscribe to notifications for deployment xyz"
```

## Error Handling

The MCP server provides structured error responses with:
- Clear error messages
- HTTP status codes
- Detailed error information when available

Example error response:
```json
{
  "error": "Deployment not found",
  "message": "No deployment found with ID: abc123",
  "status_code": 404
}
```

## Security Considerations

1. **Access Tokens**: Store access tokens securely and never commit them to version control
2. **Environment Variables**: Use environment variables for sensitive configuration
3. **Network Security**: Ensure secure connections to Guepard APIs
4. **Tool Restrictions**: Use predefined configurations to limit tool access in production environments

## Troubleshooting

### Common Issues

1. **"ACCESS_TOKEN is required"**
   - Ensure ACCESS_TOKEN environment variable is set
   - Verify token is valid and not expired

2. **"No tools available in Cursor"**
   - Restart Cursor after updating mcp.json
   - Check Docker is running
   - Verify image is pulled: `docker pull mghassen/guepard-mcp-server:1.4.0`

3. **Connection failures**
   - Test connection: Use `test_connection` tool
   - Check internet connectivity
   - Verify Guepard API endpoints are accessible

4. **Authentication errors**
   - Ensure SUPABASE_ANON_KEY is set for auth operations
   - Verify GUEPARD_AUTH_API is correct
   - Check token permissions

### Debug Mode

Enable debug logging:
```bash
docker run --rm -i -e ACCESS_TOKEN="your_token" -e DEBUG=true mghassen/guepard-mcp-server:1.4.0
```

## API Reference

### Base URLs
- **API**: https://api.guepard.run
- **Auth**: https://auth.guepard.run

### Authentication
- Bearer token authentication using ACCESS_TOKEN
- Supabase integration for user authentication

### Rate Limits
- Standard Guepard API rate limits apply
- Monitor usage through deployment metrics

## Support

- **Issues**: Report issues on GitHub
- **Documentation**: Check the main README.md
- **Guepard Platform**: Visit [guepard.run](https://guepard.run)

## Version Information

- **Current Version**: 1.4.0
- **Docker Image**: mghassen/guepard-mcp-server:1.4.0
- **Configuration**: v1 (essential deployment management tools only)
- **Architecture**: Multi-platform (linux/amd64, linux/arm64)
- **Available Tools**: 25 tools across 8 modules
- **Focus**: Core deployment lifecycle, compute management, and database operations

---

**Ready to use!** Pull the image and start managing your Guepard deployments with AI agents! 🎉
