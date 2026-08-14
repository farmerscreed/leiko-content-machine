# How the Leiko Content System Works
*Plain-English guide. Written 9 August 2026 · revised same day (§5, §6, §7, §8).*

---

## 1. The one-sentence version

Every week, I write the words for three Instagram/Facebook cards, check those
words against the brand rules, paste them into your locked design, and send the
finished pictures to your website — where they sit as **drafts waiting for your
approval**. Nothing ever goes public without you pressing approve.

---

## 2. The three systems, and who owns what

You have three moving parts. They are separate on purpose, and they meet in
exactly two places.

| System | Who runs it | What it does |
|---|---|---|
| **Content machine** (this one) | Me + you | Writes copy, renders cards, sends them |
| **Website / leiko.health** | The other AI agent | Receives cards, re-checks them, shows them in your dashboard |
| **WhatsApp agent** | You (partly built in Meta) | Answers customer questions, and feeds real questions back to me |

The two meeting points:

1. **The ingest API** — one web address on your site that I POST cards to.
2. **Supabase** — the shared database sitting behind the website. I never write
   to it directly (more on why in §7).

```
   Customer questions (WhatsApp)  ─┐
   What Nigerians/Americans are    ├──►  ME: write copy  ──►  lint  ──►  render
   saying online (Step 0)         ─┤         (words)        (gate 1)    (pictures)
   Last week's numbers (Step 1)   ─┘                                        │
                                                                            ▼
                                                          POST one card at a time
                                                                            │
                                                                            ▼
        YOU approve in the dashboard  ◄── Supabase ◄── voiceLint + vision gate
                     │                    (drafts)        (gate 2, on the site)
                     ▼
             Meta Business Suite → published
```

---

## 3. What I actually do each week (the five steps)

**Step 0 — Mine ideas.** Before writing a single word, I look at what people are
really saying: myths repeated in Nigerian health comments, diaspora "checking on
my parents" conversations, timely hooks (World Hypertension Day, NCDC releases),
and the real questions coming out of the WhatsApp agent. Output: 3–5 candidate
angles, each tagged with where it came from.

**Step 1 — Check the scoreboard.** Pull the numbers from Meta Business Suite for
everything already published: reach, saves, shares, link taps. A card that beat
the account average by 2x is a winner and can be remixed after ~90 days (same
idea, fresh words — never the identical copy). A card under half the average is
retired as an angle.

**Step 2 — Write the copy file.** One small JSON file per issue —
`copy_issueN.json`. This is the *only* thing that changes each week. It has
three sections:
- `meta` — which market (NG / US / DIASPORA), issue number, notes
- `slots` — the eleven text tokens that drop into the design
- `cards` — per card: the pillar, the title, the caption, and the sources

**Step 3 — Check the words** (`leiko_lint.py`). Explained in §5.

**Step 4 — Render the pictures** (`generate_v3.py`). Fills the tokens into the
locked HTML template, screenshots each card at 2160×2700.

**Step 5 — Send** (`leiko_ingest.py`). One card per request, three seconds
apart, to the ingest API. Each card lands as `needs_review`. You then approve in
`/admin/studio/cards` and schedule in Meta Business Suite (~10 minutes).

The three commands, in order:

```powershell
python leiko_lint.py    copy/copy_issue3.json
python generate_v3.py   copy/copy_issue3.json out_issue3/
python leiko_ingest.py  copy/copy_issue3.json out_issue3/
```

(`python`, not `python3` — Windows has no `python3` alias; the old spelling
failed outright on this machine.)

Add `--dry-run` to the last one to see exactly what would be sent, without
sending it.

---

## 4. The files, and what each one is for

| File | What it is |
|---|---|
| `COPY_RULES.md` | The rulebook (v4). Mirrors the site's `voiceLint`. If they disagree, the site wins and this file gets corrected. |
| `copy_issueN.json` | This week's words. The only file that changes weekly. |
| `leiko_lint.py` | The pre-flight checker. Catches bad copy on your machine before it's sent. |
| `generate_v3.py` | The renderer. Copy in, three PNGs out. |
| `leiko_template_v2.html` | The locked layout. Never edited. |
| `blank_1a/1b/1c.png` | The master artwork — watch screens blank and switched off. Never edited. |
| `leiko_ingest.py` | The sender. Talks to your website. |
| `ingest_log.jsonl` | A line per card sent, with its id and image path, so anything can be traced later. |
| `README_v3.md` / `INGEST_SETUP.md` | The run instructions. |

---

## 5. The gates — three of them, in order

This is the part worth understanding properly, because it's where the system
protects the brand.

**Gate 1 — `leiko_lint.py`, on your machine.** Runs before anything is sent.
It's deliberately *stricter* than the website. It blocks:
- every banned word (all FDA and regulatory terms, "diagnose", "treat", "cure",
  "predict", "prevent", fear language, `mmHg`, "certified", "cleared")
- "smartwatch" used for Leiko, and any outcome promise
- `STAT_KICK` over 20 characters, `STAT_SUB` over 50
- a caption that doesn't end with `leiko.health`
- **a statistic with no live source link, retrieved date, and verified status**
- a source older than 180 days
- an invalid pillar (which the site would otherwise silently file as "product")

It also catches sneaky ones: the site matches plain substrings, so "cure" fires
inside "secure". The linter tells you *which word* it landed inside, so the
message doesn't look insane.

**Gate 2 — `voiceLint`, on the website.** Not the same checks re-run — that was
wrong in the first draft of this doc. The relationship is:

- **Server blocks, I block too.** Every banned word `voiceLint` rejects,
  `leiko_lint.py` rejects first. If the two ever disagree, `voiceLint` wins and
  my file gets corrected. I do not fork it.
- **Server soft-flags, I hard-block.** "Cuffless" in *copy* only earns a
  `review_flag` on the server — the card still stores. My rule (COPY_RULES §5)
  refuses to send it at all unless the card carries an explicit
  `"competitor_contrast": true`, and refuses outright if "cuffless" and "Leiko"
  land in the same sentence.
- **I check, the server doesn't.** "Smartwatch" for Leiko, outcome promises,
  slot length limits, caption must end `leiko.health`, and the whole
  research-first rule (live URL + retrieved date + verified status + under 180
  days) are house rules. The server will happily accept a stat with no source.
  That gate exists only on my side, which is why skipping `leiko_lint.py` is
  never a shortcut.

The point of Gate 2 is that it can't be bypassed — including by a direct
database write, which is why we don't do those (§7).

**Gate 3 — the vision gate, on the website.** Looks at the *picture*, not the
words. Its main job: block any artwork showing a blood pressure reading on the
watch screen, or any "cuffless" wording baked into the art. If a hit comes back
starting with `image:`, the picture must change — re-writing the copy will not
fix it.

---

## 6. Reading the result of a send

| What you see | What it means |
|---|---|
| `OK` | Card is in the dashboard as `needs_review`. Go approve it. |
| `BLOCKED` | The site rejected the words. Fix the copy, re-render, re-run. |
| `CHECK` | Stored, but a human must read it. **Not a pass.** |
| `ERROR` | A required field was missing. |

How the sender decides which word to print:

- `ERROR` — the response body's `ok` is false.
- `BLOCKED` — status came back `lint_failed`.
- `CHECK` — **any** non-empty `review_flags` array, whatever the prefix. It does
  not enumerate prefixes, so `image-not-auto-checked:`, `cuffless-claim:` and
  `possible-testimonial:` are all covered by the same rule. The prefix is only
  used for display.
- `OK` — everything else.

Two things that trip people up, and one gap:

- **HTTP 200 does not mean the card passed.** The site stores a failed card and
  reports the failure inside the response body. The sender reads the per-card
  status, not the HTTP code.
- **Re-sending is safe** — same issue number + slot + market overwrites in place.
  Never invent a new slot to dodge a collision. Since the duplicate-insert race
  in `findCardId` was fixed (2026-08-09, confirmed in the website code), this
  holds for **timed-out cards too**: a retry supersedes rather than duplicating.
- **Fixed 2026-08-14:** `OK` now requires `status == "needs_review"` exactly.
  Any other status marks the card `ERROR`, prints `CONTRACT BREAK`, and the run
  exits non-zero. Proven against `mock_ingest_server.py` with a forced status.

---

## 7. Why I don't write straight to the database

Supabase would happily accept a card written directly to it — and that card
would skip `voiceLint` and the vision gate entirely. One bad row, no gate. So
the rule is: **everything goes through the ingest API, always.** The API is the
only door, and the gates are behind it.

Authentication is by a shared secret, `CONTENT_INGEST_SECRET`, sent as a Bearer
token. It lives in your shell session, never in a file, never in a commit.
**I have never held this value and cannot see it** — it is read from your
environment at run time by `leiko_ingest.py`. You confirmed on 9 Aug 2026 that
it is now set; I have no way to verify that independently, or to tell whether
the value in place is the original or the rotated one.

On your machine (Windows PowerShell) that's:

```powershell
$env:CONTENT_INGEST_SECRET = 'the-secret'
```

`INGEST_SETUP.md` now shows both syntaxes (corrected 2026-08-14).

---

## 8. Where things stand right now

**Done:** rulebook v4, local linter, renderer hardened to refuse ambiguous
masters, per-card sender with correct response handling, corrected v4b masters
(blank watch screens), and issue 3 copy written with WHO sources verified and
dated.

**Closed since the first draft (your confirmation, 9 Aug 2026):**
`CONTENT_INGEST_SECRET` is set · PR #70 merged, so the duplicate-insert race in
`findCardId` is fixed and retry-after-timeout is safe · transport decided.

**Still open:**

1. **Transport not recorded here yet.** You've told me it's decided but not
   which way — direct Vault-to-worker via `pg_net`, or the proxy hop through the
   Edge Function. Tell me and this line gets replaced with the actual answer.
   It matters because it determines whether the Edge Function is still a place
   the secret has to exist.
2. **The masters are the wrong size.** All three `blank_1*.png` are **980×1232**.
   The template declares `background-size: 1080px 1350px` and renders at
   `device_scale_factor: 2` → 2160×2700 output. So the artwork is scaled
   **2.204× horizontally and 2.192× vertically** off the source. Two consequences:
   - roughly a 10% upscale before the 2× — the product photography is resampled,
     never sampled 1:1;
   - 980×1232 is aspect ratio 0.7955, not 0.8, so it is also being stretched
     ~0.6% wider than tall.

   The token text is drawn by Chromium at full resolution and stays crisp — so
   the symptom is sharp type sitting on slightly soft product shots. Fix is to
   re-cut the masters at 2160×2700 (or at minimum 1080×1350, exact ratio 0.8).
   Nothing in the template or the copy needs to change.
3. ~~`leiko_ingest.py` has not caught up with PR #70.~~ **Closed 2026-08-14:**
   the sender's timeout messages now say a re-run is safe (supersede in place).
   It still never auto-retries a timeout — a deliberate choice, since the
   payload just spent 120s failing — but the human is no longer warned off
   re-running.
4. ~~`OK` should require `status == "needs_review"`.~~ **Closed 2026-08-14** —
   see §6.
5. Any pre-v4b card 1c images still sitting in your local folders should be
   deleted. Two different versions of a master is the one failure that silently
   produces a wrong card.
6. **The masters are JPEGs wearing a .png name.** All three `blank_1*.png` are
   actually JPEG files (~50 KB, heavily compressed) at 980×1232. Chromium
   renders them anyway, but the compression artifacts and the erasure ghosting
   (faint pink smears where the old text was removed) are visible on final
   cards. The fix is the same as item 2: re-cut clean masters at 2160×2700 from
   the original design exports — only the founder has those.

---

## 9. One thing I need to flag

The brief I was given describes Leiko as an *"FDA-listed blood pressure
smartwatch"*. Both of those are blocked by your own v4 rules, and I have not
used either anywhere:

- **All FDA and regulatory terms are banned on every channel, no exceptions.**
- **"Smartwatch" is banned as a noun for Leiko** (it's fine for competitors).

I've kept to the v4 rulebook, since that's the version `voiceLint` mirrors — but
you may want to update that older brief so the two don't drift apart. The other
constant: **Leiko has a real inflating cuff.** "Cuffless" describes competitors
only, never Leiko, and blood pressure is *measured* while activity is *tracked* —
those two never blur.
