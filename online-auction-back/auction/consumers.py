from decimal import Decimal, InvalidOperation
import json
import asyncio
from queue import Queue
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.exceptions import ObjectDoesNotExist
from auction.models import Auction, Vote
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework.authtoken.models import Token
from urllib.parse import parse_qs

class AuctionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Extract token from query parameters
        token = None
        query_string = self.scope.get('query_string', b'').decode()
        if query_string:
            params = parse_qs(query_string)
            token = params.get('token', [None])[0]

        # Authenticate user using the token
        if token:
            user = await self.get_user_from_token(token)
            if user:
                self.scope['user'] = user
            else:
                self.scope['user'] = AnonymousUser()
        else:
            self.scope['user'] = AnonymousUser()

        # Extract auction ID from URL
        self.auction_id = self.scope['url_route']['kwargs']['auction_id']
        
        # Initialize message queue for this connection
        self.message_queue = Queue()

        # Check if user is part of the auction
        if not await self.is_user_part_of_auction():
            await self.close()  # Close connection if the user is not part of the auction

        # Set the group name for WebSocket
        self.auction_group_name = f'auction_{self.auction_id}'

        # Join auction group
        await self.channel_layer.group_add(
            self.auction_group_name,
            self.channel_name
        )

        # Accept the WebSocket connection
        await self.accept()

        # Send initial auction data to the WebSocket client
        auction_data = await self.get_auction_data()
        await self.send(text_data=json.dumps(auction_data))

        # Start listening for updates in a separate task
        asyncio.create_task(self.listen_for_updates())

    async def listen_for_updates(self):
        """
        Continuously listen for updates and send them to the client
        """
        try:
            while True:
                # Get updates from the message queue
                if not self.message_queue.empty():
                    update = self.message_queue.get()
                    if update is None:  # Check for stop signal
                        break
                    await self.send(text_data=json.dumps(update))
                await asyncio.sleep(0.1)  # Small delay to prevent CPU overuse
        except Exception as e:
            print(f"Error in update listener: {e}")
            await self.close()

    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(text_data)
            
            # Handle bid placement action
            if 'action' in data and data['action'] == 'place_bid':
                # Place the bid and get the response
                response = await self.place_bid(data)

                # If bid was successful, broadcast the updated auction data
                if 'success' in response:
                    auction_data = await self.get_auction_data()
                    await self.channel_layer.group_send(
                        self.auction_group_name,
                        {
                            'type': 'auction_update',
                            'data': auction_data
                        }
                    )

                # Send the appropriate response back to the client
                await self.send(text_data=json.dumps(response))
            
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                "error": "Invalid JSON format"
            }))
        except Exception as e:
            await self.send(text_data=json.dumps({
                "error": f"Error processing message: {str(e)}"
            }))

    async def auction_update(self, event):
        """
        Handle auction updates and send them to the client
        """
        try:
            # Send the update directly to the WebSocket
            await self.send(text_data=json.dumps(event['data']))
        except Exception as e:
            print(f"Error sending auction update: {e}")

    @database_sync_to_async
    def get_user_from_token(self, token):
        try:
            token_instance = Token.objects.get(key=token)
            return token_instance.user
        except Token.DoesNotExist:
            return None

    @database_sync_to_async
    def is_user_part_of_auction(self):
        try:
            auction = Auction.objects.get(id=self.auction_id)
            return self.scope['user'] in auction.users.all()
        except ObjectDoesNotExist:
            return False

    @database_sync_to_async
    def get_auction_data(self):
        try:
            auction = Auction.objects.get(id=self.auction_id)
            last_vote = auction.votes.order_by('-id').first()
            
            base_url = "http://127.0.0.1:9000"  # Replace with your production URL
            image_url = f"{base_url}{auction.image.url}" if auction.image else None

            auction_data = {
                "title": auction.title,
                "description": auction.description,
                "image": image_url,
                "starting_price": str(auction.starting_price),
                "status": auction.status,
                "last_vote": {
                    "user": last_vote.user.email if last_vote else None,
                    "price": str(last_vote.price) if last_vote else None
                } if last_vote else None,
            }


            return auction_data
        except ObjectDoesNotExist:
            return {"error": "Auction does not exist"}

    @database_sync_to_async
    def place_bid(self, data):
        try:
            auction = Auction.objects.get(id=self.auction_id)
            
            # Retrieve price from data and convert to Decimal for comparison
            price_str = data.get('price')
            
            if not price_str:
                return {"error": "Price is required."}
            
            try:
                # Convert the string price to Decimal
                price = Decimal(price_str)
            except InvalidOperation:
                return {"error": "Invalid price format."}
            
            # Ensure the bid is higher than the starting price
            if price <= auction.starting_price:
                return {"error": f"Bid must be higher than the starting price of {auction.starting_price}."}

            # Create the vote (bid)
            vote = Vote.objects.create(
                auction=auction,
                user=self.scope['user'],
                price=price
            )
            
            # Return success message with the bid price
            return {"success": f"Bid of {price} placed successfully."}
        except ObjectDoesNotExist:
            return {"error": "Auction not found."}
        except Exception as e:
            return {"error": str(e)}

    async def disconnect(self, close_code):
        # Leave auction group
        await self.channel_layer.group_discard(
            self.auction_group_name,
            self.channel_name
        )
