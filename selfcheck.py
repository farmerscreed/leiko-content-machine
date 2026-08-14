#!/usr/bin/env python3
"""selfcheck.py — proves the gate still gates. Run it after any change here.

  python selfcheck.py          exit 0 = every check held, non-zero = a gate fell

No frameworks, no fixtures directory: one synthetic good card that must PASS,
and one deliberately bad card whose every violation must BLOCK. The bad card
carries the four failures the brand cannot survive reaching the dashboard:
a banned word, an oversized slot, an unverified stat, and a crossed market.
"""
import copy as copymod
import datetime as dt
import json, pathlib, subprocess, sys, tempfile

from leiko_lint import lint_issue, utf8_stdout

TODAY = dt.date.today().isoformat()

GOOD = {
    "meta": {"market": "NG", "issue_no": 99, "origin": "content-machine"},
    "slots": {
        "STAT_A": "6", "STAT_MID": "in", "STAT_B": "10",
        "STAT_SUB": "Adults with high blood pressure don't know it.",
        "STAT_KICK": "Numbers don't guess.",
        "MYTH": "“My doctor would have caught it.”",
        "FACT_HEAD": "One visit isn't enough.",
        "FACT_SUB": "Just 3 in 10 have it under control.",
        "GIFT_HEAD1": "Check on", "GIFT_HEAD2": "Mama",
        "GIFT_BODY": "One press on her wrist. Her numbers reach your phone.",
    },
    "cards": {
        "1a": {
            "pillar": "educate", "title": "6 in 10", "claims_a_stat": True,
            "caption": "Most adults with high blood pressure don't know it. "
                       "A reading is the only way to find out. leiko.health",
            "sources": [{
                "body": "WHO", "name": "selfcheck synthetic source",
                "url": "https://www.who.int/health-topics/hypertension",
                "figure": "synthetic figure for selfcheck",
                "retrieved": TODAY, "status": "verified",
            }],
        },
    },
}


def expect(errors, needle, label):
    hit = any(needle in e for e in errors)
    print(("  ok   " if hit else "  FAIL ") + label)
    return hit


def main():
    utf8_stdout()
    ok = True

    # ── the good card must pass ──────────────────────────────────────────────
    err, _ = lint_issue(GOOD)
    if err:
        ok = False
        print("  FAIL the known-good card was blocked:")
        for e in err:
            print("        " + e)
    else:
        print("  ok   known-good card passes")

    # ── each violation must block ────────────────────────────────────────────
    bad = copymod.deepcopy(GOOD)
    bad["meta"]["market"] = "unknown"                       # crossed market
    bad["slots"]["STAT_KICK"] = "This kicker runs far past twenty characters"
    bad["slots"]["FACT_HEAD"] = "Cleared for daily use."    # banned word
    c = bad["cards"]["1a"]
    c["caption"] = ("Leiko is a cuffless smartwatch that can lower your "
                    "blood pressure. leiko.health")
    c["sources"][0]["status"] = "pending"                   # unverified stat
    c["sources"][0]["retrieved"] = "2020-01-01"             # stale stat

    err, _ = lint_issue(bad)
    ok &= expect(err, "meta.market must be one of", "crossed/unknown market blocks")
    ok &= expect(err, "STAT_KICK is", "oversized STAT_KICK blocks")
    ok &= expect(err, "banned on card art: cleared", "banned word on artwork blocks")
    ok &= expect(err, "cuffless wording in the same sentence as Leiko",
                 "cuffless-about-Leiko blocks")
    ok &= expect(err, "banned by COPY_RULES — smartwatch", "smartwatch-for-Leiko blocks")
    ok &= expect(err, "banned by COPY_RULES — lower your blood pressure",
                 "outcome promise blocks")
    ok &= expect(err, "is not marked verified", "unverified stat blocks")
    ok &= expect(err, "days ago", "stale stat blocks")

    # a caption that does not end with leiko.health
    tail = copymod.deepcopy(GOOD)
    tail["cards"]["1a"]["caption"] = "Know the number. Check it often."
    err, _ = lint_issue(tail)
    ok &= expect(err, "caption must end with leiko.health", "caption tail rule blocks")

    # &nbsp; must not hide a banned word from the gate
    hide = copymod.deepcopy(GOOD)
    hide["slots"]["FACT_HEAD"] = "FDA&nbsp;listed"
    err, _ = lint_issue(hide)
    ok &= expect(err, "banned on card art", "entity-hidden banned term blocks")

    # ── the CLI path end to end, including Windows console/file encoding ─────
    with tempfile.TemporaryDirectory() as td:
        p = pathlib.Path(td) / "copy_selfcheck.json"
        p.write_text(json.dumps(GOOD, ensure_ascii=False), encoding="utf-8")
        r = subprocess.run([sys.executable, "leiko_lint.py", str(p)],
                           capture_output=True, cwd=pathlib.Path(__file__).parent)
        good_cli = r.returncode == 0
        print(("  ok   " if good_cli else "  FAIL ") +
              "CLI lints a UTF-8 copy file (curly quotes) without crashing")
        if not good_cli:
            print(r.stdout.decode("utf-8", "replace"))
            print(r.stderr.decode("utf-8", "replace"))
        ok &= good_cli

    print("\nSELFCHECK " + ("PASS — every gate held." if ok else "FAIL — a gate fell."))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
