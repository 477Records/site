#!/usr/bin/env python3
"""Finds a YouTube video per release from the public search page; writes _build/youtube.json {appleId: url|null}.
Keeps a hit only when the video title contains the release title and the channel or title names the artist."""
import json, os, re, sys, time, urllib.parse, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "youtube.json")
rels = json.load(open(os.path.join(HERE, "releases.json")))
done = json.load(open(OUT)) if os.path.exists(OUT) else {}
norm = lambda s: re.sub(r"[^a-z0-9æ]+", "", s.lower())
clean = lambda t: re.sub(r"\s*[\(\[](feat|with)[^\)\]]*[\)\]]|\s*-\s*(single|ep)$", "", t, flags=re.I)
def walk(o):
    if isinstance(o, dict):
        if "videoRenderer" in o: yield o["videoRenderer"]
        for v in o.values(): yield from walk(v)
    elif isinstance(o, list):
        for v in o: yield from walk(v)
empty = 0
for r in rels:
    k = str(r["id"])
    if done.get(k): continue
    title = clean(r["title"]); first = re.split(r",|&| x | and ", r["artist"])[0].strip()
    q = f"{first} {title}"
    req = urllib.request.Request("https://www.youtube.com/results?search_query=" + urllib.parse.quote(q),
        headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
                 "Accept-Language": "en-US,en;q=0.9", "Cookie": "CONSENT=YES+1; SOCS=CAI"})
    hit = None; seen = []
    try:
        page = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
        m = re.search(r"var ytInitialData = (\{.*?\});</script>", page, re.S)
        for v in list(walk(json.loads(m.group(1))))[:8]:
            vt = "".join(x["text"] for x in v["title"]["runs"]); ch = "".join(x["text"] for x in v.get("ownerText", {}).get("runs", []))
            seen.append(ch + " / " + vt)
            if norm(title) in norm(vt) and (norm(first) in norm(ch) or norm(first) in norm(vt)):
                hit = "https://www.youtube.com/watch?v=" + v["videoId"]; break
    except Exception as ex:
        print("ERR", q, repr(ex)[:120], flush=True)
    done[k] = hit
    print("ok  " if hit else "MISS", q, "" if hit else seen[:3], flush=True)
    json.dump(done, open(OUT, "w"), indent=0)
    time.sleep(2.5)
    empty = 0 if seen else empty + 1
    if empty >= 6: print('STOP: YouTube returning empty pages'); break
