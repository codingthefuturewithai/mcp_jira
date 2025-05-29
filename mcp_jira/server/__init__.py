"""MCP JIRA server package initialization."""

# Absolute imports from the mcp_jira package
from mcp_jira.config import load_config, ServerConfig # ServerConfig might be useful for type hinting if used here
from mcp_jira.server.app import create_mcp_server

# Create a server instance with the default configuration.
# load_config() will use its defined priority: override_path (None here), env var, or platformdirs default (creating one if needed).
# This 'server' instance is what `mcp dev` will attempt to find and run when targeting the package.
config: ServerConfig = load_config() 
server = create_mcp_server(config) # Pass the loaded config

__all__ = ["server", "create_mcp_server"]
