from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from project.health import health_check, readiness_check, liveness_check

schema_view = get_schema_view(
    openapi.Info(
        title="Online Auction API",
        default_version='v1',
        description="""
# Online Auction API Documentation

A real-time auction platform API with WebSocket support for live bidding.

## Authentication

All endpoints (except registration, login, and OTP verification) require token authentication.

Include the token in the `Authorization` header:
```
Authorization: Token your-auth-token-here
```

## REST API Endpoints

### Authentication Flow
1. **Register** - Create a new account (`POST /api/register/`)
2. **Verify OTP** - Verify email with OTP code (`POST /api/verify-otp/`)
3. **Login** - Get auth token (`POST /api/login/`)
4. **Get User Info** - Get current user details (`GET /api/me/`)

### Auction Flow
1. **List Auctions** - Browse available auctions (`GET /api/auctions/`)
2. **Join Auction** - Join an auction (`POST /api/auctions/{id}/join_auction/`)
3. **My Auctions** - View joined auctions (`GET /api/auctions/my_auctions/`)
4. **Auction Details** - Get auction info (`GET /api/auctions/{id}/`)

---

## WebSocket API

### Connection

Connect to the WebSocket endpoint for real-time auction updates:

```
ws://localhost:9000/ws/auction/{auction_id}/?token={auth_token}
```

**Parameters:**
- `auction_id` - The ID of the auction to join
- `token` - Your authentication token (from login)

**Note:** You must be a participant of the auction to connect.

### Messages from Server

#### Auction Update
Sent when auction data changes (new bid, status change):
```json
{
    "title": "Auction Title",
    "description": "Item description",
    "image": "http://localhost:9000/media/auction_items/image.jpg",
    "starting_price": "100.00",
    "status": "started",
    "last_vote": {
        "user": "bidder@email.com",
        "price": "150.00"
    }
}
```

#### Bid Response
After placing a bid:
```json
{"success": "Bid of 200 placed successfully."}
```
or
```json
{"error": "Bid must be higher than the starting price of 100.00."}
```

### Messages to Server

#### Place Bid
```json
{
    "action": "place_bid",
    "price": "200.00"
}
```

### Auction Status Values
- `scheduled` - Auction not yet started
- `started` - Auction is live, bidding is open
- `ended` - Auction has ended

---

## Error Responses

All error responses follow this format:
```json
{"detail": "Error message here"}
```

Common HTTP status codes:
- `400` - Bad Request (validation error)
- `401` - Unauthorized (invalid/missing token)
- `403` - Forbidden (account not verified)
- `404` - Not Found
""",
        contact=openapi.Contact(email="support@auction.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Health check endpoints
    path('api/health/', health_check, name='health-check'),
    path('api/health/ready/', readiness_check, name='readiness-check'),
    path('api/health/live/', liveness_check, name='liveness-check'),

    # Admin
    path('admin/', admin.site.urls),

    # API endpoints
    path('api/', include('accounts.urls')),
    path('api/', include('auction.urls')),

    # API Documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)