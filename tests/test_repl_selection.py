import json
from datetime import date, timedelta

from app.repl import WeatherAssistantREPL


def test_future_events_only(tmp_path):
    today = date.today()
    calendar_path = tmp_path / "calendar.json"
    calendar_path.write_text(json.dumps([
        {
            "title": "Past Game",
            "start": (today - timedelta(days=1)).isoformat() + "T18:00:00",
            "end": (today - timedelta(days=1)).isoformat() + "T21:00:00",
            "location": "Houston, TX",
        },
        {
            "title": "Future Game",
            "start": (today + timedelta(days=1)).isoformat() + "T18:00:00",
            "end": (today + timedelta(days=1)).isoformat() + "T21:00:00",
            "location": "Houston, TX",
        },
    ]))
    repl = WeatherAssistantREPL(calendar_path=str(calendar_path), use_llm=False)
    events = repl.future_events()
    assert [event.title for event in events] == ["Future Game"]
