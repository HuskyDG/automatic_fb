import subprocess

def run_with_timeout(cmd, timeout_sec):
    """Run a command with a timeout on Windows."""
    try:
        # Start the process
        proc = subprocess.Popen(cmd, shell=True, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
        
        # Wait for the process to complete or timeout
        proc.communicate(timeout=timeout_sec)
    except subprocess.TimeoutExpired:
        # Timeout occurred. Notify and write to exitnow.txt
        print(f"Process timed out after {timeout_sec} seconds. Terminating...")
        proc.terminate()  # Sends SIGTERM to the process
        proc.communicate()  # Ensure the process exits cleanly
    except Exception as e:
        print(f"An error occurred: {e}")
        proc.terminate()
        proc.communicate()

# Example usage:
command = "python traodoisub_v2.py"
timeout_seconds = 7200  # Adjust timeout as needed

run_with_timeout(command, timeout_seconds)
