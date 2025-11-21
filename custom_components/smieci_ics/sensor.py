from homeassistant.components.sensor import SensorEntity
from homeassistant.util import dt as dt_util
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from ics import Calendar
import os
import logging
import aiofiles

_LOGGER = logging.getLogger(__name__)

class SmieciSensor(SensorEntity):
    def __init__(self, hass, entry_id, nazwa, plik_ics=None, slowo_kluczowe="zmieszane",
                 godzina_przypomnienia="20:00", usluga_powiadomien=None):
        self.hass = hass
        self._entry_id = entry_id
        self._name = nazwa
        self._state = "Nie"
        self._next_event = None
        self.plik_ics = plik_ics
        self.slowo_kluczowe = slowo_kluczowe.lower()
        self.godzina_przypomnienia = godzina_przypomnienia
        self.usluga_powiadomien = usluga_powiadomien
        self._attr_unique_id = f"smieci_ics_{entry_id}"

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return {"następny_wywóz": self._next_event}

    async def async_update(self):
        try:
            if not self.plik_ics:
                self._state = "Brak pliku ICS"
                self._next_event = None
                return

            config_dir = self.hass.config.config_dir
            path = os.path.join(config_dir, "www", self.plik_ics)
            
            if not os.path.isfile(path):
                self._state = "Plik nie istnieje"
                self._next_event = None
                return

            async with aiofiles.open(path, "r", encoding="utf-8") as f:
                ics_text = await f.read()

            calendar = Calendar(ics_text)
            now = dt_util.now()
            next_event = None

            for event in calendar.events:
                event_name_lower = event.name.lower()
                if self.slowo_kluczowe in event_name_lower:
                    event_time = event.begin.datetime
                    
                    if event_time.tzinfo is None:
                        event_time = event_time.replace(tzinfo=now.tzinfo)
                    else:
                        event_time = event_time.astimezone(now.tzinfo)
                    
                    if event_time >= now:
                        if next_event is None or event_time < next_event:
                            next_event = event_time

            if next_event:
                is_today = next_event.date() == now.date()
                self._state = "Tak" if is_today else "Nie"
                self._next_event = next_event.strftime("%Y-%m-%d")
            else:
                self._state = "Nie"
                self._next_event = None

        except Exception as e:
            _LOGGER.error("Błąd podczas aktualizacji sensora %s: %s", self._name, str(e))
            self._state = "Błąd"
            self._next_event = None

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    data = config_entry.data
    sensor = SmieciSensor(
        hass=hass,
        entry_id=config_entry.entry_id,
        nazwa=data.get("nazwa"),
        plik_ics=data.get("plik_ics"),
        slowo_kluczowe=data.get("slowo_kluczowe"),
        godzina_przypomnienia=data.get("godzina_przypomnienia"),
        usluga_powiadomien=data.get("usluga_powiadomien")
    )
    async_add_entities([sensor], update_before_add=True)