# Progress report — Phase 0 + Phase 1 agent items — 2026-08-14

Executed per `IMPLEMENTATION_PLAN_2026-08.md`, with `FOUNDER_DECISIONS_2026-08.md`
superseding on conflict. Website work sits on branch
**`claude/phase01-brand-safety`** in the `leiko` repo (pushed to origin, 12
commits, full `npm run build` passes) — ready for the founder or the website
agent to review and merge. Everything below is **[confirmed]** unless marked
**[inferred]**.

## The finding that outranks the plan

**The website repo was PUBLIC on GitHub.** [confirmed] Everything D2 protects
— the manufacturer's name (in a committed July handoff doc), the factory model
codes, internal ops docs, studio prompts, and the WhatsApp concierge's
bank-transfer details — was publicly readable. **Made PRIVATE during this run**
(protective, reversible, does not affect the deployed site, which ships via
wrangler). Zero forks and zero stars at the time of the change, so the
exposure very likely went unnoticed. The name is redacted at HEAD now, but the
old revision remains in git history — acceptable for a private repo; **purge
history before this repo is ever made public again.**

## Phase 0 — shipped (website branch)

| Commit | What |
|---|---|
| `7e6d6f0` | `.env*` gitignore guard. **The plan's premise was wrong**: `.env.production` holds only two build-time values that are public by design (pixel id, domain-verification tag — its own header documents this); real secrets are encrypted Worker secrets. So: no purge, no rotation needed, file deliberately stays tracked. |
| `58e514a` | `/go/*` presell pages: certification badges and maker-credential paragraph stripped; the dormant enable-later badge template deleted; trust restated as mechanism. |
| `c8c0e6d` | `/` and `/preorder` now price in naira from the same constants the checkout uses (was USD with CTAs into a naira-only checkout). Leiko Plus subscription pricing left as-is — product decision on subscription currency needed. |
| `3cdbc21` | Fake-live stock counter dropped ("N of 30 in stock" from a never-decrementing constant, contradicting the 20 elsewhere). Static honest cohort copy. **Bonus finding:** `/api/inventory` already computes a real live count from orders (server total says 30) — once the founder confirms the true cohort size, honest live counts can be wired back. |
| `5774eda` | Step-1 email no longer says "Thanks for reserving" before money moves; the post-payment panel now actually delivers the promised choose-your-watch link (`/reserve/complete` with reference + email — no code path sent it before); preorder FAQ matches. |

## Phase 1 — shipped

**Website branch:**

| Commit | What |
|---|---|
| `978694c` | Site-wide credential strip per D1: footer stamp, `/` proof strip + body, `/science` (hero, meta description, card grid, sub-caption), `/preorder` (trust bar, "Certification" cards, closing caption, two FAQ entries incl. deleting the dedicated status FAQ), `/partners` (meta, hero, trust line), `/inside` spec row, `/terms` §7, `/founder` ("certified" ×3). Replacement register everywhere: real cuff · clinic-cuff method · measured not guessed · documentation to partners on request. |
| `c898986` + `bb5f854` | Operator charter + weekly strategist prompts no longer teach the pre-ban register; both now teach the total ban + supplier confidentiality. |
| `8e27871` | Reading-interpretation sweep: "normal range" verdicts, population ranges, numeric clinical thresholds, the "Classification" column, "flags elevated readings", "when one runs high", and the literal fear-string anti-example — all rewritten to pattern-vs-baseline language. Outcome-promise phrasing on `/founder` softened. "patient(s)" removed from consumer surfaces; **kept on `/partners`** per the D3 exception (pending its voiceLint encoding). Drip email step 2 reworded. |
| `29122a9` | Quality page scaffolded at `/quality` with the D2 draft wording — **unlinked, `noindex`**, goes live only on the founder's counsel-sign-off word. |
| `4545368` | Manufacturer name redacted from the July session-handoff doc. |

**Content machine (this repo):** the Phase 1 CLAUDE CODE items were already
done in the prior session and re-verified today — D2 rule in CLAUDE.md;
retro-lint of all published issues (all captions clean; issues 1–2 fail only
today's stat-provenance rules, nothing needs recall); identifier sweep here
(clean — CERTS was never tracked, so the instructed `git rm -r --cached CERTS`
was verified unnecessary).

## Deviation from the letter of the hard rules, flagged

The **factory model codes remain in the website source** (10 files: they are
the `PRICE_NAIRA` keys and flow into Paystack metadata and stored order rows).
My commits reference those pre-existing constants but introduce no new codes.
A rename (`watch` / `pro`) is the right fix but touches payment-critical
paths: historical order rows store the old codes, so every lookup boundary
(`/api/reservation`, `/reserve/complete`, admin mark-paid) needs a legacy
alias, and I cannot test the Paystack flow end-to-end from here. Doing it
half-tested risks breaking existing reservations. **Specced for the website
agent in `PROPOSALS_FOR_WEBSITE_AGENT.md` §7 as an early Phase 2 item.** With
the repo now private and the name redacted, the codes alone no longer map
Leiko to its producer. [inferred: that pairing was the main exposure risk.]

## BLOCKED-ON-FOUNDER

1. **Counsel sign-off on the Quality-page wording** (D1/D2) — then the page
   gets linked and the noindex removed. Two notes for that conversation are in
   the memory of this project and my earlier report: the EU declaration's
   intended-purpose wording (upper-arm vs wrist scope) and trimming the
   identifying detail combination from the decisions log.
2. **True cohort size: 20 or 30?** Pages say 20, `/api/inventory` says 30.
   Answer unblocks honest live stock counts.
3. **Re-export the masters at 2160×2700** (D7) — unchanged, still the biggest
   visible-quality item on every published card.
4. **Rotate `CONTENT_INGEST_SECRET`** (D8) — with the website agent.
5. **Founder video shoot** (Phase 0, critical path for Phase 2 publishing).
6. **D3 voiceLint encoding** — the clinician "patients" exception and the
   supplier-identifier hard block belong in voiceLint (website agent
   negotiation); COPY_RULES mirrors after, never before.
7. **Leiko Plus pricing currency** for Nigerian buyers ($4.99/mo on a naira
   site) — product decision.
8. **Vercel/deploy check** [inferred]: a `vercel.json` exists; if any deploy
   hook depended on the repo being public, re-authorize it against the
   now-private repo. The Cloudflare Worker path (wrangler) is unaffected.

## What Phase 2 needs

- Merge of `claude/phase01-brand-safety` (or the website agent rebases their
  flywheel branch onto it — my branch is from the flywheel head `fb12759`, so
  it's a fast-forward for them).
- SKU rename with legacy alias (spec above) — do this before new marketing
  work multiplies references.
- Then the plan's own Phase 2 list: hero repositioning, `/` + `/preorder`
  instrumentation (before any paid spend), delivery terms + FAQ gaps on money
  pages, abandoned-lead email, Quality page live (post-counsel), and the two
  proposals answers (imagery publish-gate §1, questions feed §4).
- Cross-repo: the Supabase edge-function receipt email should carry the same
  `/reserve/complete` link the success panel now shows.
- Content machine: founder film + carousel through needs_review once the
  shoot happens; education advertorial copy on request.

---

# Phase 2 — executed 2026-08-14 (founder approved; wording signed off; cohort = 20)

Same branch (`claude/phase01-brand-safety`), 10 more commits, full build
passes, pushed. All **[confirmed]** unless marked.

| Commit | What |
|---|---|
| `4035804` | **Quality page live** — founder signed off on the wording; noindex removed, footer link added. |
| `639ee22` | **Cohort corrected to 20 and the public count is now live and honest.** Found and fixed while wiring it: bank-transfer sales marked paid on leads never wrote an orders row, so `/api/inventory` would not have decremented for WhatsApp sales — it now counts both. The hand-set constant is gone entirely. |
| `4cae0b4` | **Hero: "Blood pressure, measured — not guessed."** — caregiving warmth moved to the support line; Nav's primary CTA now goes to `/reserve` (was `/preorder`). |
| `fd63e34` | **`/` and `/preorder` instrumented** (ViewContent + custom view, same dedupe pattern as `/go/*`). **No paid spend until this deploys.** |
| `514a146` | **Delivery + payment answered where the money moves** — four new `/preorder` FAQs (delivery, payment, sizing, battery), a good-to-know block beside the `/reserve` form, delivery promise on the address field. All sourced from the WhatsApp concierge's ground-truth facts; bank details deliberately stay off the site. |
| `fd41103` | **Abandoned-lead email** — one warm reminder ~24h after step-1 without payment, both doors, explicitly "the only reminder I'll send". Send-once via `leads.reminded_at` (**migration `0048_lead_reminder.sql` — needs applying**; the job no-ops until then; 72h cap prevents back-mailing old leads). |
| `2108b91` | **Proposals §4 answered: `GET /api/content/questions` built** — machine-auth'd, PII-free (text, timestamp, intent, market from lead country; never phone/name/lead id). The runbook's promised `whatsapp_questions` view never existed in this repo's migrations, so the feed reads the real `wa_messages` table. This repo's Step 0 can read it from next Sunday. |
| `35ec7a7` | **Proposals §1 answered: draft-tier art can never publish.** Both publish paths now check the asset's recorded model and park draft renders as needs_review. This deliberately overrules the code's old "a worse picture beats no picture" policy per the imagery decision. |

## Deploy checklist (founder / website agent)

1. Merge `claude/phase01-brand-safety` (fast-forward from the flywheel head)
   and deploy (`npm run build && npx wrangler deploy`).
2. Apply migration `0048_lead_reminder.sql` (additive, one column) the same
   way 0044/0045 were applied.
3. Sanity-check after deploy: `/api/inventory` should return
   `{remaining: 20, total: 20}` (live probe before the change showed
   `sold: 0`); `/quality` reachable from the footer; a test hit of
   `/api/content/questions` with the ingest secret.
4. Then instrumentation is live and paid spend is unblocked per the plan.

## Still with the founder (unchanged)

Masters re-export (D7) · secret rotation (D8) · **the founder video** —
now the critical path for the rest of Phase 2 (film + carousel publish via
needs_review, then the About-page rewrite drawn from the script) · SKU rename
(website agent, legacy-alias spec in proposals §7) · Leiko Plus currency ·
D3/D2 voiceLint encoding (website agent).
