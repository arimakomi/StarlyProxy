"""
Multi-Server Management for StarlyProxy
Manage multiple servers from one dashboard
"""

import requests
import json
from typing import List, Dict, Optional
from pathlib import Path
from datetime import datetime


class MultiServerManager:
    """Manages multiple StarlyProxy servers"""
    
    def __init__(self, config_file: str = "/opt/starlyproxy/servers.json"):
        self.config_file = Path(config_file)
        self.servers: Dict[str, dict] = {}
        self.load_servers()
    
    def load_servers(self):
        """Load server configurations"""
        if self.config_file.exists():
            with open(self.config_file) as f:
                self.servers = json.load(f)
        else:
            self.servers = {}
            self.save_servers()
    
    def save_servers(self):
        """Save server configurations"""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self.servers, f, indent=2)
    
    def add_server(self, name: str, host: str, port: int = 5000, 
                   api_key: Optional[str] = None) -> bool:
        """Add new server"""
        if name in self.servers:
            return False
        
        self.servers[name] = {
            "host": host,
            "port": port,
            "api_key": api_key,
            "added_at": datetime.now().isoformat(),
            "enabled": True
        }
        
        self.save_servers()
        return True
    
    def remove_server(self, name: str) -> bool:
        """Remove server"""
        if name in self.servers:
            del self.servers[name]
            self.save_servers()
            return True
        return False
    
    def get_server_url(self, name: str) -> Optional[str]:
        """Get server base URL"""
        if name not in self.servers:
            return None
        
        server = self.servers[name]
        return f"http://{server['host']}:{server['port']}"
    
    def check_server_health(self, name: str) -> Dict:
        """Check if server is reachable"""
        url = self.get_server_url(name)
        if not url:
            return {"status": "error", "message": "Server not found"}
        
        try:
            response = requests.get(f"{url}/api/system", timeout=5)
            if response.status_code == 200:
                return {
                    "status": "online",
                    "data": response.json()
                }
            else:
                return {
                    "status": "error",
                    "message": f"HTTP {response.status_code}"
                }
        except requests.exceptions.Timeout:
            return {"status": "timeout", "message": "Connection timeout"}
        except requests.exceptions.ConnectionError:
            return {"status": "offline", "message": "Cannot connect"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_server_instances(self, name: str) -> Optional[List[Dict]]:
        """Get instances from remote server"""
        url = self.get_server_url(name)
        if not url:
            return None
        
        try:
            response = requests.get(f"{url}/api/instances", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get("instances", [])
            return None
        except Exception:
            return None
    
    def start_remote_instance(self, server_name: str, instance_name: str) -> bool:
        """Start instance on remote server"""
        url = self.get_server_url(server_name)
        if not url:
            return False
        
        try:
            response = requests.post(
                f"{url}/api/instances/{instance_name}/start",
                timeout=10
            )
            return response.status_code == 200
        except Exception:
            return False
    
    def stop_remote_instance(self, server_name: str, instance_name: str) -> bool:
        """Stop instance on remote server"""
        url = self.get_server_url(server_name)
        if not url:
            return False
        
        try:
            response = requests.post(
                f"{url}/api/instances/{instance_name}/stop",
                timeout=10
            )
            return response.status_code == 200
        except Exception:
            return False
    
    def get_all_servers_status(self) -> Dict[str, dict]:
        """Get status of all configured servers"""
        status = {}
        
        for name, config in self.servers.items():
            if not config.get("enabled", True):
                status[name] = {"status": "disabled"}
                continue
            
            health = self.check_server_health(name)
            instances = self.get_server_instances(name) if health["status"] == "online" else []
            
            status[name] = {
                "config": config,
                "health": health,
                "instances": instances or [],
                "instance_count": len(instances) if instances else 0
            }
        
        return status
    
    def list_servers(self) -> List[Dict]:
        """List all configured servers"""
        return [
            {
                "name": name,
                **config
            }
            for name, config in self.servers.items()
        ]
