import requests
import utils

def register_user(email, first_name, last_name, password):
    url = f"{utils.BASE_URL}register/"
    data = {
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "password": password
    }
    response = requests.post(url, json=data)
    return response.json(), response.status_code

def login_user(email, password):
    global TOKEN  # Use the global TOKEN variable
    url = f"{utils.BASE_URL}login/"
    data = {"email": email, "password": password}
    response = requests.post(url, json=data)
    
    if response.status_code == 200:
        # Get the token from the response
        token = response.json().get("token")
        if token:
            # Save the token locally using the save_token function
            utils.save_token(token)
            # Set the global TOKEN variable
            utils.TOKEN = token
    return response.json(), response.status_code

def verify_otp(email, otp):
    url = f"{utils.BASE_URL}verify-otp/"
    data = {"email": email, "otp": otp}
    response = requests.post(url, json=data)
    return response.json(), response.status_code

def resend_otp(email):
    """Send a POST request to the resend-otp/ endpoint."""
    url = f"{utils.BASE_URL}resend-otp/"
    data = {"email": email}
    response = requests.post(url, json=data)
    return response.json(), response.status_code
