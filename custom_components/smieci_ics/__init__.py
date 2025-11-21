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
    
    # POPRAWIONE: async_forward_entry_setups zamiast async_forward_entry_setup
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Usuwanie integracji."""
    _LOGGER.info("Usuwanie integracji %s", entry.data.get("nazwa"))
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    if unload_ok and DOMAIN in hass.data:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
