#!/usr/bin/env python3
"""Build kogany.net into public/ — standard library only, no dependencies.

Each page is an HTML fragment under content/, headed by a metadata comment:

    <!--
    title: Download
    description: How to get Kogany and verify it.
    date: 2026-11-01          (announcements and engineering notes only)
    -->

content/foo.html becomes public/foo/index.html (content/index.html becomes /).
The fragment is wrapped in the shared layout below; static/ is copied as-is;
sitemap.xml and the announcements feed (announcements/atom.xml) are generated.
"""

import html
import re
import shutil
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content"
STATIC = ROOT / "static"
OUT = ROOT / "public"
SITE = "https://kogany.net"
NAME = "Kogany"
REPO = "https://github.com/boyfromcave/kogany"

NAV = [
    ("/vault/", "Vault", "Dashboard"),
    ("/download/", "Download", None),
    ("/snapshots/", "Snapshots", None),
    ("/announcements/", "Announcements", None),
    ("/engineering/", "Engineering", None),
    ("/about/", "About", None),
]
MONTHS = "January February March April May June July August September October November December".split()


def long_date(iso):
    y, m, d = iso.split("-")
    return f"{int(d)} {MONTHS[int(m) - 1]} {y}"

META_RE = re.compile(r"\A\s*<!--(.*?)-->", re.S)


def parse(path):
    text = path.read_text(encoding="utf-8")
    m = META_RE.match(text)
    if not m:
        sys.exit(f"{path}: missing metadata comment")
    meta = {}
    for line in m.group(1).strip().splitlines():
        key, _, value = line.partition(":")
        meta[key.strip()] = value.strip()
    for key in ("title", "description"):
        if key not in meta:
            sys.exit(f"{path}: metadata needs {key}")
    return meta, text[m.end():].strip()


def url_for(path):
    rel = path.relative_to(CONTENT).with_suffix("")
    parts = rel.parts
    if parts[-1] == "index":
        parts = parts[:-1]
    return "/" + "".join(p + "/" for p in parts)


def mark(cls):
    return f'<svg class="{cls}" viewBox="0 0 64 64" aria-hidden="true" focusable="false"><use href="/assets/kogany-mark.svg#mark"/></svg>'


def layout(meta, body, url):
    title = meta["title"] if url == "/" else f'{meta["title"]} · {NAME}'
    desc = html.escape(meta["description"], quote=True)
    nav = []
    for href, label, tag in NAV:
        current = ' aria-current="page"' if url.startswith(href) else ""
        cls = ' class="nav-dash"' if tag else ""
        extra = f'<span class="nav-tag">{tag}</span>' if tag else ""
        nav.append(f'<a href="{href}"{cls}{current}><span>{label}</span>{extra}</a>')
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<script src="/assets/site.js"></script>
<title>{html.escape(title)}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{SITE}{url}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{NAME}">
<meta property="og:title" content="{html.escape(title, quote=True)}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{SITE}{url}">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="alternate" type="application/atom+xml" title="{NAME} announcements" href="/announcements/atom.xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Outfit:wght@600&family=IBM+Plex+Mono:wght@400;500;600&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,500;0,8..60,600;1,8..60,400&display=swap">
<link rel="stylesheet" href="/assets/site.css">
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header">
  <div class="container">
    <a class="home-link" href="/">{mark("logo")}<span class="wordmark">kogany</span></a>
    <button class="nav-toggle" type="button" aria-controls="site-nav" aria-expanded="false" aria-label="Menu" data-nav-toggle hidden>
      <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>
    </button>
    <nav class="site-nav" id="site-nav" aria-label="Site">{"".join(nav)}</nav>
  </div>
</header>
<main id="main">
{body}
</main>
<footer class="site-footer">
  <div class="container">
    <a href="{REPO}" rel="noopener"><svg viewBox="0 0 16 16" width="16" height="16" fill="currentColor" aria-hidden="true"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38v-1.49c-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82a7.6 7.6 0 0 1 4 0c1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48v2.2c0 .21.15.46.55.38A8.01 8.01 0 0 0 16 8c0-4.42-3.58-8-8-8z"/></svg><span>boyfromcave/kogany</span></a>
    <a href="https://y.cash/" rel="noopener"><img src="/assets/ycash-logo.svg" alt="" width="16" height="16"><span>ycash</span></a>
    <div class="trailer">
      {mark("colophon")}
      <button class="theme-toggle" type="button" aria-label="Switch theme" data-theme-toggle hidden>
        <svg class="moon" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>
        <svg class="sun" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>
      </button>
    </div>
  </div>
</footer>
</body>
</html>
"""


def post_list(section, pages):
    items = sorted((p for p in pages if p["url"].startswith(f"/{section}/") and p["url"] != f"/{section}/"),
                   key=lambda p: p["meta"].get("date", ""), reverse=True)
    out = ['<ol class="post-list">']
    for p in items:
        out.append(f'<li><time datetime="{p["meta"]["date"]}">{long_date(p["meta"]["date"])}</time>'
                   f'<a href="{p["url"]}">{html.escape(p["meta"]["title"])}</a>'
                   f'<p>{html.escape(p["meta"]["description"])}</p></li>')
    out.append("</ol>")
    return "\n".join(out), items


def atom(items):
    updated = max((p["meta"]["date"] for p in items), default=date.today().isoformat())
    entries = "".join(
        f"""
  <entry>
    <title>{html.escape(p["meta"]["title"])}</title>
    <link href="{SITE}{p["url"]}"/>
    <id>{SITE}{p["url"]}</id>
    <updated>{p["meta"]["date"]}T00:00:00Z</updated>
    <summary>{html.escape(p["meta"]["description"])}</summary>
  </entry>""" for p in items)
    return f"""<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>{NAME} announcements</title>
  <link href="{SITE}/announcements/"/>
  <link rel="self" href="{SITE}/announcements/atom.xml"/>
  <id>{SITE}/announcements/</id>
  <updated>{updated}T00:00:00Z</updated>
  <author><name>The Ycash developers</name></author>{entries}
</feed>
"""


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(STATIC, OUT)
    pages = []
    for path in sorted(CONTENT.rglob("*.html")):
        meta, body = parse(path)
        pages.append({"path": path, "url": url_for(path), "meta": meta, "body": body})

    for p in pages:
        body = p["body"]
        for section in ("announcements", "engineering"):
            if "{{ " + section + " }}" in body:
                listing, items = post_list(section, pages)
                body = body.replace("{{ " + section + " }}", listing)
                if section == "announcements":
                    (OUT / "announcements").mkdir(parents=True, exist_ok=True)
                    (OUT / "announcements" / "atom.xml").write_text(atom(items), encoding="utf-8")
        if p["url"].count("/") > 2 and "date" in p["meta"]:
            back = "/" + p["url"].split("/")[1] + "/"
            banner = ""
            if "banner" in p["meta"]:
                big, _, small = p["meta"]["banner"].partition("|")
                banner = (f'<div class="banner" aria-hidden="true">{mark("banner-mark")}'
                          f'<div class="v">{html.escape(big.strip())}<small>{html.escape(small.strip())}</small></div></div>')
            body = (f'<div class="container"><article class="post prose"><p class="eyebrow">'
                    f'<time datetime="{p["meta"]["date"]}">{long_date(p["meta"]["date"])}</time></p>'
                    f'<h1>{html.escape(p["meta"]["title"])}</h1>\n{banner}{body}\n</article></div>')
        dest = OUT / p["url"].lstrip("/") / "index.html"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(layout(p["meta"], body, p["url"]), encoding="utf-8")

    notfound = OUT / "404" / "index.html"
    if notfound.exists():
        notfound.rename(OUT / "404.html")
        notfound.parent.rmdir()

    urls = "".join(f"\n  <url><loc>{SITE}{p['url']}</loc></url>" for p in pages if p["url"] != "/404/")
    (OUT / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}\n</urlset>\n',
        encoding="utf-8")
    print(f"built {len(pages)} pages into {OUT.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
