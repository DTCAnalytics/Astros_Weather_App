import argparse

from app.repl import WeatherAssistantREPL


def main() -> None:
    parser = argparse.ArgumentParser(description="Weather Assistant")
    parser.add_argument("--calendar", default="data/calendar.json", help="Path to calendar JSON file")
    parser.add_argument("--no-llm", action="store_true", help="Use rule-based advice instead of the configured LLM")
    args = parser.parse_args()

    WeatherAssistantREPL(calendar_path=args.calendar, use_llm=not args.no_llm).run()


if __name__ == "__main__":
    main()
