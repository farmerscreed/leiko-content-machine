#!/usr/bin/env python3
"""perf_log.py — appends to performance_log.md. Nothing more.

  python perf_log.py card <issue> <slot> <market> <surface> <angle> <reach> [saves] [shares] [taps]
  python perf_log.py lesson <issue> "what this issue taught us"

Examples:
  python perf_log.py card 3 1a NG IG myth-fact 1840 41 12 9
  python perf_log.py lesson 3 "Myth cards out-save stat cards two weeks running."

Verdict is suggested automatically once a market+surface has 3 rows of history:
reach ≥ 2× the running average = WINNER, < ½ = retire, else normal. Until then
it writes “–”. The log is a plain text file — edit it freely; this script only
ever appends.
"""
import datetime as dt
import pathlib, re, sys

LOG = pathlib.Path(__file__).resolve().parent / "performance_log.md"


def rows(text):
    out = []
    for line in text.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 11 and cells[0] not in ("date", "---"):
            out.append(cells)
    return out


def verdict(text, market, surface, reach):
    history = [float(r[6]) for r in rows(text)
               if r[3] == market and r[4] == surface and r[6].replace(".", "").isdigit()]
    if len(history) < 3:
        return "–"
    avg = sum(history) / len(history)
    if reach >= 2 * avg:
        return "WINNER"
    if reach < avg / 2:
        return "retire"
    return "normal"


def main(argv):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    text = LOG.read_text(encoding="utf-8")

    if argv[:1] == ["card"] and len(argv) >= 7:
        issue, slot, market, surface, angle, reach = argv[1:7]
        saves, shares, taps = (argv[7:10] + ["0", "0", "0"])[:3]
        market = market.upper()
        if market not in {"NG", "US", "DIASPORA"}:
            sys.exit(f"market {market!r} must be NG, US or DIASPORA — never mix markets")
        v = verdict(text, market, surface, float(reach))
        row = (f"| {dt.date.today().isoformat()} | {issue} | {slot} | {market} "
               f"| {surface} | {angle} | {reach} | {saves} | {shares} | {taps} | {v} |")
        # append directly under the last scoreboard row so lessons stay below
        lines = text.splitlines()
        last = max(i for i, l in enumerate(lines) if l.lstrip().startswith("|"))
        lines.insert(last + 1, row)
        LOG.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(row)
        if v == "WINNER":
            print("WINNER — remixable after ~90 days: same idea, fresh wording, never identical copy.")
        elif v == "retire":
            print("retire — drop this angle for this market.")
        return 0

    if argv[:1] == ["lesson"] and len(argv) >= 3:
        line = f"- issue {argv[1]} ({dt.date.today().isoformat()}): {' '.join(argv[2:])}"
        LOG.write_text(text.rstrip() + "\n" + line + "\n", encoding="utf-8")
        print(line)
        return 0

    sys.exit(__doc__)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
