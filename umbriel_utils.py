import json
import subprocess
import sys
from typing import Any


# Load JSON data safely, returning a default value if parsing fails.
def safe_json_loads(data: Any, default=None) -> Any:
    try:
        return json.loads(data)
    except (json.JSONDecodeError, TypeError):
        return default

# Run a command and return its output as JSON.
def run_command_json(command, shell: bool = False):
    """Run a command and return its output as JSON."""
    try:
        result = subprocess.run(command, capture_output=True, check=True, shell=shell)
        return json.loads(result.stdout)
    except (json.JSONDecodeError, TypeError, subprocess.CalledProcessError):
        return None

# Run a command and return True if successful, False otherwise.
def run_command(command):
    proc = subprocess.run(command, check=False, capture_output=True)
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr.decode())
        return False
    return True

# Send desktop notifications using notify-send for info message.
def notify_info(title: str, message: str):
    """Send a notification using notify-send."""
    run_command(["notify-send", "--icon", "info", "--app-name", "niri-pocket", title, message])


# Send desktop notifications using notify-send for error message.
def notify_error(title: str, message: str):
    """Send an error notification using notify-send."""
    run_command(["notify-send", "--icon", "error", "--app-name", "niri-pocket", "-u", "critical", title, message])
