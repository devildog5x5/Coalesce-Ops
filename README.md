# Coalesce Ops

One practice for joining separate teams, systems, and sites into a single operation.

Open `index.html` locally. The public site is `https://coalesceops.com`.

Rebuild the Hostinger drop with `powershell -File .\build_site_zip.ps1`. Python 3 is required: it checks the menu and stamps `site.config.json`. The zip is named `coalesceops-vX.Y.Z.zip`, with the version taken from `VERSION`. Unzip the result into `public_html` so the files sit at the archive root, with forward-slash paths. Every page ends with one line: Coalesce Ops v1.3.4 · © 2026 Robert Foster · Inquiries Text: 801.319.1061. The live host is only `https://coalesceops.com`.

Do not link to this repository, to source code, or to a release archive from the live site. That rule is in [SOP.md](SOP.md).

**Contact:** Inquiries Text: 801.319.1061.

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
- `sameAs` — public `https://` profile URLs only. A repository, source tree, or release archive is refused.

Coalesce Ops, Robert Foster, and 801.319.1061 are already published. They are not placeholders. Do not publish a support email address.

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
