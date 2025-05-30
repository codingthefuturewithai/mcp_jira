# Placeholder for state management functions 

import streamlit as st
from copy import deepcopy
import uuid # For unique UI IDs

# Import the original load_config from the main mcp_jira package
from mcp_jira.config import load_config as load_actual_config_from_file, ServerConfig, ConfigurationError

def initialize_session_state():
    """Loads config into session state if not already present, using a list for sites."""
    if 'editable_config' not in st.session_state:
        try:
            config_data: ServerConfig = load_actual_config_from_file()
            
            sites_list = []
            for alias, site_obj in config_data.sites.items():
                sites_list.append({
                    'ui_id': uuid.uuid4().hex, # Unique ID for Streamlit keys
                    'alias': alias,
                    'url': site_obj.url,
                    'email': site_obj.email,
                    'api_token': site_obj.api_token,
                    'cloud': site_obj.cloud
                })

            editable_config = {
                'name': config_data.name,
                'log_level': config_data.log_level,
                'default_site_alias': config_data.default_site_alias,
                'sites_list': sites_list # Store sites as a list of dicts
            }
            st.session_state.editable_config = deepcopy(editable_config)
            st.session_state.loaded_config_path = config_data.loaded_config_path
            st.session_state.config_error_message = None
        except ConfigurationError as e:
            st.session_state.editable_config = None
            st.session_state.loaded_config_path = None
            st.session_state.config_error_message = str(e)
        except Exception as e:
            st.session_state.editable_config = None
            st.session_state.loaded_config_path = None
            st.session_state.config_error_message = f"An unexpected error occurred during initial configuration load: {str(e)}"

def reset_and_reload_state():
    """Clears the editable config and re-initializes from file."""
    if 'editable_config' in st.session_state:
        del st.session_state.editable_config
    if 'loaded_config_path' in st.session_state: # Keep path if already loaded once successfully
        pass 
    if 'config_error_message' in st.session_state:
        del st.session_state.config_error_message
    
    # Clear specific messages that might persist incorrectly
    if 'show_save_success_toast' in st.session_state:
        del st.session_state.show_save_success_toast
        
    initialize_session_state()

def add_new_site_to_state():
    """Adds a new, empty site structure to the session state's sites_list."""
    if 'editable_config' not in st.session_state or st.session_state.editable_config is None:
        st.error("Cannot add site: configuration not loaded.")
        return

    new_site_ui_id = uuid.uuid4().hex
    # Find a unique default alias
    existing_aliases = {site['alias'] for site in st.session_state.editable_config.get('sites_list', [])}
    new_alias_base = "new_site"
    new_alias_counter = 1
    final_new_alias = f"{new_alias_base}_{new_alias_counter}"
    while final_new_alias in existing_aliases:
        new_alias_counter += 1
        final_new_alias = f"{new_alias_base}_{new_alias_counter}"

    new_site = {
        'ui_id': new_site_ui_id,
        'alias': final_new_alias,
        'url': '',
        'email': '',
        'api_token': '',
        'cloud': True
    }
    if 'sites_list' not in st.session_state.editable_config:
        st.session_state.editable_config['sites_list'] = []
    st.session_state.editable_config['sites_list'].append(new_site)
    st.rerun()

def delete_site_from_state(site_ui_id_to_delete: str):
    """Deletes a site from the session state's sites_list based on its ui_id."""
    if 'editable_config' not in st.session_state or \
       'sites_list' not in st.session_state.editable_config or \
       st.session_state.editable_config is None:
        st.error("Cannot delete site: configuration or sites list not found in session state.")
        return

    sites_list = st.session_state.editable_config['sites_list']
    original_length = len(sites_list)
    alias_of_deleted_site = None

    # Find and remove the site
    for i, site in enumerate(sites_list):
        if site['ui_id'] == site_ui_id_to_delete:
            alias_of_deleted_site = site.get('alias')
            sites_list.pop(i)
            break
    
    if len(sites_list) == original_length:
        st.warning(f"Site with UI ID '{site_ui_id_to_delete}' not found for deletion.")
        # No rerun needed if nothing changed
        return

    # If the deleted site was the default, clear or update the default_site_alias
    current_default_alias = st.session_state.editable_config.get('default_site_alias')
    if alias_of_deleted_site and current_default_alias == alias_of_deleted_site:
        if sites_list:
            new_default_alias = sites_list[0].get('alias', '')
            st.session_state.editable_config['default_site_alias'] = new_default_alias
            st.session_state.action_feedback_message = {
                "type": "warning", 
                "text": f"Site '{alias_of_deleted_site}' deleted. Default site alias updated to '{new_default_alias}'. Please verify and save."
            }
        else:
            st.session_state.editable_config['default_site_alias'] = ''
            st.session_state.action_feedback_message = {
                "type": "info", 
                "text": f"Site '{alias_of_deleted_site}' deleted. No sites remaining. Default site alias cleared."
            }
    elif alias_of_deleted_site:
        st.session_state.action_feedback_message = {
            "type": "info", 
            "text": f"Site '{alias_of_deleted_site}' removed. Click 'Save Configuration' to persist this change."
        }
    # Removed fallback 'else' for toast as it might be confusing if site_ui_id_to_delete was invalid (already handled by warning)
    
    st.rerun() 