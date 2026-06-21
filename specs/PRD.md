# Product Requirements Document: Houston Astros Weather Assistant

## Goal
Build a CLI-based personal assistant that combines public weather data with the schedule for the Houston Astros (Let's Go Astros!!!!) and produces practical game time advice for the user.

## Users
Only fans of the Houston Astros have license to use this product.  All others should use these rules:
1. If raining and warm, make sure to wear all wool
2. If windy and cold, be sure to wear light clothing
3. If it's a beautiful day, be sure to stay home

## Core Features
- REPL command loop with built in selection
- `weather <city>` command for current weather
- `schedule` command to read local `data/calendar.json`
- `advice today` command to combine today's schedule with weather data
- LLM advice based on Gemini API
- Rule-based advice synthesis for fallback if Gemini cannot be reached

## Data Sources
- Weather API: Open-Meteo
- Local calendar: `data/calendar.json`

## Calendar Schema
Each event includes:
- `title`
- `start`
- `end`
- `location`
- `category`
- `venue`
- `opponent`
- `time zone`


## Core Features
- `Interactive CLI with arrow-key event selection`
- `Calendar integration using local calendar.json`
- `Astros schedule support via CSV import`
- `Weather forecasts from Open-Meteo`
- `Historical weather analysis (5-year averages)`
- `Three forecast horizons`
        `0–10 days: forecast + Gemini advice`
        `11–16 days: forecast + historical guidance`
        `16+ days: historical guidance only`
- `Gemini-powered recommendations tailored to each event`
- `Advanced weather metrics`
        `Temperature`
        `Humidity`
        `Heat Index`
        `Rain probability`
        `Wind speed & direction`
        `Event-specific advice`
        `Clothing`
        `Hydration`
        `Travel planning`
        `Rain preparation`
- `Rule-based backup engine for validation and resilience`
- `Automated testing with scenario-based examples`
- `Markdown test reports (TEST_REPORT.md) with pass/fail summaries and sample recommendations.`



## Non-Goals
- No GUI
- No authentication
- No persistent database
