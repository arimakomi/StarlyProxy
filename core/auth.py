"""
Authentication Module for StarlyProxy
Simple but secure authentication system
"""

import hashlib
import secrets
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict


class AuthManager:
    """Authentication manager with session handling"""
    
    def __init__(self, config_file: str = "/opt/starlyproxy/auth.json"):
        self.config_file = Path(config_file)
        self.sessions: Dict[str, dict] = {}
        self.load_config()
    
    def load_config(self):
        """Load auth configuration"""
        if self.config_file.exists():
            with open(self.config_file) as f:
                self.config = json.load(f)
        else:
            # Default admin user
            self.config = {
                "users": {
                    "admin": {
                        "password_hash": self.hash_password("admin"),
                        "role": "admin",
                        "created_at": datetime.now().isoformat()
                    }
                },
                "session_timeout": 3600,  # 1 hour
                "max_sessions": 10
            }
            self.save_config()
    
    def save_config(self):
        """Save auth configuration"""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password with SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, username: str, password: str) -> bool:
        """Verify username and password"""
        if username not in self.config.get("users", {}):
            return False
        
        user = self.config["users"][username]
        return user["password_hash"] == self.hash_password(password)
    
    def create_session(self, username: str) -> str:
        """Create new session and return token"""
        token = secrets.token_urlsafe(32)
        
        self.sessions[token] = {
            "username": username,
            "created_at": datetime.now(),
            "expires_at": datetime.now() + timedelta(seconds=self.config["session_timeout"]),
            "role": self.config["users"][username]["role"]
        }
        
        # Clean old sessions
        self._cleanup_sessions()
        
        return token
    
    def verify_session(self, token: str) -> Optional[dict]:
        """Verify session token"""
        if token not in self.sessions:
            return None
        
        session = self.sessions[token]
        
        # Check expiration
        if datetime.now() > session["expires_at"]:
            del self.sessions[token]
            return None
        
        # Extend session
        session["expires_at"] = datetime.now() + timedelta(seconds=self.config["session_timeout"])
        
        return session
    
    def logout(self, token: str) -> bool:
        """Logout and remove session"""
        if token in self.sessions:
            del self.sessions[token]
            return True
        return False
    
    def _cleanup_sessions(self):
        """Remove expired sessions"""
        now = datetime.now()
        expired = [token for token, session in self.sessions.items() 
                   if now > session["expires_at"]]
        
        for token in expired:
            del self.sessions[token]
        
        # Limit max sessions
        if len(self.sessions) > self.config["max_sessions"]:
            # Remove oldest sessions
            sorted_sessions = sorted(self.sessions.items(), 
                                   key=lambda x: x[1]["created_at"])
            for token, _ in sorted_sessions[:-self.config["max_sessions"]]:
                del self.sessions[token]
    
    def add_user(self, username: str, password: str, role: str = "user") -> bool:
        """Add new user"""
        if username in self.config.get("users", {}):
            return False
        
        self.config["users"][username] = {
            "password_hash": self.hash_password(password),
            "role": role,
            "created_at": datetime.now().isoformat()
        }
        
        self.save_config()
        return True
    
    def change_password(self, username: str, old_password: str, new_password: str) -> bool:
        """Change user password"""
        if not self.verify_password(username, old_password):
            return False
        
        self.config["users"][username]["password_hash"] = self.hash_password(new_password)
        self.save_config()
        return True
    
    def delete_user(self, username: str) -> bool:
        """Delete user"""
        if username == "admin":  # Protect admin
            return False
        
        if username in self.config.get("users", {}):
            del self.config["users"][username]
            self.save_config()
            return True
        
        return False
    
    def list_users(self) -> list:
        """List all users"""
        return [
            {
                "username": username,
                "role": user["role"],
                "created_at": user["created_at"]
            }
            for username, user in self.config.get("users", {}).items()
        ]
