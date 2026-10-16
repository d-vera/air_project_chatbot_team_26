import asyncio
import json
from typing import Any, Dict, List, Optional
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
from app.services.upstream import UpstreamClient


class CurrentAirQualityInput(BaseModel):
    device_id: Optional[str] = Field(
        default=None,
        description="Optional device ID or sensor UID to filter readings for a specific device.",
    )


class HistoricalAirQualityInput(BaseModel):
    range_val: Optional[str] = Field(
        default=None,
        description="Predefined time range: LAST_DAY, LAST_WEEK, LAST_MONTH, or LAST_YEAR.",
    )
    from_date: Optional[str] = Field(
        default=None,
        description="Custom range start date (ISO-8601 Instant e.g. 2026-09-29T00:00:00Z or date-only YYYY-MM-DD). Mutually exclusive with range_val.",
    )
    to_date: Optional[str] = Field(
        default=None,
        description="Custom range end date (ISO-8601 Instant e.g. 2026-09-29T00:00:00Z or date-only YYYY-MM-DD). Mutually exclusive with range_val.",
    )
    device_id: Optional[str] = Field(
        default=None,
        description="Optional device ID to filter historical data for a specific device.",
    )


def create_air_quality_tools(token: str, upstream_client: Optional[UpstreamClient] = None) -> List[StructuredTool]:
    client = upstream_client or UpstreamClient()

    async def _current_air_quality(device_id: Optional[str] = None) -> str:
        data = await client.get_current_air_quality(token, device_id=device_id)
        return json.dumps(data)

    def _current_air_quality_sync(device_id: Optional[str] = None) -> str:
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If running inside existing loop, create task or new loop in thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    return pool.submit(asyncio.run, client.get_current_air_quality(token, device_id=device_id)).result()
            return asyncio.run(client.get_current_air_quality(token, device_id=device_id))
        except Exception as e:
            return f"Error fetching current air quality: {str(e)}"

    async def _historical_air_quality(
        range_val: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        device_id: Optional[str] = None,
    ) -> str:
        data = await client.get_historical_air_quality(
            token,
            range_val=range_val,
            from_date=from_date,
            to_date=to_date,
            device_id=device_id,
        )
        return json.dumps(data)

    def _historical_air_quality_sync(
        range_val: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        device_id: Optional[str] = None,
    ) -> str:
        try:
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                res = pool.submit(
                    asyncio.run,
                    client.get_historical_air_quality(
                        token,
                        range_val=range_val,
                        from_date=from_date,
                        to_date=to_date,
                        device_id=device_id,
                    ),
                ).result()
                return json.dumps(res)
        except Exception as e:
            return f"Error fetching historical air quality: {str(e)}"

    current_tool = StructuredTool.from_function(
        func=_current_air_quality_sync,
        coroutine=_current_air_quality,
        name="get_current_air_quality",
        description=(
            "Fetches latest air quality measurements (temperature, humidity, CO2, PM1.0, PM2.5, PM10) "
            "for devices. Can optionally filter by device_id."
        ),
        args_schema=CurrentAirQualityInput,
    )

    historical_tool = StructuredTool.from_function(
        func=_historical_air_quality_sync,
        coroutine=_historical_air_quality,
        name="get_historical_air_quality",
        description=(
            "Fetches historical time-aggregated air quality measurements (temperature, humidity, CO2, PM1.0, PM2.5, PM10). "
            "Accepts range_val (LAST_DAY, LAST_WEEK, LAST_MONTH, LAST_YEAR) or custom date range (from_date, to_date). "
            "Can optionally filter by device_id."
        ),
        args_schema=HistoricalAirQualityInput,
    )

    return [current_tool, historical_tool]
