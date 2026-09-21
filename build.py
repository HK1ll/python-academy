#!/usr/bin/env python3
"""Validate content/lessons.py and write public/data/lessons.json.

The front end only ever receives plain data (strings), which it renders with DOM APIs
(textContent), never as HTML - so lesson content cannot inject markup or script.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR / "content"))

from lessons import LESSONS, SECTIONS  # noqa: E402

OUTPUT = BASE_DIR / "public" / "data" / "lessons.json"
ID_PATTERN = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
BLOCK_TYPES = {"p", "h", "list", "tip", "warn", "sec", "code", "codeonly", "output"}
EXERCISE_STR_KEYS = ("prompt", "starter", "hint", "solution", "check")
MAX_TEXT = 8_000
FILE_NAME = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_.-]{0,39}")
MAX_FILES = 10
MAX_FILE_CHARS = 20_000


def fail(message: str) -> None:
    raise SystemExit(f"lessons.py: {message}")


def clean_text(value, where: str) -> str:
    if not isinstance(value, str) or not value.strip():
        fail(f"{where}: expected a non-empty string")
    if len(value) > MAX_TEXT:
        fail(f"{where}: text longer than {MAX_TEXT} characters")
    return value


def build() -> list[dict]:
    seen: set[str] = set()
    result = []
    for number, lesson in enumerate(LESSONS, start=1):
        lid = lesson.get("id")
        if not isinstance(lid, str) or not ID_PATTERN.fullmatch(lid):
            fail(f"lesson {number}: id must be lowercase-kebab-case, got {lid!r}")
        if lid in seen:
            fail(f"duplicate lesson id {lid!r}")
        seen.add(lid)
        where = f"lesson {lid}"

        blocks = []
        for index, block in enumerate(lesson["blocks"]):
            kind = block.get("type")
            if kind not in BLOCK_TYPES:
                fail(f"{where} block {index}: unknown type {kind!r}")
            if kind == "list":
                entries = [clean_text(t, f"{where} block {index} item") for t in block["items"]]
                blocks.append({"type": "list", "items": entries})
            else:
                blocks.append({"type": kind, "text": clean_text(block["text"], f"{where} block {index}")})

        exercise = lesson.get("exercise")
        exercise_out = None
        if exercise:
            exercise_out = {key: clean_text(exercise[key], f"{where} exercise.{key}") for key in EXERCISE_STR_KEYS}
            if "stdin" in exercise:
                exercise_out["stdin"] = clean_text(exercise["stdin"], f"{where} exercise.stdin")
            if "files" in exercise:
                files = exercise["files"]
                if not isinstance(files, dict) or not 0 < len(files) <= MAX_FILES:
                    fail(f"{where} exercise.files: expected 1-{MAX_FILES} files")
                for name, text in files.items():
                    if not FILE_NAME.fullmatch(name):
                        fail(f"{where} exercise.files: bad file name {name!r}")
                    if not isinstance(text, str) or len(text) > MAX_FILE_CHARS:
                        fail(f"{where} exercise.files[{name!r}]: expected text up to {MAX_FILE_CHARS} characters")
                exercise_out["files"] = dict(files)

        result.append(
            {
                "id": lid,
                "title": clean_text(lesson["title"], f"{where} title"),
                "summary": clean_text(lesson["summary"], f"{where} summary"),
                "blocks": blocks,
                "exercise": exercise_out,
            }
        )
    return result


def build_sections(lessons: list[dict]) -> list[dict]:
    """Every lesson must be in exactly one section, and sections must follow lesson order."""
    order = [lesson["id"] for lesson in lessons]
    listed = [lesson_id for section in SECTIONS for lesson_id in section["ids"]]
    if sorted(listed) != sorted(order):
        missing = sorted(set(order) - set(listed))
        unknown = sorted(set(listed) - set(order))
        duplicated = sorted({i for i in listed if listed.count(i) > 1})
        fail(f"SECTIONS must list every lesson exactly once (missing={missing}, unknown={unknown}, duplicated={duplicated})")
    if listed != order:
        fail("SECTIONS must list lessons in the same order as LESSONS")
    return [
        {"title": clean_text(section["title"], "section title"), "ids": list(section["ids"])}
        for section in SECTIONS
    ]


def render() -> str:
    lessons = build()
    return json.dumps({"sections": build_sections(lessons), "lessons": lessons}, indent=1, ensure_ascii=False) + "\n"


def main() -> int:
    text = render()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(text, encoding="utf-8", newline="\n")
    print(f"Wrote {OUTPUT.relative_to(BASE_DIR)} ({len(LESSONS)} lessons)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
