from rest_framework import viewsets
from rest_framework.response import Response
from .models import Auction
from .serializers import AuctionSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.decorators import action
from django.db.models import Case, When, IntegerField
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound, ValidationError


class AuctionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing auctions.

    Provides endpoints to list, retrieve, join auctions, and view user's auctions.
    """
    queryset = Auction.objects.order_by('start_date_time')
    serializer_class = AuctionSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=["Auctions"],
        operation_id="list_available_auctions",
        operation_description="List all scheduled auctions that the current user has NOT joined yet.",
        responses={
            200: openapi.Response('List of available auctions', AuctionSerializer(many=True)),
            401: openapi.Response(description="Not authenticated"),
        }
    )
    def list(self, request, *args, **kwargs):
        """Retrieve a list of auctions where the user is NOT a participant."""
        user = request.user
        queryset = self.queryset.filter(status='scheduled').exclude(users=user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        tags=["Auctions"],
        operation_id="get_auction_details",
        operation_description="Get detailed information about a specific auction, including whether the current user is a participant.",
        responses={
            200: openapi.Response('Auction details with participation status', AuctionSerializer),
            404: openapi.Response(description="Auction not found"),
        }
    )
    def retrieve(self, request, *args, **kwargs):
        """Retrieve details of a specific auction with participant status."""
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        user = request.user
        is_participant = instance.users.filter(id=user.id).exists()

        data = serializer.data
        data['is_participant'] = is_participant

        return Response(data)

    @swagger_auto_schema(
        tags=["Auctions"],
        operation_id="join_auction",
        operation_description="Join a specific auction. Once joined, you can participate in bidding when the auction starts.",
        responses={
            200: openapi.Response(
                description="Successfully joined",
                examples={"application/json": {"message": "Successfully joined the auction."}}
            ),
            400: openapi.Response(
                description="Already a participant",
                examples={"application/json": {"detail": "You are already a participant in this auction."}}
            ),
            404: openapi.Response(description="Auction not found"),
        }
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def join_auction(self, request, pk=None):
        """Add the logged-in user to the specified auction."""
        try:
            auction = Auction.objects.get(pk=pk)
        except Auction.DoesNotExist:
            raise NotFound("Auction not found.")

        user = request.user

        if auction.users.filter(id=user.id).exists():
            raise ValidationError("You are already a participant in this auction.")

        auction.users.add(user)
        auction.save()

        return Response({"message": "Successfully joined the auction."}, status=200)

    @swagger_auto_schema(
        tags=["Auctions"],
        operation_id="list_my_auctions",
        operation_description="List all auctions that the current user has joined. Results are sorted by status: started > scheduled > ended.",
        responses={
            200: openapi.Response('List of user\'s auctions', AuctionSerializer(many=True)),
            401: openapi.Response(description="Not authenticated"),
        }
    )
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_auctions(self, request):
        """Retrieve a list of auctions where the user is a participant."""
        user = request.user
        queryset = Auction.objects.filter(users=user).annotate(
            status_order=Case(
                When(status='started', then=0),
                When(status='scheduled', then=1),
                When(status='ended', then=2),
                default=3,
                output_field=IntegerField(),
            )
        ).order_by('status_order')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

