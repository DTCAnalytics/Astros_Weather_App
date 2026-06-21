import json

from app.calendar_store import CalendarStore


def test_load_events(tmp_path):
    calendar_path = tmp_path / "calendar.json"
    calendar_path.write_text(json.dumps([
        {
            "title": "Test Event",
            "start": "2026-06-17T10:00:00",
            "end": "2026-06-17T11:00:00",
            "location": "Boston"
        }
    ]))

    events = CalendarStore(str(calendar_path)).load_events()

    assert len(events) == 1
    assert events[0].title == "Test Event"
    assert events[0].location == "Boston"
