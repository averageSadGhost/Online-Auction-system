import json
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
            
            # Dynamically generate the absolute image URL for local development
            base_url = "http://127.0.0.1:9000"  # Replace with your local server URL if different
            image_url = f"{base_url}{auction.image.url}" if auction.image else None

            return {
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
        except ObjectDoesNotExist:
            return {"error": "Auction does not exist"}

    async def disconnect(self, close_code):
        # Leave auction group
        await self.channel_layer.group_discard(
            self.auction_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)

        # Handle bid placement action
        if 'action' in data and data['action'] == 'place_bid':
            response = await self.place_bid(data)
            await self.send(text_data=json.dumps(response))

    @database_sync_to_async
    def place_bid(self, data):
        try:
            auction = Auction.objects.get(id=self.auction_id)
            price = data.get('price')

            if not price or float(price) <= auction.starting_price:
                return {"error": "Bid must be higher than the starting price."}

            # Add a new vote (bid) to the auction
            vote = Vote.objects.create(
                auction=auction,
                user=self.scope['user'],
                price=price
            )
            return {"success": f"Bid of {price} placed successfully."}
        except ObjectDoesNotExist:
            return {"error": "Auction not found."}
        except Exception as e:
            return {"error": str(e)}

    # Send auction updates to WebSocket clients
    async def auction_update(self, event):
        await self.send(text_data=json.dumps(event['data']))
