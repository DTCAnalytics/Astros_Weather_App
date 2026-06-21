from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional


@dataclass(frozen=True)
class Event:
    title: str
    start: datetime
    end: datetime
    location: str


@dataclass(frozen=True)
class Weather:
    location: str
    date: date
    temperature_f: float
    precipitation_probability: int
    precipitation_mm: float
    wind_speed_mph: float
    wind_direction_degrees: Optional[float]
    wind_direction: Optional[str]
    weather_code: int
    source: str
    confidence: str
    humidity_percent: Optional[float] = None
    heat_index_f: Optional[float] = None
    historical_temperature_avg_f: Optional[float] = None
    historical_rain_probability: Optional[int] = None
    historical_wind_speed_avg_mph: Optional[float] = None
    historical_wind_direction: Optional[str] = None
    historical_humidity_avg_percent: Optional[float] = None
    historical_heat_index_avg_f: Optional[float] = None

    @property
    def summary(self) -> str:
        if self.weather_code in {0, 1}:
            return "clear"
        if self.weather_code in {2, 3}:
            return "cloudy"
        if 51 <= self.weather_code <= 67 or 80 <= self.weather_code <= 82:
            return "rain possible"
        if 71 <= self.weather_code <= 77 or 85 <= self.weather_code <= 86:
            return "snow possible"
        if 95 <= self.weather_code <= 99:
            return "thunderstorms possible"
        return "mixed conditions"

    @property
    def wind_summary(self) -> str:
        if self.wind_direction:
            return f"{self.wind_speed_mph:.0f} mph from {self.wind_direction}"
        return f"{self.wind_speed_mph:.0f} mph"

    @property
    def humidity_summary(self) -> str:
        if self.humidity_percent is None:
            return "unknown"
        return f"{self.humidity_percent:.0f}%"

    @property
    def heat_index_summary(self) -> str:
        if self.heat_index_f is None:
            return "not available"
        return f"{self.heat_index_f:.0f} F"

    def as_prompt_facts(self) -> str:
        return (
            f"Location: {self.location}\n"
            f"Date: {self.date}\n"
            f"Temperature: {self.temperature_f:.0f} F\n"
            f"Humidity: {self.humidity_summary}\n"
            f"Heat index: {self.heat_index_summary}\n"
            f"Condition: {self.summary}\n"
            f"Precipitation probability: {self.precipitation_probability}%\n"
            f"Wind speed: {self.wind_speed_mph:.0f} mph\n"
            f"Wind direction: {self.wind_direction or 'unknown'}"
        )
