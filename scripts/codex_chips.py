#!/usr/bin/env python3
"""Local fallback for protocol-driven-execution chips decisions.

This script is intentionally small and dependency-free. It provides a durable
numbered prompt when native Codex/OMX structured chips are unavailable, and a
record mode for answers collected by another surface.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

DEFAULT_LOG = Path(".chips/decisions.jsonl")


def load_json_arg(value: str) -> Any:
    path = Path(value)
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return json.loads(value)


def normalize_spec(spec: Dict[str, Any]) -> Dict[str, Any]:
    questions = spec.get("questions")
    if not isinstance(questions, list) or not questions:
        raise SystemExit("spec.questions must be a non-empty list")
    if len(questions) > 4:
        raise SystemExit("chips supports at most 4 questions per call")
    for index, question in enumerate(questions, start=1):
        if not question.get("id"):
            question["id"] = f"question_{index}"
        if not question.get("header"):
            question["header"] = question["id"]
        options = question.get("options")
        if not isinstance(options, list) or len(options) < 2:
            raise SystemExit(f"question {question['id']} must have at least 2 options")
        if len(options) > 4:
            raise SystemExit(f"question {question['id']} has more than 4 options")
    return spec


def ask_question(question: Dict[str, Any], auto: str | None) -> Dict[str, Any]:
    options: List[Dict[str, str]] = question["options"]
    print(f"\n[{question['header']}] {question['question']}")
    for idx, option in enumerate(options, start=1):
        label = option.get("label", f"Option {idx}")
        description = option.get("description", "")
        print(f"  {idx}. {label} — {description}")
    allow_other = bool(question.get("allow_other", True))
    if allow_other:
        print("  o. Other / free-form")

    if auto:
        if auto == "recommended":
            selected = [options[0].get("label", "Option 1")]
            return {"answers": selected, "source": "recommended_default"}
        raise SystemExit(f"unsupported --auto value: {auto}")

    if not sys.stdin.isatty():
        raise SystemExit("stdin is not a TTY; use --auto recommended or record mode")

    while True:
        raw = input("Select option number (or 'o'): ").strip()
        if raw.lower() == "o" and allow_other:
            text = input("Other: ").strip()
            if text:
                return {"answers": [text], "source": "explicit_other"}
        if raw.isdigit():
            idx = int(raw)
            if 1 <= idx <= len(options):
                return {"answers": [options[idx - 1].get("label", f"Option {idx}")], "source": "explicit_user"}
        print("Invalid choice. Try again.")


def write_log(log_path: Path, spec: Dict[str, Any], answers: Dict[str, Any], backend: str) -> Dict[str, Any]:
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "backend": backend,
        "context": spec.get("context"),
        "question_ids": [q["id"] for q in spec["questions"]],
        "answers": answers,
    }
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False, sort_keys=True) + "\n")
    return entry


def cmd_ask(args: argparse.Namespace) -> None:
    spec = normalize_spec(load_json_arg(args.spec))
    answers: Dict[str, Any] = {}
    for question in spec["questions"]:
        answers[question["id"]] = ask_question(question, args.auto)
    entry = write_log(Path(args.log), spec, answers, args.backend)
    print("\nCHIPS_RESULT=" + json.dumps(entry, ensure_ascii=False, sort_keys=True))


def cmd_record(args: argparse.Namespace) -> None:
    spec = normalize_spec(load_json_arg(args.spec))
    answers = load_json_arg(args.answers)
    if not isinstance(answers, dict):
        raise SystemExit("answers must be a JSON object keyed by question id")
    entry = write_log(Path(args.log), spec, answers, args.backend)
    print(json.dumps(entry, ensure_ascii=False, sort_keys=True))


def main() -> None:
    parser = argparse.ArgumentParser(description="Codex chips fallback adapter")
    sub = parser.add_subparsers(dest="command", required=True)

    ask = sub.add_parser("ask", help="show numbered chips prompt and record answer")
    ask.add_argument("--spec", required=True, help="JSON string or path to JSON spec")
    ask.add_argument("--log", default=os.environ.get("CODEX_CHIPS_LOG", str(DEFAULT_LOG)))
    ask.add_argument("--backend", default="local_cli")
    ask.add_argument("--auto", choices=["recommended"], help="non-interactive default selection")
    ask.set_defaults(func=cmd_ask)

    record = sub.add_parser("record", help="record answers collected by another surface")
    record.add_argument("--spec", required=True, help="JSON string or path to JSON spec")
    record.add_argument("--answers", required=True, help="JSON string or path to answers JSON")
    record.add_argument("--log", default=os.environ.get("CODEX_CHIPS_LOG", str(DEFAULT_LOG)))
    record.add_argument("--backend", default="plain_text_emergency")
    record.set_defaults(func=cmd_record)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
