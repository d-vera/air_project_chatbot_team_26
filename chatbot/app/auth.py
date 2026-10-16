from typing import Optional
import jwt
from fastapi import Header, HTTPException, status
from app.config import get_settings


class UnauthorizedException(HTTPException):
    def __init__(self, message: str = "Invalid or expired JWT token"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "unauthorized", "message": message},
        )


def validate_jwt_token(token: str, secret: str) -> dict:
    """Validate token signature and expiration. Return decoded payload or raise UnauthorizedException."""
    try:
        payload = jwt.decode(
            token,
            secret,
            algorithms=["HS256", "HS384", "HS512"],
            options={"require": ["exp"]},
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise UnauthorizedException("Invalid or expired JWT token")
    except jwt.InvalidTokenError:
        raise UnauthorizedException("Invalid or expired JWT token")
    except Exception:
        raise UnauthorizedException("Invalid or expired JWT token")


async def get_current_token(
    authorization: Optional[str] = Header(None, alias="Authorization")
) -> str:
    """Extract, validate, and return the raw JWT token."""
    if not authorization:
        raise UnauthorizedException("Invalid or expired JWT token")

    parts = authorization.strip().split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise UnauthorizedException("Invalid or expired JWT token")

    raw_token = parts[1]
    settings = get_settings()
    validate_jwt_token(raw_token, settings.jwt_secret)
    return raw_token
