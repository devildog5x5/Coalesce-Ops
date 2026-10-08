# Coalesce Ops — SOP

## Main menu

Permanent standard from Robert Foster:

Every page shows the same main menu. That menu links to all of the site's pages and to their sections. There are no dead ends. A new service page gets that same header menu. It is not published with a shorter menu, and it is not left out of the menu.

The menu is in the HTML. It is not injected by script, so it is there when the page is read, indexed, or opened without JavaScript. The same links stay in the header at every width. Section lists open from the control beside each page. Nothing in the menu depends on a hover.

What to do when a page or a section is added:

1. Give the section a stable `id` on the page.
2. Add the page, and each section, to `includes/nav.json`.
3. Run `python3 sync_nav.py`. That writes the same menu into every HTML page, including the 404 page.
4. Run `python3 check_site.py`. The zip build runs that check and stops if it fails.

The 404 page shows the same menu. It is not a destination in the menu.

Do not ship a page whose menu is a subset of the others. Do not add a public page that the menu does not link to.

The footer repeats the page links. The header menu is the one that must list every page and every section in `includes/nav.json`.

Every page ends with the same compact line, under those links: `Coalesce Ops vX.Y.Z · © 2026 Robert Foster · rmf@coalesceops.com`. The email is a mailto link. The version is the text in `VERSION`. The phone number stays as a link in the footer and on the contact page.

## Search engines

The public site is only `https://coalesceops.com`. `www`, plain `http`, `/index.html`, `/index.php`, and a trailing slash on a file all redirect to that host. The home page is linked as `/`, because `/index.html` is an alternate of the canonical URL.

`site.config.json` holds the verification tokens and the business details that are not already printed on the site. `PLACEHOLDER` and blank optional fields are left out of the pages. Do not invent an address, a service area, reviews, or ratings. Phone, email, and the founder's name stay as they are published.

After a real value is filled in, rebuild the Hostinger drop with `powershell -File .\build_site_zip.ps1` and upload that.

How to submit pages to IndexNow, and how to paste Google and Bing verification, is in the README.

## Source code and release archives

Never link to or serve source code or release zips from a live site.

The public pages, the menu, the footer, the sitemap, and structured data do not point at a repository, a source tree, or a release archive. The Hostinger drop contains only the public site. It does not contain archives, build scripts, `.git`, source-only folders, or operator documents. `.htaccess` denies those kinds of files if they are uploaded by mistake.
