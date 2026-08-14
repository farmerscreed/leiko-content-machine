# Leiko Content Machine

Weekly social card pipeline for [leiko.health](https://leiko.health) — writes
copy, renders three cards, and posts them to the site dashboard as
**drafts awaiting founder approval**. Nothing here publishes anything.

> **Read [`CLAUDE.md`](CLAUDE.md) first.** It holds the non-negotiable brand and
> compliance rules. Claude Code loads it automatically at session start.

**This repo must be private.** It contains unreleased copy, brand rules, and the
ingest architecture.

---

## Structure

```
CLAUDE.md                  guardrails — brand truth, banned language, run book
leiko_lint.py              pre-flight gate; mirrors server-side voiceLint
generate_v3.py             fills tokens → renders PNG + JPEG via Playwright
leiko_ingest.py            POSTs cards to /api/content/ingest, one per request
selfcheck.py               proves the linter still blocks every bad-card class
mock_ingest_server.py      local stand-in for the site; rehearse a send safely
perf_log.py                appends scoreboard rows / lessons to performance_log.md
performance_log.md         the running scoreboard (winner ≥2× avg, retire <½)
leiko_template_v2.html     LOCKED layout; {{TOKENS}} are the only variables
masters/                   LOCKED artwork (blank_1a / 1b / 1c)
copy/copy_issueN.json      the only file that changes each week
docs/COPY_RULES.md         canonical rulebook (v4) — also governs WhatsApp agent
docs/INGEST_SETUP.md       send setup, result codes, failure modes
docs/README_v3.md          the Sunday workflow incl. idea-mining + scoreboard
docs/AUDIT_2026-08.md      the 2026-08 audit: findings, keep/fix/kill table
docs/BRAND_REVIEW_2026-08.md          website+funnel review vs the playbook
docs/PROPOSALS_FOR_WEBSITE_AGENT.md   cross-repo asks; nothing changed unilaterally
```

## Setup

```bash
python -m pip install playwright
python -m playwright install chromium
```

```powershell
$env:CONTENT_INGEST_SECRET = '...'   # Windows — shell only, never in a file
```
```bash
export CONTENT_INGEST_SECRET='...'   # mac / Linux
```

Fonts download automatically on first render. `masters/` and the template are
already in place; do not add a second copy of a master — the renderer refuses to
guess between two versions and will stop.

## Weekly run

```bash
python leiko_lint.py    copy/copy_issue3.json
python generate_v3.py   copy/copy_issue3.json out_issue3/
python leiko_ingest.py  copy/copy_issue3.json out_issue3/     # --dry-run to preview
```

(`python` on Windows; mac/Linux may need `python3`.) The renderer emits PNG and
JPEG; the sender ships the **JPEG** — Instagram refuses PNG and the site stores
whatever bytes actually arrive. Exit code `0` only when every card came back
clean. See `docs/INGEST_SETUP.md` for what `OK` / `BLOCKED` / `CHECK` / `ERROR`
mean — `CHECK` is **not** a pass.

After any change to the scripts: `python selfcheck.py`.

## Open items

Carried over, not yet resolved:

- [ ] Rotate `CONTENT_INGEST_SECRET` — a previous value was exposed in a chat transcript
- [ ] **Masters need re-cutting** — the three `blank_1*.png` are heavily-compressed
      JPEGs (misnamed .png) at 980×1232, upscaled ~2.2× at render, with visible
      erasure ghosting on final cards. Re-export clean masters at 2160×2700 from
      the original design files (founder has them). Layout stays LOCKED.
- [ ] Confirm transport architecture (working assumption: direct `pg_net`, Edge Function proxy retired)
- [ ] Run the vision gate against the old sample PNGs
- [ ] Decide whether a BMC peer-reviewed meta-analysis counts as a valid NG stat source, or WHO/NCDC/NCS only
- [ ] `idea_shortlists/` gets created on the first real Step 0 run (one small file per issue)
