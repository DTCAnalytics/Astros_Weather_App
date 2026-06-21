from __future__ import annotations

import json
import math
import socket
from datetime import date, datetime
from statistics import mean
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

from app.models import Weather


REGION_NAME_MAP = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California",
    "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware", "FL": "Florida", "GA": "Georgia",
    "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa",
    "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
    "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi", "MO": "Missouri",
    "MT": "Montana", "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey",
    "NM": "New Mexico", "NY": "New York", "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio",
    "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
    "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah", "VT": "Vermont",
    "VA": "Virginia", "WA": "Washington", "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming",
    "ON": "Ontario", "QC": "Quebec", "BC": "British Columbia",
}

KNOWN_LOCATIONS = {
    "Houston": (29.7604, -95.3698, "Houston, TX"),
    "Houston, TX": (29.7604, -95.3698, "Houston, TX"),
    "Houston, Texas": (29.7604, -95.3698, "Houston, TX"),
    "Arlington, TX": (32.7357, -97.1081, "Arlington, TX"),
    "Seattle, WA": (47.6062, -122.3321, "Seattle, WA"),
    "Toronto, ON": (43.6532, -79.3832, "Toronto, ON"),
    "New York, NY": (40.7128, -74.0060, "New York, NY"),
    "Boston, MA": (42.3601, -71.0589, "Boston, MA"),
}

HOURLY_FORECAST_FIELDS = (
    "temperature_2m,relative_humidity_2m,precipitation_probability,"
    "precipitation,wind_speed_10m,wind_direction_10m,weather_code"
)

HOURLY_HISTORICAL_FIELDS = (
    "temperature_2m,relative_humidity_2m,precipitation,"
    "wind_speed_10m,wind_direction_10m,weather_code"
)


class WeatherClient:
    GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
    FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
    ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"

    def geocode(self, location: str) -> tuple[float, float, str]:
        original = location.strip()
        if original in KNOWN_LOCATIONS:
            lat, lon, display = KNOWN_LOCATIONS[original]
            return lat, lon, display

        city, region = self._split_city_region(original)
        params = urlencode({"name": city, "count": 10, "language": "en", "format": "json"})
        data = self._get_json(self.GEOCODE_URL, params)

        results = data.get("results", [])
        if not results:
            raise ValueError(f"Could not find location: {location}")

        selected = self._select_best_geocode_result(results, region) if region else results[0]
        display = selected.get("name", city)
        admin1 = selected.get("admin1")
        country_code = selected.get("country_code")
        if admin1 and country_code in {"US", "CA"}:
            display = f"{display}, {self._region_abbrev(admin1) or admin1}"
        return selected["latitude"], selected["longitude"], display

    def get_weather_for_event(self, location: str, target_date: date, event_hour: int = 12) -> Weather:
        days_out = (target_date - date.today()).days
        latitude, longitude, display_name = self.geocode(location)

        if days_out <= 10:
            return self._forecast(latitude, longitude, display_name, target_date, event_hour, "forecast", "normal")

        historical = self._historical_average(latitude, longitude, display_name, target_date, event_hour)

        if days_out <= 16:
            forecast = self._forecast(latitude, longitude, display_name, target_date, event_hour, "forecast_plus_history", "cautionary")
            data = forecast.__dict__.copy()
            data.update(
                historical_temperature_avg_f=historical.historical_temperature_avg_f,
                historical_rain_probability=historical.historical_rain_probability,
                historical_wind_speed_avg_mph=historical.historical_wind_speed_avg_mph,
                historical_wind_direction=historical.historical_wind_direction,
                historical_humidity_avg_percent=historical.historical_humidity_avg_percent,
                historical_heat_index_avg_f=historical.historical_heat_index_avg_f,
            )
            return Weather(**data)

        return historical

    def current_weather(self, location: str) -> Weather:
        return self.get_weather_for_event(location, date.today(), datetime.now().hour)

    def get_daily_weather(self, location: str, target_date: date) -> Weather:
        return self.get_weather_for_event(location, target_date, 12)

    def _forecast(self, latitude: float, longitude: float, display_name: str, target_date: date, event_hour: int, source: str, confidence: str) -> Weather:
        params = urlencode(
            {
                "latitude": latitude,
                "longitude": longitude,
                "hourly": HOURLY_FORECAST_FIELDS,
                "temperature_unit": "fahrenheit",
                "wind_speed_unit": "mph",
                "timezone": "auto",
                "start_date": target_date.isoformat(),
                "end_date": target_date.isoformat(),
            }
        )
        data = self._get_json(self.FORECAST_URL, params)
        hourly = data["hourly"]
        index = self._nearest_hour_index(hourly["time"], target_date, event_hour)
        temperature = float(hourly["temperature_2m"][index])
        humidity = self._optional_float(hourly.get("relative_humidity_2m", [None])[index])
        direction_degrees = hourly["wind_direction_10m"][index]

        return Weather(
            location=display_name,
            date=target_date,
            temperature_f=temperature,
            humidity_percent=humidity,
            heat_index_f=self.heat_index(temperature, humidity),
            precipitation_probability=int(hourly.get("precipitation_probability", [0])[index] or 0),
            precipitation_mm=float(hourly.get("precipitation", [0])[index] or 0),
            wind_speed_mph=float(hourly["wind_speed_10m"][index]),
            wind_direction_degrees=float(direction_degrees) if direction_degrees is not None else None,
            wind_direction=self.degrees_to_compass(direction_degrees),
            weather_code=int(hourly["weather_code"][index]),
            source=source,
            confidence=confidence,
        )

    def _historical_average(self, latitude: float, longitude: float, display_name: str, target_date: date, event_hour: int) -> Weather:
        years = [target_date.year - i for i in range(1, 6)]
        samples = []
        for year in years:
            try:
                hist_date = target_date.replace(year=year)
            except ValueError:
                hist_date = target_date.replace(year=year, day=28)

            params = urlencode(
                {
                    "latitude": latitude,
                    "longitude": longitude,
                    "start_date": hist_date.isoformat(),
                    "end_date": hist_date.isoformat(),
                    "hourly": HOURLY_HISTORICAL_FIELDS,
                    "temperature_unit": "fahrenheit",
                    "wind_speed_unit": "mph",
                    "timezone": "auto",
                }
            )
            data = self._get_json(self.ARCHIVE_URL, params)
            hourly = data["hourly"]
            index = self._nearest_hour_index(hourly["time"], hist_date, event_hour)
            temperature = float(hourly["temperature_2m"][index])
            humidity = self._optional_float(hourly.get("relative_humidity_2m", [None])[index])
            samples.append(
                {
                    "temperature_f": temperature,
                    "humidity_percent": humidity,
                    "heat_index_f": self.heat_index(temperature, humidity),
                    "precipitation_mm": float(hourly["precipitation"][index] or 0),
                    "wind_speed_mph": float(hourly["wind_speed_10m"][index]),
                    "wind_direction_degrees": hourly["wind_direction_10m"][index],
                    "weather_code": int(hourly["weather_code"][index]),
                }
            )

        avg_temp = mean(s["temperature_f"] for s in samples)
        avg_precip = mean(s["precipitation_mm"] for s in samples)
        avg_wind = mean(s["wind_speed_mph"] for s in samples)
        humidity_values = [s["humidity_percent"] for s in samples if s["humidity_percent"] is not None]
        heat_index_values = [s["heat_index_f"] for s in samples if s["heat_index_f"] is not None]
        avg_humidity = mean(humidity_values) if humidity_values else None
        avg_heat_index = mean(heat_index_values) if heat_index_values else None
        rain_probability = round(100 * sum(1 for s in samples if s["precipitation_mm"] > 0) / len(samples))
        avg_direction_degrees = self._mean_direction([s["wind_direction_degrees"] for s in samples])
        most_recent = samples[0]

        return Weather(
            location=display_name,
            date=target_date,
            temperature_f=avg_temp,
            humidity_percent=avg_humidity,
            heat_index_f=avg_heat_index,
            precipitation_probability=rain_probability,
            precipitation_mm=avg_precip,
            wind_speed_mph=avg_wind,
            wind_direction_degrees=avg_direction_degrees,
            wind_direction=self.degrees_to_compass(avg_direction_degrees),
            weather_code=most_recent["weather_code"],
            source="historical_average",
            confidence="historical",
            historical_temperature_avg_f=avg_temp,
            historical_rain_probability=rain_probability,
            historical_wind_speed_avg_mph=avg_wind,
            historical_wind_direction=self.degrees_to_compass(avg_direction_degrees),
            historical_humidity_avg_percent=avg_humidity,
            historical_heat_index_avg_f=avg_heat_index,
        )

    @staticmethod
    def _get_json(base_url: str, params: str) -> dict:
        url = f"{base_url}?{params}"
        try:
            with urlopen(url, timeout=20) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Open-Meteo request failed ({exc.code}): {body}") from exc
        except (URLError, socket.gaierror, TimeoutError) as exc:
            raise RuntimeError(f"Weather/geocoding service unavailable: {exc}") from exc

    @staticmethod
    def _split_city_region(location: str) -> tuple[str, str | None]:
        if "," in location:
            city, region = [part.strip() for part in location.split(",", 1)]
            return city, region or None
        parts = location.rsplit(" ", 1)
        if len(parts) == 2 and parts[1].upper() in REGION_NAME_MAP:
            return parts[0], parts[1].upper()
        return location, None

    @staticmethod
    def _select_best_geocode_result(results: list[dict], region: str) -> dict:
        wanted = REGION_NAME_MAP.get(region.upper(), region)
        for result in results:
            admin1 = result.get("admin1", "")
            admin1_code = result.get("admin1_code", "")
            if admin1.lower() == wanted.lower() or admin1_code.upper() == region.upper():
                return result
        return results[0]

    @staticmethod
    def _region_abbrev(region_name: str) -> str | None:
        for abbrev, full in REGION_NAME_MAP.items():
            if full.lower() == region_name.lower():
                return abbrev
        return None

    @staticmethod
    def _nearest_hour_index(times: list[str], target_date: date, event_hour: int) -> int:
        target_prefix = target_date.isoformat()
        preferred = f"{target_prefix}T{event_hour:02d}:00"
        if preferred in times:
            return times.index(preferred)
        candidates = [(i, t) for i, t in enumerate(times) if t.startswith(target_prefix)]
        if not candidates:
            return 0
        return min(candidates, key=lambda item: abs(int(item[1][11:13]) - event_hour))[0]

    @staticmethod
    def degrees_to_compass(degrees: float | None) -> str | None:
        if degrees is None:
            return None
        directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
        return directions[round(float(degrees) / 45) % 8]

    _degrees_to_compass = degrees_to_compass

    @staticmethod
    def _mean_direction(degrees: list[float | None]) -> float | None:
        valid = [float(d) for d in degrees if d is not None]
        if not valid:
            return None
        sin_sum = sum(math.sin(math.radians(d)) for d in valid)
        cos_sum = sum(math.cos(math.radians(d)) for d in valid)
        angle = math.degrees(math.atan2(sin_sum / len(valid), cos_sum / len(valid)))
        return angle % 360

    @staticmethod
    def _optional_float(value) -> float | None:
        if value is None:
            return None
        return float(value)

    @staticmethod
    def heat_index(temperature_f: float | None, humidity_percent: float | None) -> float | None:
        if temperature_f is None or humidity_percent is None:
            return None
        if temperature_f < 80 or humidity_percent < 40:
            return temperature_f

        t = float(temperature_f)
        rh = float(humidity_percent)
        hi = (
            -42.379
            + 2.04901523 * t
            + 10.14333127 * rh
            - 0.22475541 * t * rh
            - 0.00683783 * t * t
            - 0.05481717 * rh * rh
            + 0.00122874 * t * t * rh
            + 0.00085282 * t * rh * rh
            - 0.00000199 * t * t * rh * rh
        )
        return hi
