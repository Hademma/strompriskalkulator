from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.number import NumberEntity, NumberEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DEFAULTS,
    OPT_PAASLAG_ORE,
    OPT_STROM_FAST_KR,
    OPT_NETT_DAG_ORE,
    OPT_NETT_NATT_ORE,
    OPT_NETT_FAST_KR,
    OPT_ELAVGIFT_ORE,
    OPT_ENOVA_ORE,
    OPT_MVA_PROSENT,
)
from .entity import StromprisBaseEntity

@dataclass(frozen=True, kw_only=True)
class StromprisNumberDescription(NumberEntityDescription):
    option_key: str
    unit: str | None = None

NUMBERS: list[StromprisNumberDescription] = [
    StromprisNumberDescription(
        key="paaslag_ore_kwh",
        name="Påslag",
        option_key=OPT_PAASLAG_ORE,
        native_unit_of_measurement="øre/kWh",
        native_min_value=0,
        native_max_value=100,
        native_step=0.1,
    ),
    StromprisNumberDescription(
        key="strom_fastbelop_kr_mnd",
        name="Strøm fastbeløp",
        option_key=OPT_STROM_FAST_KR,
        native_unit_of_measurement="kr/mnd",
        native_min_value=0,
        native_max_value=2000,
        native_step=1,
    ),
    StromprisNumberDescription(
        key="nett_energiledd_dag_ore_kwh",
        name="Nettleie energiledd dag",
        option_key=OPT_NETT_DAG_ORE,
        native_unit_of_measurement="øre/kWh",
        native_min_value=0,
        native_max_value=300,
        native_step=0.01,
    ),
    StromprisNumberDescription(
        key="nett_energiledd_natt_ore_kwh",
        name="Nettleie energiledd natt",
        option_key=OPT_NETT_NATT_ORE,
        native_unit_of_measurement="øre/kWh",
        native_min_value=0,
        native_max_value=300,
        native_step=0.01,
    ),
    StromprisNumberDescription(
        key="nett_fastledd_kr_mnd",
        name="Nettleie fastledd",
        option_key=OPT_NETT_FAST_KR,
        native_unit_of_measurement="kr/mnd",
        native_min_value=0,
        native_max_value=5000,
        native_step=1,
    ),
    StromprisNumberDescription(
        key="elavgift_ore_kwh",
        name="Elavgift",
        option_key=OPT_ELAVGIFT_ORE,
        native_unit_of_measurement="øre/kWh",
        native_min_value=0,
        native_max_value=50,
        native_step=0.01,
    ),
    StromprisNumberDescription(
        key="enova_ore_kwh",
        name="Enova-avgift",
        option_key=OPT_ENOVA_ORE,
        native_unit_of_measurement="øre/kWh",
        native_min_value=0,
        native_max_value=20,
        native_step=0.01,
    ),
    StromprisNumberDescription(
        key="mva_prosent",
        name="MVA",
        option_key=OPT_MVA_PROSENT,
        native_unit_of_measurement="%",
        native_min_value=0,
        native_max_value=30,
        native_step=0.1,
    ),
]

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    async_add_entities([StromprisNumberEntity(hass, entry, desc) for desc in NUMBERS])

class StromprisNumberEntity(StromprisBaseEntity, NumberEntity):
    entity_description: StromprisNumberDescription
    _attr_mode = "box"

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, description: StromprisNumberDescription) -> None:
        super().__init__(entry)
        self.hass = hass
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_native_value = float(entry.options.get(description.option_key, DEFAULTS[description.option_key]))

    @property
    def native_value(self) -> float | None:
        return float(self.entry.options.get(self.entity_description.option_key, self._attr_native_value or 0))

    async def async_set_native_value(self, value: float) -> None:
        options = dict(self.entry.options)
        options[self.entity_description.option_key] = float(value)
        self.hass.config_entries.async_update_entry(self.entry, options=options)
        self.async_write_ha_state()
