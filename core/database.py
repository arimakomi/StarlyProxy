"""
Database Manager for StarlyProxy
SQLite database for tracking instances, stats, and logs
"""

import sqlite3
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger("StarlyProxy.Database")


class DatabaseManager:
    """Database manager for StarlyProxy"""
    
    def __init__(self, db_path: str = "/opt/starlyproxy/starlyproxy.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = None
        self._init_database()
    
    def _init_database(self):
        """Initialize database with required tables"""
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        
        # Create tables
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS instances (
                name TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                mode TEXT NOT NULL,
                status TEXT DEFAULT 'stopped',
                socks_port INTEGER,
                server_address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                config_json TEXT,
                pid INTEGER
            );
            
            CREATE TABLE IF NOT EXISTS stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                instance_name TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                bytes_sent INTEGER DEFAULT 0,
                bytes_received INTEGER DEFAULT 0,
                connections INTEGER DEFAULT 0,
                FOREIGN KEY (instance_name) REFERENCES instances(name) ON DELETE CASCADE
            );
            
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                instance_name TEXT,
                level TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE INDEX IF NOT EXISTS idx_stats_instance ON stats(instance_name);
            CREATE INDEX IF NOT EXISTS idx_stats_timestamp ON stats(timestamp);
            CREATE INDEX IF NOT EXISTS idx_logs_instance ON logs(instance_name);
            CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON logs(timestamp);
        """)
        self.conn.commit()
    
    def add_instance(self, name: str, instance_type: str, mode: str, 
                     socks_port: int, server_address: str, config: Dict[str, Any]) -> bool:
        """Add new instance to database"""
        try:
            self.conn.execute("""
                INSERT INTO instances (name, type, mode, socks_port, server_address, config_json)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (name, instance_type, mode, socks_port, server_address, json.dumps(config)))
            self.conn.commit()
            logger.info(f"Added instance to DB: {name}")
            return True
        except sqlite3.IntegrityError:
            logger.error(f"Instance already exists: {name}")
            return False
        except Exception as e:
            logger.error(f"Failed to add instance: {e}")
            return False
    
    def update_instance_status(self, name: str, status: str, pid: Optional[int] = None) -> bool:
        """Update instance status"""
        try:
            if pid is not None:
                self.conn.execute("""
                    UPDATE instances SET status = ?, pid = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE name = ?
                """, (status, pid, name))
            else:
                self.conn.execute("""
                    UPDATE instances SET status = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE name = ?
                """, (status, name))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to update instance status: {e}")
            return False
    
    def get_instance(self, name: str) -> Optional[Dict[str, Any]]:
        """Get instance by name"""
        try:
            cursor = self.conn.execute("SELECT * FROM instances WHERE name = ?", (name,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
        except Exception as e:
            logger.error(f"Failed to get instance: {e}")
            return None
    
    def list_instances(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all instances, optionally filtered by status"""
        try:
            if status:
                cursor = self.conn.execute("SELECT * FROM instances WHERE status = ?", (status,))
            else:
                cursor = self.conn.execute("SELECT * FROM instances")
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to list instances: {e}")
            return []
    
    def delete_instance(self, name: str) -> bool:
        """Delete instance from database"""
        try:
            self.conn.execute("DELETE FROM instances WHERE name = ?", (name,))
            self.conn.commit()
            logger.info(f"Deleted instance from DB: {name}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete instance: {e}")
            return False
    
    def add_log(self, instance_name: Optional[str], level: str, message: str):
        """Add log entry"""
        try:
            self.conn.execute("""
                INSERT INTO logs (instance_name, level, message)
                VALUES (?, ?, ?)
            """, (instance_name, level, message))
            self.conn.commit()
        except Exception as e:
            logger.error(f"Failed to add log: {e}")
    
    def get_logs(self, instance_name: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get logs, optionally filtered by instance"""
        try:
            if instance_name:
                cursor = self.conn.execute("""
                    SELECT * FROM logs WHERE instance_name = ? 
                    ORDER BY timestamp DESC LIMIT ?
                """, (instance_name, limit))
            else:
                cursor = self.conn.execute("""
                    SELECT * FROM logs ORDER BY timestamp DESC LIMIT ?
                """, (limit,))
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get logs: {e}")
            return []
    
    def add_stats(self, instance_name: str, bytes_sent: int, bytes_received: int, connections: int):
        """Add statistics entry"""
        try:
            self.conn.execute("""
                INSERT INTO stats (instance_name, bytes_sent, bytes_received, connections)
                VALUES (?, ?, ?, ?)
            """, (instance_name, bytes_sent, bytes_received, connections))
            self.conn.commit()
        except Exception as e:
            logger.error(f"Failed to add stats: {e}")
    
    def get_stats(self, instance_name: str, hours: int = 24) -> List[Dict[str, Any]]:
        """Get statistics for instance within specified hours"""
        try:
            cursor = self.conn.execute("""
                SELECT * FROM stats 
                WHERE instance_name = ? AND timestamp >= datetime('now', '-' || ? || ' hours')
                ORDER BY timestamp DESC
            """, (instance_name, hours))
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return []
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
