from rest_framework import serializers
from .models import Auction

class AuctionSerializer(serializers.ModelSerializer):
    current_bid = serializers.SerializerMethodField()
    current_bidder = serializers.SerializerMethodField()

    class Meta:
        model = Auction
        fields = ['id', 'title', 'description', 'image', 'start_date_time', 'end_date_time', 'starting_price', 'status', 'current_bid', 'current_bidder']

    def _get_highest_vote(self, obj):
        """Get the highest vote, using prefetched data if available."""
        # Check if votes are prefetched
        if hasattr(obj, '_prefetched_objects_cache') and 'votes' in obj._prefetched_objects_cache:
            votes = list(obj.votes.all())
            if votes:
                return max(votes, key=lambda v: v.price)
            return None
        # Fallback to database query if not prefetched
        return obj.votes.order_by('-price').first()

    def get_current_bid(self, obj):
        highest_vote = self._get_highest_vote(obj)
        return str(highest_vote.price) if highest_vote else None

    def get_current_bidder(self, obj):
        highest_vote = self._get_highest_vote(obj)
        return highest_vote.user.email if highest_vote else None

    def create(self, validated_data):
        auction = Auction.objects.create(**validated_data)
        return auction


class WonAuctionSerializer(serializers.ModelSerializer):
    """Serializer for won auctions with receipt details."""
    winning_price = serializers.SerializerMethodField()
    transaction_id = serializers.SerializerMethodField()
    date_won = serializers.SerializerMethodField()
    total_bids = serializers.SerializerMethodField()

    class Meta:
        model = Auction
        fields = ['id', 'title', 'description', 'image', 'start_date_time', 'end_date_time',
                  'starting_price', 'winning_price', 'transaction_id', 'date_won', 'total_bids']

    def get_winning_price(self, obj):
        winner = obj.get_winner()
        return str(winner.price) if winner else str(obj.starting_price)

    def get_transaction_id(self, obj):
        return f"AH-{obj.id}-{obj.end_date_time.strftime('%Y%m%d%H%M')}"

    def get_date_won(self, obj):
        return obj.end_date_time.strftime('%B %d, %Y at %I:%M %p')

    def get_total_bids(self, obj):
        return obj.votes.count()
