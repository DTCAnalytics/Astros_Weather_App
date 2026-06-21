from datetime import date, datetime

from app.advisor import Advisor
from app.models import Event, Weather
from app.weather_client import WeatherClient


def test_heat_index_calculation_for_humid_heat():
    heat_index = WeatherClient.heat_index(92, 80)
    assert heat_index is not None
    assert heat_index > 100


def test_rule_based_advice_uses_humidity_and_heat_index():
    event = Event(
        title="Astros Game",
        start=datetime.fromisoformat("2026-06-19T19:10:00"),
        end=datetime.fromisoformat("2026-06-19T22:10:00"),
        location="Houston, TX",
    )
    weather = Weather(
        location="Houston, TX",
        date=date.fromisoformat("2026-06-19"),
        temperature_f=92,
        humidity_percent=80,
        heat_index_f=108,
        precipitation_probability=10,
        precipitation_mm=0,
        wind_speed_mph=8,
        wind_direction_degrees=180,
        wind_direction="S",
        weather_code=1,
        source="forecast",
        confidence="normal",
    )

    advice = Advisor(use_llm=False).advice_for_event(event, weather)
    assert "heat index" in advice
    assert "humidity" in advice
