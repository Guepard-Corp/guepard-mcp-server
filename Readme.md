# Guepard MCP Server - Complete API Implementation

A comprehensive Model Context Protocol (MCP) server for the Guepard database management platform, providing access to all Guepard APIs through organized modules.

## 🚀 Quick Start

### Using Docker Hub Image

```bash
# Pull the image
docker pull mghassen/guepard-custom-mcp:latest

# Run the MCP server
docker run --rm -i -e ACCESS_TOKEN="your_guepard_token" mghassen/guepard-custom-mcp:latest
```

### Using with Cursor

Add this to your Cursor MCP settings (`~/.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "guepard": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-e", "ACCESS_TOKEN=your_guepard_token", "mghassen/guepard-custom-mcp:latest"],
      "env": {}
    }
  }
}
```

### Local Development

```bash
# Clone the repository
git clone <repository-url>
cd guepard-mcp-server

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export ACCESS_TOKEN="your_guepard_token"
export GUEPARD_API_URL="https://api.guepard.run"
export GUEPARD_AUTH_API="https://auth.guepard.run"
export SUPABASE_ANON_KEY="your_supabase_key"

# Run the server
python main.py
```

## 🛠️ Available Tools

The MCP server provides comprehensive access to all Guepard APIs through organized modules:

### 🔐 Authentication
- **`login_supabase`** - Login with Supabase authentication
- **`refresh_token_supabase`** - Refresh access token with Supabase
- **`logout_supabase`** - Logout and invalidate tokens with Supabase

### 🚀 Deployments
- **`list_deployments`** - Get all deployments (with optional filtering)
- **`create_deployment`** - Create a new database deployment
- **`get_deployment`** - Get deployment details
- **`update_deployment`** - Update deployment
- **`delete_deployment`** - Delete deployment

### 🌿 Branches
- **`list_branches`** - Get branches for deployment
- **`create_branch`** - Create a new branch from snapshot
- **`get_branch`** - Get branch details
- **`update_branch`** - Update branch
- **`checkout_branch`** - Checkout to a specific snapshot

### 📸 Snapshots
- **`create_snapshot`** - Create a snapshot
- **`list_snapshots_deployment`** - Get snapshots for deployment
- **`list_snapshots_branch`** - Get snapshots for branch
- **`create_bookmark`** - Create a bookmark

### 🖥️ Nodes
- **`list_nodes`** - Get all nodes
- **`create_node`** - Create a new node
- **`get_node`** - Get node details

### ⚡ Performance Profiles
- **`list_performance_profiles`** - Get all performance profiles
- **`create_performance_profile`** - Create performance profile
- **`update_performance_profile`** - Update performance profile
- **`get_performance_profiles`** - Get available performance profile defaults

### 💻 Compute
- **`get_compute_status`** - Get compute status
- **`start_compute`** - Start compute for a deployment
- **`stop_compute`** - Stop compute for a deployment
- **`get_deployment_status`** - Get deployment status
- **`get_deployment_logs`** - Get deployment logs
- **`get_deployment_metrics`** - Get deployment metrics

### 👥 Database Users
- **`list_database_users`** - Get database users for deployment
- **`create_database_user`** - Create database user
- **`update_database_user`** - Update database user
- **`delete_database_user`** - Delete database user
- **`grant_privileges`** - Grant privileges to database user
- **`revoke_privileges`** - Revoke privileges from database user
- **`list_user_privileges`** - List privileges for database user

### 🔑 Tokens
- **`list_tokens`** - Get all tokens
- **`generate_token`** - Generate new token
- **`revoke_token`** - Revoke token

### 📡 Notifications & Utilities
- **`subscribe_deployment`** - Subscribe to deployment notifications
- **`unsubscribe_deployment`** - Unsubscribe from deployment notifications
- **`list_subscriptions`** - List all deployment subscriptions
- **`test_connection`** - Test connection to Guepard API
- **`list_configurations`** - List available predefined configurations
- **`get_configuration`** - Get current server configuration

## 📋 Prerequisites

- Docker installed and running (for Docker usage)
- Python 3.12+ (for local development)
- Valid Guepard access token
- Cursor IDE (for MCP integration)

## 🔧 Configuration

### Environment Variables

**Required:**
- **`ACCESS_TOKEN`**: Your Guepard platform access token

**Optional:**
- **`GUEPARD_API_URL`**: Guepard API base URL (defaults to https://api.guepard.run)
- **`GUEPARD_AUTH_API`**: Guepard auth API URL (defaults to https://auth.guepard.run)
- **`SUPABASE_ANON_KEY`**: Supabase anonymous key for authentication
- **`POSTGRES16_PROFILE_ID`**: Performance profile ID for PostgreSQL 16
- **`POSTGRES17_PROFILE_ID`**: Performance profile ID for PostgreSQL 17

**Tool Activation (New!):**
- **`GUEPARD_CONFIG`**: Use predefined configuration (`minimal`, `read_only`, `production`, `development`, `monitoring`)
- **`GUEPARD_ENABLED_MODULES`**: Comma-separated list of modules to enable
- **`GUEPARD_ENABLED_TOOLS`**: Comma-separated list of specific tools to enable
- **`GUEPARD_DISABLED_TOOLS`**: Comma-separated list of tools to disable
- **`GUEPARD_DISABLED_MODULES`**: Comma-separated list of modules to disable

### Example Usage

```bash
# Test the connection (all tools enabled)
docker run --rm -i -e ACCESS_TOKEN="your_token" mghassen/guepard-custom-mcp:latest

# Use predefined configuration (minimal tools)
docker run --rm -i -e ACCESS_TOKEN="your_token" -e GUEPARD_CONFIG="minimal" mghassen/guepard-custom-mcp:latest

# Use predefined configuration (read-only)
docker run --rm -i -e ACCESS_TOKEN="your_token" -e GUEPARD_CONFIG="read_only" mghassen/guepard-custom-mcp:latest

# Use predefined configuration (production-safe)
docker run --rm -i -e ACCESS_TOKEN="your_token" -e GUEPARD_CONFIG="production" mghassen/guepard-custom-mcp:latest

# Custom configuration (specific tools only)
docker run --rm -i -e ACCESS_TOKEN="your_token" -e GUEPARD_ENABLED_TOOLS="test_connection,list_deployments,get_deployment,start_compute,stop_compute" mghassen/guepard-custom-mcp:latest

# In Cursor, ask:
# "Test my Guepard connection"
# "Get all my deployments"
# "Create a new deployment with PostgreSQL 17"
# "Start compute for deployment xyz"
# "Create a database user with specific privileges"
# "List available configurations"
# "Get current configuration"
```

## ⚙️ Tool Activation & Configuration

The Guepard MCP Server now supports selective activation of tools and modules, allowing you to build custom configurations for different use cases.

### 🚀 Predefined Configurations

| Configuration | Description | Use Case |
|---------------|-------------|----------|
| `minimal` | Minimal deployment management only | Basic operations |
| `read_only` | Read-only access to deployments and monitoring | Monitoring dashboards |
| `production` | Production environment without dangerous operations | Production deployments |
| `development` | Full development environment with all tools | Development work |
| `monitoring` | Monitoring and observability only | System monitoring |

### 🛠️ Custom Configuration Examples

```bash
# Enable only specific modules
docker run --rm -i \
  -e ACCESS_TOKEN="your_token" \
  -e GUEPARD_ENABLED_MODULES="deployments,compute" \
  mghassen/guepard-custom-mcp:latest

# Enable only specific tools
docker run --rm -i \
  -e ACCESS_TOKEN="your_token" \
  -e GUEPARD_ENABLED_TOOLS="test_connection,list_deployments,get_deployment,start_compute,stop_compute" \
  mghassen/guepard-custom-mcp:latest

# Disable dangerous operations
docker run --rm -i \
  -e ACCESS_TOKEN="your_token" \
  -e GUEPARD_DISABLED_TOOLS="delete_deployment,delete_database_user,revoke_token" \
  mghassen/guepard-custom-mcp:latest
```

### 🔍 Configuration Verification

Use the built-in tools to verify your configuration:

- **`list_configurations`** - List all available predefined configurations
- **`get_configuration`** - Get current server configuration details

## 🏗️ Project Structure

```
guepard-mcp-server/
├── src/
│   └── guepard_mcp/
│       ├── auth/           # Authentication tools
│       ├── deployments/   # Deployment management
│       ├── branches/       # Branch management
│       ├── snapshots/      # Snapshot management
│       ├── nodes/          # Node management
│       ├── performance/    # Performance profiles
│       ├── compute/        # Compute management
│       ├── users/          # Database users
│       ├── tokens/         # Token management
│       ├── utils/          # Base classes and utilities
│       └── server.py       # Main server implementation
├── main.py                 # Entry point
├── requirements.txt        # Python dependencies
├── Dockerfile             # Docker configuration
└── README.md              # This file
```

## 🐳 Docker Images

- **`mghassen/guepard-custom-mcp:latest`** - Latest version
- **`mghassen/guepard-custom-mcp:2.0.0`** - Stable version 2.0.0

## 🔍 Troubleshooting

### Common Issues

1. **"ACCESS_TOKEN is required"**
   - Make sure you've set the ACCESS_TOKEN environment variable
   - Verify your token is valid

2. **"No tools available in Cursor"**
   - Restart Cursor after updating mcp.json
   - Check that Docker is running
   - Verify the image is pulled: `docker pull mghassen/guepard-custom-mcp:latest`

3. **Connection issues**
   - Test the connection first: `docker run --rm -i -e ACCESS_TOKEN="your_token" mghassen/guepard-custom-mcp:latest`
   - Check your internet connection
   - Verify your Guepard credentials are valid

4. **Authentication errors**
   - Ensure SUPABASE_ANON_KEY is set for auth operations
   - Verify GUEPARD_AUTH_API is correct

### Debug Mode

Run with debug logging:

```bash
docker run --rm -i -e ACCESS_TOKEN="your_token" -e DEBUG=true mghassen/guepard-custom-mcp:latest
```

## 📚 API Reference

### Tool Parameters

#### Authentication Tools
- **`login_supabase`**: `email` (required), `password` (required)
- **`refresh_token_supabase`**: `refresh_token` (required)
- **`logout_supabase`**: `refresh_token` (required)

#### Deployment Tools
- **`list_deployments`**: `status` (optional), `limit` (optional)
- **`create_deployment`**: `repository_name` (required), `performance_profile_id` (required), plus optional fields
- **`get_deployment`**: `deployment_id` (required)
- **`update_deployment`**: `deployment_id` (required), plus fields to update
- **`delete_deployment`**: `deployment_id` (required)

#### Branch Tools
- **`list_branches`**: `deployment_id` (required)
- **`create_branch`**: `deployment_id`, `branch_id`, `snapshot_id`, `branch_name` (all required)
- **`get_branch`**: `branch_id` (required)
- **`update_branch`**: `deployment_id`, `branch_id` (required), plus fields to update
- **`checkout_branch`**: `deployment_id`, `branch_id`, `snapshot_id` (all required)

#### Snapshot Tools
- **`create_snapshot`**: `deployment_id`, `branch_id`, `snapshot_comment` (all required)
- **`list_snapshots_deployment`**: `deployment_id` (required)
- **`list_snapshots_branch`**: `deployment_id`, `branch_id` (both required)
- **`create_bookmark`**: `deployment_id`, `branch_id`, `snapshot_comment` (all required)

#### Node Tools
- **`list_nodes`**: No parameters
- **`create_node`**: `label_name`, `node_type`, `memory`, `cpu`, `storage` (required), plus optional fields
- **`get_node`**: `node_id` (required)

#### Performance Profile Tools
- **`list_performance_profiles`**: No parameters
- **`create_performance_profile`**: `label_name`, `min_cpu`, `min_memory` (required), plus optional fields
- **`update_performance_profile`**: `performance_profile_id` (required), plus fields to update
- **`get_performance_profiles`**: No parameters

#### Compute Tools
- **`get_compute_status`**: `deployment_id` (required)
- **`start_compute`**: `deployment_id` (required), `notify` (optional)
- **`stop_compute`**: `deployment_id` (required), `notify` (optional)
- **`get_deployment_status`**: `deployment_id` (required)
- **`get_deployment_logs`**: `deployment_id` (required), `lines` (optional)
- **`get_deployment_metrics`**: `deployment_id` (required), `time_range` (optional)

#### Database User Tools
- **`list_database_users`**: `deployment_id` (required)
- **`create_database_user`**: `deployment_id`, `username`, `password` (required), `privileges` (optional)
- **`update_database_user`**: `deployment_id`, `username` (required), `password` (optional)
- **`delete_database_user`**: `deployment_id`, `username` (required)
- **`grant_privileges`**: `deployment_id`, `username`, `privileges` (all required)
- **`revoke_privileges`**: `deployment_id`, `username`, `privileges` (all required)
- **`list_user_privileges`**: `deployment_id`, `username` (both required)

#### Token Tools
- **`list_tokens`**: No parameters
- **`generate_token`**: `name` (required), `expires_in` (optional)
- **`revoke_token`**: `token_id` (required)

#### Notification Tools
- **`subscribe_deployment`**: `deployment_id` (required)
- **`unsubscribe_deployment`**: `deployment_id` (required)
- **`list_subscriptions`**: No parameters

#### Utility Tools
- **`test_connection`**: No parameters

## 🆘 Support

- **Issues**: Report issues on GitHub
- **Documentation**: Check the main README.md
- **Guepard Platform**: Visit [guepard.run](https://guepard.run)

## 📄 License

MIT License - see LICENSE file for details.

---

**Ready to use!** Pull the image and start managing your Guepard deployments with Cursor! 🎉