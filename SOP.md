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

## Search engines

The public site is `https://coalesceops.com`.

`site.config.json` holds the verification tokens and the business details that are not already printed on the site. `PLACEHOLDER` and blank optional fields are left out of the pages. Do not invent an address, a service area, reviews, or ratings. Phone, email, and the founder's name stay as they are published.

After a real value is filled in, rebuild the Hostinger zip with `powershell -File .\build_site_zip.ps1` and upload that.

How to submit pages to IndexNow, and how to paste Google and Bing verification, is in the README.
