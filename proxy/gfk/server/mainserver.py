import subprocess
import os
import time
import sys
import signal


scripts = ['quic_server.py', 'vio_server.py']


def kill_existing_script(script_name):
    """Kill any existing instance of the script across Linux distros/containers"""
    subprocess.run(['pkill', '-f', script_name], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    subprocess.run(['killall', '-q', script_name], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)


def run_script(script_name):
    kill_existing_script(script_name)
    time.sleep(0.5)
    p = subprocess.Popen([sys.executable, script_name])
    return p


processes = []


def signal_handler(sig, frame):
    print('\nShutting down GFK server...')
    for p in processes:
        try:
            p.terminate()
            p.wait(timeout=3)
        except Exception:
            try:
                p.kill()
            except Exception:
                pass
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    if hasattr(signal, 'SIGTERM'):
        signal.signal(signal.SIGTERM, signal_handler)

    print("Starting GFK server...")
    p1 = run_script(scripts[0])
    time.sleep(1)
    p2 = run_script(scripts[1])
    processes.extend([p1, p2])

    print("GFK server running. Press Ctrl+C to stop.\n")

    try:
        p1.wait()
        p2.wait()
        print("All subprocesses have completed.")
    except KeyboardInterrupt:
        signal_handler(None, None)
