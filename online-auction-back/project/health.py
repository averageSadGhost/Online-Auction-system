"""
Health check views for monitoring and container orchestration.
"""
from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
import redis
import os


def health_check(request):
    """
    Basic health check endpoint.
    Returns 200 if the application is running.
    """
    return JsonResponse({
        'status': 'healthy',
        'service': 'online-auction-api'
    })


def readiness_check(request):
    """
    Readiness check that verifies all dependencies are available.
    Used by Kubernetes/Docker to determine if the container is ready to serve traffic.
    """
    checks = {
        'database': False,
        'redis': False,
    }
    errors = []

    # Check database connection
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
        checks['database'] = True
    except Exception as e:
        errors.append(f'Database: {str(e)}')

    # Check Redis connection
    try:
        redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379')
        from urllib.parse import urlparse
        parsed = urlparse(redis_url)
        r = redis.Redis(
            host=parsed.hostname or 'localhost',
            port=parsed.port or 6379
        )
        r.ping()
        checks['redis'] = True
    except Exception as e:
        errors.append(f'Redis: {str(e)}')

    # Determine overall status
    all_healthy = all(checks.values())
    status_code = 200 if all_healthy else 503

    return JsonResponse({
        'status': 'ready' if all_healthy else 'not_ready',
        'checks': checks,
        'errors': errors if errors else None
    }, status=status_code)


def liveness_check(request):
    """
    Liveness check endpoint.
    Returns 200 if the application process is alive.
    Used by Kubernetes/Docker to determine if the container should be restarted.
    """
    return JsonResponse({
        'status': 'alive'
    })
