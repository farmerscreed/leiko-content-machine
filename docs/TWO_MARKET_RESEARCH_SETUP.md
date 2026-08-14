# Leiko Research & Analytics Setup — Direction for the Build Agent
(Covers the two Phase 1 loops from README_v3 — idea mining and performance
tracking — now extended to TWO markets: Nigeria and the United States.)

## 0. What changes with two markets
The content machine stays one pipeline, but every Sunday run now produces
market-tagged output. Each candidate angle, each performance row, and each
copy JSON is tagged NG or US. Do NOT blend the markets: a stat that is true
for Nigeria (NCDC/WHO Nigeria data) must never appear on a US card, and vice
versa (CDC/AHA data for US cards). The diaspora angle is the one deliberate
bridge — content aimed at Nigerians in the US buying for parents at home.
Tag those DIASPORA.

## 1. Step 0 setup — idea mining, per market
Build the Sunday task to run these searches and log results to
idea_shortlists/issueN.md:

NIGERIA (sources: NCDC releases, Nigerian health news, Nigerian health
creators/pages on FB & IG, Nairaland/X conversations):
- current BP myths being repeated in comments
- questions people ask under Nigerian doctors' posts
- timely hooks (World Hypertension Day, salt/diet news, NCDC data drops)

UNITED STATES (sources: CDC, AHA/heart.org, NHANES data briefs, US health
media, Reddit r/hypertension and r/AskDocs public threads):
- prevailing myths (e.g. "you'd feel symptoms", threshold confusion)
- seasonal hooks (American Heart Month = February, World Hypertension Day
  = May 17, holiday gifting season Nov-Dec)

DIASPORA (bridge): public conversations by Nigerians abroad about checking
on parents' health, remittances for medical bills, gifting home.

COMPETITOR WATCH (mainly US): check Meta Ad Library (facebook.com/ads/library
— public, no login) for active ads from Omron HeartGuide, YHE BP Doctor,
Fitvii, Huawei Watch D and similar. Note: hooks used, how long each ad has
run (long-running = working), price points shown. Log 3-5 observations.

Output per Sunday: 3-5 candidate angles PER MARKET, each tagged with source.

## 2. Step 1 setup — the scoreboard, per market
Data source: Meta Business Suite insights for the Leiko page(s).
Access options, in order of preference:
  a. Owner exports/screenshots weekly numbers into the project (2 min).
  b. Claude in Chrome session while owner is logged into Business Suite.
  c. (Later) Meta Graph API with a system-user token — only if the owner
     wants full automation; requires a Meta app with pages_read_engagement.
Maintain performance_log.md with columns:
  date | issue | card (1a/1b/1c) | market (NG/US/DIASPORA) | reach | saves |
  shares | link taps | verdict (WINNER / normal / retire)
Winner rule: 2x+ account average → eligible for remix after ~90 days.
Below half of average → retire the angle for that market.
Important: compute averages PER MARKET — US and NG numbers are not comparable.

## 3. Copy compliance — differences the writer must respect
- NG cards: sources = WHO, NCDC, Nigerian Cardiac Society. Tone = warm
  Nigerian English.
- US cards: sources = CDC, AHA, NHANES. Tone = warm, plain American English;
  keep the caring family voice, drop Nigerian idioms.
- BOTH markets: allowed verbs only (measure, check, know, track, monitor);
  never treat/cure/prevent/diagnose.
- CRITICAL US flag: ALL regulatory and certification language is banned
  outright, in every channel, US included — see COPY_RULES §4, which is the
  only rulebook on this. US copy must never imply clearance/approval or make
  clinical accuracy claims. Before any paid US campaign, the owner should get
  permissible wording checked by a regulatory adviser. Until then, US organic
  copy leans on the education + gifting angles, not device accuracy claims.
- Diaspora cards may use Nigerian stats (they concern the parent back home)
  and Nigerian warmth, but run in US placements.

## 4. Rendering & scheduling implications
- Same template, same masters. A US card is just a copy JSON with US-verified
  stats — file naming: copy_issueN_us.json vs copy_issueN_ng.json.
- Scheduling: separate audience targeting in Meta Business Suite (NG feed vs
  US feed vs US-based Nigerian diaspora interest targeting). The owner
  approves each batch as usual.
- WhatsApp agent (see WHATSAPP_AGENT_BRIEF.md) serves NG + diaspora buyers;
  for US domestic buyers plan email/IG DM support instead — WhatsApp
  penetration in the US is low. Note this as a phase-2 item.

## 5. Build checklist
[ ] Add market tag to idea_shortlists format and performance_log.md
[ ] Add the NG / US / DIASPORA search lists to the Sunday task prompt
[ ] Add Meta Ad Library competitor check to the Sunday task
[ ] Agree analytics access route (a, b, or c above) with the owner
[ ] Create copy_issueN_us.json variant path in the run instructions
[ ] Surface the regulatory-wording flag to the owner before any US paid ads
