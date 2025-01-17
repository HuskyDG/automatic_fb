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
        try:
            with open("exitnow.txt", "w") as file:
                file.write("1")  # Tell aichat.py to stop by itself
        except Exception:
            pass

        # Wait for up to 10 minutes for the process to stop
        try:
            print("Waiting for the process to terminate gracefully...")
            proc.communicate(timeout=600)  # Wait up to 10 minutes
            print("Process terminated gracefully within 10 minutes.")
        except subprocess.TimeoutExpired:
            print("Process did not terminate within 10 minutes. Forcefully killing it.")
            proc.terminate()  # Sends SIGTERM to the process
            proc.communicate()  # Ensure the process exits cleanly
    except Exception as e:
        print(f"An error occurred: {e}")
        proc.terminate()
        proc.communicate()

# Example usage:
command = "python aichat.py"
timeout_seconds = 3600  # Adjust timeout as needed

run_with_timeout(command, timeout_seconds)
