"""
Simple runner script for instances
Used by systemd service
"""

import sys
import time
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("StarlyProxy.Runner")

if len(sys.argv) < 2:
    logger.error("Usage: python -m core.runner <instance_name>")
    sys.exit(1)

instance_name = sys.argv[1]

# Import managers
from core import InstanceManager

logger.info(f"Starting instance: {instance_name}")

try:
    mgr = InstanceManager()
    config = mgr.config_mgr.load_instance_config(instance_name)
    
    if not config:
        logger.error(f"Instance not found: {instance_name}")
        sys.exit(1)
    
    # Start based on type
    if config['type'] == 'paqet':
        from proxy.paqet_wrapper import PaqetWrapper
        wrapper = PaqetWrapper(config)
    elif config['type'] == 'gfk':
        from proxy.gfk_wrapper import GFKWrapper
        wrapper = GFKWrapper(config)
    else:
        logger.error(f"Unknown instance type: {config['type']}")
        sys.exit(1)
    
    pid = wrapper.start()
    
    if pid:
        logger.info(f"Instance started with PID: {pid}")
        
        # Keep running and monitor
        while True:
            time.sleep(30)
            # Could add health checks here
    else:
        logger.error("Failed to start instance")
        sys.exit(1)
        
except KeyboardInterrupt:
    logger.info("Received interrupt signal, shutting down...")
    sys.exit(0)
except Exception as e:
    logger.error(f"Error running instance: {e}", exc_info=True)
    sys.exit(1)
