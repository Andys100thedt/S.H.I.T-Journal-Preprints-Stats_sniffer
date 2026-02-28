"""
Windows Daemon：Looping launching/restarting a target Python script
Usage：python daemon.py
"""

import subprocess
import sys
import time
from enumerate_configuration import _DEFAULT_CONFIGURATION


def run_daemon(script_path, interval):
    """
    Daemon process loop cycle
    :param script_path: targeted Python script path
    :param interval:    interval after launching in seconds (approximately)
    """
    print(f"Daemon started, target: {script_path}, with interval: {interval} sec")

    current_process = None

    try:
        while True:
            # If the script is still running, terminate(should be already terminated after each loop)
            if current_process and current_process.poll() is None:
                print("discovered remaining process,terminating ...")
                current_process.terminate()
                try:
                    current_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    current_process.kill()
                    current_process.wait()

            # Launching new script process
            print(f"Launching {script_path} ...")
            # Pass on current Python interpreter, easy to read outputs
            current_process = subprocess.Popen([sys.executable, script_path])

            # Wait for specified interval
            time.sleep(interval)

            # Terminating script subprocess
            print(f"Interval passed, terminating {script_path} ...")
            current_process.terminate()
            try:
                # Wait for the process's termination, at most for 5 sec
                current_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # If still not terminating, kill it
                print("Process failed to terminate, killing ...")
                current_process.kill()
                current_process.wait()

            # Short hold, to avoid asset confliction due by immediate restart
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nDaemon process termination signal received, clearing ...")
        if current_process and current_process.poll() is None:
            print("Terminating script process ...")
            current_process.terminate()
            try:
                current_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                current_process.kill()
                current_process.wait()
        print("Daemon process terminated.")


if __name__ == "__main__":
    run_daemon("lifecycle.py", _DEFAULT_CONFIGURATION.lifecycle)