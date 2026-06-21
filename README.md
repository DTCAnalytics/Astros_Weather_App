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

# Vib Report

ChatGPT was used to generate the entire app.  There was no point that a 'Builder Hammer' was used.  The app was built with a stage gate mentality... start simple with scoping and continue to build.  Major phases of the project were as follows:
- `Rule based assistant with Weather and Geocoding API via Open Meteo`
- `Inclusion of Multi-horizon forecasting using history data`
- `Inclusion of the Astros schedule and tools to build a JSON based calendar of the entire Astros season`
- `Advanced weather metrics including heat index, humidity, wind speed and direction`
- `Refining actionable advice through LLM`
- `Moved from OpenAI to Gemini API to address accessibility`
- `Inclusion of model behavioral validation vs. only mechanical test of python scripts`
- `Generation of test reports from pytest output`

ChatGPT has a limited 'memory'.  I had extremely limited internet during this development making this difficult to string sessions together.  Redirection becomes constantly necessary to address 'forgetfulness' of the GPT of the overarching goals, but this is not terribly difficult to detect.  Git becomes extremely important to prevent overwriting important previous advances, although that was never an issue during this project.

The most successful steering prompt was the migration to use the Houston Astro calendar of course!  This moved the app from something very trivial to something that actually is pretty useful to me and demonstrates combination of multiple datasources to provide something where the combination is more useful than the parts.  The calendar could easily be automated to provide schedule for any sports team, but because the json file had to be hard coded for this assignment, that enhancement would violate the constraints of the project.
