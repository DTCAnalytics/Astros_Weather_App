from datetime import date, timedelta

from app.models import Weather
from app.weather_client import WeatherClient


def make_weather(source="forecast", confidence="normal"):
    return Weather(
        location="Boston",
        date=date.today(),
        temperature_f=70,
        precipitation_probability=20,
        precipitation_mm=0.0,
        wind_speed_mph=10,
        wind_direction_degrees=315,
        wind_direction="NW",
        weather_code=0,
        source=source,
        confidence=confidence,
    )


def test_weather_object_includes_wind_direction():
    weather = make_weather()
    assert weather.wind_summary == "10 mph from NW"


def test_weather_summary_for_rain_code():
    weather = make_weather()
    rainy = Weather(**{**weather.__dict__, "weather_code": 61})
    assert rainy.summary == "rain possible"


def test_partition_forecast_zero_to_ten_days(monkeypatch):
    client = WeatherClient()
    target = date.today() + timedelta(days=5)

    monkeypatch.setattr(client, "geocode", lambda location: (1.0, 2.0, location))
    monkeypatch.setattr(client, "_forecast", lambda *args, **kwargs: make_weather("forecast", "normal"))

    weather = client.get_weather_for_event("Boston", target)

    assert weather.source == "forecast"
    assert weather.confidence == "normal"
