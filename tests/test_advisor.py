from datetime import date, datetime

from app.advisor import Advisor
from app.models import Event, Weather


def make_event():
    return Event(
        title="Practice",
        start=datetime.fromisoformat("2026-06-17T18:00:00"),
        end=datetime.fromisoformat("2026-06-17T19:00:00"),
        location="Boston",
    )


def make_weather(temp=70, precip_prob=0, precip_mm=0, wind_speed=10, code=0):
    return Weather(
        location="Boston",
        date=date.fromisoformat("2026-06-17"),
        temperature_f=temp,
        precipitation_probability=precip_prob,
        precipitation_mm=precip_mm,
        wind_speed_mph=wind_speed,
        wind_direction_degrees=225,
        wind_direction="SW",
        weather_code=code,
        source="forecast",
        confidence="normal",
    )


def test_rain_advice():
    weather = make_weather(temp=70, precip_prob=80, precip_mm=1.2, wind_speed=10, code=61)
    advice = Advisor(use_llm=False).advice_for_event(make_event(), weather)
    assert "umbrella" in advice


def test_cold_advice():
    weather = make_weather(temp=35, precip_prob=0, precip_mm=0, wind_speed=10, code=0)
    advice = Advisor(use_llm=False).advice_for_event(make_event(), weather)
    assert "dress warmly" in advice


def test_manageable_weather_advice():
    weather = make_weather(temp=70, precip_prob=0, precip_mm=0, wind_speed=10, code=0)
    advice = Advisor(use_llm=False).advice_for_event(make_event(), weather)
    assert "manageable" in advice
