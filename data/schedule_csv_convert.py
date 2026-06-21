import csv
import json
from datetime import datetime, timedelta
from pathlib import Path

INPUT_CSV = Path("astros_2026_schedule.csv")
OUTPUT_JSON = Path("calendar.json")

GAME_DURATION_HOURS = 3


def parse_datetime(date_str: str, time_str: str) -> datetime:
    value = f"{date_str.strip()} {time_str.strip()}"
    formats = [
        "%Y-%m-%d %I:%M %p",
        "%m/%d/%Y %I:%M %p",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            pass
    raise ValueError(f"Unsupported date/time format: {value}")


def format_location(location: str) -> str:
    """
    Converts:
      Houston TX -> Houston, TX
      New York NY -> New York, NY
      Los Angeles CA -> Los Angeles, CA
    """
    location = location.strip()
    parts = location.rsplit(" ", 1)

    if len(parts) == 2:
        city, state = parts
        return f"{city}, {state}"

    return location


def clean_opponent(opponent: str) -> str:
    return (
        opponent.strip()
        .replace("vs. ", "")
        .replace("vs ", "")
        .replace("at ", "")
    )


def make_title(opponent: str) -> str:
    opponent = opponent.strip()

    if opponent.startswith("vs"):
        return f"Houston Astros {opponent}"

    if opponent.startswith("at"):
        return f"Houston Astros {opponent}"

    return f"Houston Astros vs. {opponent}"


def convert_csv_to_calendar_json(input_csv: Path, output_json: Path) -> None:
    events = []

    with input_csv.open(newline="", encoding="utf-8-sig") as f:
        sample = f.read(2048)
        f.seek(0)
        dialect = csv.Sniffer().sniff(sample, delimiters=",\t")
        reader = csv.DictReader(f, dialect=dialect)

        required = {"Date", "Opponent", "Location", "Venue", "Start Time (Local)", "Time Zone"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"CSV is missing required columns: {sorted(missing)}")

        for row in reader:
            start_dt = parse_datetime(row["Date"], row["Start Time (Local)"])
            end_dt = start_dt + timedelta(hours=GAME_DURATION_HOURS)
            opponent = row["Opponent"].strip()

            events.append(
                {
                    "title": make_title(opponent),
                    "start": start_dt.isoformat(),
                    "end": end_dt.isoformat(),
                    "location": format_location(row["Location"]),
                    "category": "mlb_game",
                    "team": "Houston Astros",
                    "venue": row["Venue"].strip(),
                    "opponent": clean_opponent(opponent),
                    "time_zone": row["Time Zone"].strip(),
                }
            )

    output_json.parent.mkdir(parents=True, exist_ok=True)

    with output_json.open("w", encoding="utf-8") as f:
        json.dump(events, f, indent=2)

    print(f"Created {output_json} with {len(events)} games.")


if __name__ == "__main__":
    convert_csv_to_calendar_json(INPUT_CSV, OUTPUT_JSON)
