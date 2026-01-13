from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.util import dt as dt_util

from .const import (
    DOMAIN,
    CAPACITY_TIERS,
    CONF_SPOT_ENTITY,
    CONF_POWER_ENTITY,
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
        StromprisSensorDescription(
        key="kapasitet_top3_snitt_kw",
        name="Kapasitet topp 3 snitt",
        native_unit_of_measurement="kW",
        icon="mdi:flash",
    ),
    StromprisSensorDescription(
        key="kapasitet_trinn",
        name="Kapasitet trinn",
        icon="mdi:stairs",
    ),
    StromprisSensorDescription(
        key="kapasitet_margin_kw",
        name="Margin til neste trinn",
        native_unit_of_measurement="kW",
        icon="mdi:arrow-expand-up",
    ),
    StromprisSensorDescription(
        key="kapasitet_fastledd_kr_mnd",
        name="Kapasitetsledd",
        native_unit_of_measurement="kr/mnd",
        icon="mdi:cash-multiple",
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    spot_entity: str = entry.data[CONF_SPOT_ENTITY]
    power_entity: str | None = entry.data.get(CONF_POWER_ENTITY)
    async_add_entities(
        [StromprisTotalSensor(hass, entry, d, spot_entity, power_entity) for d in SENSORS]
    )


class StromprisTotalSensor(StromprisBaseEntity, SensorEntity):
    entity_description: StromprisSensorDescription

    def _capacity_tier(self, avg_kw: float, opts: dict) -> tuple[str, float, float]:
        """
        Returns (label, price_kr_mnd, next_threshold_kw).
        next_threshold_kw = upper bound of current tier (for margin calc).
        """
        for upper, label, price_key in CAPACITY_TIERS:
            if avg_kw < upper:
                price = float(opts.get(price_key, 0.0))
                return label, price, float(upper)
        # fallback (shouldn't happen)
        return CAPACITY_TIERS[-1][1], float(opts.get(CAPACITY_TIERS[-1][2], 0.0)), float(CAPACITY_TIERS[-1][0])

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        description: StromprisSensorDescription,
        spot_entity: str,
        power_entity: str | None,
    ) -> None:
        super().__init__(entry)
        self.hass = hass
        self.entity_description = description
        self.spot_entity = spot_entity
        self.power_entity = power_entity
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self.capacity = hass.data[DOMAIN][entry.entry_id]["capacity"]

    async def async_added_to_hass(self) -> None:
        watch = [self.spot_entity]
        if self.power_entity:
            watch.append(self.power_entity)
        self.async_on_remove(
            async_track_state_change_event(self.hass, watch, self._handle_event)
        )

    @callback
    def _handle_event(self, event: Event) -> None:
        # Hvis dette var power update: feed calculator
        if self.power_entity and event.data.get("entity_id") == self.power_entity:
            st = self.hass.states.get(self.power_entity)
            try:
                kw = float(st.state) if st else 0.0
            except (TypeError, ValueError):
                kw = 0.0
            self.capacity.update(dt_util.now(), kw)

        self.async_write_ha_state()

    def _is_day_rate(self, now: datetime) -> bool:
        # Enkel standard: dag=06-22 man-fre. Alt annet natt.
        wd = now.isoweekday()  # 1=Mon..7=Sun
        is_weekday = wd in (1, 2, 3, 4, 5)
        return is_weekday and (6 <= now.hour < 22)

    @property
    def native_value(self) -> float | str | None:
        key = self.entity_description.key
        opts = dict(DEFAULTS)
        opts.update(self.entry.options)

        # Kapasitetslogikk (snitt av topp3 døgnmaks)
        avg_kw = float(self.capacity.top3_avg_kw())
        tier_label, cap_price_kr_mnd, next_upper_kw = self._capacity_tier(avg_kw, opts)
        margin_kw = max(0.0, next_upper_kw - avg_kw)

        if key == "kapasitet_top3_snitt_kw":
            return round(avg_kw, 3)

        if key == "kapasitet_trinn":
            return tier_label

        if key == "kapasitet_margin_kw":
            return round(margin_kw, 3)

        if key == "kapasitet_fastledd_kr_mnd":
            return round(cap_price_kr_mnd, 2)

        if key == "fast_kost_kr_mnd":
            # HER inkluderer vi kapasitetsledd i fast kostnad
            return round(
                float(opts[OPT_STROM_FAST_KR]) + float(opts[OPT_NETT_FAST_KR]) + cap_price_kr_mnd,
                2,
            )

        # total variabel (kr/kWh) – samme som før
        spot_state = self.hass.states.get(self.spot_entity)
        try:
            spot = float(spot_state.state) if spot_state else 0.0
        except (TypeError, ValueError):
            spot = 0.0

        now = dt_util.now()
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
            "power_entity": self.power_entity,
            "paaslag_ore_kwh": opts[OPT_PAASLAG_ORE],
            "nett_dag_ore_kwh": opts[OPT_NETT_DAG_ORE],
            "nett_natt_ore_kwh": opts[OPT_NETT_NATT_ORE],
            "elavgift_ore_kwh": opts[OPT_ELAVGIFT_ORE],
            "enova_ore_kwh": opts[OPT_ENOVA_ORE],
            "mva_prosent": opts[OPT_MVA_PROSENT],
            "kapasitet_top3_snitt_kw": round(avg_kw, 3),
            "kapasitet_trinn": tier_label,
            "kapasitet_margin_kw": round(margin_kw, 3),
            "kapasitet_fastledd_kr_mnd": round(cap_price_kr_mnd, 2),

        }
