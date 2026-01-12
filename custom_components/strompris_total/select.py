from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DEFAULTS,
    OPT_PRICE_AREA,
    OPT_DSO,
    OPT_CONTRACT,
    PRICE_AREAS,
    CONTRACTS,
)
from .entity import StromprisBaseEntity
from .tariffs import load_dso_catalog

@dataclass(frozen=True, kw_only=True)
class StromprisSelectDescription(SelectEntityDescription):
    option_key: str

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    catalog = load_dso_catalog()
    dso_values = list(catalog.keys())

    descriptions: list[StromprisSelectDescription] = [
        StromprisSelectDescription(
            key="prisomrade",
            name="Prisområde",
            option_key=OPT_PRICE_AREA,
            options=PRICE_AREAS,
        ),
        StromprisSelectDescription(
            key="avtaletype",
            name="Avtaletype",
            option_key=OPT_CONTRACT,
            options=CONTRACTS,
        ),
        StromprisSelectDescription(
            key="nettselskap",
            name="Nettselskap",
            option_key=OPT_DSO,
            options=dso_values,
        ),
    ]
    async_add_entities([StromprisSelectEntity(hass, entry, d) for d in descriptions])

class StromprisSelectEntity(StromprisBaseEntity, SelectEntity):
    entity_description: StromprisSelectDescription

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, description: StromprisSelectDescription) -> None:
        super().__init__(entry)
        self.hass = hass
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"

    @property
    def current_option(self) -> str | None:
        return self.entry.options.get(self.entity_description.option_key, DEFAULTS[self.entity_description.option_key])

    async def async_select_option(self, option: str) -> None:
        options = dict(self.entry.options)
        options[self.entity_description.option_key] = option

        # If DSO changed, merge in DSO defaults (do not overwrite user-set keys already present)
        if self.entity_description.option_key == OPT_DSO:
            catalog = load_dso_catalog()
            dso_defaults = catalog.get(option, {}).get("defaults", {})
            for k, v in dso_defaults.items():
                options.setdefault(k, v)

        self.hass.config_entries.async_update_entry(self.entry, options=options)
        self.async_write_ha_state()
