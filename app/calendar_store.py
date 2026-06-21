import json
from datetime import datetime
from pathlib import Path
from typing import List

from app.models import Event


class CalendarStore:
    def __init__(self, path: str = "data/calendar.json"):
        self.path = Path(path)

    def load_events(self) -> List[Event]:
        if not self.path.exists():
            raise FileNotFoundError(f"Calendar file not found: {self.path}")

        with self.path.open("r", encoding="utf-8") as file:
            raw_events = json.load(file)

        events = []
        for item in raw_events:
            events.append(
                Event(
                    title=item["title"],
                    start=datetime.fromisoformat(item["start"]),
                    end=datetime.fromisoformat(item["end"]),
                    location=item["location"],
                )
            )
        return events
