import voluptuous as vol
import os
import re
from homeassistant import config_entries
from .const import DOMAIN

class SmieciICSConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            if not re.match(r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$', user_input["godzina_przypomnienia"]):
                errors["godzina_przypomnienia"] = "Nieprawidłowy format godziny (HH:MM)"

            if not errors:
                config_dir = self.hass.config.config_dir
                path = os.path.join(config_dir, "www", user_input["plik_ics"])
                
                if not os.path.isfile(path):
                    errors["plik_ics"] = "Plik nie istnieje w folderze /config/www/"

            if not errors:
                return self.async_create_entry(
                    title=user_input["nazwa"], 
                    data=user_input
                )

        schema = vol.Schema({
            vol.Required("nazwa"): str,
            vol.Required("plik_ics"): str,
            vol.Required("slowo_kluczowe", default="zmieszane"): str,
            vol.Required("godzina_przypomnienia", default="20:00"): str,
            vol.Optional("usluga_powiadomien"): str
        })

        return self.async_show_form(
            step_id="user", 
            data_schema=schema,
            errors=errors
        )
