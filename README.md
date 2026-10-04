# Coalesce Ops

One practice for joining separate teams, systems, and sites into a single operation.

Open `index.html` locally, or unzip the zip into Hostinger `public_html`.

**Hostinger zip:** `CoalesceOps-1.2.0.zip` — unzip into `public_html` (files at the zip root, forward-slash paths). Rebuild with `powershell -File .\build_site_zip.ps1` (filename includes the version from `VERSION`). The build also needs Python 3, which checks the menu and stamps `site.config.json`. Footer on every page: Coalesce Ops v1.2.0.

Repo: [devildog5x5/Coalesce-Ops](https://github.com/devildog5x5/Coalesce-Ops)

**Contact:** rmf@coalesceops.com · 801.319.1061

The public site is `https://coalesceops.com`.

## Main menu

Every page uses the same header menu, and that menu links to every public page and section. The list lives in `includes/nav.json`. After a change, run `python3 sync_nav.py`. The rule is in [SOP.md](SOP.md).

## Search engines

- Sitemap: https://coalesceops.com/sitemap.xml
- Robots: https://coalesceops.com/robots.txt

### Google Search Console and Bing

Paste a code into `site.config.json`, then rebuild the zip. Paste the token only, not the whole tag. `PLACEHOLDER` is omitted.

| Field | What to paste |
|---|---|
| `googleSiteVerification` | The `content` value from Google's HTML tag method |
| `bingSiteVerification` | The `content` value from Bing's `msvalidate.01` tag |

File placement works without editing a page. Put Google's HTML file in the site root, next to `index.html`. Put `BingSiteAuth.xml` in the site root. The zip copies both. If `BingSiteAuth.xml` is not already there and `bingSiteVerification` is set, the build writes that file.

### Details that are not on the site yet

Leave these as `PLACEHOLDER` until they are real and public. Do not invent them.

- `address` — fill `streetAddress`, `addressLocality`, `addressRegion`, `postalCode`, and `addressCountry` together, or leave them all blank
- `legalName` — only if the legal name is different from Coalesce Ops
- `areaServed` — only if a service area should be published
- `sameAs` — `https://` profile URLs only

Coalesce Ops, Robert Foster, rmf@coalesceops.com, and 801.319.1061 are already published. They are not placeholders.

### IndexNow

The key file is https://coalesceops.com/3adb4c7af657a417648edbc4bdf85574.txt and the key is `3adb4c7af657a417648edbc4bdf85574`.

After that URL returns the key, submit every page in the sitemap:

```
powershell -File .\ping_indexnow.ps1 -DryRun
powershell -File .\ping_indexnow.ps1
```

`-DryRun` prints the request and does not send it. The live run posts the sitemap URLs to `https://api.indexnow.org/indexnow`.

One page from a shell:

```
curl "https://api.indexnow.org/indexnow?url=https://coalesceops.com/&key=3adb4c7af657a417648edbc4bdf85574"
```

Copyright © 2026 Robert Foster · Coalesce Ops. All rights reserved.
