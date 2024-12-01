from rest_framework import viewsets, permissions
from accounts.permissions import IsAdminUserCustom
from rest_framework.response import Response
from .models import Auction
from .serializers import AuctionSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class AuctionViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing auction instances.
    """
    queryset = Auction.objects.all().order_by('start_date_time')  
    serializer_class = AuctionSerializer
    permission_classes = [permissions.AllowAny]  # Only admins can create, update, or delete

    @swagger_auto_schema(
        operation_description="List all auctions",
        responses={
            200: openapi.Response('List of auctions', AuctionSerializer(many=True)),
        }
    )
    def list(self, request, *args, **kwargs):
        """Retrieve a list of all auctions."""
        self.permission_classes = [permissions.AllowAny]  # Allow any user to view auctions
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Retrieve a specific auction",
        responses={
            200: openapi.Response('Auction details', AuctionSerializer),
            404: 'Auction not found',
        }
    )
    def retrieve(self, request, *args, **kwargs):
        """Retrieve details of a specific auction."""
        self.permission_classes = [permissions.AllowAny]
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Create a new auction",
        request_body=AuctionSerializer,
        responses={
            201: openapi.Response('Auction created', AuctionSerializer),
            400: 'Invalid data',
            403: 'Permission denied'
        }
    )
    def create(self, request, *args, **kwargs):
        """Create a new auction."""
        self.permission_classes = [IsAdminUserCustom]
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Update a specific auction",
        request_body=AuctionSerializer,
        responses={
            200: openapi.Response('Auction updated', AuctionSerializer),
            404: 'Auction not found',
            403: 'Permission denied'
        }
    )
    def update(self, request, *args, **kwargs):
        """Update a specific auction."""
        self.permission_classes = [IsAdminUserCustom]
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Delete a specific auction",
        responses={
            204: 'Auction deleted',
            404: 'Auction not found',
            403: 'Permission denied'
        }
    )
    def destroy(self, request, *args, **kwargs):
        """Delete a specific auction."""
        self.permission_classes = [IsAdminUserCustom]
        return super().destroy(request, *args, **kwargs)
