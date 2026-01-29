#!/bin/bash

# Guepard MCP Server Installation Script
# This script helps users install and configure the Guepard MCP Server

set -e

echo "🚀 Installing Guepard MCP Server..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

echo -e "${GREEN}✅ Docker is installed${NC}"

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo -e "${RED}❌ Docker is not running. Please start Docker first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker is running${NC}"

# Pull the latest image
echo -e "${BLUE}📥 Pulling Guepard MCP Server image...${NC}"
docker pull mghassen/guepard-custom-mcp:latest

echo -e "${GREEN}✅ Image pulled successfully${NC}"

# Get user's access token
echo -e "${YELLOW}🔑 Please enter your Guepard access token:${NC}"
read -s ACCESS_TOKEN

if [ -z "$ACCESS_TOKEN" ]; then
    echo -e "${RED}❌ Access token is required${NC}"
    exit 1
fi

# Test the connection
echo -e "${BLUE}🧪 Testing connection...${NC}"
TEST_CONTAINER_NAME="guepard-mcp-test-$(date +%s)"
# Create a temporary test file
echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test-client", "version": "1.0.0"}}}' > /tmp/guepard_test.json

if docker run --rm -i --name "$TEST_CONTAINER_NAME" -e ACCESS_TOKEN="$ACCESS_TOKEN" mghassen/guepard-custom-mcp:latest < /tmp/guepard_test.json | grep -q "guepard-custom"; then
    echo -e "${GREEN}✅ Connection test successful${NC}"
else
    echo -e "${RED}❌ Connection test failed. Please check your access token.${NC}"
    rm -f /tmp/guepard_test.json
    exit 1
fi

# Clean up test file
rm -f /tmp/guepard_test.json

# Clean up any existing Guepard containers
echo -e "${BLUE}🧹 Cleaning up existing Guepard containers...${NC}"
docker ps -q --filter "ancestor=mghassen/guepard-custom-mcp:latest" | xargs -r docker stop 2>/dev/null || true

# Create Cursor MCP configuration
CURSOR_MCP_FILE="$HOME/.cursor/mcp.json"

echo -e "${BLUE}📝 Creating Cursor MCP configuration...${NC}"

# Create .cursor directory if it doesn't exist
mkdir -p "$HOME/.cursor"

# Create or update mcp.json
if [ -f "$CURSOR_MCP_FILE" ]; then
    echo -e "${BLUE}📝 Updating existing MCP configuration...${NC}"
    # Backup existing configuration
    cp "$CURSOR_MCP_FILE" "$CURSOR_MCP_FILE.backup"
    
    # Use Python to safely merge configurations
    python3 -c "
import json
import sys

# Initialize config
config = {'mcpServers': {}}

# Read existing config
try:
    with open('$CURSOR_MCP_FILE', 'r') as f:
        config = json.load(f)
    # Ensure mcpServers exists
    if 'mcpServers' not in config:
        config['mcpServers'] = {}
    print('Found existing MCP servers:', list(config['mcpServers'].keys()))
except (FileNotFoundError, json.JSONDecodeError):
    print('No existing configuration found, creating new one')

# Remove only existing guepard entries (both cases) to avoid duplicates
if 'guepard' in config['mcpServers']:
    del config['mcpServers']['guepard']
if 'Guepard' in config['mcpServers']:
    del config['mcpServers']['Guepard']

# Add/update Guepard server (preserving all other existing servers)
config['mcpServers']['Guepard'] = {
    'command': 'docker',
    'args': [
        'run', 
        '--rm', 
        '-i', 
        '-e', 'ACCESS_TOKEN=$ACCESS_TOKEN', 
        'mghassen/guepard-custom-mcp:latest'
    ],
    'env': {}
}

# Write updated config
with open('$CURSOR_MCP_FILE', 'w') as f:
    json.dump(config, f, indent=2)

print('Final MCP servers:', list(config['mcpServers'].keys()))
print('Configuration updated successfully')
"
else
    echo -e "${BLUE}📝 Creating new MCP configuration...${NC}"
    cat > "$CURSOR_MCP_FILE" << EOF
{
  "mcpServers": {
    "Guepard": {
      "command": "docker",
      "args": [
        "run", 
        "--rm", 
        "-i", 
        "-e", "ACCESS_TOKEN=$ACCESS_TOKEN", 
        "mghassen/guepard-custom-mcp:latest"
      ],
      "env": {}
    }
  }
}
EOF
fi

echo -e "${GREEN}✅ Cursor MCP configuration updated at $CURSOR_MCP_FILE${NC}"

# Inform about backup if it exists
if [ -f "$CURSOR_MCP_FILE.backup" ]; then
    echo -e "${YELLOW}📋 A backup of your original configuration was saved to $CURSOR_MCP_FILE.backup${NC}"
    echo -e "${YELLOW}   If you had other MCP servers configured, they have been preserved.${NC}"
fi

# Display success message
echo ""
echo -e "${GREEN}🎉 Installation complete!${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "1. Restart Cursor IDE"
echo "2. Test the MCP server by asking:"
echo "   - 'Test my Guepard connection'"
echo "   - 'Get all my deployments'"
echo "   - 'Show me deployment info'"
echo ""
echo -e "${BLUE}Available tools:${NC}"
echo "• get_deployments - Get deployment information"
echo "• start_compute - Start compute for a deployment"
echo "• stop_compute - Stop compute for a deployment"
echo "• create_branch - Create a branch from snapshot"
echo "• checkout_branch - Checkout a branch"
echo "• subscribe_deployment - Subscribe to notifications"
echo "• unsubscribe_deployment - Unsubscribe from notifications"
echo "• list_subscriptions - List all subscriptions"
echo "• test_connection - Test API connection"
echo ""
echo -e "${GREEN}Happy coding with Guepard! 🚀${NC}"

# Final cleanup - ensure only one container will run
echo -e "${BLUE}🧹 Final cleanup - stopping any remaining Guepard containers...${NC}"
docker ps -q --filter "ancestor=mghassen/guepard-custom-mcp:latest" | xargs -r docker stop 2>/dev/null || true


