from datetime import date

from app.weather_client import WeatherClient


def test_compass_direction():
    assert WeatherClient.degrees_to_compass(0) == "N"
    assert WeatherClient.degrees_to_compass(90) == "E"
    assert WeatherClient.degrees_to_compass(225) == "SW"


def test_nearest_hour_index_exact_match():
    times = [
        "2026-06-18T17:00",
        "2026-06-18T18:00",
        "2026-06-18T19:00",
    ]
    assert WeatherClient._nearest_hour_index(times, date(2026, 6, 18), 18) == 1


def test_forecast_parses_hourly_weather(monkeypatch):
    data = {
        "hourly": {
            "time": ["2026-06-18T18:00"],
            "temperature_2m": [75.0],
            "precipitation_probability": [62],
            "precipitation": [1.2],
            "wind_speed_10m": [8.0],
            "wind_direction_10m": [90],
            "weather_code": [61],
        }
    }

    monkeypatch.setattr(WeatherClient, "_get_json", staticmethod(lambda base_url, params: data))

    weather = WeatherClient()._forecast(
        latitude=29.7604,
        longitude=-95.3698,
        display_name="Houston",
        target_date=date(2026, 6, 18),
        event_hour=18,
        source="forecast",
        confidence="normal",
    )

    assert weather.location == "Houston"
    assert weather.temperature_f == 75.0
    assert weather.precipitation_probability == 62
    assert weather.wind_direction == "E"
    assert weather.summary == "rain possible"
