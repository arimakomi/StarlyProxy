"""
Configuration Manager for StarlyProxy
Handles all config file operations and validation
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger("StarlyProxy.Config")


class ConfigManager:
    """Central configuration manager for StarlyProxy instances"""
    
    def __init__(self, config_dir: str = "/opt/starlyproxy"):
        self.config_dir = Path(config_dir)
        self.instances_dir = self.config_dir / "instances"
        self.main_config_file = self.config_dir / "config.json"
        
        # Create directories if not exist
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.instances_dir.mkdir(parents=True, exist_ok=True)
        
        # Load or create main config
        self.main_config = self._load_main_config()
    
    def _load_main_config(self) -> Dict[str, Any]:
        """Load main configuration file"""
        if self.main_config_file.exists():
            try:
                with open(self.main_config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
        
        # Default config
        default_config = {
            "version": "3.0.1",
            "base_socks_port": 1080,
            "base_quic_port": 14000,
            "log_level": "INFO",
            "auto_restart": True,
            "max_instances": 20
        }
        self._save_main_config(default_config)
        return default_config
    
    def _save_main_config(self, config: Dict[str, Any]) -> bool:
        """Save main configuration"""
        try:
            with open(self.main_config_file, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            return False
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a configuration setting"""
        return self.main_config.get(key, default)
    
    def set_setting(self, key: str, value: Any) -> bool:
        """Set a configuration setting"""
        self.main_config[key] = value
        return self._save_main_config(self.main_config)
    
    def get_instance_config_path(self, instance_name: str) -> Path:
        """Get path to instance config file"""
        return self.instances_dir / f"{instance_name}.json"
    
    def save_instance_config(self, instance_name: str, config: Dict[str, Any]) -> bool:
        """Save instance configuration"""
        try:
            config_path = self.get_instance_config_path(instance_name)
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            logger.info(f"Saved config for instance: {instance_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to save instance config: {e}")
            return False
    
    def load_instance_config(self, instance_name: str) -> Optional[Dict[str, Any]]:
        """Load instance configuration"""
        try:
            config_path = self.get_instance_config_path(instance_name)
            if not config_path.exists():
                return None
            
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load instance config: {e}")
            return None
    
    def list_instances(self) -> list:
        """List all configured instances"""
        instances = []
        for config_file in self.instances_dir.glob("*.json"):
            instance_name = config_file.stem
            instances.append(instance_name)
        return sorted(instances)
    
    def delete_instance_config(self, instance_name: str) -> bool:
        """Delete instance configuration"""
        try:
            config_path = self.get_instance_config_path(instance_name)
            if config_path.exists():
                config_path.unlink()
                logger.info(f"Deleted config for instance: {instance_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete instance config: {e}")
            return False
