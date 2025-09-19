"""
Configuration system for Guepard MCP Server
Allows selective activation/deactivation of tools and modules
"""

import os
from typing import Dict, List, Set, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class ToolConfig:
    """Configuration manager for tool activation"""
    
    def __init__(self):
        self.enabled_modules: Set[str] = set()
        self.enabled_tools: Set[str] = set()
        self.disabled_tools: Set[str] = set()
        self._load_configuration()
    
    def _load_configuration(self):
        """Load configuration from environment variables"""
        
        # Load enabled modules
        enabled_modules_str = os.getenv("GUEPARD_ENABLED_MODULES", "")
        if enabled_modules_str:
            self.enabled_modules = set(module.strip() for module in enabled_modules_str.split(",") if module.strip())
        
        # Load enabled tools
        enabled_tools_str = os.getenv("GUEPARD_ENABLED_TOOLS", "")
        if enabled_tools_str:
            self.enabled_tools = set(tool.strip() for tool in enabled_tools_str.split(",") if tool.strip())
        
        # Load disabled tools
        disabled_tools_str = os.getenv("GUEPARD_DISABLED_TOOLS", "")
        if disabled_tools_str:
            self.disabled_tools = set(tool.strip() for tool in disabled_tools_str.split(",") if tool.strip())
        
        # Load disabled modules
        disabled_modules_str = os.getenv("GUEPARD_DISABLED_MODULES", "")
        if disabled_modules_str:
            disabled_modules = set(module.strip() for module in disabled_modules_str.split(",") if module.strip())
            # If specific modules are disabled, remove them from enabled modules
            if self.enabled_modules:
                self.enabled_modules -= disabled_modules
    
    def is_module_enabled(self, module_name: str) -> bool:
        """Check if a module is enabled"""
        # If no specific modules are configured, all are enabled
        if not self.enabled_modules:
            return True
        
        return module_name in self.enabled_modules
    
    def is_tool_enabled(self, tool_name: str) -> bool:
        """Check if a tool is enabled"""
        # If tool is explicitly disabled, it's disabled
        if tool_name in self.disabled_tools:
            return False
        
        # If specific tools are enabled, only those are enabled
        if self.enabled_tools:
            return tool_name in self.enabled_tools
        
        # If no specific tools are configured, all are enabled (unless disabled)
        return True
    
    def get_enabled_modules(self) -> List[str]:
        """Get list of enabled modules"""
        return list(self.enabled_modules) if self.enabled_modules else []
    
    def get_enabled_tools(self) -> List[str]:
        """Get list of enabled tools"""
        return list(self.enabled_tools) if self.enabled_tools else []
    
    def get_disabled_tools(self) -> List[str]:
        """Get list of disabled tools"""
        return list(self.disabled_tools)
    
    def get_configuration_summary(self) -> Dict[str, any]:
        """Get a summary of the current configuration"""
        return {
            "enabled_modules": self.get_enabled_modules(),
            "enabled_tools": self.get_enabled_tools(),
            "disabled_tools": self.get_disabled_tools(),
            "configuration_mode": "selective" if (self.enabled_modules or self.enabled_tools) else "all"
        }


# Predefined configurations for common use cases
PREDEFINED_CONFIGS = {
    "v1": {
        "description": "Basic v1 - Essential deployment management tools only",
        "enabled_modules": ["deployments", "compute", "performance", "image_providers, checkouts, snapshots, branches"],
        "enabled_tools": [
            "test_connection",

            "list_deployments", 
            "get_deployment", 
            "create_deployment",

            "start_compute", 
            "stop_compute",

            "checkout_branch",
            "create_branch_from_snapshot",
            
            "list_branches",
            "update_branch",
            "create_branch_from_snapshot",

            "start_compute",
            "stop_compute",
            "get_compute_status",

            "list_snapshots_deployment",
            "list_snapshots_branch",
            "create_snapshot",
            
            "get_deployment_logs",

            "list_performance_profiles",
            "get_performance_profiles",

            "list_image_providers"
        ]
    },
    "minimal": {
        "description": "Minimal deployment management only",
        "enabled_modules": ["deployments", "compute"],
        "enabled_tools": ["test_connection", "list_deployments", "get_deployment", "start_compute", "stop_compute"]
    },
    "deployment_only": {
        "description": "Deployment management without advanced features",
        "enabled_modules": ["deployments", "compute", "performance"],
        "disabled_tools": ["create_deployment", "delete_deployment"]
    },
    "read_only": {
        "description": "Read-only access to deployments and monitoring",
        "enabled_tools": [
            "test_connection", "list_deployments", "get_deployment", "get_deployment_status",
            "get_deployment_logs", "get_deployment_metrics", "get_compute_status",
            "list_performance_profiles", "get_performance_profiles"
        ]
    },
    "development": {
        "description": "Full development environment with all tools",
        "enabled_modules": ["auth", "deployments", "branches", "snapshots", "compute", "users"]
    },
    "production": {
        "description": "Production environment without dangerous operations",
        "disabled_tools": ["delete_deployment", "delete_database_user", "revoke_token"]
    },
    "monitoring": {
        "description": "Monitoring and observability only",
        "enabled_tools": [
            "test_connection", "get_deployment_status", "get_deployment_logs",
            "get_deployment_metrics", "get_compute_status", "list_subscriptions"
        ]
    },
    "ci_cd": {
        "description": "CI/CD pipeline tools",
        "enabled_tools": [
            "test_connection", "list_deployments", "get_deployment", 
            "create_deployment", "start_compute", "stop_compute",
            "get_deployment_status", "get_deployment_logs"
        ]
    },
    "admin": {
        "description": "Administrative tools",
        "enabled_modules": ["deployments", "compute", "users", "tokens"],
        "disabled_tools": ["delete_deployment"]
    }
}


def get_predefined_config(config_name: str) -> Optional[Dict[str, any]]:
    """Get a predefined configuration by name"""
    return PREDEFINED_CONFIGS.get(config_name)


def list_predefined_configs() -> Dict[str, str]:
    """List all available predefined configurations"""
    return {name: config["description"] for name, config in PREDEFINED_CONFIGS.items()}
