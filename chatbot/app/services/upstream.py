from typing import Any, Dict, Optional
import httpx
from fastapi import HTTPException, status
from app.config import get_settings


class BadGatewayException(HTTPException):
    def __init__(self, message: str = "Unable to reach the Air Project API"):
        super().__init__(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={"error": "bad_gateway", "message": message},
        )


class UpstreamClient:
    def __init__(self, base_url: Optional[str] = None):
        settings = get_settings()
        self.base_url = (base_url or settings.upstream_api_url).rstrip("/")

    def _headers(self, token: str) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        }

    async def get_current_air_quality(
        self, token: str, device_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Fetch latest air quality readings. Optionally filter by deviceId."""
        params = {}
        if device_id:
            params["deviceId"] = device_id

        url = f"{self.base_url}/api/air-quality/current"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, headers=self._headers(token), params=params)
                if response.status_code == 401:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail={"error": "unauthorized", "message": "Invalid or expired JWT token"},
                    )
                response.raise_for_status()
                return response.json()
        except (httpx.ConnectError, httpx.TimeoutException, httpx.NetworkError) as e:
            raise BadGatewayException() from e
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={"error": "unauthorized", "message": "Invalid or expired JWT token"},
                )
            raise BadGatewayException(f"Upstream returned status code {e.response.status_code}") from e

    async def get_historical_air_quality(
        self,
        token: str,
        range_val: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        device_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Fetch historical aggregated air quality data."""
        params = {}
        if range_val:
            params["range"] = range_val
        if from_date:
            params["from"] = from_date
        if to_date:
            params["to"] = to_date
        if device_id:
            params["deviceId"] = device_id

        url = f"{self.base_url}/api/air-quality/historical"
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(url, headers=self._headers(token), params=params)
                if response.status_code == 401:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail={"error": "unauthorized", "message": "Invalid or expired JWT token"},
                    )
                response.raise_for_status()
                return response.json()
        except (httpx.ConnectError, httpx.TimeoutException, httpx.NetworkError) as e:
            raise BadGatewayException() from e
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={"error": "unauthorized", "message": "Invalid or expired JWT token"},
                )
            raise BadGatewayException(f"Upstream returned status code {e.response.status_code}") from e

    async def get_user_preferences(self, token: str) -> Optional[Dict[str, Any]]:
        """Fetch user preferences (language, theme). Fallback gracefully on error."""
        url = f"{self.base_url}/api/preferences/me"
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url, headers=self._headers(token))
                if response.is_success:
                    return response.json()
                return None
        except Exception:
            return None

    async def get_user_profile(self, token: str) -> Optional[Dict[str, Any]]:
        """Fetch user profile details (e.g. firstName). Fallback gracefully on error."""
        url = f"{self.base_url}/api/users/me"
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url, headers=self._headers(token))
                if response.is_success:
                    return response.json()
                return None
        except Exception:
            return None
