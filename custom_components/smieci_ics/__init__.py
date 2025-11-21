"""Śmieci ICS integracja"""
import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Konfiguracja integracji z wpisu konfiguracyjnego."""
    _LOGGER.info("Ustawianie wpisu konfiguracyjnego dla %s", entry.data.get("nazwa"))

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    # Przekazanie do platformy sensor
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Usuwanie integracji - KLUCZOWA POPRAWKA!"""
    _LOGGER.info("Usuwanie integracji %s", entry.data.get("nazwa"))

    # Poprawne usuwanie platform
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])

    # Czyszczenie danych
    if unload_ok and DOMAIN in hass.data:
        hass.data[DOMAIN].pop(entry.entry_id)
        if not hass.data[DOMAIN]:  # Jeśli nie ma więcej wpisów, usuń cały domain
            hass.data.pop(DOMAIN)

    _LOGGER.info("Integracja %s została usunięta: %s", entry.data.get("nazwa"), unload_ok)
    return unload_ok
