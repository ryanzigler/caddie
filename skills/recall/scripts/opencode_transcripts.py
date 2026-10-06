#!/usr/bin/env python3
"""Index project-scoped OpenCode v2 exports and digest authored conversation text."""

import argparse
import datetime
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time


def load_export(path):
    data = json.loads(path.read_text())
    if isinstance(data, dict) and "data" in data:
        data = data["data"]
    if (not isinstance(data, dict) or not isinstance(data.get("info"), dict)
            or not isinstance(data.get("messages"), list)):
        raise ValueError(f"Unsupported OpenCode v2 export: {path}")
    info = data["info"]
    if (not isinstance(info.get("id"), str) or not isinstance(info.get("location"), dict)
            or not isinstance(info["location"].get("directory"), str)
            or not Path(info["location"]["directory"]).is_absolute()):
        raise ValueError(f"Unsupported OpenCode v2 session metadata: {path}")
    return data


def eligible(info, args):
    directory = info.get("location", {}).get("directory")
    return (isinstance(directory, str)
            and Path(directory).resolve().is_relative_to(args.project)
            and info.get("id") != args.exclude_session
            and not info.get("parentID"))


def messages(data, project):
    switches = [item for item in data["messages"]
                if isinstance(item, dict) and item.get("type") == "location-switched"]
    directory = data["info"].get("location", {}).get("directory")
    if switches:
        directory = (switches[0].get("previous") or {}).get("location", {}).get("directory")
    for item in data["messages"]:
        if not isinstance(item, dict) or not isinstance(item.get("type"), str):
            raise ValueError("Unsupported message in OpenCode export")
        role = item.get("type")
        if role == "location-switched":
            directory = item.get("location", {}).get("directory")
            continue
        if (not isinstance(directory, str) or not Path(directory).is_absolute()
                or not Path(directory).resolve().is_relative_to(project)):
            continue
        if role == "user":
            text = item.get("text", "")
        elif role == "assistant":
            text = "\n".join(part["text"] for part in item.get("content", [])
                             if isinstance(part, dict) and part.get("type") == "text"
                             and isinstance(part.get("text"), str))
        else:
            continue
        if not isinstance(text, str):
            raise ValueError("Unsupported authored text in OpenCode export")
        if text:
            yield {"message_id": item.get("id"), "timestamp": item.get("time", {}).get("created"),
                   "role": role, "text": text}


def cli(args, tail):
    command = [args.opencode, "session", *tail]
    if args.server:
        command += ["--server", args.server]
    # OpenCode v2 can exit before draining large stdout writes to a pipe.
    # A regular file keeps Node's stdout writes synchronous and exports complete.
    with tempfile.TemporaryFile(mode="w+", encoding="utf-8") as output:
        result = subprocess.run(command, cwd=args.project, stdout=output,
                                stderr=subprocess.PIPE, text=True, timeout=60)
        if result.returncode:
            raise ValueError(f"OpenCode history command failed: {result.stderr.strip()}")
        output.seek(0)
        return json.load(output)


def export_sessions(args):
    rows = cli(args, ["list", "--format", "json", "--max-count", str(args.max_sessions)])
    if not isinstance(rows, list):
        raise ValueError("Unsupported OpenCode session list")
    if len(rows) >= args.max_sessions:
        raise ValueError("Session list reached --max-sessions; increase it to avoid an incomplete index")
    cutoff = 0 if args.days == 0 else (time.time() - args.days * 86400) * 1000
    args.exports_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    paths = []
    for row in rows:
        session_id = row.get("id")
        directory = row.get("directory")
        if (not isinstance(session_id, str) or not re.fullmatch(r"ses_[A-Za-z0-9]+", session_id)
                or session_id == args.exclude_session or row.get("parentID")
                or not isinstance(directory, str)
                or not Path(directory).resolve().is_relative_to(args.project)
                or row.get("updated", 0) < cutoff):
            continue
        data = cli(args, ["export", session_id])
        path = args.exports_dir / f"{session_id}.json"
        if path.is_symlink():
            raise ValueError(f"Refusing to follow a history export symlink: {path}")
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(descriptor, "w") as stream:
            json.dump(data, stream)
        paths.append(path)
    return paths


def index(args):
    if args.offline:
        if not args.exports_dir.is_dir():
            raise ValueError(f"History export directory is unavailable: {args.exports_dir}")
        paths = list(args.exports_dir.glob("*.json"))
    else:
        paths = export_sessions(args)
    rows = []
    cutoff = 0 if args.days == 0 else (time.time() - args.days * 86400) * 1000
    for path in paths:
        if not path.resolve().is_relative_to(args.exports_dir):
            raise ValueError(f"Export path is outside the requested directory: {path}")
        data = load_export(path)
        info = data["info"]
        updated = info.get("time", {}).get("updated", 0)
        if not eligible(info, args) or updated < cutoff:
            continue
        prose = list(messages(data, args.project))
        if args.topic and not any(args.topic.casefold() in item["text"].casefold() for item in prose):
            continue
        prompts = [item for item in prose if item["role"] == "user"]
        rows.append({"session_id": info["id"], "path": str(path),
                     "cwd": info["location"]["directory"], "title": info.get("title"),
                     "modified": updated, "prompts": len(prompts),
                     "first_prompt": " ".join(prompts[0]["text"].split())[:160] if prompts else ""})
    for row in sorted(rows, key=lambda row: row["modified"], reverse=True):
        print(json.dumps(row))


def digest(args):
    path = args.path.resolve()
    if not path.is_relative_to(args.exports_dir):
        raise ValueError("Choose an export from the requested history directory")
    data = load_export(path)
    if not eligible(data["info"], args):
        raise ValueError("Export is outside the project, current session, or a child session")
    print(json.dumps({"session_id": data["info"]["id"], "path": str(path)}))
    shown = 0
    for number, item in enumerate(messages(data, args.project), 1):
        if number < args.start:
            continue
        if shown == args.limit:
            print(json.dumps({"next_start": number}))
            break
        timestamp = item["timestamp"]
        if isinstance(timestamp, (int, float)):
            item["timestamp"] = datetime.datetime.fromtimestamp(timestamp / 1000, datetime.timezone.utc).isoformat()
        print(json.dumps({"number": number, **item}))
        shown += 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--exports-dir", required=True, type=Path)
    parser.add_argument("--exclude-session", default=os.environ.get("CADDIE_OPENCODE_SESSION_ID"))
    parser.add_argument("--opencode", default="opencode")
    parser.add_argument("--server", help="Optional OpenCode server URL")
    commands = parser.add_subparsers(dest="command", required=True)
    listing = commands.add_parser("index")
    listing.add_argument("--days", type=int, default=7)
    listing.add_argument("--topic")
    listing.add_argument("--offline", action="store_true", help="Read existing exports without contacting OpenCode")
    listing.add_argument("--max-sessions", type=int, default=1000)
    reading = commands.add_parser("digest")
    reading.add_argument("path", type=Path)
    reading.add_argument("--start", type=int, default=1)
    reading.add_argument("--limit", type=int, default=40)
    args = parser.parse_args()
    args.project = args.project.expanduser().resolve()
    args.exports_dir = args.exports_dir.expanduser().resolve()
    if args.command == "digest" and (args.start < 1 or args.limit < 1):
        parser.error("--start and --limit must be positive")
    if args.command == "index" and (args.days < 0 or args.max_sessions < 1):
        parser.error("--days must be nonnegative and --max-sessions positive")
    try:
        index(args) if args.command == "index" else digest(args)
    except (ValueError, OSError, subprocess.TimeoutExpired) as error:
        parser.exit(1, f"OpenCode history unavailable: {error}\n")


if __name__ == "__main__":
    main()
