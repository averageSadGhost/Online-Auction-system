from tkinter import messagebox
import requests
import utils



def get_auctions():
    """Fetch the list of all auctions."""
    url = f"{utils.BASE_URL}auctions/"
    headers = utils.get_headers()
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        # If the status code is not 200, show the login screen
        messagebox.showerror("Session Expired", "Your session has expired. Please log in again.")
        # You can add code here to redirect to the login screen in your Tkinter app
        return None, response.status_code  # Or any other logic for handling this
    return response.json(), response.status_code

def get_auction_details(auction_id):
    """Fetch details of a specific auction."""
    url = f"{utils.BASE_URL}auctions/{auction_id}/"
    headers = utils.get_headers()
    response = requests.get(url, headers=headers)
    return response.json(), response.status_code

def join_auction(auction_id):
    """Call the API to join an auction."""
    url = f"{utils.BASE_URL}auctions/{auction_id}/join_auction/"
    headers = utils.get_headers()  # Assume get_headers returns the required headers

    try:
        response = requests.post(url, headers=headers)
        return response.json(), response.status_code
    except requests.RequestException as e:
        # Log or handle the error
        print(f"Error joining auction: {e}")
        return {"error": str(e)}, 500  # Return a default error structure

def get_my_auctions():
    """Fetch the list of auctions where the user is a participant."""
    url = f"{utils.BASE_URL}auctions/my_auctions/"
    headers = utils.get_headers()
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            messagebox.showerror("Error", "Failed to fetch your auctions. Please try again later.")
            return None, response.status_code
        
        return response.json(), response.status_code
    except requests.RequestException as e:
        # Handle exceptions, such as connection errors
        print(f"Error fetching user's auctions: {e}")
        return {"error": str(e)}, 500  # Return a default error structure
