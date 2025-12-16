#!/bin/bash
set -e

# Ensure directories exist (they may be overwritten by volume mounts)
mkdir -p /app/staticfiles /app/media /app/logs /app/data

# Wait for database to be ready (if using PostgreSQL)
if [ -n "$DATABASE_URL" ]; then
    echo "Waiting for database..."
    python << END
import sys
import time
import os

# Parse DATABASE_URL
db_url = os.environ.get('DATABASE_URL', '')
if 'postgres' in db_url:
    import psycopg2
    from urllib.parse import urlparse

    result = urlparse(db_url)
    dbname = result.path[1:]
    user = result.username
    password = result.password
    host = result.hostname
    port = result.port or 5432

    max_retries = 30
    retry_count = 0

    while retry_count < max_retries:
        try:
            conn = psycopg2.connect(
                dbname=dbname,
                user=user,
                password=password,
                host=host,
                port=port
            )
            conn.close()
            print("Database is ready!")
            sys.exit(0)
        except psycopg2.OperationalError:
            retry_count += 1
            print(f"Database not ready, waiting... ({retry_count}/{max_retries})")
            time.sleep(1)

    print("Could not connect to database")
    sys.exit(1)
else:
    print("Using SQLite, no wait needed")
    sys.exit(0)
END
fi

# Wait for Redis to be ready
if [ -n "$REDIS_URL" ]; then
    echo "Waiting for Redis..."
    python << END
import sys
import time
import os

redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379')
max_retries = 30
retry_count = 0

try:
    import redis
    from urllib.parse import urlparse

    result = urlparse(redis_url)
    host = result.hostname or 'localhost'
    port = result.port or 6379

    while retry_count < max_retries:
        try:
            r = redis.Redis(host=host, port=port)
            r.ping()
            print("Redis is ready!")
            sys.exit(0)
        except redis.ConnectionError:
            retry_count += 1
            print(f"Redis not ready, waiting... ({retry_count}/{max_retries})")
            time.sleep(1)

    print("Could not connect to Redis")
    sys.exit(1)
except ImportError:
    print("Redis package not installed, skipping check")
    sys.exit(0)
END
fi

# Run migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start the appropriate service based on the command
case "$1" in
    web)
        echo "Starting web server..."
        exec daphne -b 0.0.0.0 -p 8000 project.asgi:application
        ;;
    huey)
        echo "Starting Huey task queue..."
        exec python manage.py run_huey
        ;;
    *)
        # Default: run web server
        echo "Starting web server (default)..."
        exec daphne -b 0.0.0.0 -p 8000 project.asgi:application
        ;;
esac
