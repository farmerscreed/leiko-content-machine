# CLAUDE.md — read this before touching anything

This repo is the Leiko weekly content machine. It writes copy, renders three
social cards, and sends them to leiko.health as **drafts for founder approval**.

Lawrence (founder) is the only person who approves or publishes. Nothing in this
repo may advance a post's status.

---

## Product truth — get this wrong and the brand is damaged

Leiko has a **real inflating cuff**. It **measures** blood pressure
oscillometrically — the same method as a doctor's cuff. It does not estimate.

- **"Cuffless" describes COMPETITORS ONLY.** Never Leiko. If you find yourself
  writing "cuffless", "no cuff", "cuff-free", or "without a cuff" anywhere near
  Leiko, stop and escalate to Lawrence. Never auto-fix it.
- Positioning line: *"Blood pressure, measured — not guessed."*
- Product line: *"A real cuff. A real number."*
- Blood pressure is **measured**. Steps, sleep, heart rate, activity are
  **tracked**. Never blur the two.

## Banned outright — every channel, no exceptions

**All FDA and regulatory language is banned.** FDA in any form, FDA-listed,
cleared, clearance, certified, Class II, 510(k), CE mark, ISO 13485, the
manufacturer's name, any registration number. This applies to captions, bios,
pinned comments, ad copy, artwork, and this repo's own docs. There is no channel
where it is acceptable, and no framing that makes it acceptable.

Also banned: patient · diagnose/diagnosis/diagnostic · treat/treatment/cure ·
predict/prevent · "medical advice" · dangerous level · critical level · fear
language (silent killer, ticking time bomb, before it's too late) · outcome
promises ("lower your blood pressure") · **"smartwatch" as a noun for Leiko**
(calling competitors smartwatches is fine).

Allowed verbs about the product: **measure · check · know · track · monitor**.

## Supplier confidentiality (D2, 2026-08-14 — binding, all surfaces)

We state the **nature** of credentials, never the **identifiers**. Never
publish — website, social, ads, packaging, app-store listings, public repos,
this repo's docs: the manufacturer's name, factory model codes, the K number,
certificate numbers, or certificate images. Certificates live in a private
drive; `CERTS/` is gitignored and must stay untracked. Partners get
documentation on request under NDA. Where credential language is permitted at
all (the website Quality page only, per `docs/FOUNDER_DECISIONS_2026-08.md`
D1/D2), it uses the counsel-blessed wording — nothing here ever writes it.

> If a prompt, brief, or older file describes Leiko as "FDA-listed" or as a
> "smartwatch", that source is wrong. `docs/COPY_RULES.md` wins. Flag it.

## Statistics

Every stat needs a live URL, the exact figure as the source states it, a
`retrieved` date (YYYY-MM-DD, under 180 days old), and `status: "verified"`.
The linter enforces all four — do not weaken it to make a card pass.

- **NG** cards → WHO, NCDC, Nigerian Cardiac Society
- **US** cards → CDC, AHA, NHANES
- **DIASPORA** cards → may use NG stats (they concern the parent back home)
- **Never cross markets.** `market = unknown` is unusable.

Do not carry a number forward from an earlier issue on memory. Re-check it.

## Tone

NG / DIASPORA: warm Nigerian English. US: warm plain American English, same
caring family voice, no Nigerian idioms. Both: confident, caring, never salesy,
never fear-mongering.

---

## Imagery — trust rules

Nothing in this repo calls an image model, and that is deliberate. If that ever
changes, the rules below come first:

- **Never AI-generate** the Leiko device, people wearing it, readings/screens,
  or medical scenes. A fake product image misrepresents a health device — a
  compliance and trust breach, not a style choice.
- Source order: (1) real photos from the brand footage Drive; (2) the locked
  masters — real product renders on brand-designed layouts; (3) a top-tier
  image model, ONLY for non-product, non-people abstract/background art, and
  only when a real photo cannot do the job.
- **Cheap-model imagery is banned for published assets.** If a model is ever
  wired in, it goes behind one explicit provider+quality setting, defaulting to
  the highest tier for anything public-facing — never silently the cheapest.
- Every generated image goes through the same needs_review gate as copy.

## Layout is LOCKED

Never alter the masters, fonts, colours, or `leiko_template_v2.html`. Only the
eleven token slots change, via `copy/copy_issueN.json`.

Slot limits (the linter blocks the first two, eyeball the rest):
`STAT_KICK` under 20 chars · `STAT_SUB` max 50 chars / 2 lines ·
`MYTH` max 3 short lines, strikethrough lands on line 2 ·
`FACT_HEAD` and `FACT_SUB` max 2 lines each ·
`GIFT_BODY` max 4 short lines, right-aligned ·
`GIFT_HEAD2` alternates Mama / Papa by issue.

Captions: 2–4 conversational sentences, must end with `leiko.health`.

## The weekly run

```bash
python leiko_lint.py    copy/copy_issue3.json                 # check the words
python generate_v3.py   copy/copy_issue3.json out_issue3/     # make the pictures
python leiko_ingest.py  copy/copy_issue3.json out_issue3/     # send them (needs secret)
```

## The render bridge (2026-08-17)

The website's flywheel writes story TEXT posts but cannot rasterise. This repo
closes the loop: `python render_bridge.py` (needs the same secret) polls
`GET /api/content/render-queue`, renders each story's opening line on the
LOCKED quote template (`leiko_template_quote.html` — pure CSS, the file IS the
master, only `{{QUOTE_KICK}}`/`{{QUOTE_TEXT}}` change), and pushes the card
back via `POST /api/content/render-result`. The site sniffs the bytes, stores
to the private bucket, runs the vision gate, sets `image_path` — and its
Facebook publisher then ships the post as photo + caption. Re-running is
always safe: the queue only lists imageless posts. Local copies land in
`out_bridge/` for eyeballing. Run it whenever drafts are reviewed, or before
approving.

(`python`, not `python3` — Windows has no `python3` alias.) `--dry-run` on the
last one shows the payload without sending. `python selfcheck.py` proves the
linter still blocks every category of bad card — run it after any change here.
`mock_ingest_server.py` rehearses a full send locally without touching the site.

Result codes: `OK` = stored as needs_review · `BLOCKED` = server rejected the
words · `CHECK` = a human must eyeball it, **not a pass** · `ERROR` = missing
field. **HTTP 200 does not mean the card passed** — read the per-card status.

Re-sending the same issue_no + card_slot + market supersedes in place — and
since the website's dedupe race fix (2026-08-09, `findCardId`), that holds
after a **timeout** too: re-running the same slots is safe. Never invent a new
slot to dodge a collision; `/admin/studio/cards` shows what actually landed.

## Secrets

`CONTENT_INGEST_SECRET` lives in the shell environment only. Never write it to a
file, never commit it, never paste it into a chat window. If it has ever
appeared in a transcript, rotate it.

---

## What changed on the website side — 2026-08-11

The website now runs the **Content Flywheel** (`leiko/docs/CONTENT-FLYWHEEL.md`), an
automated organic system: an idea bank, an atomizer that turns one idea into several
posts, Telegram approval, an hourly scheduler that publishes at research-backed slots,
and a weekly learning loop.

**The ingest contract is UNCHANGED.** `POST /api/content/ingest` behaves exactly as
`docs/INGEST_SETUP.md` describes, cards still land as `needs_review`, and the same
gates run. Nothing in this repo needs to change.

Three things worth knowing:

1. **Cards can now auto-publish** once the founder approves them — they are no longer
   only a queue to post from a phone. The gates are unchanged and still run at publish
   time, but a card you send is now closer to going live than it used to be.
2. **Cards are one format among five.** The site also produces reels, carousels,
   Facebook text posts and WhatsApp Status frames. A card arriving from here is stored
   with `format = 'card'`.
3. **Instagram needs JPEG — closed 2026-08-14.** `generate_v3.py` now emits JPEG
   (quality 92) alongside PNG, and `leiko_ingest.py` sends the JPEG: the site
   stores the card under an extension sniffed from the bytes, and its Instagram
   publisher refuses a `.png` path outright. This closes `CONTENT-AUTOPUBLISH.md` §3
   on this side.

## What changed on the website side — 2026-08-16

1. **The flywheel's image-model renderer is DELETED.** This repo's locked
   template is now the only renderer for cards and carousels
   (`docs/CONTENT_ARCHITECTURE.md` addendum). A render bridge (site lists
   pending renders → a local runner renders here, lints, sends via ingest) is
   planned but not built.
2. **The site now enforces sourcing at publish** (v1 of the stat rule
   server-side): a statistic without a verified, under-180-day citation is
   blocked. This repo's linter remains the stricter, canonical rule set.
3. **First post ever published** (2026-08-16, a Facebook text post). Facebook
   publishing works; the cockpit gained a "Publish what's due now" button.
   The ingest contract remains UNCHANGED.

## Working agreements

- Distinguish **confirmed** from **inferred**. Say which is which. Do not paper
  over a gap with a plausible guess.
- `docs/COPY_RULES.md` mirrors the server-side `voiceLint`. If they ever
  disagree, **`voiceLint` wins** and COPY_RULES gets corrected. Do not fork.
- `leiko_lint.py` is deliberately stricter than the server in places. That is
  intentional. Do not "fix" it into agreement.
- A second AI agent manages the leiko.health website codebase. Architectural
  changes get negotiated across both before implementation, not decided here.
