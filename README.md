# Online Auction System

A real-time auction platform with Django REST Framework backend, React web frontend, and Python Tkinter desktop client. Features WebSocket-based live bidding.

## Features

### Backend
- User registration with email OTP verification
- Token-based authentication
- Real-time bidding via WebSocket
- Auction lifecycle management (scheduled -> started -> ended)
- Background task queue for automatic auction status updates
- Swagger/ReDoc API documentation
- Health check endpoints for container orchestration
- Management command to generate sample auctions

### React Frontend
- User authentication (login, register, OTP verification)
- Browse available auctions with current bid info
- Join auctions and track them in "My Auctions"
- Real-time bidding with live updates via WebSocket
- Responsive, modern UI

### Desktop Client (Tkinter)
- Native desktop application
- Same functionality as web frontend

## Tech Stack

### Backend
- **Framework**: Django 5.x, Django REST Framework
- **WebSocket**: Django Channels, Daphne ASGI server
- **Task Queue**: Huey with Redis
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Cache**: Redis

### Frontend
- **Framework**: React 18
- **Routing**: React Router v6
- **State**: React Context API

## Project Structure

```
Online-Auction-system/
├── online-auction-back/          # Django REST Framework Backend
│   ├── accounts/                 # User authentication app
│   ├── auction/                  # Auction & bidding app
│   │   ├── consumers.py          # WebSocket consumers
│   │   ├── models.py             # Auction, Vote models
│   │   └── management/commands/  # Custom commands
│   ├── project/                  # Django project settings
│   │   └── settings/             # Environment-specific settings
│   └── requirements.txt
│
├── online-auction-frontend/      # React Web Frontend
│   ├── src/
│   │   ├── components/           # Reusable components
│   │   ├── context/              # Auth context provider
│   │   ├── pages/                # Page components
│   │   ├── services/             # API & WebSocket services
│   │   └── utils/                # Utility functions
│   └── package.json
│
├── online-auction-client-app/    # Tkinter Desktop Client
│
├── docker-compose.yml            # Production Docker setup
└── docker-compose.dev.yml        # Development Docker setup
```

## Quick Start

### Option 1: Docker (Recommended)

```bash
# Development (with hot reload)
docker-compose -f docker-compose.dev.yml up --build

# Access:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:9000/api
# - Swagger Docs: http://localhost:9000/swagger/
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

# Start Redis (required)
redis-server

# Terminal 1: Start server with WebSocket support
daphne -b 0.0.0.0 -p 9000 project.asgi:application

# Terminal 2: Start task queue
python manage.py run_huey
```

#### React Frontend

```bash
cd online-auction-frontend

# Install dependencies
npm install

# Start development server
npm start

# Access: http://localhost:3000
```

## API Documentation

### REST Endpoints

#### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/register/` | Register new user |
| POST | `/api/verify-otp/` | Verify email OTP |
| POST | `/api/resend-otp/` | Resend OTP |
| POST | `/api/login/` | Login and get token |
| GET | `/api/me/` | Get user info |

#### Auctions
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/auctions/` | List available auctions |
| GET | `/api/auctions/{id}/` | Get auction details |
| POST | `/api/auctions/{id}/join_auction/` | Join an auction |
| GET | `/api/auctions/my_auctions/` | List user's auctions |

### Authentication Header

```
Authorization: Token your-auth-token-here
```

### WebSocket API

Connect to real-time auction:
```
ws://localhost:9000/ws/auction/{auction_id}/?token={auth_token}
```

**Place a bid:**
```json
{"action": "place_bid", "price": "150.00"}
```

**Receive updates:**
```json
{
    "title": "Auction Title",
    "starting_price": "100.00",
    "status": "started",
    "last_vote": {
        "user": "bidder@email.com",
        "price": "150.00"
    }
}
```

### Interactive Docs
- **Swagger**: http://localhost:9000/swagger/
- **ReDoc**: http://localhost:9000/redoc/

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

# Custom schedule
python manage.py generate_auctions --count 5 --days-ahead 14 --duration-hours 48
```

**Categories**: `electronics`, `jewelry`, `watches`, `vehicles`, `all`

## Environment Variables

### Backend
| Variable | Description | Default |
|----------|-------------|---------|
| `DJANGO_ENV` | Environment | development |
| `SECRET_KEY` | Django secret key | - |
| `DEBUG` | Debug mode | True |
| `ALLOWED_HOSTS` | Allowed hosts | localhost |
| `REDIS_URL` | Redis URL | redis://localhost:6379 |
| `CORS_ALLOWED_ORIGINS` | CORS origins | http://localhost:3000 |
| `DATABASE_URL` | Database URL | SQLite |
| `EMAIL_HOST_USER` | SMTP email | - |
| `EMAIL_HOST_PASSWORD` | SMTP password | - |

### Frontend
| Variable | Description | Default |
|----------|-------------|---------|
| `REACT_APP_API_URL` | Backend API URL | http://localhost:9000/api |
| `REACT_APP_WS_URL` | WebSocket URL | ws://localhost:9000/ws/auction |

## Auction Status Flow

1. **Scheduled** - Auction created, users can join
2. **Started** - Auction live, participants can bid
3. **Ended** - Auction finished, winner determined

Status transitions are automatic via Huey task queue.

## Docker Commands

```bash
# Build and start
docker-compose -f docker-compose.dev.yml up --build

# Stop
docker-compose down

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Run migrations
docker-compose exec backend python manage.py migrate

# Create superuser
docker-compose exec backend python manage.py createsuperuser

# Generate auctions
docker-compose exec backend python manage.py generate_auctions --count 10
```

## Health Check Endpoints

| Endpoint | Description |
|----------|-------------|
| `/api/health/` | Basic health check |
| `/api/health/ready/` | Readiness (DB connection) |
| `/api/health/live/` | Liveness check |

## Desktop Client Setup

```bash
cd online-auction-client-app

python -m venv venv
source venv/bin/activate

pip install requests pillow websockets

python main.py
```

## Running Tests

```bash
cd online-auction-back

# Run all tests
pytest

# With coverage
pytest --cov=. --cov-report=html

# Specific module
pytest tests/accounts/
```

## Admin Panel

- URL: http://localhost:9000/admin/
- Create superuser: `python manage.py createsuperuser`

## License

BSD License
