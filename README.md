# Houston Astro Weather Assistant

A command-line weather assistant that combines a local schedule, Open-Meteo weather data, historical weather guidance, and Gemini-generated advice.

## What it does

* Loads events from `data/calendar.json`
* Lets the user select upcoming events from an arrow-key menu
* Gets weather for the event location and time
* Adds humidity, heat index, precipitation, wind speed, and wind direction
* Uses Gemini as the primary advice model
* Uses rule-based advice as a backup if Gemini is unavailable

## Weather partitions

| Event date | Weather source | Advice behavior |
|---|---|---|
| 0-10 days out | Specific forecast | Gemini advice based on forecast facts |
| 11-16 days out | Specific forecast + 5-year history | Gemini advice with a cautionary forecast note |
| More than 16 days out | 5-year historical average | Gemini advice clearly labeled as historical guidance |

## Setup

```bash
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-2.5-flash
```

## Run the app

```bash
python -m app.main
```

At startup, the app shows upcoming schedule items from today's date forward. Use the arrow keys to select an event.

## Run tests

```bash
python -m pytest -v
```

The tests validate weather parsing, humidity, heat index, forecast partitions, calendar loading, arrow-key selection filtering, Gemini prompt construction, and realistic advice scenarios.

## Project structure

```text
app/                 application code
data/                calendar and schedule data
docs/rules.md        assistant persona and constraints
specs/PRD.md         product requirements document
tests/               automated tests and behavior examples
```

## Test Report

Run the full automated test suite:

```bash
python -m pytest
```

Generate a Markdown test report with summary tables and example scenarios:

```bash
python scripts/generate_test_report.py
```

This writes:

```text
docs/TEST_REPORT.md
docs/TEST_RUN_OUTPUT.md
```
