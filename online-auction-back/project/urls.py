from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from project.health import health_check, readiness_check, liveness_check

token_auth = openapi.Parameter(
    'Authorization',
    openapi.IN_HEADER,
    description="Token authentication. Format: 'Token <your-token>'",
    type=openapi.TYPE_STRING
)

schema_view = get_schema_view(
    openapi.Info(
        title="Online Auction API",
        default_version='v1',
        description="""
# Online Auction API Documentation

A full-featured real-time auction platform API with WebSocket support for live bidding, two-factor authentication, and comprehensive email notifications.

## Authentication

Most endpoints require token authentication. Include the token in the `Authorization` header:
```
Authorization: Token your-auth-token-here
```

---

## Public Endpoints (No Authentication Required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/register/` | Create a new account (sends OTP email) |
| POST | `/api/verify-otp/` | Verify email with 6-digit OTP code |
| POST | `/api/resend-otp/` | Resend OTP code (if expired) |
| POST | `/api/login/` | Get auth token (or 2FA challenge) |
| POST | `/api/forgot-password/` | Request password reset email |
| POST | `/api/reset-password/` | Reset password with token |
| POST | `/api/2fa/verify/` | Complete 2FA login verification |
| GET | `/api/auctions/featured/` | Get top 3 featured auctions |

---

## Authentication Flow

### Standard Login
1. **Register** - `POST /api/register/` - Creates account, sends OTP
2. **Verify OTP** - `POST /api/verify-otp/` - Verify email
3. **Login** - `POST /api/login/` - Returns auth token

### Login with Two-Factor Authentication
1. **Login** - `POST /api/login/` - Returns `requires_2fa: true` and `temp_token`
2. **Verify 2FA** - `POST /api/2fa/verify/` - Submit temp_token + TOTP code, get auth token

### Password Reset
1. **Request Reset** - `POST /api/forgot-password/` - Sends reset email
2. **Reset Password** - `POST /api/reset-password/` - Submit token + new password

---

## Two-Factor Authentication (2FA)

Enable TOTP-based 2FA with any authenticator app (Google Authenticator, Authy, etc.)

### Setup Flow
1. **Setup** - `POST /api/2fa/setup/` - Get secret and QR URI
2. **Enable** - `POST /api/2fa/enable/` - Verify code to enable 2FA

### Disable Flow
1. **Disable** - `POST /api/2fa/disable/` - Requires password + current TOTP code

### Status
- **Check Status** - `GET /api/2fa/status/` - Returns `{"enabled": true/false}`

---

## Auction Flow

1. **Featured Auctions** - `GET /api/auctions/featured/` *[Public]*
2. **List Auctions** - `GET /api/auctions/` - Browse available auctions *[Auth]*
3. **Join Auction** - `POST /api/auctions/{id}/join_auction/` *[Auth]*
4. **My Auctions** - `GET /api/auctions/my_auctions/` *[Auth]*
5. **Won Auctions** - `GET /api/auctions/won_auctions/` *[Auth]*
6. **Auction Details** - `GET /api/auctions/{id}/` *[Auth]*

### Query Parameters
- `search` - Search by title or description
- `status` - Filter by status (scheduled, started, ended)
- `min_price` / `max_price` - Price range filter
- `ordering` - Sort by field (prefix `-` for descending)

---

## WebSocket API

### Connection
```
ws://localhost:9000/ws/auction/{auction_id}/?token={auth_token}
```

**Requirements:**
- Valid authentication token
- User must be a participant of the auction

### Messages from Server

**Auction Update** (on connect and bid changes):
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

**Bid Response:**
```json
{"success": "Bid of 200 placed successfully."}
// or
{"error": "Bid must be higher than the starting price of 100.00."}
```

### Messages to Server

**Place Bid:**
```json
{
    "action": "place_bid",
    "price": "200.00"
}
```

### Auction Status Values
- `scheduled` - Users can join, bidding not open
- `started` - Auction is live, bidding is open
- `ended` - Auction finished, winner determined

---

## Error Responses

```json
{"detail": "Error message here"}
```

| Status | Description |
|--------|-------------|
| 400 | Bad Request (validation error) |
| 401 | Unauthorized (invalid/missing token) |
| 403 | Forbidden (account not verified) |
| 404 | Not Found |

---

## Health Check Endpoints

| Endpoint | Description |
|----------|-------------|
| `/api/health/` | Basic health check |
| `/api/health/ready/` | Readiness (DB connection) |
| `/api/health/live/` | Liveness check |
""",
        contact=openapi.Contact(email="support@auctionhub.com"),
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