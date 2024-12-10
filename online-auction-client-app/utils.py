import json
from datetime import datetime, timezone, timedelta
import os
from tkinter import messagebox

BASE_URL = "http://127.0.0.1:9000/api/"
TOKEN_FILE = "token.json"  # File where the token will be stored


def save_token(token):
    """Save the token to a local file."""
    with open(TOKEN_FILE, "w") as file:
        json.dump({"token": token}, file)

def load_token():
    """Load the token from a local file."""
    try:
        with open(TOKEN_FILE, "r") as file:
            data = json.load(file)
            return data.get("token")
    except (FileNotFoundError, json.JSONDecodeError):
        return None
    
def delete_token():
    """Delete the stored token."""
    try:
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, "w") as file:
                file.write("{}")  # Overwrite the token file with an empty object
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Failed to delete token: {str(e)}")  # Optional for GUI
        return False

def calculate_hours_until(start_time):
    """Calculate the number of hours until the given start time."""
    start_dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))  # Convert ISO 8601 to datetime
    now_dt = datetime.now(timezone.utc)  # Get current time in UTC
    delta = start_dt - now_dt
    hours_left = max(delta.total_seconds() // 3600, 0)  # Ensure non-negative values
    return int(hours_left)

def get_headers():
    """Get headers with the authorization token."""
    token = load_token()  # Load the token
    if token:
        return {"Authorization": f"Token {token}"}
    return {}