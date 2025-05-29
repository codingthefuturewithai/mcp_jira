"""MCP JIRA: JIRA integration for the Multi-Channel Platform (MCP)."""

import asyncio
import logging # For the main entry point logger
import sys

# Absolute imports from within the mcp_jira package
# Import the module-level server instance and the factory from server.app
# This is the server instance created with default configuration in app.py
from mcp_jira.server.app import server, create_mcp_server 
from mcp_jira.config import ServerConfig, load_config # May not be strictly needed here, but good for consistency
from mcp_jira.logging_config import setup_logging # For the main function here

__version__ = "0.1.0" # Example version

# What is publicly available when doing 'from mcp_jira import *'
# Also indicates the primary exports of the package.
__all__ = [
    "server", 
    "create_mcp_server", 
    "load_config", 
    "ServerConfig",
    "main" # Expose the main entry point from this top-level init as well
]

# This main function is similar to what mcp_echo has in its top-level __init__.
# It allows running the server via `python -m mcp_jira <transport>`.
# The click-based main in server/app.py is typically used by `mcp run` or direct script execution.

def main(transport: str = "stdio") -> None:
    """
    Package-level entry point for running the MCP JIRA server.

    Note: The primary CLI entry point with more options (like --config, --port)
    is typically mcp_jira.server.app:main, managed by Click.
    This main is a simpler way to start the server with default config.

    Args:
        transport: Transport mode to use ("sse" or "stdio"). Defaults to "stdio".
    """
    try:
        # Use the global/default server instance imported from mcp_jira.server.app
        # This server instance is already configured (with default config).
        # If we want logging here, we need to ensure it's set up.
        # The server instance in app.py should have called setup_logging.
        # However, to be safe for this entry point:
        
        # We load a config here to ensure logging is set up based on *some* config.
        # The `server` instance from app.py already did this for its own config.
        # This is slightly redundant but ensures this entry point also configures logging.
        initial_config = load_config() # Loads default or from env
        setup_logging(initial_config) # Setup logging for this entry point
        logger = logging.getLogger(__name__) # Get logger after setup

        logger.info(f"Package-level main invoked. Starting server with transport: {transport}")
        logger.info(f"Using server instance: {server.name} (from mcp_jira.server.app)")
        logger.info(f"Server config loaded from: {server.settings.loaded_config_path if hasattr(server.settings, 'loaded_config_path') else 'Default (in-memory or preloaded)'}")


        if transport == "stdio":
            asyncio.run(server.run_stdio_async())
        elif transport == "sse":
            # The global `server` instance uses default port from its config.
            # This entry point doesn't easily override port like server.app:main does.
            logger.info(f"SSE transport selected. Server will run on its configured port (default: {server.settings.port if server.settings else 'N/A'}).")
            asyncio.run(server.run_sse_async())
        else:
            logger.error(f"Invalid transport specified: {transport}. Use 'stdio' or 'sse'.")
            sys.exit(1)

    except KeyboardInterrupt:
        # Use logger if available, otherwise print
        if 'logger' in locals():
            logger.info("Server (package main) stopped by user.")
        else:
            print("Server (package main) stopped by user.")
    except Exception as e:
        if 'logger' in locals():
            logger.error(f"Failed to start MCP server (package main): {e}", exc_info=True)
        else:
            print(f"Failed to start MCP server (package main): {e}")
        sys.exit(1)

# This allows running `python -m mcp_jira`
# if __name__ == "__main__":
#     # A simple way to parse transport if needed, or just default
#     # For more complex CLI args, server.app:main with Click is better.
#     # Example: run with stdio by default if run as module.
#     main("stdio") 
# The above if __name__ == "__main__" is commented out because typically for a package,
# you'd rely on the Click entry point or direct function calls rather than
# `python -m your_package` directly executing __init__.py's main without args.
# The `main` function is provided for programmatic use or if defined as a script entry point. 