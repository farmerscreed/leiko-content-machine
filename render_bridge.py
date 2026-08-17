#!/usr/bin/env python3
"""render_bridge.py — the local runner that gives flywheel story posts their card.

The website's flywheel writes story TEXT posts but cannot rasterise an image
(a Cloudflare Worker has no browser). This bridge closes that loop, exactly as
docs/CONTENT_ARCHITECTURE.md planned:

    1. GET  /api/content/render-queue    -> story posts with no image yet
    2. render each on the LOCKED quote template (leiko_template_quote.html)
    3. POST /api/content/render-result   -> site stores the card, runs the
                                            vision gate, sets image_path

Auth is the same machine secret as ingest: CONTENT_INGEST_SECRET in the shell
environment (never in a file). Re-running is always safe — the queue only
lists posts that still have no image, and a re-send supersedes in place.

Usage:  python render_bridge.py            # render + push everything pending
        python render_bridge.py --dry-run  # render locally, send nothing

Local copies land in out_bridge/<post_id>.png/.jpg for eyeballing.
"""
import base64, json, os, pathlib, re, sys, urllib.error, urllib.request

from leiko_lint import scan, scan_cuffless, utf8_stdout

HERE = pathlib.Path(__file__).resolve().parent
SITE = os.environ.get("LEIKO_SITE", "https://leiko.health").rstrip("/")
SECRET = os.environ.get("CONTENT_INGEST_SECRET", "")
UA = "leiko-content-machine/3 (+https://leiko.health)"  # urllib's default UA is
# blocked by the Cloudflare browser-integrity check (403, error 1010)
OUT = HERE / "out_bridge"

# The kicker line per pillar. Fixed strings, linted once here by hand — they
# never come from a model.
KICK = {
    "educate": "WORTH KNOWING",
    "caregiver": "FOR THE ONES WE LOVE",
    "product": "MEASURED, NOT GUESSED",
    "founder": "FROM THE FOUNDER",
}

MAX_QUOTE_CHARS = 220


def api(path, payload=None):
    """One authenticated call. Returns (status, parsed-or-raw)."""
    req = urllib.request.Request(
        f"{SITE}{path}",
        data=json.dumps(payload).encode() if payload is not None else None,
        headers={
            "Authorization": f"Bearer {SECRET}",
            "Content-Type": "application/json",
            "User-Agent": UA,
        },
        method="POST" if payload is not None else "GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        try:
            return e.code, json.loads(body)
        except Exception:
            return e.code, {"raw": body[:300]}


def pick_quote(item):
    """The line that goes ON the card: the hook, else the script's opening.

    Cut at a sentence boundary under MAX_QUOTE_CHARS — an ellipsis mid-thought
    reads as sloppy on a card that exists to look considered.
    """
    text = (item.get("hook") or item.get("script") or "").strip()
    if len(text) <= MAX_QUOTE_CHARS:
        return text
    best = ""
    for m in re.finditer(r"[^.!?]*[.!?]", text):
        candidate = (best + m.group(0)).strip()
        if len(candidate) > MAX_QUOTE_CHARS:
            break
        best = candidate
    return best or text[:MAX_QUOTE_CHARS].rsplit(" ", 1)[0]


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render(quote, kick, out_png, out_jpg):
    tpl = (HERE / "leiko_template_quote.html").read_text(encoding="utf-8")
    tpl = tpl.replace("{{QUOTE_TEXT}}", esc(quote)).replace("{{QUOTE_KICK}}", esc(kick))
    filled = HERE / "_filled_quote.html"
    filled.write_text(tpl, encoding="utf-8")
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=2)
        pg.goto(filled.as_uri())
        pg.wait_for_timeout(700)  # fonts + the fit script
        el = pg.query_selector('[data-screen-label="quote"]')
        el.screenshot(path=str(out_png))
        el.screenshot(path=str(out_jpg), type="jpeg", quality=92)
        b.close()


def main(dry=False):
    utf8_stdout()
    if not SECRET:
        sys.exit("CONTENT_INGEST_SECRET is not set in this shell.")
    OUT.mkdir(exist_ok=True)

    code, body = api("/api/content/render-queue")
    if code != 200 or not body.get("ok"):
        sys.exit(f"render-queue failed: HTTP {code} {json.dumps(body)[:300]}")
    items = body.get("items", [])
    if not items:
        print("Nothing waiting for a card. ✨")
        return 0

    print(f"{len(items)} story post(s) need a card\n")
    bad = 0
    for it in items:
        pid = it["id"]
        quote = pick_quote(it)
        kick = KICK.get(it.get("pillar") or "", "WORTH KNOWING")

        # Belt-and-braces: the copy was voiceLint'ed server-side at insert, but
        # nothing that trips the banned list may be painted onto brand artwork.
        hits = scan(quote)
        if scan_cuffless(quote):
            hits.append("cuffless wording")
        if hits:
            print(f"  SKIP  {pid[:8]}  banned on artwork: {', '.join(hits)}")
            bad += 1
            continue

        png, jpg = OUT / f"{pid}.png", OUT / f"{pid}.jpg"
        render(quote, kick, png, jpg)
        print(f"  drew  {pid[:8]}  “{quote[:60]}…”" if len(quote) > 60 else f"  drew  {pid[:8]}  “{quote}”")

        if dry:
            continue
        b64 = base64.b64encode(jpg.read_bytes()).decode()
        code, res = api("/api/content/render-result", {"post_id": pid, "image_base64": b64})
        if code == 200 and res.get("ok"):
            extra = f"  vision hits: {res['hits']}" if res.get("hits") else ""
            print(f"  OK    {pid[:8]}  -> {res.get('image_path')}{extra}")
        else:
            print(f"  ERR   {pid[:8]}  HTTP {code} {json.dumps(res)[:200]}")
            bad += 1

    print(f"\n{'dry-run — nothing sent' if dry else 'done'}; local copies in {OUT}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(dry="--dry-run" in sys.argv))
