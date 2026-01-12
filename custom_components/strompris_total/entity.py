from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import DeviceInfo, Entity

from .const import DOMAIN, CONF_NAME

class StromprisBaseEntity(Entity):
    _attr_has_entity_name = True

    def __init__(self, entry: ConfigEntry) -> None:
        self.entry = entry
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.data.get(CONF_NAME, "Strømpris Total"),
            manufacturer="Custom",
            model="Strømpris Total (Norge)",
        )
