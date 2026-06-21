from datetime import date, datetime

from app.advisor import Advisor
from app.models import Event, Weather


class FakeGeminiClient:
    """Test double for Gemini so tests never call the real API."""

    def __init__(self, response="Gemini advice: bring water and choose covered transit if storms develop."):
        self.response = response
        self.last_prompt = None

    def generate(self, prompt: str) -> str:
        self.last_prompt = prompt
        return self.response


def make_event() -> Event:
    return Event(
        title="Houston Astros vs. Cleveland Guardians",
        start=datetime.fromisoformat("2026-06-19T19:10:00"),
        end=datetime.fromisoformat("2026-06-19T22:10:00"),
        location="Houston, TX",
    )


def make_weather(source="forecast_plus_history", confidence="cautionary") -> Weather:
    return Weather(
        location="Houston, TX",
        date=date.fromisoformat("2026-06-19"),
        temperature_f=92,
        humidity_percent=80,
        heat_index_f=108,
        precipitation_probability=62,
        precipitation_mm=1.2,
        wind_speed_mph=12,
        wind_direction_degrees=135,
        wind_direction="SE",
        weather_code=61,
        source=source,
        confidence=confidence,
        historical_temperature_avg_f=88,
        historical_rain_probability=40,
        historical_wind_speed_avg_mph=9,
        historical_wind_direction="S",
        historical_humidity_avg_percent=78,
        historical_heat_index_avg_f=99,
    )


def test_gemini_is_primary_advice_model_when_available():
    advisor = Advisor(use_llm=False)
    advisor.llm = FakeGeminiClient("Gemini primary advice for this game.")

    advice = advisor.advice_for_event(make_event(), make_weather())

    assert advice == "Gemini primary advice for this game."
    assert "heat index" not in advice.lower()  # proves rule-based text was not appended


def test_gemini_prompt_contains_weather_context_needed_for_advice():
    fake = FakeGeminiClient()
    advisor = Advisor(use_llm=False)
    advisor.llm = fake

    advisor.advice_for_event(make_event(), make_weather())
    prompt = fake.last_prompt

    assert "Houston Astros vs. Cleveland Guardians" in prompt
    assert "Humidity" in prompt
    assert "Heat index" in prompt
    assert "Wind" in prompt
    assert "Historical average temperature" in prompt
    assert "Historical rain probability" in prompt
    assert "forecast_plus_history" in prompt
    assert "cautionary" in prompt


def test_rule_based_advice_is_backup_when_gemini_unavailable():
    advisor = Advisor(use_llm=False)

    advice = advisor.advice_for_event(make_event(), make_weather()).lower()

    assert "heat index" in advice
    assert "umbrella" in advice or "rain jacket" in advice
