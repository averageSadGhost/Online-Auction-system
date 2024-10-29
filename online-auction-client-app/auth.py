import requests

BASE_URL = "http://127.0.0.1:8000/api/"

def register_user(email, first_name, last_name, password):
    url = f"{BASE_URL}register/"
    data = {
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "password": password
    }
    response = requests.post(url, json=data)
    return response.json(), response.status_code

def login_user(email, password):
    url = f"{BASE_URL}login/"
    data = {"email": email, "password": password}
    response = requests.post(url, json=data)
    return response.json(), response.status_code

def verify_otp(email, otp):
    url = f"{BASE_URL}verify-otp/"
    data = {"email": email, "otp": otp}
    response = requests.post(url, json=data)
    return response.json(), response.status_code

def resend_otp(email):
    """Send a POST request to the resend-otp/ endpoint."""
    url = f"{BASE_URL}resend-otp/"
    data = {"email": email}
    response = requests.post(url, json=data)
    return response.json(), response.status_code