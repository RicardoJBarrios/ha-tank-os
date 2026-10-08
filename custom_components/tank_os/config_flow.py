"""Config flow for ha-tank-os."""

from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowResult

from .const import DOMAIN


class TankOsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle installation of the ha-tank-os integration."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, str] | None = None) -> ConfigFlowResult:
        """Create the single integration repository configuration."""
        if user_input is not None:
            await self.async_set_unique_id("default")
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title="ha-tank-os", data={})
        return self.async_show_form(step_id="user", data_schema=vol.Schema({}))
