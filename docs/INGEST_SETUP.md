# Sending cards to leiko.health — setup and weekly run

## One-time setup

1. Put these in the project folder: `leiko_lint.py`, `leiko_ingest.py`,
   and the updated `generate_v3.py`.
2. Replace the three masters with the black-screen versions
   (`blank_1a.png`, `blank_1b.png`, `blank_1c.png`). Delete the old ones —
   if both versions sit in the folder the renderer may pick the wrong one.
3. Get `CONTENT_INGEST_SECRET` from whoever runs the website. Put it in your
   shell, never in a file that gets shared or committed:

   ```powershell
   $env:CONTENT_INGEST_SECRET = 'the-secret'   # Windows PowerShell
   ```
   ```bash
   export CONTENT_INGEST_SECRET='the-secret'   # mac / Linux
   ```

## The weekly run — three commands

```
python leiko_lint.py    copy/copy_issue3.json                 # check the words
python generate_v3.py   copy/copy_issue3.json out_issue3/     # make the pictures
python leiko_ingest.py  copy/copy_issue3.json out_issue3/     # send them
```

(`python` on Windows; on mac/Linux the same commands may be `python3`.)

Add `--dry-run` to the last one to see exactly what would be sent without
sending it.

## How to read the result

| What you see | What it means |
|---|---|
| `OK` | Card is in the dashboard as `needs_review`. Go and approve it. |
| `BLOCKED` | Website rejected the words. Fix the copy, re-render, re-run. |
| `CHECK` | The picture check could not run. **Not a pass** — eyeball it yourself. |
| `ERROR` | A required field was missing. |

The command finishes with exit code `0` only if every card came back clean.

Two things worth knowing:

- **HTTP 200 does not mean the card passed.** The site stores a bad card and
  tells you it failed. The client reads the per-card status, not the HTTP code.
- **Re-sending is safe.** The same issue number + slot + market overwrites the
  existing card instead of making a duplicate. Never invent a new slot to dodge
  a collision.

Every send is appended to `ingest_log.jsonl` with the card's id and image path,
so any card can be traced back later.

## The copy file (v2 shape)

```
meta   — market (NG / US / DIASPORA), issue_no as a NUMBER
slots  — the eleven design tokens, unchanged
cards  — per card: pillar, title, caption, sources
```

The renderer still reads `slots`, so nothing about the design changes. Old flat
copy files still work.

## What the pre-flight checker refuses to let through

- Every banned word the website blocks — including the easy-to-miss ones:
  `mmHg`, `cleared`, `certified`, `predict`, `prevent`, any bare `FDA`,
  and anything calling Leiko cuffless.
- `smartwatch` used for Leiko, and outcome promises. These are our own rules,
  stricter than the website's.
- `STAT_KICK` over 20 characters, `STAT_SUB` over 50.
- A caption that does not end with leiko.health.
- **A statistic with no source URL.** This is deliberate. A number cannot go
  out until you have pasted the link that proves it.
- A pillar that is not one of the four valid ones — otherwise the website
  silently files the card as `product`.

## Testing without touching the live site

`mock_ingest_server.py` imitates the website locally. Run it, point
`LEIKO_INGEST_URL` at `http://127.0.0.1:8787/api/content/ingest`, and you can
rehearse a full send safely.
