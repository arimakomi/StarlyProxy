"""
Xray Configuration Manager
Handles Xray-core configuration generation and management
"""

import json
import uuid
from pathlib import Path
from typing import Dict, List, Optional


class XrayConfig:
    """Xray configuration builder"""
    
    def __init__(self, config_dir: str = "/etc/starlyproxy/xray"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_dir / "config.json"
        
    def generate_uuid(self) -> str:
        """Generate UUID for clients"""
        return str(uuid.uuid4())
    
    def create_default_config(self) -> Dict:
        """Create default Xray configuration"""
        return {
            "log": {
                "access": str(self.config_dir / "access.log"),
                "error": str(self.config_dir / "error.log"),
                "loglevel": "warning"
            },
            "inbounds": [],
            "outbounds": [
                {
                    "protocol": "freedom",
                    "tag": "direct",
                    "settings": {}
                },
                {
                    "protocol": "blackhole",
                    "tag": "block",
                    "settings": {}
                }
            ],
            "routing": {
                "domainStrategy": "AsIs",
                "rules": []
            },
            "policy": {
                "levels": {
                    "0": {
                        "handshake": 4,
                        "connIdle": 300,
                        "uplinkOnly": 2,
                        "downlinkOnly": 5
                    }
                },
                "system": {
                    "statsInboundUplink": True,
                    "statsInboundDownlink": True
                }
            },
            "stats": {}
        }
    
    def add_inbound(self, protocol: str, port: int, settings: Dict, 
                    stream_settings: Optional[Dict] = None, 
                    tag: Optional[str] = None) -> Dict:
        """Add inbound configuration"""
        inbound = {
            "tag": tag or f"{protocol}-{port}",
            "port": port,
            "protocol": protocol,
            "settings": settings,
            "streamSettings": stream_settings or {}
        }
        return inbound
    
    def add_vmess_inbound(self, port: int, clients: List[Dict], 
                          tag: Optional[str] = None) -> Dict:
        """Add VMess inbound"""
        settings = {
            "clients": clients,
            "disableInsecureEncryption": True
        }
        return self.add_inbound("vmess", port, settings, tag=tag)
    
    def add_vless_inbound(self, port: int, clients: List[Dict],
                          decryption: str = "none",
                          tag: Optional[str] = None) -> Dict:
        """Add VLESS inbound"""
        settings = {
            "clients": clients,
            "decryption": decryption
        }
        return self.add_inbound("vless", port, settings, tag=tag)
    
    def add_trojan_inbound(self, port: int, clients: List[Dict],
                           tag: Optional[str] = None) -> Dict:
        """Add Trojan inbound"""
        settings = {
            "clients": clients,
            "fallbacks": []
        }
        return self.add_inbound("trojan", port, settings, tag=tag)
    
    def add_shadowsocks_inbound(self, port: int, password: str,
                                 method: str = "aes-256-gcm",
                                 tag: Optional[str] = None) -> Dict:
        """Add Shadowsocks inbound"""
        settings = {
            "method": method,
            "password": password,
            "network": "tcp,udp"
        }
        return self.add_inbound("shadowsocks", port, settings, tag=tag)
    
    def add_outbound(self, protocol: str, settings: Dict,
                     tag: str, stream_settings: Optional[Dict] = None) -> Dict:
        """Add outbound configuration"""
        outbound = {
            "tag": tag,
            "protocol": protocol,
            "settings": settings
        }
        if stream_settings:
            outbound["streamSettings"] = stream_settings
        return outbound
    
    def create_ws_stream(self, path: str = "/", host: str = "") -> Dict:
        """WebSocket stream settings"""
        return {
            "network": "ws",
            "security": "none",
            "wsSettings": {
                "path": path,
                "headers": {"Host": host} if host else {}
            }
        }
    
    def create_tcp_stream(self, header_type: str = "none") -> Dict:
        """TCP stream settings"""
        return {
            "network": "tcp",
            "security": "none",
            "tcpSettings": {
                "header": {
                    "type": header_type
                }
            }
        }
    
    def create_tls_stream(self, domain: str, cert_file: str, key_file: str) -> Dict:
        """TLS stream settings"""
        return {
            "security": "tls",
            "tlsSettings": {
                "serverName": domain,
                "certificates": [
                    {
                        "certificateFile": cert_file,
                        "keyFile": key_file
                    }
                ]
            }
        }
    
    def load_config(self) -> Dict:
        """Load existing configuration"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return self.create_default_config()
    
    def save_config(self, config: Dict) -> bool:
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def add_routing_rule(self, config: Dict, rule: Dict) -> Dict:
        """Add routing rule"""
        if "routing" not in config:
            config["routing"] = {"rules": []}
        config["routing"]["rules"].append(rule)
        return config
    
    def create_client(self, email: str, uuid: Optional[str] = None,
                      alter_id: int = 0) -> Dict:
        """Create client configuration"""
        return {
            "id": uuid or self.generate_uuid(),
            "email": email,
            "alterId": alter_id
        }
