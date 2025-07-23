import os
import yaml
import logging # Import logging module
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import platformdirs
import sys  # Ensure sys is imported for print(..., file=sys.stderr)

CONFIG_FILE_NAME = "config.yaml"
APP_NAME = "mcp_jira"
APP_AUTHOR = "MCPJira"  # Or your specific author string for platformdirs

# Get a logger for this module
logger = logging.getLogger(__name__)

CONFIG_TEMPLATE = """# MCP JIRA Server Configuration
# Please update the placeholder values below with your actual JIRA details.
# You can configure multiple JIRA sites, each with a unique alias.

name: "MCP JIRA Server"
log_level: "INFO"

default_site_alias: "primary"

sites:
  primary:
    url: "https://your-domain.atlassian.net"
    email: "your-email@example.com"
    api_token: "YOUR_API_TOKEN_HERE"
    cloud: true
"""

@dataclass
class JiraSiteConfig:
    """Configuration for a single JIRA site."""
    url: str
    email: str
    api_token: str
    cloud: bool = True

@dataclass
class ServerConfig:
    """Overall server configuration."""
    default_site_alias: str
    sites: Dict[str, JiraSiteConfig]
    log_level: str = "INFO"
    name: str = "MCP Jira"
    loaded_config_path: Optional[str] = None

class ConfigurationError(Exception):
    """Custom exception for configuration loading errors."""
    pass

def load_config(config_file_path_override: Optional[str] = None) -> ServerConfig:
    """
    Loads JIRA server configuration.
    Priority for config file path:
    1. config_file_path_override (e.g., from CLI)
    2. MCP_JIRA_CONFIG_PATH environment variable
    3. Default path from platformdirs (OS-agnostic).
    If the config file is not found, its directory is created, and a template config.yaml
    with commented-out examples is written. A warning is logged.
    Raises ConfigurationError if the config (even after template creation) is invalid or empty.
    """
    path_to_load = config_file_path_override

    if path_to_load is None:
        path_to_load = os.getenv("MCP_JIRA_CONFIG_PATH")

    if path_to_load is None:
        default_config_dir = platformdirs.user_config_dir(APP_NAME, appauthor=APP_AUTHOR)
        # We expect the directory to exist or be creatable by the user if they want to place config there.
        # The server itself won't create the directory structure if user_config_dir points to a new place.
        path_to_load = os.path.join(default_config_dir, CONFIG_FILE_NAME)
    
    config_dir = os.path.dirname(path_to_load)
    if not os.path.exists(config_dir):
        try:
            os.makedirs(config_dir, exist_ok=True)
            logger.info(f"Created configuration directory: {config_dir}")
        except OSError as e:
            # If directory creation fails, we can't proceed to write config there.
            raise ConfigurationError(f"Failed to create configuration directory '{config_dir}': {e}. Please check permissions.") from e

    if not os.path.exists(path_to_load):
        try:
            with open(path_to_load, "w") as f:
                f.write(CONFIG_TEMPLATE)
            warning_message = (
                f"CONFIGURATION ACTION REQUIRED: A template configuration file has been created at: '{path_to_load}'. "
                f"Please edit this file with your actual JIRA site details for the server to function correctly."
            )
            logger.warning(warning_message)
            # Also print to stderr for immediate visibility during startup, as logger might not be fully configured yet for console output.
            print(f"WARNING: {warning_message}", file=sys.stderr) 
        except IOError as e:
            raise ConfigurationError(f"Failed to create template configuration file at '{path_to_load}': {e}. Please check permissions.") from e

    # Proceed to load and parse the file (which might be the newly created template or an existing one)
    try:
        with open(path_to_load, "r") as f:
            raw_config_from_file = yaml.safe_load(f)
    except Exception as e:
        raise ConfigurationError(f"Error reading or parsing YAML configuration file at '{path_to_load}': {e}") from e

    # If raw_config_from_file is None (e.g. empty file or only comments), treat as invalid.
    if raw_config_from_file is None:
        raw_config_from_file = {} # Ensure it's a dict for downstream checks to avoid NoneType errors

    if not isinstance(raw_config_from_file, dict):
        # This case should ideally not be hit if YAML parsing failed earlier for truly malformed files,
        # but as a safeguard if safe_load somehow returns a non-dict for non-empty but invalid YAML.
        raise ConfigurationError(
            f"Invalid configuration in '{path_to_load}'. The file content must be a YAML dictionary (it might be empty or only comments)."
        )

    sites_section = raw_config_from_file.get("sites")
    # Check if sites_section is a dictionary AND is not empty
    if not isinstance(sites_section, dict) or not sites_section: 
        raise ConfigurationError(
            f"Configuration Error in '{path_to_load}': The 'sites' key must be present, be a dictionary, "
            f"and contain at least one uncommented JIRA site configuration. "
            f"Please edit the file and provide your site details."
        )

    yaml_default_site_alias = raw_config_from_file.get("default_site_alias")
    if not isinstance(yaml_default_site_alias, str) or not yaml_default_site_alias:
        raise ConfigurationError(
            f"Configuration Error in '{path_to_load}': The 'default_site_alias' key must be present, "
            f"be a non-empty string, and correspond to an uncommented site defined in 'sites'. "
            f"Please edit the file."
        )

    parsed_sites: Dict[str, JiraSiteConfig] = {}
    for alias, site_data in sites_section.items():
        if not isinstance(site_data, dict):
            # This might occur if a site entry is not a dictionary (e.g., just a string)
            logger.warning(f"Skipping invalid site entry '{alias}' in '{path_to_load}': value is not a dictionary.")
            continue # Skip this invalid site entry

        try:
            missing_keys = [k for k in ['url', 'email', 'api_token'] if k not in site_data]
            if missing_keys:
                logger.warning(f"Skipping site '{alias}' in '{path_to_load}' due to missing required key(s): {', '.join(missing_keys)}.")
                continue # Skip this site entry
            
            # Ensure critical values are not None or empty strings before creating JiraSiteConfig
            if not site_data.get('url') or not site_data.get('email') or not site_data.get('api_token'):
                logger.warning(f"Skipping site '{alias}' in '{path_to_load}' because url, email, or api_token is empty or missing.")
                continue

            parsed_sites[alias] = JiraSiteConfig(
                url=str(site_data['url']),
                email=str(site_data['email']),
                api_token=str(site_data['api_token']),
                cloud=bool(site_data.get('cloud', True))
            )
        except Exception as e:
             # Log a warning for this specific site and skip it, rather than failing all config loading
             logger.warning(f"Error processing site '{alias}' in '{path_to_load}', it will be skipped: {e}. Ensure correct data types and required fields.")
             continue # Skip this site

    # After attempting to parse all sites, check if we ended up with any valid ones.
    if not parsed_sites:
        raise ConfigurationError(
            f"Configuration Error in '{path_to_load}': No valid JIRA sites were successfully parsed. "
            f"This could be because all site entries under 'sites:' are commented out, incomplete, or invalid. "
            f"Please uncomment and/or correct at least one site configuration."
        )

    # Now check default_site_alias against the successfully parsed_sites
    if yaml_default_site_alias not in parsed_sites:
        raise ConfigurationError(
            f"Configuration Error in '{path_to_load}': The 'default_site_alias' ('{yaml_default_site_alias}') "
            f"does not correspond to any of the successfully parsed and valid site aliases: {list(parsed_sites.keys())}."
        )

    final_default_site_alias = os.getenv("MCP_JIRA_DEFAULT_ALIAS_OVERRIDE", yaml_default_site_alias)
    if final_default_site_alias not in parsed_sites: # Check again if env var override is invalid
        raise ConfigurationError(
            f"Configuration Error: The final default site alias '{final_default_site_alias}' (from config or MCP_JIRA_DEFAULT_ALIAS_OVERRIDE) "
            f"is not among the valid, parsed sites: {list(parsed_sites.keys())}."
        )
    
    server_name = str(raw_config_from_file.get("name", "MCP Jira"))
    log_level = os.getenv("LOG_LEVEL", str(raw_config_from_file.get("log_level", "INFO"))).upper()

    return ServerConfig(
        default_site_alias=final_default_site_alias,
        sites=parsed_sites,
        log_level=log_level,
        name=server_name,
        loaded_config_path=path_to_load
    )

def get_active_jira_config(
    alias: Optional[str] = None, server_config: Optional[ServerConfig] = None
) -> JiraSiteConfig:
    """
    Retrieves the JIRA site configuration for the given alias or the default.
    Uses the provided server_config or loads a default one.
    """
    effective_config = server_config if server_config is not None else load_config()
    target_alias = alias if alias else effective_config.default_site_alias
    site = effective_config.sites.get(target_alias)

    if site is None:
        raise ConfigurationError(
            f"JIRA site alias '{target_alias}' not found in the loaded configuration. "
            f"Available aliases: {list(effective_config.sites.keys())} "
            f"(Configuration loaded from: '{effective_config.loaded_config_path}')"
        )
    return site