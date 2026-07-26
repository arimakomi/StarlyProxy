"""
Xray Inbound Manager
Manages inbound connections (protocols, ports, clients)
"""

from typing import Dict, List, Optional
from .config import XrayConfig


class InboundManager:
    """Manage Xray inbounds"""
    
    def __init__(self, config_dir: str = "/etc/starlyproxy/xray"):
        self.config = XrayConfig(config_dir)
        self.inbounds_file = self.config.config_dir / "inbounds.json"
        
    def list_inbounds(self) -> List[Dict]:
        """List all inbounds"""
        config = self.config.load_config()
        return config.get("inbounds", [])
    
    def get_inbound(self, tag: str) -> Optional[Dict]:
        """Get inbound by tag"""
        inbounds = self.list_inbounds()
        for inbound in inbounds:
            if inbound.get("tag") == tag:
                return inbound
        return None
    
    def add_inbound(self, protocol: str, port: int, settings: Dict,
                    stream_settings: Optional[Dict] = None,
                    tag: Optional[str] = None,
                    sniffing: Optional[Dict] = None) -> bool:
        """Add new inbound"""
        try:
            config = self.config.load_config()
            
            # Check if port already in use
            for inbound in config.get("inbounds", []):
                if inbound.get("port") == port:
                    return False
            
            inbound = {
                "tag": tag or f"{protocol}-{port}",
                "port": port,
                "protocol": protocol,
                "settings": settings,
                "streamSettings": stream_settings or {},
            }
            
            if sniffing:
                inbound["sniffing"] = sniffing
            
            if "inbounds" not in config:
                config["inbounds"] = []
            
            config["inbounds"].append(inbound)
            return self.config.save_config(config)
        except Exception as e:
            print(f"Error adding inbound: {e}")
            return False
    
    def remove_inbound(self, tag: str) -> bool:
        """Remove inbound by tag"""
        try:
            config = self.config.load_config()
            inbounds = config.get("inbounds", [])
            
            new_inbounds = [ib for ib in inbounds if ib.get("tag") != tag]
            
            if len(new_inbounds) == len(inbounds):
                return False  # Not found
            
            config["inbounds"] = new_inbounds
            return self.config.save_config(config)
        except Exception as e:
            print(f"Error removing inbound: {e}")
            return False
    
    def update_inbound(self, tag: str, updates: Dict) -> bool:
        """Update inbound configuration"""
        try:
            config = self.config.load_config()
            inbounds = config.get("inbounds", [])
            
            for i, inbound in enumerate(inbounds):
                if inbound.get("tag") == tag:
                    inbounds[i].update(updates)
                    config["inbounds"] = inbounds
                    return self.config.save_config(config)
            
            return False  # Not found
        except Exception as e:
            print(f"Error updating inbound: {e}")
            return False
    
    def add_vmess(self, port: int, clients: List[Dict],
                  ws_path: str = "/", tag: Optional[str] = None) -> bool:
        """Add VMess inbound with WebSocket"""
        settings = {
            "clients": clients,
            "disableInsecureEncryption": True
        }
        
        stream_settings = {
            "network": "ws",
            "security": "none",
            "wsSettings": {
                "path": ws_path
            }
        }
        
        sniffing = {
            "enabled": True,
            "destOverride": ["http", "tls"]
        }
        
        return self.add_inbound("vmess", port, settings, stream_settings, tag, sniffing)
    
    def add_vless(self, port: int, clients: List[Dict],
                  flow: str = "xtls-rprx-direct",
                  tag: Optional[str] = None) -> bool:
        """Add VLESS inbound"""
        settings = {
            "clients": clients,
            "decryption": "none",
            "fallbacks": []
        }
        
        stream_settings = {
            "network": "tcp",
            "security": "none",
            "tcpSettings": {
                "header": {
                    "type": "none"
                }
            }
        }
        
        sniffing = {
            "enabled": True,
            "destOverride": ["http", "tls"]
        }
        
        return self.add_inbound("vless", port, settings, stream_settings, tag, sniffing)
    
    def add_trojan(self, port: int, passwords: List[str],
                   tag: Optional[str] = None) -> bool:
        """Add Trojan inbound"""
        clients = [{"password": pwd, "email": f"user{i}@trojan"} 
                   for i, pwd in enumerate(passwords)]
        
        settings = {
            "clients": clients,
            "fallbacks": []
        }
        
        stream_settings = {
            "network": "tcp",
            "security": "none"
        }
        
        sniffing = {
            "enabled": True,
            "destOverride": ["http", "tls"]
        }
        
        return self.add_inbound("trojan", port, settings, stream_settings, tag, sniffing)
    
    def add_shadowsocks(self, port: int, password: str,
                        method: str = "aes-256-gcm",
                        tag: Optional[str] = None) -> bool:
        """Add Shadowsocks inbound"""
        settings = {
            "method": method,
            "password": password,
            "network": "tcp,udp"
        }
        
        return self.add_inbound("shadowsocks", port, settings, tag=tag)
    
    def get_inbound_stats(self, tag: str) -> Dict:
        """Get inbound statistics (placeholder)"""
        return {
            "tag": tag,
            "uplink": 0,
            "downlink": 0,
            "clients": 0
        }
