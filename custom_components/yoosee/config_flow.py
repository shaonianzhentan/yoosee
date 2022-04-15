from __future__ import annotations

from typing import Any
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, OptionsFlow, ConfigEntry
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, DEFAULT_NAME
from urllib.parse import urlparse

DATA_SCHEMA = vol.Schema({
    vol.Required("name", default=DEFAULT_NAME): str,
    vol.Required("url"): str
})

class SimpleConfigFlow(ConfigFlow, domain=DOMAIN):

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
    
        if user_input is None:
            errors = {}
            return self.async_show_form(step_id="user", data_schema=DATA_SCHEMA, errors=errors)

        parsed = urlparse(user_input['url'])
        return self.async_create_entry(title=parsed.hostname, data=user_input)