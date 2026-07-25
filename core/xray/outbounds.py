"""
Xray Outbound Manager
Manages outbound connections and routing
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from .config import XrayConfig


class OutboundManager:
    """Manage Xray outbounds"""
    
    def __init__(self, config_dir: str = "/etc/starlyproxy/xray"):
        self.config = XrayConfig(config_dir)
        
    def list_outbounds(self) -> List[Dict]:
        """List all outbounds"""
        config = self.config.load_config()
        return config.get("outbounds", [])
    
    def get_outbound(self, tag: str) -> Optional[Dict]:
        """Get outbound by tag"""
        outbounds = self.list_outbounds()
        for outbound in outbounds:
            if outbound.get("tag") == tag:
                return outbound
        return None
    
    def add_outbound(self, protocol: str, tag: str, settings: Dict,
                     stream_settings: Optional[Dict] = None) -> bool:
        """Add new outbound"""
        try:
            config = self.config.load_config()
            
            # Check if tag already exists
            for outbound in config.get("outbounds", []):
                if outbound.get("tag") == tag:
                    return False
            
            outbound = {
                "tag": tag,
                "protocol": protocol,
                "settings": settings
            }
            
            if stream_settings:
                outbound["streamSettings"] = stream_settings
            
            if "outbounds" not in config:
                config["outbounds"] = []
            
            config["outbounds"].append(outbound)
            return self.config.save_config(config)
        except Exception as e:
            print(f"Error adding outbound: {e}")
            return False
    
    def remove_outbound(self, tag: str) -> bool:
        """Remove outbound by tag"""
        try:
            config = self.config.load_config()
            outbounds = config.get("outbounds", [])
            
            # Don't allow removing default outbounds
            if tag in ["direct", "block"]:
                return False
            
            new_outbounds = [ob for ob in outbounds if ob.get("tag") != tag]
            
            if len(new_outbounds) == len(outbounds):
                return False  # Not found
            
            config["outbounds"] = new_outbounds
            return self.config.save_config(config)
        except Exception as e:
            print(f"Error removing outbound: {e}")
            return False
    
    def update_outbound(self, tag: str, updates: Dict) -> bool:
        """Update outbound configuration"""
        try:
            config = self.config.load_config()
            outbounds = config.get("outbounds", [])
            
            for i, outbound in enumerate(outbounds):
                if outbound.get("tag") == tag:
                    outbounds[i].update(updates)
                    config["outbounds"] = outbounds
                    return self.config.save_config(config)
            
            return False  # Not found
        except Exception as e:
            print(f"Error updating outbound: {e}")
            return False
    
    def connect_server(self, server_address: str, server_port: int,
                       protocol: str = "vmess", uuid: str = "",
                       tag: str = "proxy-server") -> bool:
        """Connect to remote server as outbound"""
        try:
            settings = {}
            
            if protocol == "vmess":
                settings = {
                    "vnext": [{
                        "address": server_address,
                        "port": server_port,
                        "users": [{
                            "id": uuid,
                            "alterId": 0,
                            "security": "auto"
                        }]
                    }]
                }
            elif protocol == "vless":
                settings = {
                    "vnext": [{
                        "address": server_address,
                        "port": server_port,
                        "users": [{
                            "id": uuid,
                            "encryption": "none"
                        }]
                    }]
                }
            elif protocol == "trojan":
                settings = {
                    "servers": [{
                        "address": server_address,
                        "port": server_port,
                        "password": uuid  # Using uuid field as password
                    }]
                }
            elif protocol == "shadowsocks":
                settings = {
                    "servers": [{
                        "address": server_address,
                        "port": server_port,
                        "method": "aes-256-gcm",
                        "password": uuid
                    }]
                }
            else:
                return False
            
            stream_settings = {
                "network": "tcp",
                "security": "none"
            }
            
            return self.add_outbound(protocol, tag, settings, stream_settings)
        except Exception as e:
            print(f"Error connecting server: {e}")
            return False
    
    def add_routing_rule(self, rule_type: str, values: List[str],
                         outbound_tag: str) -> bool:
        """Add routing rule"""
        try:
            config = self.config.load_config()
            
            rule = {
                "type": "field",
                "outboundTag": outbound_tag
            }
            
            if rule_type == "domain":
                rule["domain"] = values
            elif rule_type == "ip":
                rule["ip"] = values
            elif rule_type == "protocol":
                rule["protocol"] = values
            elif rule_type == "port":
                rule["port"] = values[0] if len(values) == 1 else ",".join(values)
            else:
                return False
            
            if "routing" not in config:
                config["routing"] = {"rules": []}
            
            if "rules" not in config["routing"]:
                config["routing"]["rules"] = []
            
            config["routing"]["rules"].append(rule)
            return self.config.save_config(config)
        except Exception as e:
            print(f"Error adding routing rule: {e}")
            return False
    
    def list_routing_rules(self) -> List[Dict]:
        """List all routing rules"""
        config = self.config.load_config()
        routing = config.get("routing", {})
        return routing.get("rules", [])
    
    def remove_routing_rule(self, index: int) -> bool:
        """Remove routing rule by index"""
        try:
            config = self.config.load_config()
            rules = config.get("routing", {}).get("rules", [])
            
            if 0 <= index < len(rules):
                rules.pop(index)
                config["routing"]["rules"] = rules
                return self.config.save_config(config)
            
            return False
        except Exception as e:
            print(f"Error removing routing rule: {e}")
            return False
