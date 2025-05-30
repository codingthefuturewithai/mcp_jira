# Placeholder for configuration I/O functions 

import streamlit as st
import yaml
from copy import deepcopy

def save_configuration_to_file(config_dict_to_save: dict, file_path: str) -> bool:
    """Saves the provided configuration dictionary to the specified YAML file path.
    Transforms sites_list back to sites dictionary for saving.
    Returns True on success, False on validation or IO error.
    Error messages are displayed using st.error directly.
    """
    if not config_dict_to_save or not file_path:
        st.error("Cannot save, essential configuration data or file path is missing.")
        return False

    transformed_config = deepcopy(config_dict_to_save)

    sites_dict = {}
    defined_aliases = set()
    if 'sites_list' in transformed_config:
        for site_item in transformed_config['sites_list']:
            alias = site_item.get('alias', '').strip()
            if not alias:
                st.error(f"Validation Error: Site alias cannot be empty. Found in site with URL: '{site_item.get('url')}'.")
                return False
            if alias in defined_aliases:
                st.error(f"Validation Error: Site alias '{alias}' is duplicated. Aliases must be unique.")
                return False
            defined_aliases.add(alias)
            
            site_data_to_save = {k: v for k, v in site_item.items() if k != 'ui_id' and k != 'alias'}
            
            # Check for required fields in site_data_to_save
            url_present = bool(site_data_to_save.get('url'))
            email_present = bool(site_data_to_save.get('email'))
            token_present = bool(site_data_to_save.get('api_token'))

            if not (url_present and email_present and token_present):
                st.error(f"Validation Error: Site '{alias}' is missing required fields (URL, Email, or API Token).")
                return False
            sites_dict[alias] = site_data_to_save
        transformed_config['sites'] = sites_dict
        del transformed_config['sites_list']
    else:
        transformed_config['sites'] = {}

    default_alias = transformed_config.get('default_site_alias')
    if not default_alias:
        if sites_dict:
            st.error("Validation Error: Default site alias is not set, but sites are defined.")
            return False
        transformed_config['default_site_alias'] = '' 
    elif default_alias not in sites_dict:
        st.error(f"Validation Error: Default site alias '{default_alias}' does not match any defined site alias.")
        return False
    
    transformed_config.setdefault('name', 'MCP Jira')
    transformed_config.setdefault('log_level', 'INFO')

    try:
        with open(file_path, 'w') as f:
            yaml.dump(transformed_config, f, sort_keys=False, indent=2, default_flow_style=False)
        # Set action_feedback_message for success, to be displayed by app.py
        st.session_state.action_feedback_message = {
            "type": "success", 
            "text": f"Configuration saved successfully to '{file_path}'"
        }
        return True
    except Exception as e:
        st.error(f"Failed to save configuration to '{file_path}': {str(e)}")
        return False 