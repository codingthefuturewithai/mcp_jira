import streamlit as st
from mcp_jira.config import load_config, ServerConfig, JiraSiteConfig, ConfigurationError
import yaml
import os
from copy import deepcopy

# Helper function to mask API tokens (from Conduit example, adapted)
def mask_api_token(token: str) -> str:
    """
    Masks an API token.
    - Shows the token as is if it's 8 characters or shorter.
    - For tokens longer than 8 characters, shows the first 4,
      then a fixed number of asterisks (30), then the last 4.
    """
    if not token:
        return "********"  # Default for empty/None

    token_len = len(token)
    fixed_asterisks = "******************************" # 30 asterisks

    if token_len <= 8:
        # If the token is 8 characters or less, show it as is.
        # Masking would offer little benefit or make it confusing.
        return token
    else: # token_len > 8
        # Show first 4, fixed asterisks, and last 4.
        return f"{token[:4]}{fixed_asterisks}{token[-4:]}"

def initialize_session_state():
    """Loads config into session state if not already present."""
    if 'editable_config' not in st.session_state:
        try:
            config_data: ServerConfig = load_config()
            # Convert dataclasses to dicts for easier manipulation in session_state
            editable_config = {
                'name': config_data.name,
                'log_level': config_data.log_level,
                'default_site_alias': config_data.default_site_alias,
                'sites': {
                    alias: {
                        'url': site.url,
                        'email': site.email,
                        'api_token': site.api_token, # Store actual token
                        'cloud': site.cloud
                    } for alias, site in config_data.sites.items()
                }
            }
            st.session_state.editable_config = deepcopy(editable_config) # Ensure it's a mutable copy
            st.session_state.loaded_config_path = config_data.loaded_config_path
            st.session_state.config_error_message = None # Clear any previous error
        except ConfigurationError as e:
            st.session_state.editable_config = None # Indicate config loading failed
            st.session_state.loaded_config_path = None
            st.session_state.config_error_message = str(e)
        except Exception as e: # Catch other potential errors during initial load
            st.session_state.editable_config = None
            st.session_state.loaded_config_path = None
            st.session_state.config_error_message = f"An unexpected error occurred during initial configuration load: {str(e)}"


def save_configuration():
    """Saves the current editable_config from session_state back to the file."""
    if not st.session_state.editable_config or not st.session_state.loaded_config_path:
        st.error("Cannot save, configuration was not loaded properly.")
        return

    config_to_save = deepcopy(st.session_state.editable_config)

    # Basic Validation (can be expanded)
    if not config_to_save.get('default_site_alias') or \
       config_to_save['default_site_alias'] not in config_to_save.get('sites', {}):
        st.error(f"Validation Error: Default site alias '{config_to_save.get('default_site_alias')}' is invalid or does not exist among the defined sites.")
        return

    for alias, site_data in config_to_save.get('sites', {}).items():
        if not site_data.get('url') or not site_data.get('email') or not site_data.get('api_token'):
            st.error(f"Validation Error: Site '{alias}' is missing required fields (URL, Email, or API Token).")
            return
        if not alias.strip():
             st.error(f"Validation Error: Site alias cannot be empty for site with URL '{site_data.get('url')}'.")
             return


    try:
        with open(st.session_state.loaded_config_path, 'w') as f:
            yaml.dump(config_to_save, f, sort_keys=False, indent=2, default_flow_style=False)
        
        # Set a success message flag in session_state
        st.session_state.show_save_success_toast = f"Configuration saved successfully to {st.session_state.loaded_config_path}"
        
        del st.session_state.editable_config 
        initialize_session_state() # Reload to reflect saved state immediately if needed for logic before rerun
        st.rerun()
    except Exception as e:
        st.error(f"Failed to save configuration: {str(e)}")


def main():
    st.set_page_config(
        page_title="MCP JIRA Configuration Editor",
        page_icon="⚙️",
        layout="wide",
    )
    # Check for and display save success toast at the beginning of a rerun
    if st.session_state.get('show_save_success_toast'):
        st.toast(st.session_state.show_save_success_toast, icon="✅")
        del st.session_state.show_save_success_toast # Clear the flag

    st.title("MCP JIRA Server Configuration Editor")

    initialize_session_state()

    if st.session_state.config_error_message and not st.session_state.editable_config:
        st.error(f"Initial Configuration Error: {st.session_state.config_error_message}")
        st.warning(
            "Could not load JIRA configuration for editing. "
            "If this is the first time, a template `config.yaml` might have been created. "
            "Please check the default configuration paths (see README.md), ensure it's valid, then refresh this page."
        )
        # Display default paths from README
        st.markdown("---")
        st.markdown("**Default Configuration File Locations (for reference):**")
        st.markdown("- **macOS**: `~/Library/Application Support/mcp_jira/config.yaml`")
        st.markdown("- **Linux**: `~/.config/mcp_jira/config.yaml`")
        st.markdown("- **Windows**: `%APPDATA%\\\\MCPJira\\\\mcp_jira\\\\config.yaml`")
        return # Stop further rendering if initial load failed catastrophically

    if not st.session_state.editable_config: # Should be caught above, but as a safeguard
        st.error("Configuration could not be loaded. Please check logs or the config file.")
        return

    # --- UI for Editing ---
    config = st.session_state.editable_config # Shorthand

    if st.session_state.loaded_config_path:
        st.info(f"**Editing configuration file:** `{st.session_state.loaded_config_path}`")
    else: # Should not happen if editable_config is present, but good for robustness
        st.warning("Configuration path is not identified.")

    # General Settings
    st.subheader("General Settings")
    config['name'] = st.text_input(
        "Configuration Name", 
        value=config.get('name', 'MCP Jira')
    )
    
    log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    current_log_level_idx = log_levels.index(config.get('log_level', 'INFO').upper()) if config.get('log_level', 'INFO').upper() in log_levels else log_levels.index("INFO")
    config['log_level'] = st.selectbox(
        "Log Level", 
        options=log_levels, 
        index=current_log_level_idx
    )

    site_aliases = list(config.get('sites', {}).keys())
    if not site_aliases: # Handle case with no sites yet
        st.session_state.editable_config['default_site_alias'] = st.text_input(
             "Default JIRA Site Alias (No sites defined yet)", 
             value=config.get('default_site_alias', ''),
             help="Define sites below first, then select a default."
        )
    else:
        current_default_alias = config.get('default_site_alias', '')
        default_alias_idx = site_aliases.index(current_default_alias) if current_default_alias in site_aliases else 0
        config['default_site_alias'] = st.selectbox(
            "Default JIRA Site Alias", 
            options=site_aliases, 
            index=default_alias_idx,
            help="Select the default JIRA connection to use."
        )
    
    st.markdown("---")
    st.subheader("JIRA Site Details")

    # --- Iterate over a copy of site aliases for stable editing if aliases change ---
    # This part needs careful handling if site aliases themselves are made editable directly in the text field.
    # For now, let's assume alias editing is complex and handle other fields.
    # We will operate on st.session_state.editable_config.sites directly.
    
    site_aliases_to_iterate = list(config.get('sites', {}).keys()) # Get current aliases

    for alias in site_aliases_to_iterate:
        site_data = config['sites'][alias]
        with st.expander(f"Site: {alias} {'(Default)' if alias == config.get('default_site_alias') else ''}", expanded=True):
            # If we want to make alias editable, it's tricky because it's the dict key.
            # For now, alias is displayed based on the key.
            # new_alias = st.text_input("Site Alias", value=alias, key=f"alias_{alias}") -> Needs logic to update dict key
            
            site_data['url'] = st.text_input("Site URL", value=site_data.get('url', ''), key=f"url_{alias}")
            site_data['email'] = st.text_input("Email", value=site_data.get('email', ''), key=f"email_{alias}")
            # Show actual token for editing
            site_data['api_token'] = st.text_input("API Token", value=site_data.get('api_token', ''), key=f"token_{alias}", type="password") 
            # Keep type="password" for API token during editing for basic obfuscation while typing
            
            site_data['cloud'] = st.checkbox("JIRA Cloud", value=site_data.get('cloud', True), key=f"cloud_{alias}")
            
            # Placeholder for delete button (Phase 3)
            # if st.button("Delete This Site", key=f"delete_{alias}", type="secondary"):
            #     # Add deletion logic here
            #     pass

    # Placeholder for Add New Site button (Phase 2)
    # if st.button("Add New JIRA Site"):
    #    # Add new site logic here
    #    pass
    
    st.markdown("---")
    if st.button("Save Configuration", type="primary"):
        save_configuration()

if __name__ == "__main__":
    # Note: For the Streamlit UI to correctly find the mcp_jira package (and thus mcp_jira.config),
    # you should run it from the root of the mcp_jira project, e.g.,
    # PYTHONPATH=. streamlit run mcp_jira/ui/app.py
    # or ensure mcp_jira is installed in the environment where Streamlit is running.
    main() 