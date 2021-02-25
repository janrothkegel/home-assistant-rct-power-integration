from collections import defaultdict
from datetime import timedelta
from logging import Logger
from typing import Callable, List, Optional, TypeVar

from homeassistant.core import CALLBACK_TYPE, HomeAssistant, callback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .api import ApiResponseValue, RctPowerApiClient, RctPowerData, ValidApiResponse
from .const import DOMAIN


class RctPowerDataUpdateCoordinator(DataUpdateCoordinator[RctPowerData]):
    """Class to manage fetching data from the rct power inverter API."""

    def __init__(
        self,
        hass: HomeAssistant,
        name: str,
        logger: Logger,
        client: RctPowerApiClient,
        entity_descriptors: List["EntityDescriptor"],
        update_interval: Optional[timedelta] = None,
    ) -> None:
        self.client = client
        self.entity_descriptors = entity_descriptors

        super().__init__(
            hass=hass, logger=logger, name=name, update_interval=update_interval
        )

    def get_latest_response(self, object_id: int):
        return self.data.get(object_id)

    def get_valid_value_or(self, object_id: int, default_value: ApiResponseValue):
        latest_response = self.get_latest_response(object_id)

        if isinstance(latest_response, ValidApiResponse):
            return latest_response.value
        else:
            return default_value

    @property
    def object_ids(self):
        return [
            object_info.object_id
            for entity_descriptor in self.entity_descriptors
            for object_info in entity_descriptor.object_infos
        ]

    async def _async_update_data(self):
        return await self.client.async_get_data(object_ids=self.object_ids)


from .entity import EntityDescriptor
