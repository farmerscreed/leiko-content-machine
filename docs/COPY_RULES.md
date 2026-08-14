# Leiko Copy Rules — v4 (mirrors `voiceLint`; codebase is the source of truth)

If this file and `voiceLint` ever disagree, `voiceLint` wins and this file is
corrected. Do not fork.

## 1. Product truth (P0 — highest priority)
Leiko has a REAL INFLATING CUFF. It MEASURES blood pressure by the oscillometric
method — the same method as a doctor's cuff. The cuff inflates around the wrist,
holds, deflates, and reports a measured number.

- "Cuffless" describes COMPETITORS ONLY. Never Leiko. Competitors estimate
  optically from the pulse; Leiko does not estimate.
- Positioning line: "Blood pressure, measured — not guessed."
- Product line: "A real cuff. A real number."
- Never write "no cuff", "without a cuff", "cuff-free", or anything implying
  Leiko estimates rather than measures.

## 2. Precision rule
Blood pressure is MEASURED (real cuff). Steps, sleep, heart rate and activity
are TRACKED. Never blur the two into one claim.

## 3. Allowed verbs (about the product)
measure · check · know · track · monitor

## 4. Banned outright
- patient
- diagnose / diagnosis / diagnostic
- treat / treatment / cure
- predict / prevent (disease)
- fear language: silent killer, ticking time bomb, before it's too late
- "medical advice"
- dangerous level / critical level
- outcome promises ("lower your blood pressure", "improves your BP")
- ALL FDA and regulatory terms, no exceptions, no channel exempt:
  FDA (any form) · FDA-listed · cleared · clearance · certified · Class II ·
  510(k) · CE mark · ISO 13485 · the manufacturer's name · any registration number
- "smartwatch" as a noun for Leiko (calling COMPETITORS smartwatches is fine)

## 5. Flag for human review
- "cuffless" applied to Leiko — always an error; escalate, never auto-fix silently

## 6. Statistics
Every statistic real, verifiable, and source-named with a URL.
- NG cards → WHO, NCDC, Nigerian Cardiac Society
- US cards → CDC, AHA, NHANES
- DIASPORA cards → may use NG stats (they concern the parent back home)
- NEVER cross markets. A `market = unknown` input is unusable for either market.

## 7. Tone
NG / DIASPORA: warm Nigerian English. US: warm, plain American English, same
caring family voice, no Nigerian idioms. Both: confident, caring, never salesy,
never fear-mongering.

## 8. Slot limits (design is locked)
STAT_A / STAT_MID / STAT_B — big stat
STAT_SUB — max 2 lines (~50 chars)
STAT_KICK — under ~20 characters
MYTH — max 3 short lines; strikethrough lands on line 2
FACT_HEAD — max 2 lines · FACT_SUB — max 2 lines
GIFT_HEAD1/2 — "Check on" + Mama/Papa (alternate)
GIFT_BODY — max 4 short lines, right-aligned
Captions: 2-4 conversational sentences, ending with leiko.health.

## 9. Publishing posture
Every row written to `content_posts` has `status = 'needs_review'`. This side
never advances status. Approval happens only in the founder's dashboard.
