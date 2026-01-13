from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_ENTITY_ID
from homeassistant.helpers import selector

from .const import (
    DOMAIN,
    CONF_NAME,
    CONF_SPOT_ENTITY,
    CONF_PRICE_AREA,
    CONF_DSO,
    CONF_CONTRACT,
    DEFAULTS,
    OPT_PRICE_AREA,
    OPT_DSO,
    OPT_CONTRACT,
    PRICE_AREAS,
    CONTRACTS,
)
from .tariffs import load_dso_catalog

def _dso_options() -> list[tuple[str, str]]:
    catalog = load_dso_catalog()
    # returns list of (value,label)
    return [(k, v.get("label", k)) for k, v in catalog.items()]

class StromprisTotalConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            await self.async_set_unique_id(f"{DOMAIN}_{user_input[CONF_NAME]}")
            self._abort_if_unique_id_configured()

            data = {
                CONF_NAME: user_input[CONF_NAME],
                CONF_SPOT_ENTITY: user_input[CONF_SPOT_ENTITY],
                CONF_PRICE_AREA: user_input[CONF_PRICE_AREA],
                CONF_DSO: user_input[CONF_DSO],
                CONF_CONTRACT: user_input[CONF_CONTRACT],
                CONF_POWER_ENTITY: user_input[CONF_POWER_ENTITY],
            }

            # Seed options with defaults + DSO defaults + chosen values
            options: dict[str, Any] = dict(DEFAULTS)
            options[OPT_PRICE_AREA] = user_input[CONF_PRICE_AREA]
            options[OPT_DSO] = user_input[CONF_DSO]
            options[OPT_CONTRACT] = user_input[CONF_CONTRACT]

            catalog = load_dso_catalog()
            dso = user_input[CONF_DSO]
            dso_defaults = catalog.get(dso, {}).get("defaults", {})
            options.update(dso_defaults)

            return self.async_create_entry(title=user_input[CONF_NAME], data=data, options=options)

        schema = vol.Schema({
            vol.Required(CONF_NAME, default="Hjem"): str,
            vol.Required(CONF_SPOT_ENTITY): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="sensor")
            ),
            vol.Required(CONF_PRICE_AREA, default=DEFAULTS[OPT_PRICE_AREA]): vol.In(PRICE_AREAS),
            vol.Required(CONF_DSO, default=DEFAULTS[OPT_DSO]): vol.In([k for k, _ in _dso_options()]),
            vol.Required(CONF_CONTRACT, default=DEFAULTS[OPT_CONTRACT]): vol.In(CONTRACTS),
            vol.Required(CONF_POWER_ENTITY): selector.EntitySelector(selector.EntitySelectorConfig(domain="sensor")),
        })
        return self.async_show_form(step_id="user", data_schema=schema)

    @staticmethod
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        return StromprisTotalOptionsFlowHandler(config_entry)

class StromprisTotalOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, entry: config_entries.ConfigEntry) -> None:
        self.entry = entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            # Apply option changes
            options = dict(self.entry.options)
            options.update(user_input)

            # If DSO changed, merge in DSO defaults (but do not overwrite fields user already set in this submission)
            catalog = load_dso_catalog()
            dso = options.get(OPT_DSO, DEFAULTS[OPT_DSO])
            dso_defaults = catalog.get(dso, {}).get("defaults", {})
            for k, v in dso_defaults.items():
                options.setdefault(k, v)

            return self.async_create_entry(title="", data=options)

        current = dict(DEFAULTS)
        current.update(self.entry.options)

        schema = vol.Schema({
            vol.Required(OPT_PRICE_AREA, default=current.get(OPT_PRICE_AREA)): vol.In(PRICE_AREAS),
            vol.Required(OPT_DSO, default=current.get(OPT_DSO)): vol.In([k for k, _ in _dso_options()]),
            vol.Required(OPT_CONTRACT, default=current.get(OPT_CONTRACT)): vol.In(CONTRACTS),
        })
        return self.async_show_form(step_id="init", data_schema=schema)
