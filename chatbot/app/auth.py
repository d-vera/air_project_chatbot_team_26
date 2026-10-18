import base64
import logging
from typing import Optional
import jwt
from fastapi import Header, HTTPException, status
from app.config import get_settings

logger = logging.getLogger(__name__)


class UnauthorizedException(HTTPException):
    def __init__(self, message: str = "Invalid or expired JWT token"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "unauthorized", "message": message},
        )


def validate_jwt_token(token: str, secret: str) -> dict:
    """Validate token signature and expiration. Return decoded payload or raise UnauthorizedException."""
    keys_to_try = []
    try:
        b64_key = base64.b64decode(secret)
        keys_to_try.append(("base64-decoded", b64_key))
    except Exception:
        pass
    keys_to_try.append(("raw-string", secret))

    for label, key in keys_to_try:
        try:
            payload = jwt.decode(
                token,
                key,
                algorithms=["HS256", "HS384", "HS512"],
                options={"require": ["exp"]},
            )
            logger.info("JWT validated successfully using %s key", label)
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("JWT expired (tried %s key)", label)
            raise UnauthorizedException("Invalid or expired JWT token")
        except jwt.InvalidTokenError as e:
            logger.warning("JWT invalid with %s key: %s", label, e)
            continue
        except Exception as e:
            logger.warning("JWT unexpected error with %s key: %s", label, e)
            continue

    logger.error("JWT validation failed with all keys. Secret length=%d, token prefix=%s...", len(secret), token[:20])
    raise UnauthorizedException("Invalid or expired JWT token")


async def get_current_token(
    authorization: Optional[str] = Header(None, alias="Authorization")
) -> str:
    """Extract, validate, and return the raw JWT token."""
    if not authorization:
        logger.warning("No Authorization header present")
        raise UnauthorizedException("Invalid or expired JWT token")

    parts = authorization.strip().split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        logger.warning("Malformed Authorization header: %s", authorization[:30])
        raise UnauthorizedException("Invalid or expired JWT token")

    raw_token = parts[1]
    settings = get_settings()
    logger.info("Validating token (alg from header: %s)", jwt.get_unverified_header(raw_token).get("alg"))
    validate_jwt_token(raw_token, settings.jwt_secret)
    return raw_token

