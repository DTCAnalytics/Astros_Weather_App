# Weather Assistant Test Report

Generated: 2026-06-20

## Test Summary

| Test Suite | Status |
| --- | --- |
| Weather Client | PASS |
| Calendar Store | PASS |
| Advisor | PASS |
| Historical Guidance | PASS |
| Gemini Primary | PASS |
| Example Scenarios | PASS |

Total Tests: 20

Passed: 20

Failed: 0

---

## Advice Architecture

Gemini is the primary advice model. The rule-based advisor is retained as a deterministic backup and validation layer when Gemini is unavailable.

---

## Example Scenario: Rainy Astros Game

### Input

Event:

* Astros vs Rangers
* Houston, TX

Weather:

* Temperature: 75°F
* Humidity: 92%
* Rain Probability: 90%
* Wind: 5 mph from E

### Expected Advice

Bring rain gear and consider public transit, covered transportation, or covered seating. Expect wet conditions and possible delays.

Result: PASS

---

## Example Scenario: Extreme Heat

### Input

Weather:

* Temperature: 92°F
* Humidity: 80%
* Heat Index: 108°F

### Expected Advice

Bring water, seek shade, and take breaks from the heat.

Result: PASS

---

## Example Scenario: Historical Guidance

### Input

Event Date:

* 45 days in future

### Expected Advice

Historical guidance should be presented and clearly identified as not being a forecast.

Result: PASS

---

## Raw Pytest Output

Raw pytest output is saved separately in `docs/TEST_RUN_OUTPUT.md`.
