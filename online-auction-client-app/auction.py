from tkinter import messagebox
import requests
import utils
import websockets
import asyncio
import json
import threading
from queue import Queue

def get_auctions():
    """Fetch the list of all auctions."""
    url = f"{utils.BASE_URL}auctions/"
    headers = utils.get_headers()
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        messagebox.showerror("Session Expired", "Your session has expired. Please log in again.")
        return None, response.status_code
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
    headers = utils.get_headers()

    try:
        response = requests.post(url, headers=headers)
        return response.json(), response.status_code
    except requests.RequestException as e:
        print(f"Error joining auction: {e}")
        return {"error": str(e)}, 500

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
        print(f"Error fetching user's auctions: {e}")
        return {"error": str(e)}, 500

class AuctionWebSocket:
    """Handles WebSocket connection and communication for a specific auction."""
    
    def __init__(self, auction_id, token):
        self.auction_id = auction_id
        self.token = token
        self.websocket = None
        self.is_connected = False
        self.auction_data = None

    async def connect(self):
        """Connect to the WebSocket server and get initial data."""
        try:
            # Construct WebSocket URL with token
            ws_url = f"{utils.WEB_SOCKET_URL}{self.auction_id}/?token={self.token}"
            self.websocket = await websockets.connect(ws_url)
            self.is_connected = True

            # Receive initial auction data
            initial_data = await self.websocket.recv()
            self.auction_data = json.loads(initial_data)
            return self.auction_data
        except Exception as e:
            print(f"WebSocket connection error: {e}")
            return None

    async def listen(self):
        """Listen for updates from the auction and push to the queue."""
        try:
            while self.is_connected:
                message = await self.websocket.recv()
                update = json.loads(message)
                yield update
        except websockets.exceptions.ConnectionClosed:
            print("WebSocket connection closed")  # Debugging
            self.is_connected = False
        except Exception as e:
            print(f"Error receiving message: {e}")  # Debugging
            self.is_connected = False

    async def place_bid(self, price):
        """Send a bid via the WebSocket."""
        if not self.is_connected:
            return None

        try:
            bid_data = {'action': 'place_bid', 'price': str(price)}
            await self.websocket.send(json.dumps(bid_data))
            response = await self.websocket.recv()
            return json.loads(response)
        except Exception as e:
            print(f"Error placing bid: {e}")  # Debugging
            return None

    async def close(self):
        """Close the WebSocket connection."""
        if self.websocket:
            await self.websocket.close()
            self.is_connected = False

async def listen_to_auction_updates(websocket, message_queue):
    """Asynchronously listen for auction updates and push to the queue."""
    try:
        while websocket.is_connected:
            message = await websocket.websocket.recv()
            update = json.loads(message)
            message_queue.put(update)
    except Exception as e:
        print(f"Error in async listener: {e}")
        message_queue.put(None)  # Signal to stop on error


def connect_to_auction_websocket(auction_id):
    """
    Connect to an auction WebSocket and ensure we get the initial data.
    """
    token = utils.load_token()

    async def async_connect():
        ws = AuctionWebSocket(auction_id, token)
        auction_data = await ws.connect()
        if auction_data is None:
            raise Exception("Failed to receive initial auction data")
        return ws

    # Run the async function in a new event loop thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    return loop.run_until_complete(async_connect())


def place_auction_bid(websocket, price):
    """
    Ensure price is numeric before sending it as part of the bid.
    """
    try:
        price = float(price)  # Convert price to float
    except ValueError:
        return {"error": "Invalid price. Please enter a numeric value."}

    async def async_place_bid():
        return await websocket.place_bid(price)

    try:
        # Use the existing event loop if available
        loop = asyncio.get_event_loop()
        if loop.is_running():
            return asyncio.run_coroutine_threadsafe(async_place_bid(), loop).result()
        else:
            return loop.run_until_complete(async_place_bid())
    except Exception as e:
        print(f"Bid placement error: {e}")
        return {"error": str(e)}

