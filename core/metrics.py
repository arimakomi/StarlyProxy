"""
Metrics Collection System for StarlyProxy
Collects and stores instance metrics
"""

import time
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from .database import DatabaseManager


class MetricsCollector:
    """Collects performance metrics for instances"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.start_time = time.time()
    
    def collect_instance_metrics(self, instance_name: str, pid: int) -> Optional[Dict]:
        """Collect metrics for a running instance"""
        try:
            process = psutil.Process(pid)
            
            # Get process info
            with process.oneshot():
                cpu_percent = process.cpu_percent(interval=0.1)
                memory_info = process.memory_info()
                connections = len(process.connections())
                
            metrics = {
                "timestamp": datetime.now().isoformat(),
                "instance_name": instance_name,
                "cpu_percent": cpu_percent,
                "memory_mb": memory_info.rss / (1024 * 1024),
                "memory_percent": process.memory_percent(),
                "connections": connections,
                "status": process.status()
            }
            
            # Store in database
            self._store_metrics(metrics)
            
            return metrics
            
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return None
    
    def collect_system_metrics(self) -> Dict:
        """Collect overall system metrics"""
        cpu = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        net_io = psutil.net_io_counters()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "cpu_percent": cpu,
            "memory_percent": memory.percent,
            "memory_used_mb": memory.used / (1024 * 1024),
            "memory_total_mb": memory.total / (1024 * 1024),
            "disk_percent": disk.percent,
            "disk_used_gb": disk.used / (1024**3),
            "disk_total_gb": disk.total / (1024**3),
            "network_sent_mb": net_io.bytes_sent / (1024 * 1024),
            "network_recv_mb": net_io.bytes_recv / (1024 * 1024),
            "uptime_seconds": time.time() - self.start_time
        }
    
    def get_instance_history(self, instance_name: str, hours: int = 24) -> List[Dict]:
        """Get metrics history for instance"""
        # This would query the database
        # For now, return empty list
        return []
    
    def get_system_history(self, hours: int = 24) -> List[Dict]:
        """Get system metrics history"""
        return []
    
    def _store_metrics(self, metrics: Dict):
        """Store metrics in database"""
        # Implementation would store in database
        pass
    
    def cleanup_old_metrics(self, days: int = 7):
        """Remove metrics older than specified days"""
        cutoff = datetime.now() - timedelta(days=days)
        # Implementation would delete from database
        pass
