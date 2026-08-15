# Prompt templates — the weekly machine, in copy-paste form

The Sunday workflow existed only as prose (`README_v3.md`) and as an unchecked
build item ("add the search lists to the Sunday task prompt"). These are that
prompt, plus the three others the plan actually calls for. Copy a block, fill
the `[brackets]`, run it.

**Rule zero for every prompt here:** `docs/COPY_RULES.md` is the rulebook and
`leiko_lint.py` is the enforcement. These templates deliberately do **not**
restate the banned-word list — a second copy would drift out of date and the
drift would be invisible. Every prompt tells its agent to read COPY_RULES
first, and nothing ships that the linter blocks.

Contents: **A** the Sunday run · **B** write an issue · **C** creator brief ·
**D** frame-swipe worksheet · **E** hook bank.

---

## A — The Sunday run (master prompt)

Run this once a week. It produces one issue, staged for approval.

```text
You are running the Leiko weekly content machine from the repo root.

Read first, in this order: CLAUDE.md · docs/COPY_RULES.md ·
docs/CONTENT_ARCHITECTURE.md. COPY_RULES is the rulebook; the server-side
voiceLint outranks it; leiko_lint.py is stricter than both on purpose and must
never be weakened to make a card pass.

Market for this issue: [NG | US | DIASPORA]      Issue number: [N]

STEP 0 — MINE IDEAS. Produce 3-5 candidate angles, each tagged with where it
came from. Sources, in priority order:
  1. Real customer questions — GET https://leiko.health/api/content/questions?days=7
     with header  Authorization: Bearer $CONTENT_INGEST_SECRET
     (returns question text, timestamp, intent, market — no personal data).
     Questions customers actually ask are the best MYTH / FACT_HEAD candidates.
  2. What people are saying publicly this week about blood pressure in the
     target market — myths repeated in comments, questions under health
     creators' posts, diaspora "checking on my parents" conversations.
  3. Timely hooks: World Hypertension Day (May 17), May Measurement Month,
     NCDC releases, salt/diet news, Detty December and gifting seasons,
     American Heart Month (Feb) for US.
  4. Competitor watch (mainly US): Meta Ad Library — hooks used, how long each
     ad has run, price points. Log 3-5 observations.
Write the shortlist to idea_shortlists/issue[N].md.

STEP 1 — READ THE SCOREBOARD. Open performance_log.md. Compute the running
average PER MARKET AND PER SURFACE (NG and US numbers are not comparable, and
neither are Instagram and TikTok). Apply the rule: a card at 2x+ the average is
a WINNER and may be remixed after ~90 days with fresh wording, never identical
copy; a card under half the average retires that angle for that market. Write
the one-line lesson. Weight Step 0's shortlist by what you find.

STEP 2 — WRITE THE COPY. Use Prompt B below to produce copy/copy_issue[N].json.
The chosen angles must come from the Step 0 shortlist.

STEP 3 — CHECK, RENDER, SEND (Windows: python, not python3):
    python leiko_lint.py    copy/copy_issue[N].json
    python generate_v3.py   copy/copy_issue[N].json out_issue[N]/
    python leiko_ingest.py  copy/copy_issue[N].json out_issue[N]/ --dry-run
  Fix every BLOCK at the source — never by weakening the linter. When the
  dry-run looks right, re-run without --dry-run to send.

STEP 4 — REPORT. Read the per-card result, not the HTTP code: OK = stored as
needs_review · BLOCKED = the site rejected the words · CHECK = a human must
eyeball it, NOT a pass · ERROR = missing field. Then tell the founder: the
three captions, every stat with its source URL, the Step 0 shortlist so he can
see why these angles, and the Step 1 lesson. He approves in the dashboard or
by Telegram. Nothing here publishes anything.
```

---

## B — Write an issue (`copy_issueN.json`)

```text
Write copy/copy_issue[N].json for market [NG | US | DIASPORA].

Read docs/COPY_RULES.md first and obey it exactly. Start from
copy/copy_issue_TEMPLATE.json.

THE ELEVEN SLOTS (design is LOCKED — only these change):
  STAT_A / STAT_MID / STAT_B   the big stat, e.g. "6" "in" "10"
  STAT_SUB                     max 2 lines, ~50 chars (linter blocks over)
  STAT_KICK                    under 20 chars (linter blocks over)
  MYTH                         max 3 short lines; the strikethrough lands on line 2
  FACT_HEAD / FACT_SUB         max 2 lines each
  GIFT_HEAD1                   "Check on"
  GIFT_HEAD2                   Mama or Papa — ALTERNATES each issue; check the
                               last issue and switch
  GIFT_BODY                    max 4 short lines, right-aligned
Use &nbsp; to control where a line breaks. The linter reads through entities,
so it cannot be used to hide anything.

THE THREE CARDS: 1a stat · 1b myth/fact · 1c gifting. Each needs a pillar
(educate | product | caregiver | founder — an invalid one is silently filed as
"product" by the server, so the linter blocks it), a title, and a caption.

CAPTIONS: 2-4 conversational sentences, ending with leiko.health. Tone per
COPY_RULES §7 — warm Nigerian English for NG and DIASPORA; warm plain American
English for US, same caring family voice, no Nigerian idioms.

STATISTICS — the part that fails most often. Every stat needs, in `sources`:
  body      WHO / NCDC / Nigerian Cardiac Society for NG and DIASPORA;
            CDC / AHA / NHANES for US. NEVER cross markets.
  url       a live link you actually opened this run
  figure    the exact number as the source states it
  retrieved YYYY-MM-DD, under 180 days old
  status    "verified" — only after you opened the link and confirmed it
Do NOT carry a number forward from an earlier issue on memory. Re-check it.
Set claims_a_stat true on any card that states a statistic.

Then run: python leiko_lint.py copy/copy_issue[N].json — and fix what it says.
```

---

## C — Creator brief (Phase 3, when recruiting creators)

```text
LEIKO — CREATOR BRIEF

WHO WE ARE. Leiko is a wrist blood-pressure device with a real inflating cuff.
It MEASURES blood pressure the same way a clinic cuff does — the oscillometric
method. It does not estimate. Positioning: "Blood pressure, measured — not
guessed." Product line: "A real cuff. A real number."

WHAT WE WANT FROM YOU. [1 video, 30-60s, vertical] on the angle: [angle].
Give us 3 different hooks for the same body so we can test which opens best
(see the hook bank). Raw footage rights included. Shot on a phone is fine —
real beats polished.

THE FEELING. Warm, calm, confident. A family that cares about each other.
Never salesy. Never frightening.

WHAT YOU MUST NEVER DO — this is a health brand and these are absolute:
  - Never say the device treats, cures, prevents, diagnoses, or lowers
    anything, or that it will improve someone's health.
  - Never use fear ("silent killer", "before it's too late", "dangerous").
  - Never read out or interpret anyone's real blood-pressure numbers, and
    never say a number is normal, high, or dangerous.
  - Never call Leiko a smartwatch, and never say or imply it is "cuffless" —
    that word describes competitors only.
  - Never mention regulators, approvals, certifications or standards of any
    kind, in any form.
  - Never invent a doctor, nurse, or expert, and never dress as one.
  - No fake countdowns, fake stock counts, or invented urgency.
If you are unsure whether something is allowed, ask before you film it.

WHAT WORKS. The cuff physically inflating on the wrist is our single best
visual — nobody expects it. The 30-second check woven into a real day. Sunday
calls home. "Do you know your number?"

DELIVERY. [date] · [rate] · Everything is reviewed before it goes anywhere.
```

---

## D — Frame-swipe worksheet (studying a winner)

Steal structure, never content. One row per video studied; keep them in
`idea_shortlists/`.

```text
Source & link          [creator, platform, views, date found]
Beginning / middle / end   [one line each]
Hook & open loop       [exact first line · what question it leaves open ·
                        when the loop closes]
Location & visuals     [setting, props, camera style]
Pacing                 [cut frequency · where it speeds up · any dead air]
Script trigger words   [the charged words doing the work]
On-screen text         [title style, caption rhythm]
Viewer feeling by stage [curious -> surprised -> reassured, etc.]
LEIKO ADAPTATION       [which pillar · which true story of ours · what we'd
                        change · compliance notes]
```

---

## E — Hook bank

Openers that hold a loop, use allowed verbs, and carry no fear. From the
playbook's Appendix C. **Every line below was run through `leiko_lint.py`'s
gate on 2026-08-15 and passes** — but a hook is only the first line, so lint
the finished caption anyway.

- "Do you know your number? Most people don't — and checking takes 30 seconds."
- "This just inflated on my wrist. Here's why that matters."
- "Your fitness band shows a blood pressure number. Ask it one question: did
  you measure that, or guess it?"
- "I stopped asking Mama 'how are you?' and started asking a better question."
- "The same method as the cuff in a clinic — on your wrist. Let me show you."
- "5,000 kilometres from home, I still know how Papa is doing every Sunday."
- "Everyone in this market has 30 seconds. Watch what she does with hers."
- "Before you buy Mama another wrapper this December… watch this."

Pair each with 2-3 delivery variations; the winning hook can be spliced onto
several bodies. For video, the founder-story package
(`Leiko_Founder_Story_Package.docx`) already carries three tested hooks for
the hero film.
