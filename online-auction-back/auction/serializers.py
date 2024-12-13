from rest_framework import serializers
from .models import Auction

class AuctionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Auction
        fields = ['id', 'title', 'description', 'image', 'start_date_time', 'end_date_time', 'starting_price', 'status']

    def create(self, validated_data):
        auction = Auction.objects.create(**validated_data)
        return auction
