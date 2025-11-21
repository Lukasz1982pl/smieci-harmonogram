{# Śmieci ICS Integration

Integracja Home Assistant do śledzenia harmonogramu wywozu śmieci z plików ICS.

## Funkcje
- Obsługa wielu typów śmieci (zmieszane, segregowane, plastik, papier, etc.)
- Konfiguracja przez interfejs graficzny (Config Flow)
- Automatyczne wykrywanie następnego wywozu
- Ładne karty z kolorami i animacjami
- Powiadomienia (opcjonalnie)

## Wymagania
- Pliki ICS w folderze `/config/www/`
- Biblioteka `ics` i `aiofiles`

## Instalacja przez HACS
1. Dodaj to repozytorium do HACS
2. Zainstaluj integrację
3. Zrestartuj Home Assistant
4. Dodaj integrację przez konfigurację

## Konfiguracja
1. Przejdź do Settings → Devices & Services
2. Kliknij "Add Integration"
3. Wyszukaj "Śmieci ICS"
4. Podaj wymagane dane:
   - Nazwę sensora
   - Nazwę pliku ICS
   - Słowo kluczowe (np. "zmieszane", "segregowanych")
   - Godzinę przypomnienia
