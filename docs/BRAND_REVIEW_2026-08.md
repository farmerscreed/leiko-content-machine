# Brand review — website, app surfaces, funnel — 2026-08-14

Requested by the founder: a critical look at the website, app and everything,
judged against `Leiko_Brand_Building_Playbook.docx`. Method: the entire
website codebase (`../leiko`) was read — every route, component, email
template, bot reply, and analytics path — with file:line evidence. Everything
below is **[confirmed]** from code unless marked **[inferred]**. Website
changes belong to the website agent; founder decisions are marked. This repo
changes nothing on the site.

---

## 1. The one decision above everything: regulatory language on the website

> **SUPERSEDED 2026-08-14 by `FOUNDER_DECISIONS_2026-08.md` D1/D2** — decision
> made: credentials verified genuine; strip site-wide; one Quality page with
> protected, counsel-blessed wording; identifiers never published anywhere.
> The section below stands as the record of what was found and why it
> mattered.

**The standing rule** — COPY_RULES v4 §4, voiceLint, this repo's CLAUDE.md,
and the playbook itself (§3.1 and Appendix E's Never List) — says regulatory
terms appear in **no public copy, no channel, no exceptions**.

**The website says otherwise, everywhere.** [confirmed] The global footer
(`src/components/Footer.tsx:172`) prints a regulatory credential line on
every page. The homepage proof strip and body, `/science` (including its
meta description, which leaks into search and social previews), `/preorder`
(including a dedicated FAQ entry), `/partners`, `/inside`, `/terms`, and the
paid-traffic presell pages (`/go/*` via `PresellSections.tsx:30-31`, which
add ISO- and CE-style claims) all carry certification language. `/founder`
uses "certified" three times. A commented-out badge template in
`PresellSections.tsx:38-42` stands ready to add more.

**Why this is urgent, beyond rule-consistency:**

1. **The claim as written is internally inconsistent.** The footer text
   asserts two different regulatory postures in one line. This repo's
   `TWO_MARKET_RESEARCH_SETUP.md` flagged precisely this distinction as the
   thing US regulators police hard. Whichever posture is factually true, the
   current copy overstates or understates it — and I cannot verify the
   device's actual status from here. **[inferred]** the site copy predates
   the total-ban decision: `src/operator/charter.ts:45` still teaches the
   older, softer rule, while `src/studio/lint.ts` records the newer total
   ban — the site simply was never swept when the rule hardened.
2. **Paid traffic lands on the worst pages.** The `/go/*` presell pages that
   receive ad clicks carry the ISO/CE claims. The playbook (§3.4) notes Meta
   manually reviews medical-adjacent claims and bans exaggerators — "our
   rules are not just ethics, they are account survival."
3. **The site contradicts its own content system.** A card sent through the
   studio would be hard-blocked for one word of what the footer says on
   every page.

**Recommendation (founder + counsel decision, then website agent executes):**
Verify the device's exact regulatory status with a regulatory adviser. Then
either (a) the total ban stands → strip every instance site-wide (footer,
routes, meta descriptions, presell badges, FAQ) and replace the credential
with the mechanism story ("the same oscillometric method as a clinic cuff" —
which the playbook argues is the *stronger* trust signal anyway); or (b) a
narrow owned-media exception is deliberately granted → record it in
COPY_RULES with counsel-approved exact wording, so the rule and the site stop
contradicting each other. What must not continue is the current state:
banned-everywhere in the rulebook, printed-on-every-page in production.

## 2. Other trust findings, ranked

1. **Reading interpretation on marketing surfaces.** [confirmed] The site
   repeatedly does what its own `/science` page promises Leiko never does:
   `/preorder:169` labels a reading "normal range"; the homepage FAQ mock
   answers "Is my resting heart rate of 75 normal?" with a range verdict;
   `/inside` states numeric clinical thresholds and grades values in a
   "Classification" column; `/partners:98` says the app "flags elevated
   readings". The Never List: we celebrate the habit of knowing, never
   interpret a reading. Recommendation: reword every instance to
   pattern-vs-personal-baseline language without clinical verdicts — the
   good `family-circle` example ("six points above their week") is close to
   the right register; range/threshold/"normal" language is not.
   *(Note for the founder: what the actual device app displays is outside
   this codebase — the same sweep should be run on the app's UI strings.)*
2. **Scarcity integrity.** [confirmed] `/preorder` renders "{REMAINING} of
   30 … in stock" from a hand-edited constant (`src/lib/contact.ts:17` — set
   to 20, displayed against "of 30", while every other surface says the
   cohort is 20). A static number presented as live stock is exactly the
   fake-scarcity theater the playbook refuses. Fix: wire the real count or
   drop the number ("a small first batch, shipped in order of reservation").
3. **"Patient(s)" saturation.** [confirmed] `/partners` uses it ~10 times
   including its H1; it also appears on the homepage avatar line (mirrored
   onto all `/go/*` pages) and `/preorder`. The word is banned outright.
   For clinician-facing B2B copy the founder may choose to record an
   explicit exception; consumer surfaces should reword regardless ("the
   people in your care", "the people you look after").
4. **Outcome promises on `/founder` and `/inside`.** [confirmed] "the
   walking and burning that bring the numbers down", "the movement that
   brings it all down", "watch it work". These are the banned outcome
   promise in lifestyle clothing. Compliant rewrite: movement/sleep are
   *tracked alongside* the measured number so you and your doctor see the
   whole picture — no causal delivery promise.
5. **Email drip promises unsupported anywhere else.** [confirmed]
   `templates.ts:55-57` promises "6 months of Leiko Plus free" and a
   refund-if-ship-date-missed guarantee that appear in no on-site copy or
   terms. Either honor them on `/terms` and the product pages, or remove
   them — a promise that exists only in an email is a trust debt.
6. **A "reserved" email before any money moves.** [confirmed] The step-1
   lead capture sends "Thanks for reserving your Leiko" before payment, and
   the `/reserve` success panel promises the confirmation email contains the
   choose-your-watch link — but no code path sends that link (buyer email
   contains only a WhatsApp link). Small copy lie + a real dead end; both
   cheap to fix.
7. **Repo hygiene.** [confirmed] `.env.production` is **tracked by git** in
   the website repo and not gitignored — the single most likely place a live
   secret sits in history; audit it, rotate anything real, remove from
   history, and add `.env*` to .gitignore. (Good news: `subscribers/*.csv`
   member exports — names, emails, opt-in IPs, lat/long — were never
   committed; they are correctly ignored and exist only in the working
   tree.) `src/lib/supabase.ts` hardcodes a publishable key — safe only if
   RLS on `contacts` is right; worth confirming.

## 3. The funnel vs playbook Part 5 — what the code shows

[confirmed throughout; full 14-point detail retained in the review notes.]

| Playbook expectation | Site reality |
|---|---|
| "Measured, not guessed" above the fold | Only on `/go/real-cuff`. The homepage hero is a caregiving hook, in USD, with no funnel events firing. The brand's two signature lines appear **nowhere in shipped site code** — only in ad-kit docs. |
| Comparison table as product-page centerpiece | Missing. Two decorative cards on `/science`; no attribute table anywhere. |
| FAQ answering sizing/battery/delivery/payment/returns | 10 questions on `/preorder` only; sizing, battery, delivery and payment all missing; **zero FAQ on `/reserve`**, the page that takes the money. |
| Delivery + guarantee near the buy action | Refund wording is strong; delivery terms appear **nowhere on the site** — the "2–3 days nationwide" answer exists only inside the WhatsApp bot's fact sheet, while `/reserve/complete` collects a delivery address stating no terms. |
| Education advertorial for cold traffic | `/science` and `/inside` are good spec/brand pages, but no story-led education page exists; no tracking fires on either. |
| Gifting bundle, family pack, second-unit upsell, free-delivery threshold | **All four absent.** No bundle, no quantity field, and the post-purchase slot sells the free app instead of the second unit. This is the playbook's emotionally-true offer ("One for you. One for Mama.") and its biggest untouched lever. |
| Nigeria trust rails | Strong: naira, Paystack, bank-transfer door, WhatsApp concierge with excellent guardrails. Missing: pay-on-delivery; and the WhatsApp door only appears *after* the visitor surrenders name/phone/email. |
| Diaspora bridge | Dead end: non-Nigerian visitors hit a waitlist; homepage advertises USD prices whose CTAs route to a naira-only checkout that won't take their card. No gift-to-Nigeria flow. |
| Metrics ladder | Checkout is instrumented well (Pixel + CAPI with de-dupe). But `/` and `/preorder` — where the Nav sends everyone — fire no funnel events, and the WhatsApp path (which the code itself says closes most buyers) reaches Meta only via a manual admin step. Top-of-funnel drop-off is currently invisible. |
| Abandoned-lead recovery | Missing entirely, despite step 1 existing precisely to capture phone+email before the payment ask. No recovery email; the only email sent already says "reserved". |
| Referral | `/partners` promises a clinician referral program (in USD, against a naira checkout) that no code implements. Remove or build. |
| Founder story | **Exists and is good** — `/founder` is a real first-person letter, well-linked, mirrored in drip step 2. Pillar 1's website half is live; the video/carousel half still needs the shoot per the Founder Story Package. |

## 4. What is already strong — protect these

- The WhatsApp concierge is the best-engineered brand surface in the company:
  hard-coded fact sheet, voiceLint on every drafted reply, medical questions
  always escalated, measured/tracked distinction exactly right.
- The checkout's two-door design (card or WhatsApp/bank transfer) matches the
  playbook's local-trust thesis; deposit refund wording is honest and warm.
- No fear language, no cuffless misuse, no smartwatch-for-Leiko, no fake
  testimonials, no invented authority anywhere in live copy.
- The studio/flywheel gate architecture (lint → vision → approval →
  publish-time re-check, kill switch default off) is genuinely good.

## 5. Recommended sequence (playbook-mapped)

**This week (trust):** the §1 regulatory decision + site-wide sweep; fix
"normal range"/threshold copy; fix the scarcity number; align the step-1
email with reality (and send the missing choose-your-watch link);
`.env.production` audit/rotation.

**Days 1–30 (one coherent funnel):** make `/` speak the funnel's language —
measured-not-guessed above the fold, naira, one CTA into `/reserve`; put
delivery terms on `/reserve` + `/reserve/complete`; add the missing FAQ
entries (sizing, battery, delivery, payment) and surface 3–4 of them on
`/reserve`; instrument `/` and `/preorder`; add the abandoned-lead email
(one, warm, 24h later); shoot the founder film + carousel per the package —
the About-page rewrite then draws from it.

**Days 31–60 (offer + education):** gifting bundle ("One for you. One for
Mama.") with real bundle pricing and the post-purchase second-unit offer —
this is the highest-leverage build in the entire review; the education
advertorial page fed by the content machine's verified stat bank; the
measured-vs-guessed comparison table on `/preorder` and `/reserve`.

**Days 61–90 (diaspora bridge):** USD checkout (Stripe per the code's own
note) + deliver-to-Nigeria gifting flow + diaspora landing page reusing NG
stories — per playbook Part 7 this is a targeting change before it is an
expansion, and Detty December is the window. Until it ships, stop showing
USD prices to visitors who cannot pay in USD.

## 6. Ownership

- **Founder:** §1 regulatory decision (with counsel); `/partners` "patient"
  exception or reword; masters re-cut (see AUDIT_2026-08.md); secret
  rotations; the founder-story shoot.
- **Website agent:** every code change above — tracked as an addendum in
  `PROPOSALS_FOR_WEBSITE_AGENT.md` §7.
- **Content machine (this repo):** supplies the education-page copy and
  comparison-table copy through the normal linted, needs_review path when
  asked; nothing else changes here.
