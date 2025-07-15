"""
Configuration management for RTAR application.
"""

import json
import os
import logging
from typing import Any, Dict, Optional


class ConfigManager:
    """Manages application configuration with hierarchical key support."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration manager."""
        self.config_path = config_path or self._get_default_config_path()
        self.config: Dict[str, Any] = {}
        self.load_config()
        self.setup_logging()
    
    def _get_default_config_path(self) -> str:
        """Get default configuration file path."""
        return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config', 'config.json')
    
    def load_config(self) -> bool:
        """Load configuration from file."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                self.setup_logging()  # Re-setup logging after config reload
                return True
            else:
                print(f"Configuration file not found: {self.config_path}")
                return False
        except Exception as e:
            print(f"Error loading configuration: {e}")
            return False
    
    def save_config(self) -> bool:
        """Save current configuration to file."""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"Error saving configuration: {e}")
            return False
    
    def get_value(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value by key path (e.g., 'reality.mediaId').
        
        Args:
            key_path: Dot-separated key path
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key_path.split('.')
        current = self.config
        
        try:
            for key in keys:
                if isinstance(current, dict):
                    if key in current:
                        value = current[key]
                        # Handle config format with 'value' key
                        if isinstance(value, dict) and 'value' in value:
                            current = value['value']
                        else:
                            current = value
                    else:
                        return default
                else:
                    return default
            return current
        except (KeyError, TypeError):
            return default
    
    def set_value(self, key_path: str, value: Any) -> bool:
        """
        Set configuration value by key path.
        
        Args:
            key_path: Dot-separated key path
            value: Value to set
            
        Returns:
            True if successful, False otherwise
        """
        keys = key_path.split('.')
        current = self.config
        
        try:
            for key in keys[:-1]:
                if key not in current:
                    current[key] = {}
                current = current[key]
            
            last_key = keys[-1]
            if isinstance(current.get(last_key), dict) and 'value' in current[last_key]:
                current[last_key]['value'] = value
            else:
                current[last_key] = value
            
            return True
        except (KeyError, TypeError):
            return False
    
    def update_config(self, new_config: Dict[str, Any]) -> bool:
        """Update configuration with new values."""
        try:
            self.config.update(new_config)
            return self.save_config()
        except Exception as e:
            print(f"Error updating configuration: {e}")
            return False
    
    def get_all_config(self) -> Dict[str, Any]:
        """Get all configuration as dictionary."""
        return self.config.copy()
    
    def validate_config(self) -> bool:
        """Validate required configuration keys."""
        required_keys = [
            'reality.mediaId',
            'reality.vLiveId',
            'reality.gid',
            'reality.auth',
            'openai.apiKey',
            'openai.apiBase',
            'openai.model'
        ]
        
        for key in required_keys:
            if self.get_value(key) is None:
                print(f"Missing required configuration: {key}")
                return False
        
        return True
    
    def setup_logging(self):
        """Setup logging based on debug configuration."""
        debug_mode = self.get_value('debug', False)
        
        # Configure root logger
        root_logger = logging.getLogger()
        
        # Clear existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        if debug_mode:
            # Debug mode - detailed logging
            logging.basicConfig(
                level=logging.DEBUG,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.StreamHandler(),
                    logging.FileHandler('rtar_debug.log', encoding='utf-8')
                ]
            )
            logging.getLogger('urllib3').setLevel(logging.WARNING)
            logging.getLogger('websockets').setLevel(logging.WARNING)
            logging.getLogger('httpx').setLevel(logging.WARNING)
            logging.getLogger('openai').setLevel(logging.WARNING)
        else:
            # Normal mode - minimal logging
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s',
                handlers=[logging.StreamHandler()]
            )
            # Suppress noisy libraries
            logging.getLogger('urllib3').setLevel(logging.ERROR)
            logging.getLogger('websockets').setLevel(logging.ERROR)
            logging.getLogger('aiohttp').setLevel(logging.ERROR)
            logging.getLogger('httpx').setLevel(logging.ERROR)
            logging.getLogger('openai').setLevel(logging.ERROR)
            logging.getLogger('httpcore').setLevel(logging.ERROR)
    
    def is_debug_mode(self) -> bool:
        """Check if debug mode is enabled."""
        return self.get_value('debug', False)