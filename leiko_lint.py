#!/usr/bin/env python3
"""leiko_lint.py — pre-flight gate. Mirrors voiceLint (src/studio/lint.ts).

Catches a bad card HERE, before it is sent, instead of letting it land in the
dashboard as lint_failed. If this file and voiceLint ever disagree, voiceLint
wins and this file gets corrected. Do not fork.

CLI:  python3 leiko_lint.py copy_issue1.json
Lib:  from leiko_lint import lint_issue
"""
import datetime as dt
import html, json, pathlib, re, sys

# ── §4 text gate: banned substrings, case-insensitive ────────────────────────
BANNED = [
    "patient", "diagnose", "diagnosis", "diagnostic", "treat", "treatment",
    "cure", "silent killer", "ticking time bomb", "before it's too late",
    "medical advice", "dangerous level", "critical level",
    "fda approved", "fda-approved", "fda-listed", "fda listed",
    "510(k)", "510k", "class ii", "class 2", "class iia",
    "ce mark", "ce-mark", "iso 13485", "registration number",
    "mmhg", "cleared", "clearance", "fda-cleared", "fda cleared", "certified",
]

# ── §4 text gate: regex hits ─────────────────────────────────────────────────
PATTERNS = [
    (r"\bfda\b",                        "bare FDA"),
    (r"\bpredict\w*",                   "predict*"),
    (r"\bprevent\w*",                   "prevent*"),
]

# "cuffless" is NOT a hard text block on the server — confirmed against the
# deployed lint.ts. In copy it is a soft flag (voiceFlags): the card still
# stores as needs_review with a review_flags entry. It is a HARD block only in
# artwork, via the vision gate.
#
# Our house rule (COPY_RULES §5) is stricter than the server on purpose:
# "cuffless" describing Leiko is always an error and must be escalated, never
# auto-fixed. But the words are legitimate when drawing a competitor contrast.
# So: blocked here by default, and released only by an explicit, deliberate
# acknowledgement on the card — "competitor_contrast": true.
CUFFLESS = r"cuff-?less|no cuff|without a cuff"

# ── local-only rules the server does not check (COPY_RULES.md) ───────────────
LOCAL_BANNED = ["smartwatch", "lower your blood pressure", "improves your blood pressure"]

SLOTS = ["STAT_A", "STAT_MID", "STAT_B", "STAT_SUB", "STAT_KICK", "MYTH",
         "FACT_HEAD", "FACT_SUB", "GIFT_HEAD1", "GIFT_HEAD2", "GIFT_BODY"]
LIMITS = {"STAT_KICK": 20, "STAT_SUB": 50}
PILLARS = {"educate", "product", "caregiver", "founder"}
MARKETS = {"NG", "US", "DIASPORA"}

# a source older than this must be re-checked, never reused on trust
STALE_DAYS = 180
PLACEHOLDER_URLS = ["example.", "localhost", "your-source-here", "TODO", "…"]


def utf8_stdout():
    """Windows consoles default to the locale codepage (cp1252, cp936, …);
    lint messages quote the copy text, which holds curly quotes and em-dashes,
    and print() then crashes mid-report. Force UTF-8, replacing anything the
    terminal cannot show."""
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8", errors="replace")


def plain(s: str) -> str:
    """Strip entities and non-breaking spaces so &nbsp; can't hide a banned word."""
    return html.unescape(str(s)).replace("\u00a0", " ")


def word_around(text: str, sub: str) -> str:
    """The actual word a banned substring landed inside.

    The server matches with String.includes() — no word boundaries — so 'cure'
    fires inside 'secure' and 'treat' inside 'retreat'. Those are real blocks,
    not bugs, and the writer needs to see WHY or the message looks insane.
    """
    t = plain(text)
    i = t.lower().find(sub)
    if i < 0:
        return sub
    a = i
    while a > 0 and (t[a-1].isalnum() or t[a-1] in "-'"):
        a -= 1
    b = i + len(sub)
    while b < len(t) and (t[b].isalnum() or t[b] in "-'"):
        b += 1
    return t[a:b]


def scan(text: str):
    """Return the list of gate hits in a piece of text.

    Substring matching, mirroring String.includes() on the server — deliberately
    NOT word-anchored.
    """
    t = plain(text).lower()
    hits = []
    for b in BANNED:
        if b in t:
            w = word_around(text, b)
            hits.append(b if w.lower() == b else f"{b} (inside “{w}”)")
    hits += [name for rx, name in PATTERNS if re.search(rx, t)]
    return hits


def scan_cuffless(text: str):
    return bool(re.search(CUFFLESS, plain(text).lower()))


def scan_local(text: str):
    t = plain(text).lower()
    return [b for b in LOCAL_BANNED if b in t]


def lint_issue(doc: dict):
    """Lint a v2 copy file. Returns (errors, warnings)."""
    err, warn = [], []
    meta = doc.get("meta", {})

    # ── required payload fields (§2) ─────────────────────────────────────────
    market = str(meta.get("market", "")).strip()
    if market not in MARKETS:
        err.append(f"meta.market must be one of {sorted(MARKETS)} — got {market!r}")
    if not isinstance(meta.get("issue_no"), int):
        err.append("meta.issue_no must be a NUMBER, not a string")

    # ── design slots ─────────────────────────────────────────────────────────
    slots = doc.get("slots", {})
    for k in SLOTS:
        if k not in slots:
            err.append(f"missing slot {k}")
    for k, lim in LIMITS.items():
        if k in slots:
            n = len(plain(slots[k]))
            if n > lim:
                err.append(f"{k} is {n} chars, limit ~{lim}: {plain(slots[k])!r}")
    for k, v in slots.items():
        for h in scan(v):
            err.append(f"slot {k} — banned on card art: {h}")
        if scan_cuffless(v):
            err.append(f"slot {k} — cuffless wording on ARTWORK: hard block at the "
                       f"vision gate, no exemption. Leiko measures with a real cuff.")
        for h in scan_local(v):
            err.append(f"slot {k} — banned by COPY_RULES: {h}")

    # ── per-card text that the server's text gate reads ──────────────────────
    cards = doc.get("cards", {})
    if not cards:
        err.append("no cards block — nothing to send")
    for slot, card in cards.items():
        where = f"card {slot}"
        pillar = card.get("pillar")
        if pillar not in PILLARS:
            err.append(f"{where}: pillar {pillar!r} invalid — would silently become 'product'")

        text = " ".join(filter(None, [card.get("title", ""), card.get("caption", "")]
                              + list((card.get("captions") or {}).values())))
        for h in scan(text):
            err.append(f"{where}: banned in title/caption — {h}")
        for h in scan_local(text):
            err.append(f"{where}: banned by COPY_RULES — {h}")
        if scan_cuffless(text):
            # The acknowledgement excuses a competitor contrast. It must never
            # excuse the claim being made about Leiko — that is the one error
            # COPY_RULES §5 says is always wrong. If both appear in the same
            # sentence, the contrast reading is not available.
            body = re.sub(r"leiko\.health", " ", plain(text), flags=re.I)
            same_sentence = any(re.search(CUFFLESS, s.lower()) and "leiko" in s.lower()
                                for s in re.split(r"[.!?]+", body))
            if same_sentence:
                err.append(f"{where}: cuffless wording in the same sentence as Leiko. "
                           "Leiko measures with a real inflating cuff — this is wrong "
                           "however it is flagged. Escalate, do not auto-fix.")
            elif card.get("competitor_contrast") is True:
                warn.append(f"{where}: cuffless wording kept as a competitor contrast. "
                            "The server soft-flags this — the card will arrive with a "
                            "review_flag and needs a human read before approval.")
            else:
                err.append(f"{where}: cuffless wording in copy. The server ALLOWS this "
                           "(soft flag only) but COPY_RULES §5 says escalate, never "
                           "auto-fix. If it describes a COMPETITOR, set "
                           '"competitor_contrast": true on this card. If it describes '
                           "Leiko, it is simply wrong — Leiko has a real cuff.")

        cap = plain(card.get("caption", "")).strip()
        if not cap:
            warn.append(f"{where}: no caption")
        else:
            if not cap.endswith("leiko.health"):
                err.append(f"{where}: caption must end with leiko.health")
            body = re.sub(r"leiko\.health\s*$", "", cap)
            n = len([s for s in re.split(r"[.!?]+", body) if s.strip()])
            if not 2 <= n <= 4:
                warn.append(f"{where}: caption is {n} sentences (house rule 2-4)")

        # ── every stat must be freshly researched (COPY_RULES §6) ───────────
        # A source is only usable if it was gathered THIS run: a real link, the
        # date it was retrieved, and an explicit verified mark. Numbers must
        # never be carried forward from an earlier issue on memory alone.
        for i, s in enumerate(card.get("sources", [])):
            tag = f"{where}: source {i+1} ({s.get('body','?')})"
            url = str(s.get("url", "")).strip()
            if not url:
                err.append(f"{tag} has no URL — go and find it")
            elif not url.startswith(("http://", "https://")):
                err.append(f"{tag} URL is not a link: {url!r}")
            elif any(p in url for p in PLACEHOLDER_URLS):
                err.append(f"{tag} URL is a placeholder, not a real source: {url!r}")

            if s.get("status") != "verified":
                err.append(f"{tag} is not marked verified — status={s.get('status')!r}. "
                           "Open the link, confirm the figure, then set status.")
            if not s.get("figure"):
                warn.append(f"{tag} has no 'figure' — record the number as the source states it")

            got = str(s.get("retrieved", "")).strip()
            if not got:
                err.append(f"{tag} has no 'retrieved' date — when did you pull this?")
            else:
                try:
                    age = (dt.date.today() - dt.date.fromisoformat(got)).days
                except ValueError:
                    err.append(f"{tag} retrieved={got!r} is not a YYYY-MM-DD date")
                else:
                    if age < 0:
                        err.append(f"{tag} retrieved date is in the future: {got}")
                    elif age > STALE_DAYS:
                        err.append(f"{tag} was retrieved {age} days ago — re-check it "
                                   f"before reuse (limit {STALE_DAYS})")

            if market in {"NG", "DIASPORA"} and s.get("body") not in {"WHO", "NCDC", "Nigerian Cardiac Society"}:
                warn.append(f"{where}: source body {s.get('body')!r} unusual for {market}")
            if market == "US" and s.get("body") not in {"CDC", "AHA", "NHANES"}:
                warn.append(f"{where}: source body {s.get('body')!r} unusual for US")
        if card.get("claims_a_stat") and not card.get("sources"):
            err.append(f"{where}: card states a statistic but has no sources — "
                       "research it before writing the copy")

    return err, warn


def main(path):
    utf8_stdout()
    # encoding is explicit everywhere: copy files are UTF-8, but Windows'
    # default is the locale codepage and read_text() without it crashes.
    doc = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    err, warn = lint_issue(doc)
    for w in warn:
        print("  WARN ", w)
    for e in err:
        print("  BLOCK", e)
    if err:
        print(f"\nFAILED — {len(err)} blocking issue(s). Fix before sending.")
        return 1
    print(f"\nPASS — clean ({len(warn)} warning(s)).")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("usage: python3 leiko_lint.py copy_issueN.json")
    sys.exit(main(sys.argv[1]))
