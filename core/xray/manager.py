"""
Xray Core Manager
Handles Xray-core process lifecycle and configuration management
"""

import subprocess
import signal
import os
import psutil
from pathlib import Path
from typing import Optional, Dict, List, Tuple


class XrayManager:
    """Manage Xray-core process"""
    
    def __init__(self, config_dir: str = "/etc/starlyproxy/xray",
                 binary_path: str = "/usr/local/bin/xray"):
        self.config_dir = Path(config_dir)
        self.binary_path = Path(binary_path)
        self.config_file = self.config_dir / "config.json"
        self.pid_file = self.config_dir / "xray.pid"
        self.log_file = self.config_dir / "xray.log"
        
    def is_installed(self) -> bool:
        """Check if Xray is installed"""
        return self.binary_path.exists()
    
    def install_xray(self) -> bool:
        """Install Xray-core"""
        try:
            # Download and install Xray
            install_script = """
            bash -c "$(curl -L https://github.com/XTLS/Xray-install/raw/main/install-release.sh)" @ install
            """
            result = subprocess.run(
                install_script,
                shell=True,
                capture_output=True,
                timeout=300
            )
            return result.returncode == 0
        except Exception as e:
            print(f"Installation failed: {e}")
            return False
    
    def get_version(self) -> Optional[str]:
        """Get Xray version"""
        try:
            result = subprocess.run(
                [str(self.binary_path), "version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                # Parse version from output
                for line in result.stdout.split('\n'):
                    if 'Xray' in line:
                        return line.strip()
            return None
        except Exception:
            return None
    
    def start(self) -> bool:
        """Start Xray service"""
        if not self.config_file.exists():
            print("Configuration file not found")
            return False
        
        if self.is_running():
            print("Xray is already running")
            return True
        
        try:
            # Start Xray process
            process = subprocess.Popen(
                [str(self.binary_path), "run", "-c", str(self.config_file)],
                stdout=open(self.log_file, 'a'),
                stderr=subprocess.STDOUT,
                start_new_session=True
            )
            
            # Save PID
            with open(self.pid_file, 'w') as f:
                f.write(str(process.pid))
            
            return True
        except Exception as e:
            print(f"Failed to start Xray: {e}")
            return False
    
    def stop(self) -> bool:
        """Stop Xray service"""
        try:
            if not self.pid_file.exists():
                return True
            
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            try:
                os.kill(pid, signal.SIGTERM)
                # Wait for process to terminate
                for _ in range(10):
                    try:
                        os.kill(pid, 0)
                        subprocess.run(['sleep', '0.5'])
                    except OSError:
                        break
                else:
                    # Force kill if still running
                    os.kill(pid, signal.SIGKILL)
            except OSError:
                pass  # Process already dead
            
            # Remove PID file
            self.pid_file.unlink(missing_ok=True)
            return True
        except Exception as e:
            print(f"Failed to stop Xray: {e}")
            return False
    
    def restart(self) -> bool:
        """Restart Xray service"""
        self.stop()
        return self.start()
    
    def is_running(self) -> bool:
        """Check if Xray is running"""
        if not self.pid_file.exists():
            return False
        
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            # Check if process exists
            os.kill(pid, 0)
            return True
        except (OSError, ValueError):
            return False
    
    def get_status(self) -> Dict:
        """Get Xray service status"""
        status = {
            "running": self.is_running(),
            "installed": self.is_installed(),
            "version": self.get_version(),
            "config_exists": self.config_file.exists()
        }
        
        if status["running"]:
            try:
                with open(self.pid_file, 'r') as f:
                    pid = int(f.read().strip())
                process = psutil.Process(pid)
                status["pid"] = pid
                status["memory"] = process.memory_info().rss / 1024 / 1024  # MB
                status["cpu"] = process.cpu_percent(interval=0.1)
                status["uptime"] = int(process.create_time())
            except Exception:
                pass
        
        return status
    
    def get_logs(self, lines: int = 50) -> List[str]:
        """Get Xray logs"""
        if not self.log_file.exists():
            return []
        
        try:
            result = subprocess.run(
                ['tail', '-n', str(lines), str(self.log_file)],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.stdout.split('\n')
        except Exception:
            return []
    
    def test_config(self) -> Tuple[bool, str]:
        """Test Xray configuration"""
        if not self.config_file.exists():
            return False, "Configuration file not found"
        
        try:
            result = subprocess.run(
                [str(self.binary_path), "test", "-c", str(self.config_file)],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return True, "Configuration is valid"
            else:
                return False, result.stderr
        except Exception as e:
            return False, str(e)
