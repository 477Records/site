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


def page(name, title, desc, body, current=""):
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
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:type" content="website">
<meta property="og:image" content="https://www.477records.com/assets/og.jpg">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#edf0eb">
<meta name="robots" content="noindex">
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
    <img src="assets/wordmark.svg" width="3738" height="1870" alt="">
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
  <span>© 2026 477 Records</span>
  <a href="mailto:gd@477records.com">gd@477records.com</a>
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
            f'<span class="pic"><img src="assets/r/{r["id"]}.jpg" width="500" height="500" alt=""{load}></span>'
            f'<span class="t">{e(r["title"])}</span><span class="s">{e(r["artist"])}</span>'
            f'<span class="d">{nice_date(r)}</span></a><span class="listen">{where}</span></li>')


# ---------- home ----------
people = "\n".join(
    f'      <li><a href="roster.html#{a["slug"]}"><span class="pic"><img src="assets/{a["img"]}" width="640" height="800" '
    f'alt="{e(a["name"])}" loading="lazy"></span><span class="t">{e(a["name"])}</span></a></li>'
    for a in ARTISTS)
latest = "\n".join("      " + cover_li(r) for r in releases[:8])
page("index.html", "477 Records",
     "477 Records is a New York-based independent record label.",
     f"""<main>
  <section class="hero pad">
    <figure class="lockup">
      <img class="tape" src="assets/tape.webp" width="874" height="329" alt="">
      <img class="mark" src="assets/wordmark.svg" width="3738" height="1870" alt="477 Records">
    </figure>
    <div class="pitch">
      <h1>477 Records is a New York&#8209;based independent record label.</h1>
    </div>
  </section>

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
</main>""")

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
        <h2>{e(a["name"])}</h2>
        <p class="links"><a class="under" href="{a["spotify"]}" target="_blank" rel="noopener">Listen on Spotify</a><a class="under" href="releases.html#{a["slug"]}">See releases</a></p>
      </div>
    </li>""")
page("roster.html", "Roster | 477 Records", "The artists signed to 477 Records.",
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
</script>""", current="roster.html")

# ---------- releases ----------
filters = [dict(slug="all", name="All")] + ARTISTS + EXTRA_FILTERS
fbtn = "\n".join(
    f'        <li><button type="button" data-filter="{f["slug"]}" aria-pressed="{"true" if f["slug"] == "all" else "false"}">{e(f["name"])}</button></li>'
    for f in filters)
grid = "\n".join("    " + cover_li(r, eager=i < 8) for i, r in enumerate(releases))
page("releases.html", "Releases | 477 Records", "Every release on 477 Records.",
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

print("built 3 pages,", len(releases), "releases")
