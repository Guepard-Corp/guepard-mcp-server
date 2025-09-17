# Guepard MCP Server - Configuration Examples

This document provides examples of how to configure the Guepard MCP Server with different tool activation settings.

## 🚀 Quick Start Configurations

### 1. Minimal Configuration (Deployment Management Only)

```bash
# Using predefined configuration
docker run --rm -i \
  -e ACCESS_TOKEN="your_token" \
  -e GUEPARD_CONFIG="minimal" \
  mghassen/guepard-custom-mcp:latest
```

**Available tools:**
- `test_connection`
- `list_deployments`
- `get_deployment`
- `start_compute`
- `stop_compute`

### 2. Read-Only Configuration (Monitoring Only)

```bash
# Using predefined configuration
docker run --rm -i \
  -e ACCESS_TOKEN="your_token" \
  -e GUEPARD_CONFIG="read_only" \
  mghassen/guepard-custom-mcp:latest
```

**Available tools:**
- `test_connection`
- `list_deployments`
- `get_deployment`
- `get_deployment_status`
- `get_deployment_logs`
- `get_deployment_metrics`
- `get_compute_status`
- `list_performance_profiles`
- `get_performance_profiles`

### 3. Production Configuration (Safe Operations Only)

```bash
# Using predefined configuration
docker run --rm -i \
  -e ACCESS_TOKEN="your_token" \
  -e GUEPARD_CONFIG="production" \
  mghassen/guepard-custom-mcp:latest
```

**Disabled tools:**
- `delete_deployment`
- `delete_database_user`
- `revoke_token`

## 🛠️ Custom Configurations

### Enable Specific Modules Only

```bash
# Only deployments and compute modules
docker run --rm -i \
  -e ACCESS_TOKEN="your_token" \
  -e GUEPARD_ENABLED_MODULES="deployments,compute" \
  mghassen/guepard-custom-mcp:latest
```

### Enable Specific Tools Only

```bash
# Only specific tools
docker run --rm -i \
  -e ACCESS_TOKEN="your_token" \
  -e GUEPARD_ENABLED_TOOLS="test_connection,list_deployments,get_deployment,start_compute,stop_compute" \
  mghassen/guepard-custom-mcp:latest
```

### Disable Specific Tools

```bash
# Disable dangerous operations
docker run --rm -i \
  -e ACCESS_TOKEN="your_token" \
  -e GUEPARD_DISABLED_TOOLS="delete_deployment,delete_database_user,revoke_token" \
  mghassen/guepard-custom-mcp:latest
```

### Disable Specific Modules

```bash
# Disable authentication and tokens modules
docker run --rm -i \
  -e ACCESS_TOKEN="your_token" \
  -e GUEPARD_DISABLED_MODULES="auth,tokens" \
  mghassen/guepard-custom-mcp:latest
```

## 🔧 Advanced Configuration Examples

### Development Environment

```bash
# Full development environment
docker run --rm -i \
  -e ACCESS_TOKEN="your_token" \
  -e GUEPARD_CONFIG="development" \
  mghassen/guepard-custom-mcp:latest
```

### Monitoring Environment

```bash
# Monitoring and observability only
docker run --rm -i \
  -e ACCESS_TOKEN="your_token" \
  -e GUEPARD_CONFIG="monitoring" \
  mghassen/guepard-custom-mcp:latest
```

### Custom Minimal Setup

```bash
# Custom minimal setup with specific tools
docker run --rm -i \
  -e ACCESS_TOKEN="your_token" \
  -e GUEPARD_ENABLED_TOOLS="test_connection,list_deployments,get_deployment,get_deployment_status,get_deployment_logs" \
  mghassen/guepard-custom-mcp:latest
```

## 📋 Available Predefined Configurations

| Configuration | Description | Use Case |
|---------------|-------------|----------|
| `minimal` | Minimal deployment management only | Basic operations |
| `deployment_only` | Deployment management without advanced features | Standard deployments |
| `read_only` | Read-only access to deployments and monitoring | Monitoring dashboards |
| `development` | Full development environment with all tools | Development work |
| `production` | Production environment without dangerous operations | Production deployments |
| `monitoring` | Monitoring and observability only | System monitoring |

## 🎯 Use Case Examples

### For CI/CD Pipelines

```bash
# Safe operations for CI/CD
docker run --rm -i \
  -e ACCESS_TOKEN="your_token" \
  -e GUEPARD_ENABLED_TOOLS="test_connection,list_deployments,get_deployment,start_compute,stop_compute,get_deployment_status,get_deployment_logs" \
  mghassen/guepard-custom-mcp:latest
```

### For Monitoring Dashboards

```bash
# Read-only monitoring
docker run --rm -i \
  -e ACCESS_TOKEN="your_token" \
  -e GUEPARD_CONFIG="monitoring" \
  mghassen/guepard-custom-mcp:latest
```

### For Development Teams

```bash
# Full development access
docker run --rm -i \
  -e ACCESS_TOKEN="your_token" \
  -e GUEPARD_CONFIG="development" \
  mghassen/guepard-custom-mcp:latest
```

### For Production Operations

```bash
# Production-safe operations
docker run --rm -i \
  -e ACCESS_TOKEN="your_token" \
  -e GUEPARD_CONFIG="production" \
  mghassen/guepard-custom-mcp:latest
```

## 🔍 Configuration Verification

Use the built-in tools to verify your configuration:

```bash
# List available configurations
docker run --rm -i \
  -e ACCESS_TOKEN="your_token" \
  -e GUEPARD_CONFIG="minimal" \
  mghassen/guepard-custom-mcp:latest

# Then use: list_configurations
```

```bash
# Get current configuration
docker run --rm -i \
  -e ACCESS_TOKEN="your_token" \
  -e GUEPARD_CONFIG="minimal" \
  mghassen/guepard-custom-mcp:latest

# Then use: get_configuration
```

## 🚨 Security Considerations

### Production Environments

- Use `production` configuration to disable dangerous operations
- Consider using `read_only` for monitoring systems
- Avoid enabling `delete_*` tools in production

### Development Environments

- Use `development` configuration for full access
- Enable all modules for testing
- Consider disabling specific tools if needed

### Monitoring Environments

- Use `monitoring` configuration for observability
- Enable only read-only tools
- Disable all write operations

## 💡 Tips

1. **Start with predefined configurations** - They're tested and safe
2. **Use specific tool lists** - More control over what's available
3. **Test your configuration** - Use `get_configuration` to verify
4. **Document your setup** - Keep track of what tools are enabled
5. **Use environment files** - Store configurations in `.env` files

## 📝 Environment File Example

Create a `.env` file:

```bash
# .env
ACCESS_TOKEN=your_guepard_token
GUEPARD_CONFIG=production
GUEPARD_DISABLED_TOOLS=delete_deployment,delete_database_user,revoke_token
```

Then run:

```bash
docker run --rm -i --env-file .env mghassen/guepard-custom-mcp:latest
```
