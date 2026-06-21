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
