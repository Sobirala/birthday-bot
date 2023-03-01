from typing import Any, Dict, Optional

from geopy import GoogleV3, Location, Point
from geopy.adapters import AioHTTPAdapter
from pytz.tzinfo import BaseTzInfo

from bot.services.singleton import SingletonMeta


class GoogleMaps(metaclass=SingletonMeta):
    adapter: GoogleV3

    def __init__(self, api_key: str):
        self.adapter = GoogleV3(
            api_key=api_key,
            user_agent="birthday_bot",
            adapter_factory=AioHTTPAdapter,
            timeout=1000,
        )

    async def get_address(self, city: str, language: str) -> Location:
        address = await self.adapter.geocode(city, exactly_one=True, language=language)
        return address

    @staticmethod
    async def get_country_by_address(address: Any) -> Optional[Dict[str, Any]]:
        for address_component in address.raw["address_components"]:
            if "country" in address_component["types"]:
                return address_component
        return None

    async def get_timezone(self, latitude: float, longitude: float) -> BaseTzInfo:
        timezone = (
            await self.adapter.reverse_timezone(
                Point(latitude=latitude, longitude=longitude)
            )
        ).pytz_timezone
        return timezone
