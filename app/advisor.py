from app.llm_client import LLMClient
from app.models import Event, Weather


class Advisor:
    def __init__(self, use_llm: bool = True):
        self.llm = LLMClient() if use_llm else None

    def advice_for_event(self, event: Event, weather: Weather) -> str:
        llm_text = self._llm_advice(event, weather)
        if llm_text and not llm_text.startswith("LLM unavailable"):
            return llm_text
        fallback = self._rule_based_advice(event, weather)
        if llm_text:
            return f"{llm_text}\n{fallback}"
        return fallback

    def _llm_advice(self, event: Event, weather: Weather) -> str | None:
        if not self.llm:
            return None

        prompt = f"""
You are a practical weather assistant.
Use only the facts below. Do not invent weather data.

Event:
- Title: {event.title}
- Time: {event.start.strftime('%Y-%m-%d %I:%M %p')} to {event.end.strftime('%I:%M %p')}
- Location: {event.location}

Weather:
- Source: {weather.source}
- Confidence: {weather.confidence}
- Temperature: {weather.temperature_f:.0f} F
- Humidity: {weather.humidity_summary}
- Heat index: {weather.heat_index_summary}
- Condition: {weather.summary}
- Precipitation probability: {weather.precipitation_probability}%
- Precipitation amount: {weather.precipitation_mm:.2f} mm
- Wind: {weather.wind_summary}
- Historical average temperature: {weather.historical_temperature_avg_f}
- Historical rain probability: {weather.historical_rain_probability}
- Historical average wind speed: {weather.historical_wind_speed_avg_mph}
- Historical wind direction: {weather.historical_wind_direction}
- Historical average humidity: {weather.historical_humidity_avg_percent}
- Historical average heat index: {weather.historical_heat_index_avg_f}

Instructions:
- Do not restate the forecast line by line.
- Do not repeat exact numbers unless they directly affect advice.
- Focus on what the user should do.
- Mention clothing, travel, timing, hydration, rain gear, or indoor backup only when relevant.
- Keep it to 2-4 sentences.
- If source is historical, clearly say this is historical guidance, not a forecast.
""".strip()
        return self.llm.generate(prompt)
    
    def _rule_based_advice(self, event: Event, weather: Weather) -> str:
        tips = []

        if weather.source == "forecast_plus_history":
            tips.append("this 11-16 day forecast should be treated cautiously")

        if weather.source == "historical_average":
            tips.append("this is historical guidance, not a forecast")

        if (
            weather.precipitation_probability >= 50
            or weather.precipitation_mm > 0
        ):
            tips.append(
                "bring an umbrella or rain jacket and consider public transit or covered transportation"
            )

        if weather.wind_speed_mph >= 20:
            tips.append(
                f"expect wind from {weather.wind_direction or 'an unknown direction'} and allow extra travel time"
            )

        if weather.temperature_f <= 40:
            tips.append("dress warmly")

        # NEW: humidity and heat index logic
        if (
            hasattr(weather, "heat_index_f")
            and weather.heat_index_f is not None
            and weather.heat_index_f >= 100
        ):
            tips.append(
                f"heat index near {weather.heat_index_f:.0f} F; bring water, seek shade, and take breaks from the heat"
            )
        elif weather.temperature_f >= 85:
            tips.append("bring water and plan for heat")

        if (
            hasattr(weather, "humidity_percent")
            and weather.humidity_percent is not None
            and weather.humidity_percent >= 75
        ):
            tips.append(
                "high humidity may make conditions feel significantly warmer than the air temperature"
            )

        if not tips:
            tips.append("weather looks manageable")

        return (
            f"{event.title}: {weather.temperature_f:.0f} F, "
            f"{weather.summary}, wind {weather.wind_summary}. "
            f"Advice: {', '.join(tips)}."
        )

    def weather_then_advice(self, event: Event, weather: Weather) -> str:
        lines = [
            f"{event.start.strftime('%a %Y-%m-%d %I:%M %p')} - {event.title} ({event.location})",
            f"Weather: {weather.temperature_f:.0f} F, humidity {weather.humidity_summary}, heat index {weather.heat_index_summary}, {weather.summary}, precipitation {weather.precipitation_probability}%, wind {weather.wind_summary}.",
        ]
        if weather.source == "forecast_plus_history":
            lines.append(
                "Note: This is an 11-16 day forecast, so treat it as cautionary. "
                f"5-year history: avg {weather.historical_temperature_avg_f:.0f} F, "
                f"rain in {weather.historical_rain_probability}% of years, "
                f"avg wind {weather.historical_wind_speed_avg_mph:.0f} mph from {weather.historical_wind_direction}."
            )
        elif weather.source == "historical_average":
            lines.append(
                "Note: Forecast is unavailable this far out. "
                f"Using 5-year historical guidance: avg {weather.historical_temperature_avg_f:.0f} F, "
                f"rain in {weather.historical_rain_probability}% of years, "
                f"avg wind {weather.historical_wind_speed_avg_mph:.0f} mph from {weather.historical_wind_direction}."
            )
        lines.append(f"Advice: {self.advice_for_event(event, weather)}")
        return "\n".join(lines)
