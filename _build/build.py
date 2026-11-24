#!/usr/bin/env python3
"""Rebuilds index.html, roster.html and releases.html from releases.json.

Run:  python3 _build/build.py   (from the 477-site folder)
Covers live in assets/r/<apple collection id>.jpg, artist photos in assets/.
"""
import datetime
import html
import json
import os
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TODAY = datetime.date.today().isoformat()

ARTISTS = [
    dict(slug="two-feet", name="Two Feet", match="two feet", img="twofeet.jpg",
         spotify="https://open.spotify.com/artist/5sWHDYs0csV6RS48xBl0tH"),
    dict(slug="michele-morrone", name="Michele Morrone", match="michele morrone", img="morrone.jpg",
         spotify="https://open.spotify.com/artist/03fLoIOO015incUitpfkad"),
    dict(slug="brothel", name="Brothel", match="brothel", img="brothel.jpg",
         spotify="https://open.spotify.com/artist/3xYvvJ6tjXyJJdEXBs8qf0"),
    dict(slug="bec-lauder-and-the-noise", name="Bec Lauder and the Noise", match="bec lauder", img="bec.jpg",
         spotify="https://open.spotify.com/artist/5Wl79QF98JiagVPHNOl8g6"),
    dict(slug="toby-mai", name="Toby Mai", match="toby mai", img="tobymai.jpg",
         spotify="https://open.spotify.com/artist/71XRExAcKFmzM0fckCrCvo"),
    dict(slug="wntrbrk", name="WNTRBRK", match="wntrbrk", img="wntrbrk.jpg",
         spotify="https://open.spotify.com/artist/75trH1P5A8F6DZV4gB2SDN"),
]
# extra filter names on the releases page (artists with a release but no roster entry)
EXTRA_FILTERS = []

# short roster bios (WNTRBRK's is his own press bio; the rest are written from public sources)
BIOS = {
    "two-feet": "Two Feet is New York singer, guitarist and producer Bill Dess. \u201cGo Fuck Yourself\u201d and \u201cI Feel Like I\u2019m Drowning\u201d are both certified Gold, and the latter reached No. 1 on Billboard\u2019s Alternative Songs chart in 2018. He founded 477 Records.",
    "michele-morrone": "Michele Morrone is an Italian actor and singer-songwriter from Bitonto, known worldwide for 365 Days. His albums are Dark Room (2020) and Double (2023). He signed to 477 Records in 2024.",
    "brothel": "Brothel is an electronic producer who has been releasing music since 2016. He is known for \u201cTimmy Turner\u201d, \u201cSlide\u201d with barnacle boi, and a long run of collaborations with Sidewalks and Skeletons.",
    "bec-lauder-and-the-noise": "Bec Lauder and the Noise are a New York glam-punk trio: Bec Lauder on vocals and guitar, Maggie Bishop on drums and Soph Shreds on guitar. Their 477 releases include \u201cHard To Get\u201d, \u201cMore Than Chemical\u201d and the EP Before Everything Changes.",
    "toby-mai": "Toby Mai is a producer and singer-songwriter who blends R&B and electronic music with jazz progressions and bass-heavy production. His 477 releases run from \u201cCities\u201d with Two Feet through \u201c19\u201d.",
    "wntrbrk": "WNTRBRK is a Paterson, New Jersey artist building a raw, emotionally charged world where alternative music, R&B, hip-hop, and rock influences collide. Known for guitar-driven performances and an intimate, unfiltered approach to songwriting, his music moves between vulnerable, melodic moments and intense, mosh-pit energy.",
}

# LIVE=1 python3 _build/build.py  -> build for www.477records.com (indexable, canonical links, CNAME file).
# Without it the build is the hidden preview at 477records.github.io/site.
LIVE = os.environ.get("LIVE") == "1"
DOMAIN = "www.477records.com"
SITE = f"https://{DOMAIN}/"
INSTAGRAM = "https://www.instagram.com/official477records/"
ABOUT = [
    "477 Records is a New York-based independent record label.",
    "Founded by Two Feet, a platinum-and-gold-certified musician and producer, in 2024, 477 Records grew out of his experience as an independent artist.",
    "We find, sign, and develop independent artists and help them develop their sound. We offer the reach and services of a major label while staying independent.",
]
PAGES = []   # every indexable page, for sitemap.xml


def url_of(name):
    return SITE + ("" if name == "index.html" else name)


def ROBOTS(name, index=True):
    if not LIVE or not index:
        return '<meta name="robots" content="noindex">'
    return f'<link rel="canonical" href="{url_of(name)}">'


def jsonld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False).replace("</", "<\\/") + "</script>"


LABEL = {
    "@type": "Organization", "@id": SITE + "#label", "name": "477 Records", "url": SITE,
    "logo": SITE + "assets/icon-180.png", "email": "gd@477records.com",
    "description": " ".join(ABOUT),
    "address": {"@type": "PostalAddress", "addressLocality": "New York", "addressRegion": "NY", "addressCountry": "US"},
    "founder": {"@type": "MusicGroup", "name": "Two Feet", "url": SITE + "two-feet.html"},
    "sameAs": [INSTAGRAM],
}


e = html.escape
import hashlib
CSS_V = hashlib.md5(open(os.path.join(ROOT, "assets", "site.css"), "rb").read()).hexdigest()[:8]
releases = json.load(open(os.path.join(HERE, "releases.json")))
releases.sort(key=lambda r: r["date"], reverse=True)


def tags(r):
    hay = (r["artist"] + " " + r["title"]).lower()
    return [a["slug"] for a in ARTISTS + EXTRA_FILTERS if a["match"] in hay]


def nice_date(r):
    d = datetime.date.fromisoformat(r["date"])
    if r["date"] > TODAY:
        return '<span class="soon">Out ' + d.strftime("%b %-d") + "</span>"
    return d.strftime("%b %Y")


def page(name, title, desc, body, current="", image="assets/og.jpg", ld=None, index=True, base=""):
    if index:
        PAGES.append(name)
    def nav(href, label):
        cur = ' aria-current="page"' if href == current else ""
        return f'<a href="{href}"{cur}>{label}</a>'
    doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
{f'<base href="{base}">' if base else ""}
<meta property="og:site_name" content="477 Records">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{url_of(name)}">
<meta property="og:image" content="{SITE}{image}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#edf0eb">
{ROBOTS(name, index)}
{jsonld(ld) if ld else ""}
<link rel="icon" type="image/png" href="assets/favicon.png">
<link rel="apple-touch-icon" href="assets/icon-180.png">
<link rel="stylesheet" href="assets/site.css?v={CSS_V}">
</head>
<body>
<header class="top">
  <a class="home" href="./">477 Records</a>
  <nav aria-label="Pages">
    {nav("roster.html", "Roster")}
    {nav("releases.html", "Releases")}
    <a href="./#contact">Contact</a>
  </nav>
  <button class="menu-btn" type="button" aria-expanded="false" aria-controls="menu" aria-label="Open menu"><span></span><span></span><span></span></button>
</header>
<div class="menu" id="menu" hidden>
  <div class="menu-top"><a class="home" href="./">477 Records</a><button class="menu-close" type="button" aria-label="Close menu">&times;</button></div>
  <nav aria-label="Menu">
    <a href="./">Home</a>
    <a href="roster.html">Roster</a>
    <a href="releases.html">Releases</a>
    <a href="./#contact">Contact</a>
  </nav>
  <div class="menu-foot">
    <a href="mailto:gd@477records.com">gd@477records.com</a>
    <img src="assets/wordmark.svg?v=2" width="3790" height="1870" alt="">
  </div>
</div>
<script>
(function () {{
  var m = document.getElementById('menu'), b = document.querySelector('.menu-btn');
  function set(open) {{ m.hidden = !open; b.setAttribute('aria-expanded', open); document.documentElement.classList.toggle('menu-open', open); }}
  b.addEventListener('click', function () {{ set(true); }});
  m.querySelector('.menu-close').addEventListener('click', function () {{ set(false); }});
  m.addEventListener('click', function (ev) {{ if (ev.target.closest('a')) set(false); }});
  addEventListener('keydown', function (ev) {{ if (ev.key === 'Escape') set(false); }});
}})();
</script>
{body}
<footer class="foot pad">
  <section class="about" aria-labelledby="about-h">
    <h2 id="about-h">About</h2>
    <div>
{"".join(f"      <p>{e(t)}</p>" + chr(10) for t in ABOUT).rstrip()}
    </div>
  </section>
  <div class="foot-row">
    <span>© 2026 477 Records</span>
    <span class="foot-links"><a href="{INSTAGRAM}" target="_blank" rel="noopener">Instagram</a><a href="privacy.html">Privacy</a><a href="mailto:gd@477records.com">gd@477records.com</a></span>
  </div>
</footer>
</body>
</html>
"""
    open(os.path.join(ROOT, name), "w").write(doc)


LINKS_P = os.path.join(HERE, "links.json")   # {apple id: {"spotify": url, "youtube": url}}
LINKS = json.load(open(LINKS_P)) if os.path.exists(LINKS_P) else {}


def listen(r):
    """Spotify / Apple Music / YouTube links for one release. Falls back to a search link once it is out."""
    got = LINKS.get(str(r["id"]), {})
    out_now = r["date"] <= TODAY
    q = urllib.parse.quote(r["artist"].split(",")[0].split("&")[0].strip() + " " + r["title"])
    sp = got.get("spotify") or (out_now and "https://open.spotify.com/search/" + q)
    yt = got.get("youtube") or (out_now and "https://www.youtube.com/results?search_query=" + q)
    return [(n, u) for n, u in (("Spotify", sp), ("Apple Music", r["apple"]), ("YouTube", yt)) if u]


def short(n):
    return n.replace(" Music", '<span class="lg"> Music</span>')


def cover_li(r, eager=False):
    load = "" if eager else ' loading="lazy"'
    ls = listen(r)
    where = "".join(f'<a href="{e(u)}" target="_blank" rel="noopener" aria-label="{e(r["title"])} on {n}">{short(n)}</a>' for n, u in ls)
    return (f'<li data-tags="{" ".join(tags(r))}"><a class="art" href="{e(ls[0][1])}" target="_blank" rel="noopener">'
            f'<span class="pic"><img src="assets/r/{r["id"]}.jpg" width="500" height="500" alt="{e(r["title"])} by {e(r["artist"])}, cover art"{load}></span>'
            f'<span class="t">{e(r["title"])}</span><span class="s">{e(r["artist"])}</span>'
            f'<span class="d">{nice_date(r)}</span></a><span class="listen">{where}</span></li>')


# ---------- home ----------
people = "\n".join(
    f'      <li><a href="{a["slug"]}.html"><span class="pic"><img src="assets/{a["img"]}" width="640" height="800" '
    f'alt="{e(a["name"])}" loading="lazy"></span><span class="t">{e(a["name"])}</span></a></li>'
    for a in ARTISTS)
latest = "\n".join("      " + cover_li(r) for r in releases[:8])
page("index.html", "477 Records | Independent record label, New York",
     "477 Records is a New York-based independent record label. Home of Two Feet, Michele Morrone, Brothel, Bec Lauder and the Noise, Toby Mai and WNTRBRK.",
     f"""<main class="home">
  <section class="hero pad">
    <figure class="lockup">
      <img class="tape" src="assets/eyes.webp" width="1294" height="342" alt="">
      <img class="mark" src="assets/wordmark.svg?v=2" width="3790" height="1870" alt="477 Records">
    </figure>
    <div class="pitch">
      <h1>477 Records is a New York&#8209;based independent record label.</h1>
    </div>
  </section>
  <script>
  (function () {{
    /* keep the description's last line on the baseline of "Records" (the wordmark has 200/1870 of space under it) */
    var mark = document.querySelector('.lockup .mark'), h = document.querySelector('.pitch h1');
    function fit() {{
      if (getComputedStyle(h.parentNode).justifySelf !== 'end') {{ h.style.paddingBottom = ''; return; }}
      var f = parseFloat(getComputedStyle(h).fontSize);
      h.style.paddingBottom = Math.max(0, mark.getBoundingClientRect().height * 200 / 1870 - .255 * f) + 'px';
    }}
    addEventListener('resize', fit); if (mark.complete) fit(); else mark.addEventListener('load', fit);
  }})();
  </script>

  <section class="sec pad">
    <div class="sec-head"><h2>Roster</h2><a class="under" href="roster.html">View the roster</a></div>
    <ul class="tiles people">
{people}
    </ul>
  </section>

  <section class="sec pad">
    <div class="sec-head"><h2>Releases</h2><a class="under" href="releases.html">All {len(releases)} releases</a></div>
    <ul class="tiles covers">
{latest}
    </ul>
  </section>

  <section class="contact pad" id="contact">
    <p>Reach out for information</p>
    <a href="mailto:gd@477records.com">gd@477records.com</a>
  </section>
</main>""", ld={"@context": "https://schema.org", "@graph": [
        LABEL,
        {"@type": "WebSite", "@id": SITE + "#site", "url": SITE, "name": "477 Records", "publisher": {"@id": SITE + "#label"}},
    ]})

# ---------- roster ----------
cards = []
for a in ARTISTS:
    mine = [r for r in releases if a["slug"] in tags(r)]
    out = [r for r in mine if r["date"] <= TODAY]
    nxt = [r for r in mine if r["date"] > TODAY]
    lines = [f'{len(mine)} release{"s" if len(mine) != 1 else ""} on 477 Records']
    if out:
        lines.append(f'Latest: {e(out[0]["title"])} ({out[0]["date"][:4]})')
    if nxt:
        d = datetime.date.fromisoformat(nxt[-1]["date"]).strftime("%b %-d")
        lines.append(f'Next: {e(nxt[-1]["title"])}, out {d}')
    cards.append(f"""    <li class="card" id="{a["slug"]}">
      <a class="shot" href="#{a["slug"]}" aria-label="{e(a["name"])}"><img src="assets/{a["img"]}" width="640" height="800" alt="{e(a["name"])}"></a>
      <div class="info">
        <h2><a href="{a["slug"]}.html">{e(a["name"])}</a></h2>
        <p class="bio">{e(BIOS.get(a["slug"], ""))}</p>
        <p class="links"><a class="under" href="{a["spotify"]}" target="_blank" rel="noopener">Listen on Spotify</a><a class="under" href="{a["slug"]}.html">Releases and more</a></p>
      </div>
    </li>""")
page("roster.html", "Roster | 477 Records", "The artists on 477 Records: " + ", ".join(a["name"] for a in ARTISTS) + ".",
     f"""<main>
  <h1 class="mega roster-word">Roster</h1>
  <ol class="reel">
{chr(10).join(cards)}
  </ol>
</main>
<script>
(function () {{
  var cards = [].slice.call(document.querySelectorAll('.card')), ticking = false;
  function pick() {{
    ticking = false;
    var mid = innerHeight / 2 + 20, best = null, gap = 1e9;
    cards.forEach(function (c) {{
      var r = c.getBoundingClientRect(), g = Math.abs(r.top + r.height / 2 - mid);
      if (g < gap) {{ gap = g; best = c; }}
    }});
    cards.forEach(function (c) {{ c.classList.toggle('active', c === best); }});
  }}
  function centre(c, smooth) {{
    var calm = matchMedia('(prefers-reduced-motion: reduce)').matches;
    c.scrollIntoView({{ block: 'center', behavior: smooth && !calm ? 'smooth' : 'auto' }});
  }}
  addEventListener('scroll', function () {{ if (!ticking) {{ ticking = true; requestAnimationFrame(pick); }} }}, {{ passive: true }});
  addEventListener('resize', pick);
  cards.forEach(function (c) {{
    c.querySelector('.shot').addEventListener('click', function (ev) {{ ev.preventDefault(); centre(c, true); history.replaceState(null, '', '#' + c.id); }});
  }});
  var start = location.hash && document.getElementById(location.hash.slice(1));
  if (start) centre(start, false);
  pick();
}})();
</script>""", current="roster.html", ld={"@context": "https://schema.org", "@type": "ItemList", "name": "477 Records roster",
     "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": SITE + a["slug"] + ".html", "name": a["name"]} for i, a in enumerate(ARTISTS)]})

# ---------- releases ----------
filters = [dict(slug="all", name="All")] + ARTISTS + EXTRA_FILTERS
fbtn = "\n".join(
    f'        <li><button type="button" data-filter="{f["slug"]}" aria-pressed="{"true" if f["slug"] == "all" else "false"}">{e(f["name"])}</button></li>'
    for f in filters)
grid = "\n".join("    " + cover_li(r, eager=i < 8) for i, r in enumerate(releases))
page("releases.html", "Releases | 477 Records", f"All {len(releases)} releases on 477 Records, with links to Spotify, Apple Music and YouTube.",
     f"""<main class="pad">
  <div class="works-head">
    <h1 class="mega">Releases<sup id="count">{len(releases)}</sup></h1>
    <button class="filters-toggle" type="button" aria-expanded="true" aria-controls="controls">Close Filters</button>
    <div class="controls" id="controls">
      <div class="group">
        <span class="label" id="l-artist">Artist</span>
        <ul aria-labelledby="l-artist">
{fbtn}
        </ul>
      </div>
      <div class="group">
        <span class="label" id="l-view">View</span>
        <ul aria-labelledby="l-view">
          <li><button type="button" data-view="grid" aria-pressed="true">Grid</button></li>
          <li><button type="button" data-view="list" aria-pressed="false">List</button></li>
        </ul>
      </div>
    </div>
  </div>
  <ul class="tiles covers works" id="works">
{grid}
  </ul>
  <div class="works-end"></div>
</main>
<script>
(function () {{
  var list = document.getElementById('works'), items = [].slice.call(list.children), count = document.getElementById('count');
  var fb = [].slice.call(document.querySelectorAll('[data-filter]')), vb = [].slice.call(document.querySelectorAll('[data-view]'));
  function press(group, on) {{ group.forEach(function (b) {{ b.setAttribute('aria-pressed', b === on ? 'true' : 'false'); }}); }}
  function filter(slug) {{
    var btn = fb.filter(function (b) {{ return b.dataset.filter === slug; }})[0];
    if (!btn) return;
    var n = 0;
    items.forEach(function (li) {{
      var show = slug === 'all' || li.dataset.tags.split(' ').indexOf(slug) > -1;
      li.hidden = !show; if (show) n++;
    }});
    count.textContent = n;
    press(fb, btn);
  }}
  fb.forEach(function (b) {{ b.addEventListener('click', function () {{
    filter(b.dataset.filter);
    history.replaceState(null, '', b.dataset.filter === 'all' ? location.pathname : '#' + b.dataset.filter);
  }}); }});
  vb.forEach(function (b) {{ b.addEventListener('click', function () {{
    list.classList.toggle('list', b.dataset.view === 'list');
    press(vb, b);
  }}); }});
  var ft = document.querySelector('.filters-toggle'), head = document.querySelector('.works-head');
  ft.addEventListener('click', function () {{
    var shut = head.classList.toggle('shut');
    ft.textContent = shut ? 'Open Filters' : 'Close Filters'; ft.setAttribute('aria-expanded', !shut);
  }});
  if (location.hash) filter(location.hash.slice(1));
}})();
</script>""", current="releases.html")

# ---------- artist pages ----------
def first_sentences(t, n=155):
    out = ""
    for part in t.replace("\u201d", "\u201d ").split(". "):
        nxt = (out + part.strip() + ". ") if out else (part.strip() + ". ")
        if len(nxt) > n and out:
            break
        out = nxt
    out = out.strip().replace(".. ", ". ").rstrip(".") + "."
    if len(out) < 90:   # first sentence too thin for a search snippet: use more of the bio, cut at a word
        out = t if len(t) <= n else t[:n].rsplit(" ", 1)[0].rstrip(",;:") + "\u2026"
    return out


for a in ARTISTS:
    mine = [r for r in releases if a["slug"] in tags(r)]
    bio = BIOS.get(a["slug"], "")
    tiles = "\n".join("      " + cover_li(r, eager=i < 4) for i, r in enumerate(mine))
    page(a["slug"] + ".html", f'{a["name"]} | 477 Records', first_sentences(bio) if bio else f'{a["name"]} on 477 Records.',
         f"""<main class="pad artist">
  <h1 class="mega artist-name">{e(a["name"])}</h1>
  <div class="artist-top">
    <figure class="artist-shot"><img src="assets/{a["img"]}" width="640" height="800" alt="{e(a["name"])}"></figure>
    <div class="artist-info">
      <p class="artist-bio">{e(bio)}</p>
      <p class="links"><a class="under" href="{a["spotify"]}" target="_blank" rel="noopener">Listen on Spotify</a><a class="under" href="roster.html#{a["slug"]}">Back to the roster</a></p>
    </div>
  </div>
  <section class="sec">
    <div class="sec-head"><h2>Releases<sup>{len(mine)}</sup></h2><a class="under" href="releases.html">All {len(releases)} releases</a></div>
    <ul class="tiles covers">
{tiles}
    </ul>
  </section>
  <div class="works-end"></div>
</main>""", current="roster.html", image="assets/" + a["img"], ld={
        "@context": "https://schema.org", "@type": "MusicGroup", "@id": SITE + a["slug"] + ".html#artist",
        "name": a["name"], "url": SITE + a["slug"] + ".html", "image": SITE + "assets/" + a["img"],
        "description": bio, "sameAs": [a["spotify"]],
        "album": [{"@type": "MusicAlbum", "name": r["title"], "url": r["apple"], "datePublished": r["date"],
                   "image": SITE + "assets/r/" + str(r["id"]) + ".jpg", "byArtist": {"@type": "MusicGroup", "name": r["artist"]}}
                  for r in mine[:20]],
    })

# ---------- privacy ----------
page("privacy.html", "Privacy | 477 Records", "How the 477 Records website handles your information.",
     """<main class="pad legal">
  <h1 class="mega">Privacy</h1>
  <div class="legal-body">
    <p class="k">Last updated November 20, 2026</p>
    <h2>What we collect</h2>
    <p>Nothing. This website has no accounts, forms, mailing list, analytics or advertising tracking, and it does not set cookies.</p>
    <h2>Our host</h2>
    <p>The site is hosted on GitHub Pages. Like any web host, GitHub may record technical information such as your IP address when you load a page, for security and to keep the service running. See <a class="under" href="https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement" target="_blank" rel="noopener">GitHub\u2019s privacy statement</a>.</p>
    <h2>Links to other services</h2>
    <p>Links to Spotify, Apple Music, YouTube and Instagram take you to those services, which have their own privacy policies.</p>
    <h2>Email</h2>
    <p>If you email us, we use your message and address only to reply.</p>
    <h2>Questions</h2>
    <p>Write to <a class="under" href="mailto:gd@477records.com">gd@477records.com</a>.</p>
  </div>
</main>""")

# ---------- 404 (served for any missing address, so asset paths need a base) ----------
page("404.html", "Page not found | 477 Records", "This page does not exist.",
     """<main class="pad legal">
  <h1 class="mega">Not found</h1>
  <div class="legal-body">
    <p>This page doesn\u2019t exist. The 477 Records site was rebuilt in November 2026, so older links may no longer work.</p>
    <p class="links"><a class="under" href="./">Home</a><a class="under" href="roster.html">Roster</a><a class="under" href="releases.html">Releases</a></p>
  </div>
</main>""", index=False, base="/" if LIVE else "/site/")

# old Wix address
open(os.path.join(ROOT, "portfolio.html"), "w").write(
    '<!doctype html><meta charset="utf-8"><title>477 Records</title><meta name="robots" content="noindex">'
    '<link rel="canonical" href="' + SITE + 'roster.html"><meta http-equiv="refresh" content="0; url=roster.html">'
    '<a href="roster.html">Roster</a>\n')

# ---------- sitemap + robots ----------
lastmod = TODAY
open(os.path.join(ROOT, "sitemap.xml"), "w").write(
    '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    + "".join(f"  <url><loc>{url_of(n)}</loc><lastmod>{lastmod}</lastmod></url>\n" for n in PAGES)
    + "</urlset>\n")
open(os.path.join(ROOT, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}sitemap.xml\n")

cname = os.path.join(ROOT, "CNAME")
if LIVE:
    open(cname, "w").write(DOMAIN + "\n")
elif os.path.exists(cname):
    os.remove(cname)
print("built", len(PAGES), "indexable pages,", len(releases), "releases")
