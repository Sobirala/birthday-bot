from types import TracebackType
from typing import Any, Dict, Optional, Self, Type

from geopy import GoogleV3, Location  # type: ignore
from geopy.adapters import AioHTTPAdapter  # type: ignore
from tzfpy import get_tz

from bot.settings import settings


class GeoService:
    client: GoogleV3

    def __init__(self) -> None:
        self.client = GoogleV3(
            api_key=settings.GOOGLE_TOKEN.get_secret_value(),
            user_agent="birthday_bot",
            adapter_factory=AioHTTPAdapter,
            timeout=1000,
        )

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, exc_type: Type[BaseException], exc_val: BaseException, exc_tb: TracebackType) -> None:
        await self.client.__aexit__(exc_type, exc_val, exc_tb)

    async def get_address(self, city: str, language: str) -> Location:
        return await self.client.geocode(city, exactly_one=True, language=language)

    @staticmethod
    async def get_country_by_address(address: Any) -> Optional[Dict[str, Any]]:
        for address_component in address.raw["address_components"]:
            if "country" in address_component["types"]:
                return address_component
        return None

    @staticmethod
    async def get_timezone(latitude: float, longitude: float) -> str:
        return get_tz(longitude, latitude)
