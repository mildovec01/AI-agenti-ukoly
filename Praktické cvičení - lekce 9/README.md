# My AI Agent (LLM + Tools + SQLite)

Agent odpovídá přes LLM a umí volat nástroje (tool calling). Součástí je SQLite databáze pro ukládání a vyhledávání poznámek.

## Funkce
- Chat přes LLM
- Tools:
  - `get_weather(city)` – aktuální počasí přes Open-Meteo
  - `save_note(title, content)` – uloží poznámku do SQLite
  - `search_notes(query, limit)` – vyhledá poznámky v SQLite

## Instalace a spuštění
1. `pip install -r requirements.txt`
2. vytvoř `.env` podle `.env.example` (OPENAI_API_KEY)
3. `python src/main.py`

## Příklady dotazů
- Jaké je počasí v Praze?
- Ulož poznámku: title="maturita" content="angličtina a český jazyk"
- Najdi poznámky o maturitě a shrň je.
