#!/usr/bin/env python
# extract_chat.py  –  sits next to chatgpt.json
import json, textwrap, sys, pathlib

# ── configuration ───────────────────────────────────────────────────────────
DATA_FILE    = pathlib.Path(__file__).with_name("chatgpt.json")      # export file
THREAD_TITLE = sys.argv[1] if len(sys.argv) > 1 else None            # chat title
# ────────────────────────────────────────────────────────────────────────────


def load_export(path: pathlib.Path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def pick_thread(data, title: str | None):
    """Return the conversation dict whose 'title' matches, case-insensitive."""
    if title is None:
        print("🔎  Available thread titles:\n")
        for obj in data:
            print(" •", obj["title"])
        sys.exit('\n👆  Re-run with:  python extract_chat.py "Exact Thread Title"')

    title_lc = title.lower()
    try:
        return next(obj for obj in data if obj["title"].lower() == title_lc)
    except StopIteration:
        sys.exit(f"❌  No chat titled “{title}” — check spelling & quotes.")


def pretty_print(thread):
    """Print USER / ASSISTANT messages in chronological order, skipping blanks."""
    messages = sorted(
        (n["message"] for n in thread["mapping"].values() if n.get("message")),
        key=lambda m: (m.get("create_time") or 0),   # None → 0   ✅
    )

    for m in messages:
        parts = (m.get("content") or {}).get("parts") or []
        if not parts:             # system / dev-only records
            continue
        role = (m.get("role") or "unknown").upper()
        print(f"\n{role}:")
        print(textwrap.fill(str(parts[0]), width=100))


if __name__ == "__main__":
    data   = load_export(DATA_FILE)
    thread = pick_thread(data, THREAD_TITLE)
    pretty_print(thread)

