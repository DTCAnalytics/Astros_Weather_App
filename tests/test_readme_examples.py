"""Human-readable output examples for project demos and screenshots."""

from datetime import date, datetime

from app.advisor import Advisor
from app.models import Event, Weather


def test_print_rainy_game_example(capsys):
    event = Event(
        title="Houston Astros vs. Cleveland Guardians",
        start=datetime.fromisoformat("2026-06-19T19:10:00"),
        end=datetime.fromisoformat("2026-06-19T22:10:00"),
        location="Houston, TX",
    )
    weather = Weather(
        location="Houston, TX",
        date=date.fromisoformat("2026-06-19"),
        temperature_f=75,
        precipitation_probability=85,
        precipitation_mm=2.5,
        wind_speed_mph=5,
        wind_direction_degrees=90,
        wind_direction="E",
        weather_code=61,
        source="forecast",
        confidence="normal",
    )

    output = Advisor(use_llm=False).weather_then_advice(event, weather)
    print(output)

    captured = capsys.readouterr().out.lower()
    assert "weather:" in captured
    assert "advice:" in captured
    assert "umbrella" in captured or "rain jacket" in captured
    assert "public transit" in captured or "covered transportation" in captured or "bus" in captured
