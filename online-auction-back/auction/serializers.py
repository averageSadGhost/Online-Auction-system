from rest_framework import serializers
from .models import Auction

class AuctionSerializer(serializers.ModelSerializer):
    current_bid = serializers.SerializerMethodField()
    current_bidder = serializers.SerializerMethodField()

    class Meta:
        model = Auction
        fields = ['id', 'title', 'description', 'image', 'start_date_time', 'end_date_time', 'starting_price', 'status', 'current_bid', 'current_bidder']

    def get_current_bid(self, obj):
        last_vote = obj.votes.order_by('-price').first()
        return str(last_vote.price) if last_vote else None

    def get_current_bidder(self, obj):
        last_vote = obj.votes.order_by('-price').first()
        return last_vote.user.email if last_vote else None

    def create(self, validated_data):
        auction = Auction.objects.create(**validated_data)
        return auction
