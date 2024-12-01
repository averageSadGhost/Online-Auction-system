import json
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
