from tkinter import messagebox
import requests
import utils
import websockets
import asyncio
import json

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
        """
        Initialize WebSocket connection for a specific auction.
        
        :param auction_id: ID of the auction to connect to
        :param token: Authentication token for the user
        """
        self.auction_id = auction_id
        self.token = token
        self.websocket = None
        self.is_connected = False
        self.auction_data = None

    async def connect(self):
        """
        Establish WebSocket connection and retrieve initial auction data.
        
        :return: Auction data or None if connection fails
        """
        try:
            # Construct WebSocket URL with token
            # Note: Replace with your actual WebSocket server URL
            ws_url = f"{utils.WEB_SOCKET_URL}{self.auction_id}/?token={self.token}"
            
            # Connect to WebSocket
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
        """
        Continuously listen for auction updates.
        
        :return: Generator of auction updates
        """
        try:
            while self.is_connected:
                message = await self.websocket.recv()
                update = json.loads(message)
                yield update
        
        except websockets.exceptions.ConnectionClosed:
            print("WebSocket connection closed")
            self.is_connected = False
        
        except Exception as e:
            print(f"Error receiving message: {e}")
            self.is_connected = False

    async def place_bid(self, price):
        """
        Place a bid through the WebSocket.
        
        :param price: Bid price
        :return: Bid response
        """
        if not self.is_connected:
            print("Not connected to WebSocket")
            return None

        try:
            bid_data = {
                'action': 'place_bid',
                'price': str(price)
            }
            await self.websocket.send(json.dumps(bid_data))
            
            # Wait for and return the bid response
            response = await self.websocket.recv()
            return json.loads(response)
        
        except Exception as e:
            print(f"Error placing bid: {e}")
            return None

    async def close(self):
        """Close the WebSocket connection."""
        if self.websocket:
            await self.websocket.close()
            self.is_connected = False

def connect_to_auction_websocket(auction_id):
    """
    Synchronously connect to an auction WebSocket.
    
    :param auction_id: ID of the auction to connect to
    :return: AuctionWebSocket instance with initialized auction_data
    """
    try:
        # Get the authentication token
        token = utils.load_token()
        
        # Create async function to connect
        async def async_connect():
            ws = AuctionWebSocket(auction_id, token)
            # Wait for the connection and initial data
            auction_data = await ws.connect()
            if auction_data is None:
                raise Exception("Failed to receive initial auction data")
            return ws
        
        # Run the async connection in the event loop
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(async_connect())
    
    except Exception as e:
        print(f"Failed to connect to WebSocket: {e}")
        return None

def listen_to_auction_updates(websocket):
    """
    Synchronously listen to auction updates.
    
    :param websocket: AuctionWebSocket instance
    :return: Generator of auction updates
    """
    try:
        async def async_listen():
            async for update in websocket.listen():
                yield update
        
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(async_listen())
    
    except Exception as e:
        print(f"Error listening to updates: {e}")
        return None

def place_auction_bid(websocket, price):
    """
    Synchronously place a bid in an auction.
    
    :param websocket: AuctionWebSocket instance
    :param price: Bid price
    :return: Bid response
    """
    try:
        async def async_bid():
            return await websocket.place_bid(price)
        
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(async_bid())
    
    except Exception as e:
        print(f"Error placing bid: {e}")
        return None