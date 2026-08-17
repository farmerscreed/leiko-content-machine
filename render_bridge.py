#!/usr/bin/env python3
"""render_bridge.py — the local runner that gives flywheel posts their visuals.

The website's flywheel writes copy but cannot rasterise an image (a Cloudflare
Worker has no browser). This bridge closes that loop, exactly as
docs/CONTENT_ARCHITECTURE.md planned:

    1. GET  /api/content/render-queue    -> posts with no visuals yet
    2. render on the LOCKED templates:
         text     -> leiko_template_quote.html      (one card)
         carousel -> leiko_template_carousel.html   (cover / body / close per slide)
    3. POST /api/content/render-result   -> site stores the images, runs the
                                            vision gate, sets the paths

Auth is the same machine secret as ingest: CONTENT_INGEST_SECRET, read from the
shell env or (for the scheduled task, whose session env is stale) straight from
its HKCU\\Environment home. Never in a file, never in this repo.

Usage:  python render_bridge.py            # render + push everything pending
        python render_bridge.py --dry-run  # render locally, send nothing

Local copies land in out_bridge/ for eyeballing. Re-running is always safe —
the queue only lists posts that still have no image.
"""
import base64, json, os, pathlib, re, sys, urllib.error, urllib.request

from leiko_lint import scan, scan_cuffless, utf8_stdout

HERE = pathlib.Path(__file__).resolve().parent
SITE = os.environ.get("LEIKO_SITE", "https://leiko.health").rstrip("/")
SECRET = os.environ.get("CONTENT_INGEST_SECRET", "")
if not SECRET and os.name == "nt":
    # The scheduled task inherits a stale session environment (Windows only
    # refreshes it at login), so read the persistent User variable straight
    # from its registry home. Same store the founder's one-time
    # SetEnvironmentVariable(..., 'User') wrote to — still no file, no repo.
    try:
        import winreg

        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as _k:
            SECRET = winreg.QueryValueEx(_k, "CONTENT_INGEST_SECRET")[0]
    except OSError:
        pass

UA = "leiko-content-machine/3 (+https://leiko.health)"  # urllib's default UA is
# blocked by the Cloudflare browser-integrity check (403, error 1010)
OUT = HERE / "out_bridge"

# The quote-card kicker per pillar. Fixed strings, linted once by hand — they
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
        with urllib.request.urlopen(req, timeout=180) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        try:
            return e.code, json.loads(body)
        except Exception:
            return e.code, {"raw": body[:300]}


def pick_quote(item):
    """The line that goes ON a quote card: hook, else script, else the Facebook
    caption — for a text post the caption often IS the post, and the first
    bridge run (2026-08-17) drew two blank cards by not looking there.

    Cut at a sentence boundary under MAX_QUOTE_CHARS — an ellipsis mid-thought
    reads as sloppy on a card that exists to look considered.
    """
    captions = item.get("captions") or {}
    text = (item.get("hook") or item.get("script") or captions.get("facebook") or "").strip()
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


def fill(tpl_name, tokens):
    tpl = (HERE / tpl_name).read_text(encoding="utf-8")
    for k, v in tokens.items():
        tpl = tpl.replace("{{" + k + "}}", esc(v))
    filled = HERE / "_filled_bridge.html"
    filled.write_text(tpl, encoding="utf-8")
    return filled


def lint_hits(text):
    hits = scan(text)
    if scan_cuffless(text):
        hits.append("cuffless wording")
    return hits


def source_line(item):
    """The citation for a closing slide — a designed element, never clutter
    (D-C4). Empty string when the post states no sourced figure."""
    sources = item.get("sources") or []
    if not sources:
        return ""
    s = sources[0]
    body = (s.get("body") or "").strip()
    name = (s.get("name") or "").strip()
    url = (s.get("url") or "").strip()
    domain = re.sub(r"^https?://(www\.)?", "", url).split("/")[0] if url else ""
    label = name or domain
    if not body and not label:
        return ""
    return f"Source: {body}" + (f" — {label}" if label else "")


def carousel_tokens(slides, i, n, src):
    """Map atomizer slides onto the three locked layouts: slide 1 is the hook
    (cover), the last is the takeaway (close), the middle are the reference."""
    s = slides[i]
    heading = (s.get("heading") or "").strip()
    body = (s.get("body") or "").strip()
    if i == 0:
        return "cover", {"COVER_HEAD": heading or body, "COVER_SUB": body if heading else "",
                         "COVER_COUNT": f"1 / {n}"}
    if i == n - 1:
        return "close", {"CLOSE_HEAD": heading or "Worth keeping.", "CLOSE_SUB": body,
                         "CLOSE_COUNT": f"{n} / {n}", "CLOSE_SRC": src}
    return "body", {"BODY_NUM": str(i), "BODY_HEAD": heading, "BODY_TEXT": body,
                    "BODY_COUNT": f"{i + 1} / {n}"}


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
        print("Nothing waiting for a card.")
        return 0

    print(f"{len(items)} post(s) need visuals\n")
    bad = 0

    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=2)

        def shoot(filled, label, out_png, out_jpg):
            page.goto(filled.as_uri())
            page.wait_for_timeout(700)  # fonts + fit scripts
            el = page.query_selector(f'[data-screen-label="{label}"]')
            el.screenshot(path=str(out_png))
            el.screenshot(path=str(out_jpg), type="jpeg", quality=92)

        for it in items:
            pid = it["id"]

            # ── carousel: one image per slide ──────────────────────────────
            if it.get("format") == "carousel":
                slides = it.get("slides") or []
                n = len(slides)
                if n < 2:
                    print(f"  SKIP  {pid[:8]}  carousel has fewer than 2 slides")
                    bad += 1
                    continue
                all_text = " ".join(f"{s.get('heading') or ''} {s.get('body') or ''}" for s in slides)
                hits = lint_hits(all_text)
                if hits:
                    print(f"  SKIP  {pid[:8]}  banned on artwork: {', '.join(hits)}")
                    bad += 1
                    continue
                src = source_line(it)
                payload = []
                for i in range(n):
                    label, tokens = carousel_tokens(slides, i, n, src)
                    png, jpg = OUT / f"{pid}-s{i}.png", OUT / f"{pid}-s{i}.jpg"
                    shoot(fill("leiko_template_carousel.html", tokens), label, png, jpg)
                    payload.append({"index": i, "image_base64": base64.b64encode(jpg.read_bytes()).decode()})
                print(f"  drew  {pid[:8]}  carousel, {n} slides")
                if dry:
                    continue
                code, res = api("/api/content/render-result", {"post_id": pid, "slides": payload})
                if code == 200 and res.get("ok"):
                    extra = f"  vision hits: {res['hits']}" if res.get("hits") else ""
                    print(f"  OK    {pid[:8]}  -> {res.get('image_path')}{extra}")
                else:
                    print(f"  ERR   {pid[:8]}  HTTP {code} {json.dumps(res)[:200]}")
                    bad += 1
                continue

            # ── text: the quote card ───────────────────────────────────────
            quote = pick_quote(it)
            if not quote:
                # A blank card must never exist — better no image than an empty one.
                print(f"  SKIP  {pid[:8]}  post has no text anywhere (hook/script/caption)")
                bad += 1
                continue
            hits = lint_hits(quote)
            if hits:
                print(f"  SKIP  {pid[:8]}  banned on artwork: {', '.join(hits)}")
                bad += 1
                continue
            kick = KICK.get(it.get("pillar") or "", "WORTH KNOWING")
            png, jpg = OUT / f"{pid}.png", OUT / f"{pid}.jpg"
            shoot(fill("leiko_template_quote.html", {"QUOTE_TEXT": quote, "QUOTE_KICK": kick}), "quote", png, jpg)
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

        browser.close()

    print(f"\n{'dry-run - nothing sent' if dry else 'done'}; local copies in {OUT}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(dry="--dry-run" in sys.argv))
