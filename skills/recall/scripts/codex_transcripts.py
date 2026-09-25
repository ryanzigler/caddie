#!/usr/bin/env python3
"""Index and digest local Codex rollouts without printing tool output or reasoning."""

import argparse
import datetime
import json
import os
from pathlib import Path
import sys
import time


def records(path):
    with path.open() as stream:
        for number, line in enumerate(stream, 1):
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                print(f"Skipped incomplete or invalid record: {path}:{number}", file=sys.stderr)
                continue
            if isinstance(record, dict):
                yield record


def metadata(path):
    for record in records(path):
        if record.get("type") == "session_meta":
            return record.get("payload", {})
    return {}


def in_project(meta, project):
    cwd = meta.get("cwd")
    return isinstance(cwd, str) and Path(cwd).resolve().is_relative_to(project)


def messages(path):
    for record in records(path):
        payload = record.get("payload", {})
        if record.get("type") != "response_item" or payload.get("type") != "message":
            continue
        role = payload.get("role")
        if role not in ("user", "assistant"):
            continue
        if role == "assistant" and payload.get("channel") == "analysis":
            continue
        content = payload.get("content", [])
        if not isinstance(content, list):
            continue
        text = "\n".join(
            block["text"] for block in content
            if isinstance(block, dict)
            and block.get("type") in ("input_text", "output_text", "text")
            and isinstance(block.get("text"), str)
        )
        # These user-role records are injected context, not human prompts.
        if role == "user" and text.lstrip().startswith((
            "# AGENTS.md instructions", "<environment_context>", "<permissions instructions>"
        )):
            continue
        if text:
            yield {"timestamp": record.get("timestamp"), "role": role, "text": text}


def index(args):
    roots = [args.codex_home / "sessions", args.codex_home / "archived_sessions"]
    if not any(root.is_dir() for root in roots):
        raise ValueError(f"No local Codex session directories under {args.codex_home}")
    cutoff = 0 if args.days == 0 else time.time() - args.days * 86400
    paths = [path for root in roots for path in root.rglob("*.jsonl")]
    paths.sort(key=lambda path: path.stat().st_mtime, reverse=True)
    for path in paths:
        mtime = path.stat().st_mtime
        if mtime < cutoff:
            continue
        meta = metadata(path)
        session_id = meta.get("id") or meta.get("session_id")
        source = json.dumps([meta.get("source"), meta.get("thread_source")]).lower()
        if (not in_project(meta, args.project) or not session_id
                or session_id == args.exclude_session or "subagent" in source):
            continue
        first_prompt = ""
        count = 0
        matched = not args.topic
        for message in messages(path):
            if args.topic and args.topic.casefold() in message["text"].casefold():
                matched = True
            if message["role"] == "user":
                count += 1
                if not first_prompt:
                    first_prompt = " ".join(message["text"].split())[:160]
        if matched:
            print(json.dumps({
                "session_id": session_id, "path": str(path), "cwd": meta["cwd"],
                "modified": datetime.datetime.fromtimestamp(mtime, datetime.timezone.utc).isoformat(),
                "prompts": count, "first_prompt": first_prompt,
            }))


def digest(args):
    path = args.path.resolve()
    roots = [args.codex_home / "sessions", args.codex_home / "archived_sessions"]
    if not any(path.is_relative_to(root.resolve()) for root in roots):
        raise ValueError("Choose a rollout from the Codex session index")
    meta = metadata(path)
    if not in_project(meta, args.project):
        raise ValueError("Session cwd is outside the requested project")
    print(json.dumps({"session_id": meta.get("id") or meta.get("session_id"), "path": str(path)}))
    shown = 0
    for number, message in enumerate(messages(path), 1):
        if number < args.start:
            continue
        if shown == args.limit:
            print(json.dumps({"next_start": number, "note": "More messages remain; continue if relevant."}))
            break
        print(json.dumps({"message": number, **message}))
        shown += 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--codex-home", type=Path, default=Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))))
    parser.add_argument("--project", type=Path, required=True)
    commands = parser.add_subparsers(dest="command", required=True)
    listing = commands.add_parser("index")
    listing.add_argument("--days", type=int, default=7, help="Modification window; 0 means all history")
    listing.add_argument("--topic", default="")
    listing.add_argument("--exclude-session", default=os.environ.get("CODEX_THREAD_ID", ""))
    reading = commands.add_parser("digest")
    reading.add_argument("path", type=Path)
    reading.add_argument("--start", type=int, default=1)
    reading.add_argument("--limit", type=int, default=40)
    args = parser.parse_args()
    args.project = args.project.resolve()
    args.codex_home = args.codex_home.expanduser().resolve()
    if args.command == "index" and args.days < 0:
        parser.error("--days must be nonnegative")
    if args.command == "digest" and (args.start < 1 or args.limit < 1):
        parser.error("--start and --limit must be positive")
    try:
        (index if args.command == "index" else digest)(args)
    except (OSError, ValueError) as error:
        parser.exit(1, f"{error}\n")


if __name__ == "__main__":
    main()
