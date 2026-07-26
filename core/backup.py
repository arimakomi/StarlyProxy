"""
Backup and Restore System for StarlyProxy
Handles database and configuration backups
"""

import shutil
import tarfile
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict


class BackupManager:
    """Manages backups and restores"""
    
    def __init__(self, backup_dir: str = "/opt/starlyproxy/backups"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        self.base_dir = Path("/opt/starlyproxy")
        self.db_file = self.base_dir / "starlyproxy.db"
        self.config_file = self.base_dir / "panel_config.json"
        self.auth_file = self.base_dir / "auth.json"
    
    def create_backup(self, name: Optional[str] = None) -> str:
        """Create full backup"""
        if name is None:
            name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        backup_path = self.backup_dir / f"{name}.tar.gz"
        
        # Create tar archive
        with tarfile.open(backup_path, "w:gz") as tar:
            # Add database
            if self.db_file.exists():
                tar.add(self.db_file, arcname="starlyproxy.db")
            
            # Add panel config
            if self.config_file.exists():
                tar.add(self.config_file, arcname="panel_config.json")
            
            # Add auth config
            if self.auth_file.exists():
                tar.add(self.auth_file, arcname="auth.json")
            
            # Add instance configs directory
            instances_dir = self.base_dir / "instances"
            if instances_dir.exists():
                tar.add(instances_dir, arcname="instances")
        
        # Create metadata
        metadata = {
            "name": name,
            "created_at": datetime.now().isoformat(),
            "size_bytes": backup_path.stat().st_size,
            "files": ["starlyproxy.db", "panel_config.json", "auth.json", "instances/"]
        }
        
        metadata_path = self.backup_dir / f"{name}.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return str(backup_path)
    
    def restore_backup(self, name: str) -> bool:
        """Restore from backup"""
        backup_path = self.backup_dir / f"{name}.tar.gz"
        
        if not backup_path.exists():
            return False
        
        try:
            # Extract to temporary directory
            temp_dir = self.backup_dir / "temp_restore"
            temp_dir.mkdir(exist_ok=True)
            
            with tarfile.open(backup_path, "r:gz") as tar:
                tar.extractall(temp_dir)
            
            # Restore files
            if (temp_dir / "starlyproxy.db").exists():
                shutil.copy2(temp_dir / "starlyproxy.db", self.db_file)
            
            if (temp_dir / "panel_config.json").exists():
                shutil.copy2(temp_dir / "panel_config.json", self.config_file)
            
            if (temp_dir / "auth.json").exists():
                shutil.copy2(temp_dir / "auth.json", self.auth_file)
            
            if (temp_dir / "instances").exists():
                instances_target = self.base_dir / "instances"
                if instances_target.exists():
                    shutil.rmtree(instances_target)
                shutil.copytree(temp_dir / "instances", instances_target)
            
            # Cleanup
            shutil.rmtree(temp_dir)
            
            return True
            
        except Exception as e:
            print(f"Restore failed: {e}")
            return False
    
    def list_backups(self) -> List[Dict]:
        """List all available backups"""
        backups = []
        
        for backup_file in self.backup_dir.glob("*.tar.gz"):
            metadata_file = backup_file.with_suffix('.json')
            
            if metadata_file.exists():
                with open(metadata_file) as f:
                    metadata = json.load(f)
                    backups.append(metadata)
            else:
                # Create basic metadata
                backups.append({
                    "name": backup_file.stem,
                    "created_at": datetime.fromtimestamp(backup_file.stat().st_mtime).isoformat(),
                    "size_bytes": backup_file.stat().st_size
                })
        
        return sorted(backups, key=lambda x: x["created_at"], reverse=True)
    
    def delete_backup(self, name: str) -> bool:
        """Delete a backup"""
        backup_path = self.backup_dir / f"{name}.tar.gz"
        metadata_path = self.backup_dir / f"{name}.json"
        
        deleted = False
        
        if backup_path.exists():
            backup_path.unlink()
            deleted = True
        
        if metadata_path.exists():
            metadata_path.unlink()
        
        return deleted
    
    def cleanup_old_backups(self, keep_count: int = 10):
        """Keep only the most recent backups"""
        backups = self.list_backups()
        
        if len(backups) > keep_count:
            for backup in backups[keep_count:]:
                self.delete_backup(backup["name"])
