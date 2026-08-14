# Leiko Content Machine — v3 (adds idea-mining + performance loops)

## What this is
Your approved "Leiko Social Set" turned into a self-rendering template — now with a
smarter Sunday brain. The design pipeline is UNCHANGED:
- masters/blank_1a|1b|1c.png — original exports with only per-issue text removed
- leiko_template_v2.html — original layout markup; text slots are {{TOKENS}}
- generate_v3.py — fills tokens from a copy JSON and renders 2160x2700 PNGs
- copy_issueN.json — one small file per weekly issue; this is ALL that changes

## Run
python3 generate_v3.py copy_issueN.json out_issueN/

## Slots & rules (unchanged — non-negotiable)
STAT_A / STAT_MID / STAT_B  — big stat ("1 in 3", "30 sec ✓")
STAT_SUB   — headline, max 2 lines (~50 chars)
STAT_KICK  — coral kicker, KEEP UNDER ~20 chars
MYTH       — quote, max 3 short lines; strikethrough lands on line 2
FACT_HEAD  — max 2 lines; FACT_SUB — max 2 lines
GIFT_HEAD1/2 — "Check on" + name (Mama/Papa alternate)
GIFT_BODY  — max 4 short lines, right-aligned
Fixed chrome (LEIKO, tags, footers, CTA bar) is baked into the blanks.

Copy rules: every statistic real and verifiable with source named (WHO, NCDC,
Nigerian Cardiac Society). Allowed verbs: measure, check, know, track, monitor.
Forbidden: treat, cure, prevent, diagnose, or any claim Leiko improves a
condition. Tone: warm Nigerian English, confident, caring, never salesy or
fear-mongering. Each card gets one conversational caption (2-4 sentences)
ending with leiko.health.

## Weekly scheduled task (Cowork) — v3 workflow
Every Sunday, in this order:

**Step 0 — Mine ideas (NEW).**
Before writing anything, search for what Nigerians are actually saying about
blood pressure this week: common myths being repeated, questions in comments on
Nigerian health pages/creators, diaspora "checking on parents" conversations,
and any timely hook (World Hypertension Day, salt/diet news, NCDC releases).
Also pull the running list of real customer questions from the WhatsApp agent
log (see WHATSAPP_AGENT_BRIEF.md) — questions customers actually ask are the
best MYTH / FACT_HEAD candidates. Output: a shortlist of 3-5 candidate angles,
each tagged with where it came from.

**Step 1 — Check the scoreboard (NEW).**
Pull Meta Business Suite insights for all previously published issues. For each
past card note: reach, saves, shares, link taps. Tag by angle (stat / myth-fact /
gifting) and by Mama vs Papa. Maintain a simple running file, performance_log.md:
one line per card, one "lesson" line per issue. Rule of thumb: a card that beat
the account average by 2x+ is a WINNER — eligible for remix after ~90 days
(same idea, fresh wording, never identical copy). A card below half of average
is retired as an angle.

**Step 2 — Write copy_issueN.json.**
Follow the slot rules and copy rules above. The chosen angles must come from
Step 0's shortlist, weighted by Step 1's lessons. Every stat verified; name the
source next to the draft in the approval note. Keep the issue-rotation spirit
(education stat → product stat → myth/fact → gifting; alternate Mama/Papa).

**Step 3 — Render.** python3 generate_v3.py copy_issueN.json out_issueN/

**Step 4 — Stage for approval.** Save the 3 PNGs to Notion/Drive as
"Leiko Issue N — pending approval" together with: the captions, the sources for
every stat, the Step 0 shortlist (so you see why these angles), and the one-line
Step 1 lesson.

**Step 5 — Notify.** Email that the batch is ready. You approve, then schedule
in Meta Business Suite (~10 min).

## Files this version adds
- performance_log.md — running scoreboard + lessons (created after first Step 1 run)
- idea_shortlists/ — one small file per issue with the mined candidate angles
Nothing in masters/, fonts/, or the template ever changes.
