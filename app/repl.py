from datetime import date, datetime, time, timedelta
from typing import Optional

try:
    import questionary
except ImportError:  # pragma: no cover
    questionary = None

from app.advisor import Advisor
from app.calendar_store import CalendarStore
from app.models import Event
from app.weather_client import WeatherClient


class WeatherAssistantREPL:
    def __init__(self, calendar_path: str = "data/calendar.json", use_llm: bool = True):
        self.calendar = CalendarStore(calendar_path)
        self.weather = WeatherClient()
        self.advisor = Advisor(use_llm=use_llm)

    def run(self) -> None:
        print("Weather Assistant")
        print("Default view: select a future scheduled event, then see weather followed by advice.")
        print("Type 'help' for commands.\n")

        # Default startup behavior: show all events from today forward as a selectable menu.
        self.select_future_event()

        while True:
            command = input("\n> ").strip()
            if command in {"exit", "quit"}:
                print("Goodbye!")
                break
            self.handle(command)

    def handle(self, command: str) -> None:
        if command == "help":
            print("Commands: select, games, week, weather <city>, schedule, advice today, exit")
        elif command in {"select", "games", "events", ""}:
            self.select_future_event()
        elif command in {"week", "next week"}:
            print(self.next_week_weather_and_advice())
        elif command.startswith("weather "):
            location = command.removeprefix("weather ").strip()
            self.show_weather_with_advice(location)
        elif command == "schedule":
            self.show_schedule(future_only=True)
        elif command == "advice today":
            print(self.weather_and_advice_for_range(date.today(), date.today()))
        else:
            print("Unknown command. Type 'help'.")

    def select_future_event(self) -> None:
        events = self.future_events()
        if not events:
            print("No scheduled events found from today forward.")
            return

        if questionary:
            choices = [
                questionary.Choice(
                    title=self._event_choice_label(event),
                    value=event,
                )
                for event in events
            ]
            choices.append(questionary.Choice(title="Cancel", value=None))

            selected = questionary.select(
                "Select a scheduled event:",
                choices=choices,
            ).ask()

            if selected is None:
                print("Selection cancelled.")
                return

            self.show_event_weather_and_advice(selected)
            return

        # Fallback if questionary is not installed or cannot be imported.
        for idx, event in enumerate(events, start=1):
            print(f"{idx}. {self._event_choice_label(event)}")
        raw = input("Select an event number, or press Enter to cancel: ").strip()
        if not raw:
            print("Selection cancelled.")
            return
        try:
            number = int(raw)
            selected = events[number - 1]
        except (ValueError, IndexError):
            print("Invalid selection.")
            return
        self.show_event_weather_and_advice(selected)

    def future_events(self) -> list[Event]:
        today = date.today()
        events = [event for event in self.calendar.load_events() if event.start.date() >= today]
        return sorted(events, key=lambda event: event.start)

    def show_event_weather_and_advice(self, event: Event) -> None:
        try:
            weather = self.weather.get_weather_for_event(event.location, event.start.date(), event.start.hour)
            print("\n" + self.advisor.weather_then_advice(event, weather))
        except Exception as exc:
            print(f"{event.title} ({event.location}): Could not fetch weather: {exc}")

    def show_weather_with_advice(self, location: str) -> None:
        now = date.today()
        event = Event(
            title="General weather check",
            start=datetime.combine(now, time(hour=12)),
            end=datetime.combine(now, time(hour=13)),
            location=location,
        )
        weather = self.weather.get_weather_for_event(location, now, 12)
        print(self.advisor.weather_then_advice(event, weather))

    def show_schedule(self, future_only: bool = False) -> None:
        events = self.future_events() if future_only else self.calendar.load_events()
        if not events:
            print("No scheduled events found.")
            return
        for event in events:
            print(self._event_choice_label(event))

    def next_week_weather_and_advice(self) -> str:
        today = date.today()
        return self.weather_and_advice_for_range(today, today + timedelta(days=7))

    def weather_and_advice_for_range(self, start: date, end: date) -> str:
        events = [event for event in self.calendar.load_events() if start <= event.start.date() <= end]
        if not events:
            return "No scheduled events in this range."

        sections = []
        for event in sorted(events, key=lambda item: item.start):
            try:
                weather = self.weather.get_weather_for_event(event.location, event.start.date(), event.start.hour)
                sections.append(self.advisor.weather_then_advice(event, weather))
            except Exception as exc:
                sections.append(f"{event.title} ({event.location}): Could not fetch weather: {exc}")
        return "\n\n".join(sections)

    @staticmethod
    def _event_choice_label(event: Event) -> str:
        return f"{event.start.strftime('%Y-%m-%d %I:%M %p')} - {event.title} - {event.location}"
