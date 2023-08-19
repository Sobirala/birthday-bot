from typing import Any, Dict, Optional, Self

from geopy import GoogleV3, Location, Point
from geopy.adapters import AioHTTPAdapter
from pytz.tzinfo import BaseTzInfo

from bot.services.singleton import SingletonMeta
from bot.settings import settings


class GoogleMaps(metaclass=SingletonMeta):
    client: GoogleV3

    def __init__(self):
        self.client = GoogleV3(
            api_key=settings.GOOGLE_TOKEN.get_secret_value(),
            user_agent="birthday_bot",
            adapter_factory=AioHTTPAdapter,
            timeout=1000,
        )

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.__aexit__(exc_type, exc_val, exc_tb)

    async def get_address(self, city: str, language: str) -> Location:
        address = await self.client.geocode(city, exactly_one=True, language=language)
        return address

    @staticmethod
    async def get_country_by_address(address: Any) -> Optional[Dict[str, Any]]:
        for address_component in address.raw["address_components"]:
            if "country" in address_component["types"]:
                return address_component
        return None

    async def get_timezone(self, latitude: float, longitude: float) -> BaseTzInfo:
        timezone = (
            await self.client.reverse_timezone(
                Point(latitude=latitude, longitude=longitude)
            )
        ).pytz_timezone
        return timezone
