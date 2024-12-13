from rest_framework import viewsets, permissions
from accounts.permissions import IsAdminUserCustom
from rest_framework.response import Response
from .models import Auction
from .serializers import AuctionSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils.timezone import now
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound, ValidationError


class AuctionViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing auction instances.
    """
    queryset = Auction.objects.filter(start_date_time__gt=now()).order_by('start_date_time')
    serializer_class = AuctionSerializer
    permission_classes = [IsAuthenticated]  # Only authenticated users can access

    @swagger_auto_schema(
        operation_description="List auctions where the user is not a participant",
        responses={
            200: openapi.Response('List of auctions', AuctionSerializer(many=True)),
        }
    )
    def list(self, request, *args, **kwargs):
        """Retrieve a list of auctions where the user is NOT a participant."""
        user = request.user
        queryset = self.queryset.filter(status='Scheduled').exclude(users=user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Retrieve a specific auction with participant status",
        responses={
            200: openapi.Response('Auction details', AuctionSerializer),
            404: 'Auction not found',
        }
    )
    def retrieve(self, request, *args, **kwargs):
        """Retrieve details of a specific auction with participant status."""
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        # Determine if the logged-in user is a participant
        user = request.user
        is_participant = instance.users.filter(id=user.id).exists()

        # Add `is_participant` to the serialized data
        data = serializer.data
        data['is_participant'] = is_participant

        return Response(data)

    @swagger_auto_schema(
        operation_description="Join an auction by providing auction ID",
        responses={
            200: "Successfully joined the auction",
            400: "Invalid data",
            404: "Auction not found",
        }
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def join_auction(self, request, pk=None):
        """Add the logged-in user to the specified auction."""
        try:
            # Fetch the auction using the primary key (auction ID)
            auction = Auction.objects.get(pk=pk)
        except Auction.DoesNotExist:
            raise NotFound("Auction not found.")

        user = request.user

        # Check if the user is already added to the auction
        if auction.users.filter(id=user.id).exists():
            raise ValidationError("You are already a participant in this auction.")

        # Add the user to the auction's users
        auction.users.add(user)
        auction.save()

        return Response({"message": "Successfully joined the auction."}, status=200)

    @swagger_auto_schema(
        operation_description="List auctions where the user is a participant",
        responses={
            200: openapi.Response('List of auctions', AuctionSerializer(many=True)),
        }
    )
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_auctions(self, request):
        """Retrieve a list of auctions where the user is a participant."""
        user = request.user
        queryset = self.queryset.filter(users=user)  # Only include auctions where the user is a participant
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

