from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_NAME,
    CONF_SPOT_ENTITY,
    DEFAULTS,
    OPT_PAASLAG_ORE,
    OPT_NETT_DAG_ORE,
    OPT_NETT_NATT_ORE,
    OPT_ELAVGIFT_ORE,
    OPT_ENOVA_ORE,
    OPT_MVA_PROSENT,
    OPT_STROM_FAST_KR,
    OPT_NETT_FAST_KR,
)
from .entity import StromprisBaseEntity

@dataclass(frozen=True, kw_only=True)
class StromprisSensorDescription(SensorEntityDescription):
    pass

SENSORS: list[StromprisSensorDescription] = [
    StromprisSensorDescription(
        key="total_variabel_kr_kwh",
        name="Total variabel",
        native_unit_of_measurement="kr/kWh",
        icon="mdi:currency-usd",
    ),
    StromprisSensorDescription(
        key="fast_kost_kr_mnd",
        name="Fast kostnad",
        native_unit_of_measurement="kr/mnd",
        icon="mdi:cash",
    ),
]

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    spot_entity = entry.data[CONF_SPOT_ENTITY]
    async_add_entities([StromprisTotalSensor(hass, entry, d, spot_entity) for d in SENSORS])

class StromprisTotalSensor(StromprisBaseEntity, SensorEntity):
    entity_description: StromprisSensorDescription

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, description: StromprisSensorDescription, spot_entity: str) -> None:
        super().__init__(entry)
        self.hass = hass
        self.entity_description = description
        self.spot_entity = spot_entity
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(async_track_state_change_event(self.hass, [self.spot_entity], self._handle_event))

    @callback
    def _handle_event(self, event: Event) -> None:
        self.async_write_ha_state()

    def _is_day_rate(self, now: datetime) -> bool:
        # Enkel standard: dag=06-22 man-fre. Alt annet natt.
        wd = now.isoweekday()  # 1=Mon..7=Sun
        is_weekday = wd in (1, 2, 3, 4, 5)
        return is_weekday and (6 <= now.hour < 22)

    @property
    def native_value(self) -> float | None:
        key = self.entity_description.key
        opts = dict(DEFAULTS)
        opts.update(self.entry.options)

        if key == "fast_kost_kr_mnd":
            return round(float(opts[OPT_STROM_FAST_KR]) + float(opts[OPT_NETT_FAST_KR]), 2)

        # total variabel (kr/kWh)
        spot_state = self.hass.states.get(self.spot_entity)
        try:
            spot = float(spot_state.state) if spot_state else 0.0
        except (TypeError, ValueError):
            spot = 0.0

        now = datetime.now()
        nett_energiledd_ore = float(opts[OPT_NETT_DAG_ORE]) if self._is_day_rate(now) else float(opts[OPT_NETT_NATT_ORE])

        paaslag_kr = float(opts[OPT_PAASLAG_ORE]) / 100.0
        nett_kr = float(nett_energiledd_ore) / 100.0
        elavgift_kr = float(opts[OPT_ELAVGIFT_ORE]) / 100.0
        enova_kr = float(opts[OPT_ENOVA_ORE]) / 100.0
        mva = float(opts[OPT_MVA_PROSENT]) / 100.0

        eks_mva = spot + paaslag_kr + nett_kr + elavgift_kr + enova_kr
        return round(eks_mva * (1.0 + mva), 4)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        if self.entity_description.key != "total_variabel_kr_kwh":
            return {}
        opts = dict(DEFAULTS)
        opts.update(self.entry.options)
        return {
            "spot_entity": self.spot_entity,
            "paaslag_ore_kwh": opts[OPT_PAASLAG_ORE],
            "nett_dag_ore_kwh": opts[OPT_NETT_DAG_ORE],
            "nett_natt_ore_kwh": opts[OPT_NETT_NATT_ORE],
            "elavgift_ore_kwh": opts[OPT_ELAVGIFT_ORE],
            "enova_ore_kwh": opts[OPT_ENOVA_ORE],
            "mva_prosent": opts[OPT_MVA_PROSENT],
        }
