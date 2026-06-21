"""Behavior-style examples for the weather assistant advice engine.

These tests do more than check one helper function. They show that the
assistant produces realistic recommendations for common user scenarios.
"""

from datetime import date, datetime

from app.advisor import Advisor
from app.models import Event, Weather


def make_astros_event() -> Event:
    return Event(
        title="Houston Astros vs. Cleveland Guardians",
        start=datetime.fromisoformat("2026-06-19T19:10:00"),
        end=datetime.fromisoformat("2026-06-19T22:10:00"),
        location="Houston, TX",
    )


def make_weather(
    *,
    temp: float = 75,
    precip_prob: int = 0,
    precip_mm: float = 0.0,
    wind_speed: float = 5,
    wind_direction: str = "E",
    weather_code: int = 0,
    source: str = "forecast",
    confidence: str = "normal",
) -> Weather:
    return Weather(
        location="Houston, TX",
        date=date.fromisoformat("2026-06-19"),
        temperature_f=temp,
        precipitation_probability=precip_prob,
        precipitation_mm=precip_mm,
        wind_speed_mph=wind_speed,
        wind_direction_degrees=90,
        wind_direction=wind_direction,
        weather_code=weather_code,
        source=source,
        confidence=confidence,
    )


def test_example_rainy_astros_game_recommends_rain_plan_and_transportation():
    """Example: a rainy baseball game should produce useful action advice."""
    event = make_astros_event()
    weather = make_weather(precip_prob=85, precip_mm=2.5, weather_code=61)

    advice = Advisor(use_llm=False).advice_for_event(event, weather).lower()

    assert "umbrella" in advice or "rain jacket" in advice
    assert "public transit" in advice or "covered transportation" in advice or "bus" in advice


def test_example_hot_astros_game_recommends_water_or_heat_planning():
    """Example: a hot Houston game should produce hydration/heat advice."""
    event = make_astros_event()
    weather = make_weather(temp=93, precip_prob=10, precip_mm=0, weather_code=1)

    advice = Advisor(use_llm=False).advice_for_event(event, weather).lower()

    assert "water" in advice or "heat" in advice or "hydrate" in advice


def test_example_windy_game_mentions_wind_direction_or_travel_time():
    """Example: a windy event should call out wind and travel impact."""
    event = make_astros_event()
    weather = make_weather(wind_speed=24, wind_direction="SE", weather_code=2)

    advice = Advisor(use_llm=False).advice_for_event(event, weather).lower()

    assert "wind" in advice
    assert "se" in advice or "travel time" in advice
