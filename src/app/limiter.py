import json

from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address

# Global baseline limiter -- applies to every route unless a route
# overrides it with its own @limiter.limit(...), mirroring the Node
# backend's app-wide limiter (100/15min, src/app.ts:39-46). Without
# this, only /auth/login had any throttling at all.
limiter = Limiter(key_func=get_remote_address, default_limits=["100/15 minutes"])


def login_rate_limit_key(request: Request) -> str:
    """
    Keys the login-specific rate limit by IP + attempted email, mirroring
    src/middlewares/rateLimiters.ts's loginRateLimiter exactly: one IP
    can't be used to spray many accounts unnoticed, and one attacker
    can't lock out a legitimate user by hammering their email from many
    IPs, the way plain IP-only keying would allow either.

    Reads request._body directly rather than `await request.body()`:
    slowapi calls key_func synchronously (it is not awaited), but by the
    time it runs here, FastAPI has already read and cached the body
    while resolving this route's `login_data: LoginRequest` parameter --
    so the bytes are already sitting in Starlette's Request cache, not
    read fresh. Falls back to IP-only if that's ever not true (e.g. a
    malformed/non-JSON body) rather than raising out of a rate limiter.
    """
    ip = get_remote_address(request)
    body = getattr(request, "_body", None)
    if not body:
        return ip

    try:
        email = json.loads(body).get("email")
    except (ValueError, AttributeError):
        email = None

    return f"{ip}:{str(email).lower() if email else 'unknown'}"
