from __future__ import annotations

import re
import subprocess
import sys
from datetime import date
from pathlib import Path

REPORT_PATH = Path("docs/TEST_REPORT.md")
RAW_OUTPUT_PATH = Path("docs/TEST_RUN_OUTPUT.md")

TEST_SUITES = [
    ("Weather Client", "tests/test_weather_client.py"),
    ("Calendar Store", "tests/test_calendar_store.py"),
    ("Advisor", "tests/test_advisor.py"),
    ("Historical Guidance", "tests/test_weather_partitions.py"),
    ("Gemini Primary", "tests/test_gemini_advisor.py"),
    ("Example Scenarios", "tests/test_advice_examples.py"),
]


def run_pytest(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "pytest", *args],
        capture_output=True,
        text=True,
    )


def parse_counts(output: str) -> tuple[int, int, int]:
    """Return (total, passed, failed) from pytest output."""
    passed = 0
    failed = 0

    passed_match = re.search(r"(\d+) passed", output)
    failed_match = re.search(r"(\d+) failed", output)

    if passed_match:
        passed = int(passed_match.group(1))
    if failed_match:
        failed = int(failed_match.group(1))

    return passed + failed, passed, failed


def suite_status(path: str) -> str:
    if not Path(path).exists():
        return "MISSING"

    result = run_pytest([path, "-q"])
    return "PASS" if result.returncode == 0 else "FAIL"


def main() -> int:
    full_result = run_pytest(["-q"])
    combined_output = f"{full_result.stdout}\n{full_result.stderr}"
    total, passed, failed = parse_counts(combined_output)

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    RAW_OUTPUT_PATH.write_text(
        "# Weather Assistant Raw Pytest Output\n\n"
        f"Generated: {date.today().isoformat()}\n\n"
        f"Exit code: {full_result.returncode}\n\n"
        "```text\n"
        f"{combined_output}"
        "\n```\n",
        encoding="utf-8",
    )

    suite_rows = []
    for label, path in TEST_SUITES:
        suite_rows.append((label, suite_status(path)))

    report = [
        "# Weather Assistant Test Report",
        "",
        f"Generated: {date.today().isoformat()}",
        "",
        "## Test Summary",
        "",
        "| Test Suite | Status |",
        "| --- | --- |",
    ]

    for label, status in suite_rows:
        report.append(f"| {label} | {status} |")

    report.extend(
        [
            "",
            f"Total Tests: {total}",
            "",
            f"Passed: {passed}",
            "",
            f"Failed: {failed}",
            "",
            "---",
            "",
            "## Advice Architecture",
            "",
            "Gemini is the primary advice model. The rule-based advisor is retained as a deterministic backup and validation layer when Gemini is unavailable.",
            "",
            "---",
            "",
            "## Example Scenario: Rainy Astros Game",
            "",
            "### Input",
            "",
            "Event:",
            "",
            "* Astros vs Rangers",
            "* Houston, TX",
            "",
            "Weather:",
            "",
            "* Temperature: 75°F",
            "* Humidity: 92%",
            "* Rain Probability: 90%",
            "* Wind: 5 mph from E",
            "",
            "### Expected Advice",
            "",
            "Bring rain gear and consider public transit, covered transportation, or covered seating. Expect wet conditions and possible delays.",
            "",
            f"Result: {'PASS' if full_result.returncode == 0 else 'CHECK TEST OUTPUT'}",
            "",
            "---",
            "",
            "## Example Scenario: Extreme Heat",
            "",
            "### Input",
            "",
            "Weather:",
            "",
            "* Temperature: 92°F",
            "* Humidity: 80%",
            "* Heat Index: 108°F",
            "",
            "### Expected Advice",
            "",
            "Bring water, seek shade, and take breaks from the heat.",
            "",
            f"Result: {'PASS' if full_result.returncode == 0 else 'CHECK TEST OUTPUT'}",
            "",
            "---",
            "",
            "## Example Scenario: Historical Guidance",
            "",
            "### Input",
            "",
            "Event Date:",
            "",
            "* 45 days in future",
            "",
            "### Expected Advice",
            "",
            "Historical guidance should be presented and clearly identified as not being a forecast.",
            "",
            f"Result: {'PASS' if full_result.returncode == 0 else 'CHECK TEST OUTPUT'}",
            "",
            "---",
            "",
            "## Raw Pytest Output",
            "",
            "Raw pytest output is saved separately in `docs/TEST_RUN_OUTPUT.md`.",
            "",
        ]
    )

    REPORT_PATH.write_text("\n".join(report), encoding="utf-8")
    print(f"Wrote {REPORT_PATH}")
    print(f"Wrote {RAW_OUTPUT_PATH}")
    return full_result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
