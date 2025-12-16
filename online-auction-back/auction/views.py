from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .models import Auction
from .serializers import AuctionSerializer, WonAuctionSerializer
from .filters import AuctionFilter
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.decorators import action
from django.db.models import Case, When, IntegerField
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import NotFound, ValidationError

# Authorization header parameter for Swagger docs
auth_header = openapi.Parameter(
    'Authorization',
    openapi.IN_HEADER,
    description="Token authentication required. Format: 'Token your-auth-token'",
    type=openapi.TYPE_STRING,
    required=True
)

# Search parameter for Swagger docs
search_param = openapi.Parameter(
    'search',
    openapi.IN_QUERY,
    description="Search auctions by title (case-insensitive)",
    type=openapi.TYPE_STRING,
    required=False
)

# Filter parameters for Swagger docs
status_param = openapi.Parameter(
    'status',
    openapi.IN_QUERY,
    description="Filter by auction status",
    type=openapi.TYPE_STRING,
    enum=['scheduled', 'started', 'ended'],
    required=False
)

min_price_param = openapi.Parameter(
    'min_price',
    openapi.IN_QUERY,
    description="Filter auctions with starting price >= this value",
    type=openapi.TYPE_NUMBER,
    required=False
)

max_price_param = openapi.Parameter(
    'max_price',
    openapi.IN_QUERY,
    description="Filter auctions with starting price <= this value",
    type=openapi.TYPE_NUMBER,
    required=False
)

# Ordering parameter for Swagger docs
ordering_param = openapi.Parameter(
    'ordering',
    openapi.IN_QUERY,
    description="Sort results by field. Prefix with '-' for descending. Options: title, starting_price, start_date_time, end_date_time",
    type=openapi.TYPE_STRING,
    required=False
)


class AuctionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing auctions.

    Provides endpoints to list, retrieve, join auctions, and view user's auctions.
    Supports search by title, filtering by status/price, and sorting.
    """
    # Optimized queryset with prefetch for votes to reduce N+1 queries
    queryset = Auction.objects.prefetch_related(
        'votes', 'votes__user', 'users'
    ).order_by('start_date_time')
    serializer_class = AuctionSerializer
    permission_classes = [IsAuthenticated]

    # Filter, search, and ordering configuration
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = AuctionFilter
    search_fields = ['title', 'description']
    ordering_fields = ['title', 'starting_price', 'start_date_time', 'end_date_time']
    ordering = ['start_date_time']  # Default ordering

    @swagger_auto_schema(
        tags=["Auctions"],
        operation_id="list_available_auctions",
        operation_description="""List all scheduled auctions that the current user has NOT joined yet. **Authentication required.**

**Query Parameters:**
- `search`: Search by title or description (case-insensitive)
- `status`: Filter by status (scheduled, started, ended)
- `min_price`: Minimum starting price
- `max_price`: Maximum starting price
- `ordering`: Sort by field (prefix with '-' for descending). Options: title, starting_price, start_date_time, end_date_time
""",
        manual_parameters=[auth_header, search_param, status_param, min_price_param, max_price_param, ordering_param],
        responses={
            200: openapi.Response('List of available auctions', AuctionSerializer(many=True)),
            401: openapi.Response(description="Not authenticated"),
        }
    )
    def list(self, request, *args, **kwargs):
        """Retrieve a list of auctions where the user is NOT a participant."""
        user = request.user
        queryset = self.queryset.exclude(users=user)

        # Apply filters, search, and ordering
        queryset = self.filter_queryset(queryset)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        tags=["Auctions"],
        operation_id="get_auction_details",
        operation_description="Get detailed information about a specific auction, including whether the current user is a participant. **Authentication required.**",
        manual_parameters=[auth_header],
        responses={
            200: openapi.Response('Auction details with participation status', AuctionSerializer),
            401: openapi.Response(description="Not authenticated"),
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
        operation_description="Join a specific auction. Once joined, you can participate in bidding when the auction starts. **Authentication required.**",
        manual_parameters=[auth_header],
        responses={
            200: openapi.Response(
                description="Successfully joined",
                examples={"application/json": {"message": "Successfully joined the auction."}}
            ),
            400: openapi.Response(
                description="Already a participant",
                examples={"application/json": {"detail": "You are already a participant in this auction."}}
            ),
            401: openapi.Response(description="Not authenticated"),
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
        operation_description="""List all auctions that the current user has joined. Results are sorted by status: started > scheduled > ended. **Authentication required.**

**Query Parameters:**
- `search`: Search by title or description (case-insensitive)
- `status`: Filter by status (scheduled, started, ended)
- `min_price`: Minimum starting price
- `max_price`: Maximum starting price
""",
        manual_parameters=[auth_header, search_param, status_param, min_price_param, max_price_param],
        responses={
            200: openapi.Response('List of user\'s auctions', AuctionSerializer(many=True)),
            401: openapi.Response(description="Not authenticated"),
        }
    )
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_auctions(self, request):
        """Retrieve a list of auctions where the user is a participant."""
        user = request.user
        queryset = Auction.objects.filter(users=user).prefetch_related(
            'votes', 'votes__user'
        ).annotate(
            status_order=Case(
                When(status='started', then=0),
                When(status='scheduled', then=1),
                When(status='ended', then=2),
                default=3,
                output_field=IntegerField(),
            )
        ).order_by('status_order')

        # Apply filters and search
        queryset = self.filter_queryset(queryset)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        tags=["Auctions"],
        operation_id="list_featured_auctions",
        operation_description="List top 3 scheduled auctions by highest starting price. No authentication required.",
        responses={
            200: openapi.Response('List of featured auctions', AuctionSerializer(many=True)),
        }
    )
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def featured(self, request):
        """Return top 3 scheduled auctions by highest starting price."""
        queryset = Auction.objects.filter(status='scheduled').prefetch_related(
            'votes', 'votes__user'
        ).order_by('-starting_price')[:3]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        tags=["Auctions"],
        operation_id="list_won_auctions",
        operation_description="List all auctions that the current user has won (ended auctions where user is the highest bidder). **Authentication required.**",
        manual_parameters=[auth_header],
        responses={
            200: openapi.Response('List of won auctions', WonAuctionSerializer(many=True)),
            401: openapi.Response(description="Not authenticated"),
        }
    )
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def won_auctions(self, request):
        """Retrieve a list of auctions where the user is the winner (highest bidder)."""
        user = request.user

        # Get all ended auctions where user participated
        ended_auctions = Auction.objects.filter(
            status='ended',
            users=user
        ).prefetch_related('votes')

        # Filter to only auctions where user is the winner
        won_auctions = []
        for auction in ended_auctions:
            winner = auction.get_winner()
            if winner and winner.user_id == user.id:
                won_auctions.append(auction)

        serializer = WonAuctionSerializer(won_auctions, many=True)
        return Response(serializer.data)
