#!/usr/bin/env python3
"""Fail the build if the menu, SEO tags, or internal links drift."""

from __future__ import annotations

import json
import re
import struct
import sys
from pathlib import Path

from sync_nav import END, START, ROOT, load_nav, render_block

REQUIRED_SERVICES = [
    "Operating picture",
    "Ownership",
    "Cadence",
    "Systems",
    "Sites",
    "Transition",
    "Security and compliance",
    "Infrastructure assessment",
    "SaaS governance and vendor cost",
    "AI on the work",
    "IT strategy and governance",
]
PAGE_SERVICE = {
    "secops-consulting.html": "Security and compliance",
    "infrastructure-assessment.html": "Infrastructure assessment",
    "cloud-cost-reliability.html": "SaaS governance and vendor cost",
}
ARTICLE_PAGES = {
    "incident-response-readiness.html",
    "fractional-devops-sre.html",
}
ORIGIN = "https://coalesceops.com"


def fail(errors: list[str]) -> None:
    print("\n".join(errors), file=sys.stderr)
    raise SystemExit(1)


def png_size(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{path.name} is not a PNG")
    return struct.unpack(">II", data[16:24])


def meta(html: str, name: str) -> str:
    match = re.search(
        rf'<meta[^>]+(?:name|property)="{re.escape(name)}"[^>]+content="([^"]*)"',
        html,
    )
    if match:
        return match.group(1)
    match = re.search(
        rf'<meta[^>]+content="([^"]*)"[^>]+(?:name|property)="{re.escape(name)}"',
        html,
    )
    return match.group(1) if match else ""


def json_ld_blocks(html: str) -> list:
    blocks = []
    for raw in re.findall(
        r'<script type="application/ld\+json">\s*(.*?)\s*</script>',
        html,
        flags=re.S,
    ):
        blocks.append(json.loads(raw))
    return blocks


def walk(node):
    if isinstance(node, dict):
        yield node
        for value in node.values():
            yield from walk(value)
    elif isinstance(node, list):
        for item in node:
            yield from walk(item)


def ids_in(html: str) -> set[str]:
    return set(re.findall(r'\sid="([^"]+)"', html))


def page_file(href: str) -> str:
    path = href.split("#", 1)[0]
    if path in ("", "/", "index.html"):
        return "index.html"
    return path


def source_leaks(text: str, label: str) -> list[str]:
    found = []
    lowered = text.lower()
    for needle in ("github.com", "github.io", "gitlab.com", "bitbucket.org", "releases/download", "source code"):
        if needle in lowered:
            found.append(f"{label} mentions {needle}")
    for href in re.findall(r'(?:href|src)\s*=\s*["\']([^"\']+)', text, flags=re.I):
        target = href.lower().split("#", 1)[0].split("?", 1)[0]
        if target.endswith(".zip") or "/releases/" in href.lower():
            found.append(f"{label} links to a release or zip: {href}")
    return found


def main() -> None:
    errors = []
    nav = load_nav()
    expected_nav = render_block()
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    config = json.loads((ROOT / "site.config.json").read_text(encoding="utf-8"))
    key = config["indexNowKey"].strip()
    key_path = ROOT / f"{key}.txt"
    if not key_path.is_file() or key_path.read_text(encoding="utf-8").strip() != key:
        errors.append(f"IndexNow key file {key}.txt is missing or does not match site.config.json")

    pages = {path.name: path.read_text(encoding="utf-8") for path in sorted(ROOT.glob("*.html"))}
    if "404.html" not in pages or "index.html" not in pages:
        errors.append("index.html and 404.html are required")

    public = []
    for item in nav["items"]:
        public.append(item["href"])
        for section in item.get("sections") or []:
            href = section["href"]
            if "#" not in href:
                errors.append(f"Section link has no id: {href}")
                continue
            filename, anchor = href.split("#", 1)
            filename = page_file(filename if filename else "/")
            if filename not in pages:
                errors.append(f"Menu points at missing page {filename}")
                continue
            if anchor not in ids_in(pages[filename]):
                errors.append(f"Missing section id #{anchor} on {filename}")

    linked_pages = {page_file(item["href"]) for item in nav["items"]}
    for name in pages:
        if name == "404.html":
            continue
        if name not in linked_pages:
            errors.append(f"{name} is a public page and is not in the main menu")

    titles = {}
    descriptions = {}
    for name, html in pages.items():
        if START not in html or END not in html:
            errors.append(f"{name} is missing the site-nav markers")
        else:
            block = html[html.index(START) : html.index(END) + len(END)]
            if block != expected_nav:
                errors.append(f"{name} menu does not match includes/nav.json. Run python3 sync_nav.py")
        title = re.search(r"<title>(.*?)</title>", html, re.S)
        title_text = re.sub(r"\s+", " ", title.group(1)).strip() if title else ""
        if not title_text:
            errors.append(f"{name} is missing a title")
        elif title_text in titles:
            errors.append(f"Duplicate title on {name} and {titles[title_text]}")
        else:
            titles[title_text] = name
            if not 40 <= len(title_text) <= 60:
                errors.append(f"{name} title is {len(title_text)} characters; aim for 40–60")
        description = meta(html, "description")
        if not description:
            errors.append(f"{name} is missing a meta description")
        elif description in descriptions:
            errors.append(f"Duplicate meta description on {name} and {descriptions[description]}")
        else:
            descriptions[description] = name
            if not 120 <= len(description) <= 160:
                errors.append(f"{name} meta description is {len(description)} characters; aim for 120–160")
        canonical = re.search(r'<link rel="canonical" href="([^"]+)"', html)
        canonical_href = canonical.group(1) if canonical else ""
        expected_canonical = ORIGIN + "/" if name == "index.html" else f"{ORIGIN}/{name}"
        if canonical_href != expected_canonical:
            errors.append(f"{name} canonical is {canonical_href or 'missing'}")
        for prop in (
            "og:title",
            "og:description",
            "og:url",
            "og:image",
            "og:image:width",
            "og:image:height",
            "og:image:alt",
            "twitter:card",
            "twitter:title",
            "twitter:description",
            "twitter:image",
            "twitter:image:alt",
        ):
            if not meta(html, prop):
                errors.append(f"{name} is missing {prop}")
        if meta(html, "og:image:width") not in ("", "1200"):
            errors.append(f"{name} og:image:width is not 1200")
        if meta(html, "og:image:height") not in ("", "630"):
            errors.append(f"{name} og:image:height is not 630")
        if meta(html, "og:url") != canonical_href:
            errors.append(f"{name} og:url does not match canonical")
        if meta(html, "twitter:card") not in ("", "summary_large_image"):
            errors.append(f"{name} twitter:card is not summary_large_image")
        for needle in (
            'rel="manifest"',
            "assets/favicon.svg",
            "assets/favicon-32.png",
            "assets/apple-touch-icon.png",
            "assets/site.css?v=" + version,
            "assets/site.js?v=" + version,
            f"Coalesce Ops v{version}",
            "<!-- site-config:verification -->",
        ):
            if needle not in html:
                errors.append(f"{name} is missing {needle}")
        if name == "404.html":
            if meta(html, "robots") != "noindex":
                errors.append("404.html must be noindex")
        elif "noindex" in meta(html, "robots"):
            errors.append(f"{name} is noindex")
        if "PLACEHOLDER" in html:
            errors.append(f"{name} contains a PLACEHOLDER value")
        if re.search(r"starting at|\$\s?\d", html, re.I):
            errors.append(f"{name} publishes a price. This site has no price list.")
        errors.extend(source_leaks(html, name))
        main = re.search(r"<main\b.*</main>", html, re.S)
        words = re.findall(r"[A-Za-z0-9']+", re.sub(r"<[^>]+>", " ", main.group(0) if main else ""))
        minimum = {
            "contact.html": 400,
            "method.html": 400,
            "services.html": 450,
            "engagements.html": 450,
            "faq.html": 450,
            "index.html": 600,
        }.get(name)
        if minimum and len(words) < minimum:
            errors.append(f"{name} main copy is {len(words)} words; it needs at least {minimum} to be worth indexing")
        headings = [int(level) for level in re.findall(r"<h([1-6])\b", html)]
        if headings.count(1) != 1:
            errors.append(f"{name} should have exactly one h1, found {headings.count(1)}")
        previous = 0
        for level in headings:
            if previous and level > previous + 1:
                errors.append(f"{name} heading jumps from h{previous} to h{level}")
                break
            previous = level
        for image in re.findall(r"<img\b[^>]*>", html):
            alt = re.search(r'\balt="([^"]*)"', image)
            if not alt or not alt.group(1).strip():
                errors.append(f"{name} has an image without descriptive alt text")
            elif "favicon.svg" in image and alt.group(1) != "Coalesce Ops logo":
                errors.append(f"{name} logo alt is {alt.group(1)!r}")
        for href in re.findall(r'href="([^"]+)"', html):
            if href.startswith(("mailto:", "tel:", "https://", "http://", "#")):
                continue
            path_part, _, anchor = href.partition("#")
            if path_part.startswith("/"):
                path_part = path_part[1:]
            path_part = page_file(path_part if path_part else "/")
            target = ROOT / path_part
            if path_part.endswith(".html") and not target.is_file():
                errors.append(f"{name} links to missing {href}")
            elif anchor and target.is_file() and anchor not in ids_in(target.read_text(encoding="utf-8")):
                errors.append(f"{name} links to missing #{anchor} on {path_part}")
        blocks = []
        try:
            blocks = json_ld_blocks(html)
        except json.JSONDecodeError as exc:
            errors.append(f"{name} has invalid JSON-LD: {exc}")
        for block in blocks:
            dumped = json.dumps(block)
            if "aggregateRating" in dumped or '"@type": "Review"' in dumped or "reviewCount" in dumped:
                errors.append(f"{name} JSON-LD includes a review or rating")
        nodes = [node for block in blocks for node in walk(block)]
        types = []
        for node in nodes:
            same_as = node.get("sameAs") or []
            if isinstance(same_as, str):
                same_as = [same_as]
            for url in same_as:
                if isinstance(url, str):
                    errors.extend(source_leaks(url, f"{name} sameAs"))
            kind = node.get("@type")
            if isinstance(kind, list):
                types.extend(kind)
            elif kind:
                types.append(kind)
        if "ProfessionalService" not in types and "Organization" not in types:
            errors.append(f"{name} JSON-LD needs ProfessionalService or Organization")
        if "WebSite" not in types:
            errors.append(f"{name} JSON-LD needs WebSite")
        service_names = [
            node.get("name")
            for node in nodes
            if node.get("@type") == "Service" or (
                isinstance(node.get("@type"), list) and "Service" in node["@type"]
            )
        ]
        if name in ("index.html", "services.html"):
            for service_name in REQUIRED_SERVICES:
                if service_name not in service_names:
                    errors.append(f"{name} is missing Service JSON-LD for {service_name}")
        if name in PAGE_SERVICE and PAGE_SERVICE[name] not in service_names:
            errors.append(f"{name} is missing its Service JSON-LD")
        if name in ARTICLE_PAGES:
            if "Article" not in types:
                errors.append(f"{name} is missing Article JSON-LD")
            if any("Fractional" in (service or "") for service in service_names):
                errors.append(f"{name} must not claim a fractional-hire Service")

    robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
    if f"Sitemap: {ORIGIN}/sitemap.xml" not in robots:
        errors.append("robots.txt does not point at the sitemap")
    sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    locs = re.findall(r"<loc>\s*([^<]+?)\s*</loc>", sitemap)
    expected_locs = [ORIGIN + "/"]
    for href in linked_pages:
        if href == "index.html":
            continue
        expected_locs.append(f"{ORIGIN}/{href}")
    if sorted(locs) != sorted(expected_locs):
        errors.append(f"sitemap locs {locs} do not match public pages {expected_locs}")
    if "404.html" in sitemap:
        errors.append("sitemap includes 404.html")
    errors.extend(source_leaks(sitemap, "sitemap.xml"))
    errors.extend(source_leaks(json.dumps(nav), "includes/nav.json"))
    for url in config.get("sameAs") or []:
        if isinstance(url, str):
            errors.extend(source_leaks(url, "site.config.json sameAs"))

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for url in re.findall(r"https?://[^\s)>]+", readme):
        errors.extend(source_leaks(url, "README"))

    htaccess = (ROOT / ".htaccess").read_text(encoding="utf-8")
    denied = set()
    for group in re.findall(r"\(\?i\)\\\.\(([^)]+)\)", htaccess):
        denied.update(group.split("|"))
    for extension in ("zip", "ps1", "py", "json", "md", "sh"):
        if extension not in denied:
            errors.append(f".htaccess does not deny *.{extension}")
    for needle in ("Require all denied", "Deny from all", ".git", "includes", "installers"):
        if needle not in htaccess:
            errors.append(f".htaccess is missing {needle}")
    for needle in (
        "https://coalesceops.com",
        "www\\.coalesceops\\.com",
        "index\\.(html|php)",
        "X-Forwarded-Proto",
        "BROTLI_COMPRESS",
        "max-age=2592000",
    ):
        if needle not in htaccess:
            errors.append(f".htaccess is missing the canonical-host or cache rule {needle}")
    if "faq.html" in pages:
        faq_blocks = json_ld_blocks(pages["faq.html"])
        faq_types = []
        for block in faq_blocks:
            for node in walk(block):
                kind = node.get("@type")
                if isinstance(kind, list):
                    faq_types.extend(kind)
                elif kind:
                    faq_types.append(kind)
        if "FAQPage" not in faq_types:
            errors.append("faq.html is missing FAQPage JSON-LD")

    manifest = json.loads((ROOT / "site.webmanifest").read_text(encoding="utf-8"))
    if manifest.get("name") != "Coalesce Ops":
        errors.append("manifest name is wrong")
    width, height = png_size(ROOT / "assets" / "og.png")
    if (width, height) != (1200, 630):
        errors.append(f"og.png is {width}x{height}, expected 1200x630")
    for filename, size in (
        ("favicon-32.png", (32, 32)),
        ("apple-touch-icon.png", (180, 180)),
        ("icon-192.png", (192, 192)),
        ("icon-512.png", (512, 512)),
    ):
        actual = png_size(ROOT / "assets" / filename)
        if actual != size:
            errors.append(f"{filename} is {actual[0]}x{actual[1]}")

    if errors:
        fail(errors)
    print(f"Site check passed ({len(pages)} pages, v{version}).")


if __name__ == "__main__":
    main()
