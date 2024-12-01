import requests
import utils

def get_headers():
    """Get headers with the authorization token."""
    if utils.TOKEN:
        return {"Authorization": f"Token {utils.TOKEN}"}
    return {}

def get_auctions():
    """Fetch the list of all auctions."""
    url = f"{utils.BASE_URL}auctions/"
    headers = get_headers()
    response = requests.get(url, headers=headers)
    return response.json(), response.status_code

def get_auction_details(auction_id):
    """Fetch details of a specific auction."""
    url = f"{utils.BASE_URL}auctions/{auction_id}/"
    headers = get_headers()
    response = requests.get(url, headers=headers)
    return response.json(), response.status_code

def create_auction(data):
    """Create a new auction."""
    url = f"{utils.BASE_URL}auctions/"
    headers = get_headers()
    response = requests.post(url, json=data, headers=headers)
    return response.json(), response.status_code

def update_auction(auction_id, data):
    """Update an existing auction."""
    url = f"{utils.BASE_URL}auctions/{auction_id}/"
    headers = get_headers()
    response = requests.put(url, json=data, headers=headers)
    return response.json(), response.status_code

def delete_auction(auction_id):
    """Delete an auction."""
    url = f"{utils.BASE_URL}auctions/{auction_id}/"
    headers = get_headers()
    response = requests.delete(url, headers=headers)
    return response.json(), response.status_code
