from homeassistant.components.sensor import SensorEntity
from homeassistant.util import dt as dt_util
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from ics import Calendar
import os
import logging
import aiofiles
from datetime import datetime

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
            _LOGGER.info("🎯 === ROZPOCZĘCIE AKTUALIZACJI SENSORA %s ===", self._name)
            _LOGGER.info("🔍 Słowo kluczowe: '%s'", self.slowo_kluczowe)
            
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

            calendars = list(Calendar.parse_multiple(ics_text))
            now = dt_util.now()
            
            _LOGGER.info("📅 AKTUALNA DATA SYSTEMU: %s", now)
            _LOGGER.info("📅 AKTUALNA DATA (tylko data): %s", now.date())
            _LOGGER.info("🌍 STREFA CZASOWA: %s", now.tzinfo)
            
            next_event = None
            found_today = False
            event_count = 0

            for calendar in calendars:
                for event in calendar.events:
                    event_count += 1
                    event_name_lower = event.name.lower()
                    _LOGGER.info("📋 Wydarzenie %d: '%s'", event_count, event.name)
                    
                    # SPRAWDZENIE CZY WYDARZENIE PASUJE
                    matches_keyword = self.slowo_kluczowe in event_name_lower
                    
                    # Dla sortowane - sprawdź też "segregowanych" jeśli szukasz "sortowane"
                    if self._name.lower() == "sortowane" and not matches_keyword:
                        matches_keyword = "segregowanych" in event_name_lower
                    
                    if matches_keyword:
                        _LOGGER.info("✅ ZNALEZIONO PASUJĄCE WYDARZENIE: %s", event.name)
                        
                        event_time = event.begin.datetime
                        _LOGGER.info("   📅 Data wydarzenia (surowe): %s", event_time)
                        _LOGGER.info("   📅 Data wydarzenia (tylko data): %s", event_time.date())
                        
                        # Sprawdź czy to wydarzenie całodniowe
                        is_all_day = hasattr(event.begin, 'value') and event.begin.value == 'DATE'
                        _LOGGER.info("   🕒 Czy całodniowe: %s", is_all_day)
                        
                        # Konwersja strefy czasowej
                        if event_time.tzinfo is None:
                            event_time = event_time.replace(tzinfo=now.tzinfo)
                            _LOGGER.info("   🌍 Dodano strefę czasową: %s", event_time.tzinfo)
                        else:
                            event_time = event_time.astimezone(now.tzinfo)
                            _LOGGER.info("   🌍 Skonwertowano strefę czasową: %s", event_time.tzinfo)
                        
                        _LOGGER.info("   📅 Data po konwersji: %s", event_time)
                        _LOGGER.info("   📅 Data po konwersji (tylko data): %s", event_time.date())
                        
                        # Sprawdź czy to dzisiaj
                        is_today = event_time.date() == now.date()
                        _LOGGER.info("   ❓ Czy dzisiaj? %s (wydarzenie: %s, dzisiaj: %s)", 
                                   is_today, event_time.date(), now.date())
                        
                        if is_today:
                            found_today = True
                            _LOGGER.info("   🎉 🎉 🎉 DZISIAJ JEST WYWÓZ! 🎉 🎉 🎉")
                        
                        # Znajdź następne wydarzenie (nawet jeśli dzisiaj jest wywóz)
                        if event_time >= now:
                            if next_event is None or event_time < next_event:
                                next_event = event_time
                                _LOGGER.info("   ⏭️ Nowe najbliższe wydarzenie: %s", next_event.date())

            _LOGGER.info("📊 Podsumowanie:")
            _LOGGER.info("   📈 Przetworzonych wydarzeń: %d", event_count)
            _LOGGER.info("   🗓️ Znaleziono dzisiaj: %s", found_today)
            _LOGGER.info("   ⏭️ Następne wydarzenie: %s", next_event.date() if next_event else "BRAK")

            # Ustaw stan
            self._state = "Tak" if found_today else "Nie"
            _LOGGER.info("🎯 USTAWIONO STAN: %s", self._state)

            # Ustaw następną datę
            if next_event:
                self._next_event = next_event.strftime("%Y-%m-%d")
                _LOGGER.info("📅 NASTĘPNY WYWÓZ: %s", self._next_event)
                
                # Jeśli dzisiaj jest wywóz, znajdź następny po dzisiejszym
                if found_today:
                    # Tutaj potrzebowalibyśmy wszystkich przyszłych wydarzeń, ale na razie zostawiamy jak jest
                    _LOGGER.info("ℹ️ Dzisiaj jest wywóz, następny wywóz: %s", self._next_event)
            else:
                self._next_event = None
                _LOGGER.info("❌ BRAK NASTĘPNEGO WYDARZENIA")

            _LOGGER.info("🎯 === ZAKOŃCZENIE AKTUALIZACJI SENSORA %s ===", self._name)

        except Exception as e:
            _LOGGER.error("💥 BŁĄD podczas aktualizacji sensora %s: %s", self._name, str(e), exc_info=True)
            self._state = "Błąd"
            self._next_event = None

# FUNKCJA SETUP - MUSI BYĆ NA NAJWYŻSZYM POZIOMIE (bez wcięć)
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
