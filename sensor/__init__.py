"""Platform for sensor integration."""
import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from ..sensor import SmieciSensor

_LOGGER = logging.getLogger(__name__)

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

# DODANE: Funkcja do usuwania platformy
async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return True
