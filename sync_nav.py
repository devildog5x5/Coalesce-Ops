#!/usr/bin/env python3
"""Write includes/nav.json into every HTML page.

The menu block between the site-nav markers must be identical on every page.
Edit includes/nav.json, then run: python3 sync_nav.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
NAV_PATH = ROOT / "includes" / "nav.json"
START = "<!-- site-nav:start -->"
END = "<!-- site-nav:end -->"


def load_nav() -> dict:
    data = json.loads(NAV_PATH.read_text(encoding="utf-8"))
    if not data.get("items"):
        raise SystemExit("includes/nav.json has no items")
    return data


def render_nav(data: dict | None = None) -> str:
    data = data or load_nav()
    items = data["items"]
    lines = ['  <nav class="nav" id="site-nav" aria-label="Primary">']
    last_align = max(0, len(items) - 3)
    for index, item in enumerate(items):
        group_class = "nav-group align-end" if index >= last_align else "nav-group"
        lines.append(f'    <div class="{group_class}">')
        css = "nav-link nav-cta" if item.get("cta") else "nav-link"
        lines.append(f'      <a class="{css}" href="{item["href"]}">{item["label"]}</a>')
        sections = item.get("sections") or []
        if sections:
            lines.append('      <details class="nav-sections">')
            lines.append(
                f'        <summary><span class="sr-only">{item["sectionsLabel"]}</span></summary>'
            )
            lines.append('        <div class="nav-panel">')
            for section in sections:
                lines.append(
                    f'          <a href="{section["href"]}">{section["label"]}</a>'
                )
            lines.append("        </div>")
            lines.append("      </details>")
        lines.append("    </div>")
    lines.append("  </nav>")
    return "\n".join(lines)


def render_block(data: dict | None = None) -> str:
    return f"{START}\n{render_nav(data)}\n  {END}"


def html_files() -> list[Path]:
    return sorted(ROOT.glob("*.html"))


def sync() -> int:
    block = render_block()
    changed = 0
    missing = []
    for path in html_files():
        text = path.read_text(encoding="utf-8")
        if START not in text or END not in text:
            missing.append(path.name)
            continue
        before, rest = text.split(START, 1)
        _, after = rest.split(END, 1)
        updated = before + block + after
        if updated != text:
            path.write_text(updated, encoding="utf-8")
            changed += 1
    if missing:
        raise SystemExit(
            "Missing site-nav markers in: " + ", ".join(missing)
        )
    print(f"Menu synced into HTML ({changed} file(s) updated).")
    return changed


if __name__ == "__main__":
    sync()
    sys.exit(0)
