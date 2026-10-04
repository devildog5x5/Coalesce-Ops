#!/usr/bin/env python3
"""Stamp site.config.json into a staged copy of the site.

Blank and PLACEHOLDER values are omitted. This does not edit the source HTML
unless you pass --stage pointing at a copy (the zip build does that).
"""

from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

ROOT = Path(__file__).resolve().parent
MARK = "<!-- site-config:verification -->"
PLACEHOLDERS = {
    "",
    "PLACEHOLDER",
    "REPLACE_ME",
    "TODO",
    "YOUR_CODE",
    "PASTE",
    "PASTE_HERE",
}
BUSINESS_ID = "https://coalesceops.com/#business"


def clean(value):
    if not isinstance(value, str):
        return ""
    text = value.strip()
    if text.upper() in PLACEHOLDERS:
        return ""
    return text


def load_config(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def verification_meta(config: dict) -> str:
    lines = []
    google = clean(config.get("googleSiteVerification", ""))
    bing = clean(config.get("bingSiteVerification", ""))
    if google:
        if any(ch.isspace() for ch in google) or "<" in google or ">" in google:
            raise SystemExit(
                "googleSiteVerification must be the token only, not the full meta tag."
            )
        lines.append(
            f'  <meta name="google-site-verification" content="{html.escape(google, quote=True)}" />'
        )
    if bing:
        if any(ch.isspace() for ch in bing) or "<" in bing or ">" in bing:
            raise SystemExit(
                "bingSiteVerification must be the token only, not the full meta tag."
            )
        lines.append(
            f'  <meta name="msvalidate.01" content="{html.escape(bing, quote=True)}" />'
        )
    return "\n".join(lines)


def address_from(config: dict):
    raw = config.get("address") or {}
    fields = [
        "streetAddress",
        "addressLocality",
        "addressRegion",
        "postalCode",
        "addressCountry",
    ]
    values = {name: clean(raw.get(name, "")) for name in fields}
    filled = [name for name, value in values.items() if value]
    if not filled:
        return None
    if len(filled) != len(fields):
        print(
            "WARNING: address is incomplete, so it was omitted from structured data. "
            "Fill streetAddress, addressLocality, addressRegion, postalCode, and addressCountry together.",
            file=sys.stderr,
        )
        return None
    values["@type"] = "PostalAddress"
    return values


def source_link_reason(url: str) -> str:
    lowered = url.lower()
    if any(host in lowered for host in ("github.com", "github.io", "gitlab.com", "bitbucket.org")):
        return "a source repository"
    path = lowered.split("?", 1)[0].split("#", 1)[0]
    if path.endswith(".zip"):
        return "a zip download"
    if "/releases/" in lowered or "releases/download" in lowered:
        return "a release archive"
    return ""


def same_as_from(config: dict) -> list[str]:
    urls = []
    for item in config.get("sameAs") or []:
        url = clean(item) if isinstance(item, str) else ""
        if not url:
            continue
        if not url.startswith("https://"):
            print(f"WARNING: skipped sameAs value that is not an https URL: {url}", file=sys.stderr)
            continue
        reason = source_link_reason(url)
        if reason:
            raise SystemExit(f"sameAs must not point at {reason}: {url}")
        urls.append(url)
    return urls


def enrich(node, extras: dict) -> None:
    if isinstance(node, dict):
        if node.get("@id") == BUSINESS_ID:
            if extras.get("address"):
                node["address"] = extras["address"]
            if extras.get("areaServed"):
                node["areaServed"] = extras["areaServed"]
            if extras.get("legalName"):
                node["legalName"] = extras["legalName"]
            if extras.get("sameAs"):
                node["sameAs"] = extras["sameAs"]
        for value in node.values():
            enrich(value, extras)
    elif isinstance(node, list):
        for item in node:
            enrich(item, extras)


def apply_html(text: str, meta: str, extras: dict) -> str:
    if MARK not in text:
        raise SystemExit("A staged HTML file is missing the verification marker.")
    text = text.replace(f"  {MARK}\n", (meta + "\n") if meta else "")
    text = text.replace(MARK, meta)

    parts = []
    cursor = 0
    token = '<script type="application/ld+json">'
    close = "</script>"
    while True:
        start = text.find(token, cursor)
        if start < 0:
            parts.append(text[cursor:])
            break
        parts.append(text[cursor:start])
        end = text.find(close, start)
        if end < 0:
            raise SystemExit("Unclosed JSON-LD script.")
        raw = text[start + len(token) : end].strip()
        if raw:
            data = json.loads(raw)
            enrich(data, extras)
            rendered = json.dumps(data, indent=2, ensure_ascii=False)
            parts.append(token + "\n" + rendered + "\n  " + close)
        else:
            parts.append(text[start : end + len(close)])
        cursor = end + len(close)
    return "".join(parts)


def write_bing_file(stage: Path, code: str) -> None:
    dest = stage / "BingSiteAuth.xml"
    if dest.exists():
        print("BingSiteAuth.xml is already in the stage; left it in place.")
        return
    xml = (
        '<?xml version="1.0"?>\n'
        "<users>\n"
        f"  <user>{xml_escape(code)}</user>\n"
        "</users>\n"
    )
    dest.write_text(xml, encoding="utf-8")
    print("Wrote BingSiteAuth.xml from bingSiteVerification.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", required=True, help="Directory of staged site files")
    parser.add_argument("--config", default=str(ROOT / "site.config.json"))
    args = parser.parse_args()
    stage = Path(args.stage)
    config = load_config(Path(args.config))
    meta = verification_meta(config)
    extras = {}
    address = address_from(config)
    if address:
        extras["address"] = address
    area = clean(config.get("areaServed", ""))
    if area:
        extras["areaServed"] = area
    legal = clean(config.get("legalName", ""))
    if legal:
        extras["legalName"] = legal
    same_as = same_as_from(config)
    if same_as:
        extras["sameAs"] = same_as

    for path in sorted(stage.glob("*.html")):
        path.write_text(apply_html(path.read_text(encoding="utf-8"), meta, extras), encoding="utf-8")

    bing = clean(config.get("bingSiteVerification", ""))
    if bing:
        write_bing_file(stage, bing)
    print("Applied site.config.json to the staged site.")


if __name__ == "__main__":
    main()
