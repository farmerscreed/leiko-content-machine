#!/usr/bin/env python3
"""leiko_ingest.py — sends rendered cards to the Leiko website.

  python3 leiko_ingest.py copy_issue1.json out_issue1/            # send
  python3 leiko_ingest.py copy_issue1.json out_issue1/ --dry-run  # show, send nothing

Needs the secret in the environment, never in a file:
  export CONTENT_INGEST_SECRET='...'

Exit codes: 0 all cards clean · 1 a card failed a gate or errored · 2 bad setup.
"""
import base64, hashlib, json, os, pathlib, re, socket, sys, time
import urllib.request, urllib.error

from leiko_lint import lint_issue, utf8_stdout

ENDPOINT = os.environ.get("LEIKO_INGEST_URL", "https://leiko.health/api/content/ingest")
SECRET = os.environ.get("CONTENT_INGEST_SECRET", "")
TIMEOUT = 120
GAP_SECONDS = 3     # self-imposed. The worker has NO rate limit of any kind.

# Ingest can only ever answer with these two. Anything else is a contract break:
# the other five ContentStatus members are downstream dashboard states.
EXPECTED_STATUS = {"needs_review", "lint_failed"}

# template label -> API card_slot. Explicit, because "1c Check on Mama" is
# hardcoded in the template even on Papa issues.
SLOT_OF_LABEL = {"1a": "1a", "1b": "1b", "1c": "1c"}


def find_image(outdir: pathlib.Path, slot: str):
    """Match leiko_1a_Stat.jpg -> slot 1a, whatever the label says after it.

    JPEG is preferred: the site stores the card under an extension sniffed from
    the actual bytes, and Instagram publishing refuses a .png path outright
    (website publishers.ts). Facebook accepts JPEG too, so JPEG serves both.
    PNG is the fallback for output rendered before the JPEG change.
    """
    for pattern in ("*.jpg", "*.png"):
        for p in sorted(outdir.glob(pattern)):
            m = re.match(r"leiko_(\d[a-c])", p.name)
            if m and SLOT_OF_LABEL.get(m.group(1)) == slot:
                return p
    return None


def build_cards(doc, outdir):
    meta, slots = doc["meta"], doc["slots"]
    cards, missing = [], []
    for slot, card in doc["cards"].items():
        png = find_image(outdir, slot)
        if png is None:
            missing.append(slot)
            continue
        raw = png.read_bytes()
        cards.append({
            "market":       meta["market"],
            "issue_no":     meta["issue_no"],          # number, not string
            "card_slot":    slot,
            "image_base64": base64.b64encode(raw).decode(),
            "title":        card.get("title", ""),
            "caption":      card.get("caption", ""),
            "captions":     card.get("captions") or {},
            "pillar":       card.get("pillar", "product"),
            "sources":      card.get("sources", []),
            "copy_json":    slots,
            "origin":       meta.get("origin", "content-machine"),
            "_local": {"file": str(png), "bytes": len(raw),
                       "sha256": hashlib.sha256(raw).hexdigest()[:16]},
        })
    return cards, missing


def post(card, attempts=2):
    """POST ONE card. Returns (http_code, body). code 0 = never landed.

    Retry policy is deliberately narrow. A refused connection never reached the
    worker, so retrying is free. A TIMEOUT may have landed and been committed —
    and the site has a known race where a retry can insert a duplicate row with
    a fresh id instead of superseding. So timeouts are never auto-retried; the
    human is told to check the dashboard first.
    """
    data = json.dumps(card).encode()
    for i in range(attempts):
        req = urllib.request.Request(
            ENDPOINT, data=data,
            headers={"Content-Type": "application/json",
                     "Authorization": f"Bearer {SECRET}"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                return r.status, json.loads(r.read().decode())
        except urllib.error.HTTPError as e:          # server answered, not 2xx
            try:
                body = e.read().decode()
            except Exception:
                # a server that rejects without consuming our (large) upload can
                # abort the socket mid-read; the verdict is the code, keep it
                body = ""
            try:
                return e.code, json.loads(body)
            except Exception:
                return e.code, {"raw": body[:500]}
        except TimeoutError:
            return -1, {"error": "timed out — the card MAY already be stored"}
        except urllib.error.URLError as e:
            reason = e.reason
            if isinstance(reason, TimeoutError):
                return -1, {"error": "timed out — the card MAY already be stored"}
            if isinstance(reason, (ConnectionRefusedError, socket.gaierror)):
                # provably never reached the worker (refused / DNS failure) —
                # the one class of failure where a retry is free
                if i + 1 < attempts:
                    print(f"    could not connect ({reason}) — retrying in 5s")
                    time.sleep(5)
                    continue
                return 0, {"error": str(reason)}
            return -1, {"error": f"connection died mid-request ({reason}) — "
                                 "the card MAY already be stored"}
        except Exception as e:
            # e.g. RemoteDisconnected after the request went out: the worker
            # may have committed the card, so this is never retried
            return -1, {"error": f"{e} — the card MAY already be stored"}


def one_result(body):
    """The endpoint accepts a bare card or a batch; normalise either reply."""
    rs = body.get("results")
    return rs[0] if rs else body


def explain(code):
    return {-1:  "TIMED OUT — the card may or may not be stored. Re-running the "
                 "same issue/slot/market is safe: the site supersedes in place "
                 "(dedupe race fixed website-side 2026-08-09). Never invent a "
                 "new slot; if unsure what landed, /admin/studio/cards shows it.",
            0:   "could not reach the site at all — check the URL, the network, "
                 "or whether the site is up. Nothing was sent, so nothing is half-done.",
            400: "bad JSON, empty batch, or more than 50 cards",
            401: "bad or missing CONTENT_INGEST_SECRET",
            503: "secret not configured on the worker — tell the site owner"}.get(code)


def main(copy_path, outdir, dry=False):
    utf8_stdout()
    doc = json.loads(pathlib.Path(copy_path).read_text(encoding="utf-8"))
    outdir = pathlib.Path(outdir)

    print("── pre-flight ──")
    err, warn = lint_issue(doc)
    for w in warn:
        print("  WARN ", w)
    for e in err:
        print("  BLOCK", e)
    if err:
        print("\nNothing sent. Fix the blocking issues above.")
        return 1
    print(f"  clean ({len(warn)} warning(s))")

    cards, missing = build_cards(doc, outdir)
    if missing:
        print(f"\nNo rendered PNG found for slot(s) {missing} in {outdir}")
        return 2
    print(f"\n── issue {doc['meta']['issue_no']} / {doc['meta']['market']} "
          f"/ {len(cards)} card(s), sent ONE PER REQUEST ──")
    for c in cards:
        L = c["_local"]
        print(f"  {c['card_slot']}  {c['pillar']:<9} {L['bytes']/1024:6.0f} KB  "
              f"sha {L['sha256']}  {pathlib.Path(L['file']).name}")

    if dry:
        print("\n--dry-run: nothing sent. First payload (image truncated):")
        prev = dict(cards[0], image_base64=cards[0]["image_base64"][:48] + "…")
        prev.pop("_local", None)
        print(json.dumps(prev, indent=2)[:1400])
        return 0

    if not SECRET:
        print("\nCONTENT_INGEST_SECRET is not set. export it first.")
        return 2

    print(f"\n── POST {ENDPOINT} ──")
    log = pathlib.Path("ingest_log.jsonl").open("a", encoding="utf-8")
    bad = stalled = 0

    for n, c in enumerate(cards):
        c.pop("_local", None)
        slot = c["card_slot"]
        if n:
            time.sleep(GAP_SECONDS)          # nothing throttles us; be polite
        t0 = time.time()
        code, body = post(c)
        took = time.time() - t0

        why = explain(code)
        if why:
            print(f"  FAILED  {slot}  HTTP {code}  ({took:.1f}s)")
            print(f"          {why}")
            print("          " + json.dumps(body)[:300])
            bad += 1
            if code == -1:
                stalled += 1
            continue

        # HTTP 200 does NOT mean the card passed the brand gates.
        r = one_result(body)
        status = r.get("status", "?")
        hits   = r.get("lint_hits", []) or []
        flags  = r.get("review_flags", []) or []

        if not r.get("ok"):
            mark, bad = "ERROR  ", bad + 1
        elif status == "lint_failed":
            mark, bad = "BLOCKED", bad + 1
        elif status != "needs_review":
            # OK is a claim that the card is sitting in the review queue. Any
            # other status is a contract break and must fail the run, not warn.
            mark, bad = "ERROR  ", bad + 1
        elif flags:
            mark = "CHECK  "        # stored, but a human must read it — not a pass
        else:
            mark = "OK     "
        print(f"  {mark} {slot}  status={status}  id={r.get('id','-')}  "
              f"path={r.get('image_path','-')}  ({took:.1f}s)")

        if status not in EXPECTED_STATUS:
            print(f"          CONTRACT BREAK: ingest returned {status!r}; only "
                  f"{sorted(EXPECTED_STATUS)} are possible. Tell the site owner.")

        for h in hits:
            # image: prefixed hits come from the vision gate — the artwork is at
            # fault, not the words, so re-rendering the copy will not fix them.
            if str(h).startswith("image:"):
                print(f"          ARTWORK: {h}  — the picture must change, not the copy")
            else:
                print(f"          hit: {h}")
        for f in flags:
            print(f"          flag: {str(f).split(':')[0]} — a human must read this; "
                  "it is not a pass")
            print(f"                {str(f)[:160]}")
        if r.get("error"):
            print(f"          error: {r['error']}")

        log.write(json.dumps({"ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
                              "issue_no": c["issue_no"], "market": c["market"],
                              "card_slot": slot, "http": code, **r}) + "\n")
    log.close()

    if stalled:
        print(f"\n{stalled} card(s) timed out. Re-running the same slots is safe — "
              "the site supersedes in place. Never invent a new slot to dodge a "
              "collision; /admin/studio/cards shows what actually landed.")
    if bad:
        print(f"\n{bad} card(s) did not land clean. Fix at the source, re-render, "
              "re-run — same issue_no/card_slot/market supersedes in place.")
        return 1
    print("\nAll cards stored as needs_review. Approve them in "
          "/admin/studio/cards. Nothing auto-publishes. Logged to ingest_log.jsonl")
    return 0


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) < 2:
        sys.exit("usage: python3 leiko_ingest.py copy_issueN.json out_issueN/ [--dry-run]")
    sys.exit(main(args[0], args[1], dry="--dry-run" in sys.argv))
