import subprocess
import os
import time
import sys
import signal
import platform

IS_WINDOWS = platform.system() == 'Windows'

scripts = ['quic_client.py', 'vio_client.py']


def kill_existing_script(script_name):
    """Kill any existing instance of the script (cross-platform)"""
    if IS_WINDOWS:
        # On Windows, try taskkill via wmic first, then PowerShell for Windows 11 where WMIC is deprecated/removed
        try:
            result = subprocess.run(
                ['wmic', 'process', 'where',
                 f"commandline like '%{script_name}%' and name like '%python%'",
                 'get', 'processid'],
                capture_output=True, text=True, stderr=subprocess.DEVNULL
            )
            for line in result.stdout.split('\n'):
                line = line.strip()
                if line.isdigit():
                    subprocess.run(['taskkill', '/F', '/PID', line],
                                 stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        except Exception:
            pass
        try:
            subprocess.run([
                'powershell', '-NoProfile', '-Command',
                f"Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object {{ $_.CommandLine -like '*{script_name}*' -and $_.Name -like '*python*' }} | ForEach-Object {{ Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }}"
            ], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        except Exception:
            pass
    else:
        subprocess.run(['pkill', '-f', script_name], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        subprocess.run(['killall', '-q', script_name], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)


def run_script(script_name):
    """Start a script, killing any existing instance first"""
    kill_existing_script(script_name)
    time.sleep(0.5)

    if IS_WINDOWS:
        p = subprocess.Popen([sys.executable, script_name],
                           creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
    else:
        p = subprocess.Popen([sys.executable, script_name])
    return p


processes = []


def signal_handler(sig, frame):
    print('\nShutting down GFK client...')
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
    if not IS_WINDOWS:
        signal.signal(signal.SIGTERM, signal_handler)

    print("Starting GFK client...")
    p1 = run_script(scripts[0])
    time.sleep(1)
    p2 = run_script(scripts[1])
    processes.extend([p1, p2])

    print("GFK running. Press Ctrl+C to stop.\n")

    try:
        p1.wait()
        p2.wait()
        print("All subprocesses have completed.")
    except KeyboardInterrupt:
        signal_handler(None, None)

