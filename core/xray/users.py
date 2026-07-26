"""
Xray User Manager
Manages clients/users for Xray protocols
"""

import json
import uuid
from typing import Dict, List, Optional
from datetime import datetime
from .config import XrayConfig


class UserManager:
    """Manage Xray users/clients"""
    
    def __init__(self, config_dir: str = "/etc/starlyproxy/xray"):
        self.config = XrayConfig(config_dir)
        self.users_file = self.config.config_dir / "users.json"
        self._init_users_db()
    
    def _init_users_db(self):
        """Initialize users database"""
        if not self.users_file.exists():
            self._save_users({})
    
    def _load_users(self) -> Dict:
        """Load users database"""
        if self.users_file.exists():
            with open(self.users_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_users(self, users: Dict) -> bool:
        """Save users database"""
        try:
            with open(self.users_file, 'w') as f:
                json.dump(users, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving users: {e}")
            return False
    
    def create_user(self, email: str, protocol: str = "vmess",
                    inbound_tag: str = "", uuid_str: Optional[str] = None,
                    enable: bool = True, traffic_limit: int = 0) -> Dict:
        """Create new user"""
        user_uuid = uuid_str or str(uuid.uuid4())
        
        user = {
            "uuid": user_uuid,
            "email": email,
            "protocol": protocol,
            "inbound_tag": inbound_tag,
            "enable": enable,
            "traffic_limit": traffic_limit,  # GB, 0 = unlimited
            "traffic_used": 0,
            "created_at": datetime.utcnow().isoformat(),
            "last_active": None,
            "expire_time": None
        }
        
        users = self._load_users()
        users[user_uuid] = user
        
        if self._save_users(users):
            return user
        return {}
    
    def list_users(self, inbound_tag: Optional[str] = None) -> List[Dict]:
        """List all users or filter by inbound"""
        users = self._load_users()
        user_list = list(users.values())
        
        if inbound_tag:
            user_list = [u for u in user_list if u.get("inbound_tag") == inbound_tag]
        
        return user_list
    
    def get_user(self, user_uuid: str) -> Optional[Dict]:
        """Get user by UUID"""
        users = self._load_users()
        return users.get(user_uuid)
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        users = self._load_users()
        for user in users.values():
            if user.get("email") == email:
                return user
        return None
    
    def update_user(self, user_uuid: str, updates: Dict) -> bool:
        """Update user information"""
        try:
            users = self._load_users()
            
            if user_uuid not in users:
                return False
            
            users[user_uuid].update(updates)
            return self._save_users(users)
        except Exception as e:
            print(f"Error updating user: {e}")
            return False
    
    def delete_user(self, user_uuid: str) -> bool:
        """Delete user"""
        try:
            users = self._load_users()
            
            if user_uuid not in users:
                return False
            
            del users[user_uuid]
            return self._save_users(users)
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False
    
    def enable_user(self, user_uuid: str) -> bool:
        """Enable user"""
        return self.update_user(user_uuid, {"enable": True})
    
    def disable_user(self, user_uuid: str) -> bool:
        """Disable user"""
        return self.update_user(user_uuid, {"enable": False})
    
    def update_traffic(self, user_uuid: str, upload: int, download: int) -> bool:
        """Update user traffic usage"""
        try:
            users = self._load_users()
            
            if user_uuid not in users:
                return False
            
            current = users[user_uuid].get("traffic_used", 0)
            users[user_uuid]["traffic_used"] = current + upload + download
            users[user_uuid]["last_active"] = datetime.utcnow().isoformat()
            
            return self._save_users(users)
        except Exception as e:
            print(f"Error updating traffic: {e}")
            return False
    
    def check_traffic_limit(self, user_uuid: str) -> bool:
        """Check if user exceeded traffic limit"""
        user = self.get_user(user_uuid)
        if not user:
            return False
        
        limit = user.get("traffic_limit", 0)
        if limit == 0:  # Unlimited
            return True
        
        used = user.get("traffic_used", 0)
        return used < (limit * 1024 * 1024 * 1024)  # Convert GB to bytes
    
    def set_expire_time(self, user_uuid: str, expire_time: str) -> bool:
        """Set user expiration time (ISO format)"""
        return self.update_user(user_uuid, {"expire_time": expire_time})
    
    def is_expired(self, user_uuid: str) -> bool:
        """Check if user is expired"""
        user = self.get_user(user_uuid)
        if not user:
            return True
        
        expire_time = user.get("expire_time")
        if not expire_time:
            return False
        
        try:
            expire_dt = datetime.fromisoformat(expire_time)
            return datetime.utcnow() > expire_dt
        except Exception:
            return False
    
    def generate_vmess_link(self, user_uuid: str, server_address: str,
                            server_port: int, remarks: str = "") -> str:
        """Generate VMess link for user"""
        user = self.get_user(user_uuid)
        if not user:
            return ""
        
        config = {
            "v": "2",
            "ps": remarks or user.get("email", ""),
            "add": server_address,
            "port": str(server_port),
            "id": user.get("uuid"),
            "aid": "0",
            "net": "ws",
            "type": "none",
            "host": "",
            "path": "/",
            "tls": ""
        }
        
        import base64
        config_str = json.dumps(config)
        encoded = base64.b64encode(config_str.encode()).decode()
        return f"vmess://{encoded}"
    
    def generate_vless_link(self, user_uuid: str, server_address: str,
                            server_port: int, remarks: str = "") -> str:
        """Generate VLESS link for user"""
        user = self.get_user(user_uuid)
        if not user:
            return ""
        
        params = f"type=tcp&security=none"
        remark = remarks or user.get("email", "")
        
        return f"vless://{user.get('uuid')}@{server_address}:{server_port}?{params}#{remark}"
    
    def get_user_stats(self, user_uuid: str) -> Dict:
        """Get user statistics"""
        user = self.get_user(user_uuid)
        if not user:
            return {}
        
        return {
            "uuid": user_uuid,
            "email": user.get("email"),
            "protocol": user.get("protocol"),
            "enable": user.get("enable"),
            "traffic_used_gb": user.get("traffic_used", 0) / (1024**3),
            "traffic_limit_gb": user.get("traffic_limit", 0),
            "created_at": user.get("created_at"),
            "last_active": user.get("last_active"),
            "expire_time": user.get("expire_time"),
            "is_expired": self.is_expired(user_uuid),
            "traffic_exceeded": not self.check_traffic_limit(user_uuid)
        }
