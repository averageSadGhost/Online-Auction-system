# Online Auction System

A full-featured real-time auction platform with Django REST Framework backend, React web frontend, and Python Tkinter desktop client. Features WebSocket-based live bidding, two-factor authentication, and email notifications.

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [API Documentation](#api-documentation)
- [WebSocket API](#websocket-api)
- [Data Models](#data-models)
- [Email Notifications](#email-notifications)
- [Environment Variables](#environment-variables)
- [Docker Commands](#docker-commands)
- [Management Commands](#management-commands)
- [Testing](#testing)

---

## Features

### Backend
- **User Authentication**
  - Email/password registration with OTP email verification
  - Token-based authentication (DRF Token Auth)
  - Two-factor authentication (TOTP) with authenticator app support
  - Password reset via email link
- **Auction Management**
  - Create, list, and manage auctions
  - Real-time bidding via WebSocket
  - Automatic status transitions (scheduled → started → ended)
  - Search, filter, and sort auctions
- **Notifications**
  - Email notifications for auction events (start, end, outbid, winner)
  - Prevents duplicate notifications
- **API Documentation**
  - Interactive Swagger UI
  - ReDoc documentation
- **Health Checks**
  - Liveness and readiness endpoints for container orchestration

### React Frontend
- Landing page with featured auctions
- User authentication (login, register, OTP verification, password reset)
- Two-factor authentication setup and management
- Browse and search available auctions
- Join auctions and track them in "My Auctions"
- Real-time bidding with live WebSocket updates
- Won auctions history
- Dark/light theme support
- Responsive, modern UI

### Desktop Client (Tkinter)
- Native desktop application
- Full authentication flow
- Browse and join auctions
- Real-time bidding

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              CLIENTS                                     │
├─────────────────┬─────────────────┬─────────────────────────────────────┤
│  React Frontend │  Desktop Client │         Mobile App (Future)          │
│   (Port 3000)   │    (Tkinter)    │                                      │
└────────┬────────┴────────┬────────┴─────────────────────────────────────┘
         │                 │
         │    HTTP/REST    │    WebSocket
         ▼                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         DJANGO BACKEND                                   │
│                          (Port 9000)                                     │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                   │
│  │  REST API    │  │   WebSocket  │  │    Admin     │                   │
│  │  (DRF)       │  │  (Channels)  │  │   Panel      │                   │
│  └──────────────┘  └──────────────┘  └──────────────┘                   │
│                                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                   │
│  │   Accounts   │  │   Auction    │  │    Huey      │                   │
│  │     App      │  │     App      │  │   Tasks      │                   │
│  └──────────────┘  └──────────────┘  └──────────────┘                   │
└─────────────────────────────────────────────────────────────────────────┘
         │                 │                    │
         ▼                 ▼                    ▼
┌─────────────────┐ ┌──────────────┐  ┌──────────────────┐
│    Database     │ │    Redis     │  │   Email Server   │
│ (SQLite/Postgres)│ │  (Cache/MQ)  │  │     (SMTP)       │
└─────────────────┘ └──────────────┘  └──────────────────┘
```

---

## Tech Stack

### Backend
| Component | Technology |
|-----------|------------|
| Framework | Django 5.x, Django REST Framework |
| WebSocket | Django Channels, Daphne ASGI |
| Task Queue | Huey with Redis backend |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Cache/Message Broker | Redis |
| 2FA | PyOTP (TOTP) |
| API Docs | drf-yasg (Swagger/ReDoc) |

### Frontend
| Component | Technology |
|-----------|------------|
| Framework | React 18 |
| Routing | React Router v6 |
| State | React Context API |
| WebSocket | Native WebSocket API |
| Styling | CSS with CSS Variables (theming) |

---

## Project Structure

```
Online-Auction-system/
├── online-auction-back/              # Django REST Framework Backend
│   ├── accounts/                     # User authentication app
│   │   ├── models.py                 # CustomUser model (email auth, 2FA)
│   │   ├── views.py                  # Auth views (register, login, 2FA)
│   │   ├── serializers.py            # Request/response serializers
│   │   └── utils.py                  # Email sending utilities
│   ├── auction/                      # Auction & bidding app
│   │   ├── models.py                 # Auction, Vote, Notification models
│   │   ├── views.py                  # Auction CRUD & actions
│   │   ├── consumers.py              # WebSocket consumer
│   │   ├── tasks.py                  # Huey background tasks
│   │   ├── filters.py                # Auction filters
│   │   └── management/commands/      # Custom management commands
│   ├── project/                      # Django project settings
│   │   ├── settings/                 # Environment-specific settings
│   │   │   ├── base.py               # Common settings
│   │   │   ├── development.py        # Dev settings
│   │   │   └── production.py         # Prod settings
│   │   ├── asgi.py                   # ASGI config (WebSocket)
│   │   ├── urls.py                   # URL routing & Swagger setup
│   │   └── health.py                 # Health check endpoints
│   ├── Dockerfile                    # Production Docker image
│   ├── entrypoint.sh                 # Container entrypoint script
│   └── requirements.txt              # Python dependencies
│
├── online-auction-frontend/          # React Web Frontend
│   ├── src/
│   │   ├── components/               # Reusable UI components
│   │   │   ├── Navbar.js             # Navigation with theme toggle
│   │   │   ├── AuctionCard.js        # Auction display card
│   │   │   └── ProtectedRoute.js     # Auth route wrapper
│   │   ├── context/                  # React Context providers
│   │   │   └── AuthContext.js        # Authentication state
│   │   ├── pages/                    # Page components
│   │   │   ├── Landing.js            # Public landing page
│   │   │   ├── Login.js              # Login page
│   │   │   ├── Register.js           # Registration page
│   │   │   ├── VerifyOtp.js          # OTP verification
│   │   │   ├── ForgotPassword.js     # Password reset request
│   │   │   ├── ResetPassword.js      # Password reset form
│   │   │   ├── TwoFactorSetup.js     # 2FA setup page
│   │   │   ├── Auctions.js           # Browse auctions
│   │   │   ├── MyAuctions.js         # User's joined auctions
│   │   │   ├── WonAuctions.js        # User's won auctions
│   │   │   └── AuctionDetail.js      # Real-time bidding page
│   │   ├── services/                 # API & WebSocket services
│   │   │   └── api.js                # REST API client
│   │   ├── config/                   # App configuration
│   │   │   └── settings.js           # API URLs, constants
│   │   └── utils/                    # Utility functions
│   │       └── formatters.js         # Date/currency formatters
│   ├── Dockerfile                    # Production Docker image
│   ├── nginx.conf                    # Nginx configuration
│   └── package.json                  # Node dependencies
│
├── online-auction-client-app/        # Tkinter Desktop Client
│   └── main.py                       # Desktop app entry point
│
├── docker-compose.yml                # Production Docker setup
└── docker-compose.dev.yml            # Development Docker setup
```

---

## Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/your-repo/Online-Auction-system.git
cd Online-Auction-system

# Start all services
docker-compose up --build

# Access:
# - Frontend:     http://localhost:3000
# - Backend API:  http://localhost:9000/api/
# - Swagger Docs: http://localhost:9000/swagger/
# - ReDoc:        http://localhost:9000/redoc/
# - Admin Panel:  http://localhost:9000/admin/
```

### Option 2: Manual Setup

#### Backend

```bash
cd online-auction-back

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Generate sample auctions (optional)
python manage.py generate_auctions --category all --count 5

# Start Redis (required for WebSocket and tasks)
redis-server

# Terminal 1: Start server with WebSocket support
daphne -b 0.0.0.0 -p 9000 project.asgi:application

# Terminal 2: Start task queue worker
python manage.py run_huey
```

#### Frontend

```bash
cd online-auction-frontend

# Install dependencies
npm install

# Start development server
npm start

# Access: http://localhost:3000
```

---

## API Documentation

### Interactive Documentation

| URL | Description |
|-----|-------------|
| `/swagger/` | Swagger UI - Interactive API explorer |
| `/redoc/` | ReDoc - Clean API documentation |

### Authentication Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/register/` | No | Register new user (sends OTP email) |
| POST | `/api/verify-otp/` | No | Verify email with 6-digit OTP |
| POST | `/api/resend-otp/` | No | Resend OTP (if expired) |
| POST | `/api/login/` | No | Login (returns token or 2FA challenge) |
| GET | `/api/me/` | Yes | Get current user info |
| POST | `/api/forgot-password/` | No | Request password reset email |
| POST | `/api/reset-password/` | No | Reset password with token |

### Two-Factor Authentication Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/2fa/setup/` | Yes | Generate 2FA secret and QR URI |
| POST | `/api/2fa/enable/` | Yes | Enable 2FA with verification code |
| POST | `/api/2fa/disable/` | Yes | Disable 2FA (requires password + code) |
| GET | `/api/2fa/status/` | Yes | Get current 2FA status |
| POST | `/api/2fa/verify/` | No | Verify 2FA code during login |

### Auction Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/auctions/` | Yes | List available auctions (not joined) |
| GET | `/api/auctions/{id}/` | Yes | Get auction details |
| POST | `/api/auctions/{id}/join_auction/` | Yes | Join an auction |
| GET | `/api/auctions/my_auctions/` | Yes | List user's joined auctions |
| GET | `/api/auctions/featured/` | No | Get top 3 featured auctions |
| GET | `/api/auctions/won_auctions/` | Yes | List user's won auctions |

#### Auction Query Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `search` | Search by title or description | `?search=watch` |
| `status` | Filter by status | `?status=started` |
| `min_price` | Minimum starting price | `?min_price=100` |
| `max_price` | Maximum starting price | `?max_price=1000` |
| `ordering` | Sort field (prefix `-` for desc) | `?ordering=-starting_price` |

### Health Check Endpoints

| Endpoint | Description |
|----------|-------------|
| `/api/health/` | Basic health check |
| `/api/health/ready/` | Readiness check (DB connection) |
| `/api/health/live/` | Liveness check |

### Authentication Header

All authenticated endpoints require the `Authorization` header:

```
Authorization: Token your-auth-token-here
```

### Request/Response Examples

#### Register User
```bash
POST /api/register/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123",
  "first_name": "John",
  "last_name": "Doe"
}

# Response (201 Created)
{
  "detail": "OTP sent to your email."
}
```

#### Login (with 2FA)
```bash
POST /api/login/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123"
}

# Response - No 2FA (200 OK)
{
  "token": "abc123...",
  "requires_2fa": false
}

# Response - 2FA Required (200 OK)
{
  "requires_2fa": true,
  "temp_token": "eyJ0..."
}
```

#### Complete 2FA Login
```bash
POST /api/2fa/verify/
Content-Type: application/json

{
  "temp_token": "eyJ0...",
  "code": "123456"
}

# Response (200 OK)
{
  "token": "abc123..."
}
```

---

## WebSocket API

### Connection

Connect to real-time auction updates:

```
ws://localhost:9000/ws/auction/{auction_id}/?token={auth_token}
```

**Requirements:**
- Valid authentication token
- User must be a participant of the auction

### Messages from Server

#### Auction State Update
Sent on connection and when auction data changes:

```json
{
  "title": "Vintage Rolex Watch",
  "description": "1960s Rolex Submariner in excellent condition",
  "image": "http://localhost:9000/media/auction_items/watch.jpg",
  "starting_price": "5000.00",
  "status": "started",
  "last_vote": {
    "user": "bidder@email.com",
    "price": "5500.00"
  }
}
```

#### Bid Response
After placing a bid:

```json
// Success
{"success": "Bid of 6000.00 placed successfully."}

// Error
{"error": "Bid must be higher than the starting price of 5000.00."}
```

### Messages to Server

#### Place Bid
```json
{
  "action": "place_bid",
  "price": "6000.00"
}
```

### Status Values
- `scheduled` - Auction not yet started, users can join
- `started` - Auction is live, bidding is open
- `ended` - Auction has finished, winner determined

---

## Data Models

### User (CustomUser)

| Field | Type | Description |
|-------|------|-------------|
| email | EmailField | Unique email (username) |
| first_name | CharField | User's first name |
| last_name | CharField | User's last name |
| user_type | CharField | 'admin' or 'client' |
| is_verified | Boolean | Email verified status |
| two_factor_enabled | Boolean | 2FA enabled status |
| two_factor_secret | CharField | TOTP secret key |

### Auction

| Field | Type | Description |
|-------|------|-------------|
| title | CharField | Auction item title |
| description | TextField | Item description |
| image | ImageField | Item image |
| starting_price | DecimalField | Starting bid price |
| start_date_time | DateTimeField | Auction start time |
| end_date_time | DateTimeField | Auction end time |
| status | CharField | 'scheduled', 'started', 'ended' |
| users | ManyToMany | Participants |

### Vote (Bid)

| Field | Type | Description |
|-------|------|-------------|
| auction | ForeignKey | Related auction |
| user | ForeignKey | Bidder |
| price | DecimalField | Bid amount |
| created_at | DateTimeField | Bid timestamp |

---

## Email Notifications

The system sends automatic email notifications for:

| Event | Description |
|-------|-------------|
| OTP Verification | 6-digit code for email verification |
| Password Reset | Link to reset password |
| Auction Starting Soon | 15 minutes before auction starts |
| Auction Started | When auction goes live |
| Auction Ending Soon | 15 minutes before auction ends |
| Auction Ended | When auction closes |
| Outbid | When another user places a higher bid |
| Winner | Notification to auction winner |

---

## Environment Variables

### Backend

| Variable | Description | Default |
|----------|-------------|---------|
| `DJANGO_ENV` | Environment (development/production) | development |
| `SECRET_KEY` | Django secret key | - |
| `DEBUG` | Debug mode | True |
| `ALLOWED_HOSTS` | Comma-separated allowed hosts | localhost |
| `DATABASE_URL` | Database URL | sqlite:///db.sqlite3 |
| `REDIS_URL` | Redis connection URL | redis://localhost:6379 |
| `CORS_ALLOWED_ORIGINS` | Allowed CORS origins | http://localhost:3000 |
| `EMAIL_HOST` | SMTP server | smtp.gmail.com |
| `EMAIL_PORT` | SMTP port | 587 |
| `EMAIL_USE_TLS` | Use TLS | True |
| `EMAIL_HOST_USER` | SMTP username | - |
| `EMAIL_HOST_PASSWORD` | SMTP password | - |
| `FRONTEND_URL` | Frontend URL (for email links) | http://localhost:3000 |

### Frontend

| Variable | Description | Default |
|----------|-------------|---------|
| `REACT_APP_API_URL` | Backend API URL | http://localhost:9000/api |
| `REACT_APP_WS_URL` | WebSocket URL | ws://localhost:9000/ws/auction |

---

## Docker Commands

```bash
# Build and start all services
docker-compose up --build

# Start in detached mode
docker-compose up -d

# View logs
docker-compose logs -f
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f huey

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Rebuild specific service
docker-compose build backend
docker-compose up -d backend

# Run Django commands in container
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
docker-compose exec backend python manage.py generate_auctions --count 10

# View container status
docker-compose ps
```

---

## Management Commands

### Generate Sample Auctions

```bash
# Generate 5 auctions from all categories
python manage.py generate_auctions --count 5

# Generate specific category
python manage.py generate_auctions --category electronics --count 10
python manage.py generate_auctions --category jewelry --count 5
python manage.py generate_auctions --category watches --count 5
python manage.py generate_auctions --category vehicles --count 5

# Custom schedule (auctions starting within 14 days, lasting 48 hours)
python manage.py generate_auctions --count 5 --days-ahead 14 --duration-hours 48
```

**Available Categories:** `electronics`, `jewelry`, `watches`, `vehicles`, `all`

---

## Testing

```bash
cd online-auction-back

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/accounts/test_views.py

# Run with coverage report
pytest --cov=. --cov-report=html

# View coverage report
open htmlcov/index.html
```

---

## Auction Status Flow

```
┌────────────┐     Time Reached     ┌────────────┐     Time Reached     ┌────────────┐
│  SCHEDULED │ ──────────────────▶  │  STARTED   │ ──────────────────▶  │   ENDED    │
│            │    start_date_time   │            │    end_date_time     │            │
└────────────┘                      └────────────┘                      └────────────┘
      │                                   │                                   │
      │                                   │                                   │
      ▼                                   ▼                                   ▼
 Users can join                    Users can bid                    Winner determined
 via REST API                      via WebSocket                    Notifications sent
```

Status transitions are handled automatically by Huey background tasks that run every minute.

---

## Admin Panel

Access the Django admin panel at `/admin/` to:
- Manage users and permissions
- Create and edit auctions
- View bids and notifications
- Monitor system activity

```bash
# Create admin user
python manage.py createsuperuser
```

---

## License

BSD License
