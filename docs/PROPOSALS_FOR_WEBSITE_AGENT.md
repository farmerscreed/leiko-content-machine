# Proposals for the website agent — 2026-08-14

From the content-machine audit (see `AUDIT_2026-08.md`). Nothing here was
changed unilaterally: the ingest contract is jointly owned, so each item is a
proposal — problem, evidence, smallest possible change, and what this repo does
once accepted. Evidence references are to the website repo
(`../leiko`), verified by reading the code on 2026-08-14.

---

## 1. Draft-tier AI imagery must never reach a published surface

**Problem.** The founder reports cheaper image models produce output that hurts
the brand. The flywheel drafts card art on the cheap tier by design
(`src/studio/fal.ts` — `DRAFT_MODEL` = Seedream, "~$0.03-0.04/image … Used for
DRAFT card art"), and re-renders on the flagship only after approval
(`src/studio/artwork.ts` `promoteArtwork`). If publish ever wins the race
against promotion — or promotion fails and nobody notices — a cheap draft goes
live.

**Evidence.** `src/studio/fal.ts:39-101` (model registry with tiers),
`src/studio/artwork.ts:233` (draft on `DRAFT_MODEL`), `:359-380`
(`promoteArtwork` re-render after approval).

**Smallest change.** In `gateAtPublish` (`src/studio/schedule.ts`), refuse to
publish an AI-produced image whose recorded model is not the flagship tier —
the same shape as the existing `producer === "ai" && !ai_label` refusal. If the
generating model isn't currently recorded on the row, record it at generation
time; that is the one-column enabler.

**This repo's part once accepted.** None — this repo calls no image models
(policy now written into its CLAUDE.md: cheap-model imagery banned for
published assets).

## 2. Extend the vision gate to the product-truth rules for generated art

**Problem.** The brand rule is: never AI-generate the Leiko device, people
wearing it, readings/screens, or medical scenes — a fake product image
misrepresents a health device. The ingest-path vision gate currently blocks
three things only: FDA text, cuffless wording, and a visible BP reading
(`src/studio/content.ts:381-387`). Meanwhile `fal.ts` advertises
`flux-2-pro — people / lifestyle scenes`, i.e. the pipeline is set up to
generate exactly what the rule forbids next to a health product.

**Smallest change.** Add two checks to the generator-side gate
(`src/studio/vision.ts` `brandCheck`): (a) flag any watch/wrist-device
depiction that is not a pasted-in real product photo (composites are fine —
that is the masters approach); (b) flag medical scenes (clinics, stethoscopes,
readings). Route hits through the existing `image:` prefix so they hard-fail
like the current three. And drop or re-scope the "people / lifestyle scenes"
model label so nobody reaches for it for product shots.

**This repo's part.** None; cards keep their locked masters.

## 3. Accept a `format` field at ingest (enables video/founder-story drafts)

**Problem.** The brand is adding founder-story and demo videos, and TikTok as a
surface. This repo should be able to send a **video post's caption + metadata**
as a draft — but `IngestCard` has no `format` key, so everything ingested
becomes `format='card'` by DB default.

**Evidence.** `src/studio/content.ts:420-433` (IngestCard — no format),
`supabase/migrations/0045_content_flywheel.sql:229-230` (column default
`'card'`), `src/studio/content.ts:117` (`FORMATS = ["reel", "carousel",
"card", "text", "status"]`).

**Smallest change.** Accept optional `format` in `IngestCard`, validated
against `FORMATS`, default `'card'` — plus wherever a reel/video draft carries
its media, accept the same from ingest (or explicitly document that video
drafts arrive as caption-only and the media is attached website-side).

**This repo's part once accepted.** Send `format` explicitly (cards send
`'card'`); add a small video-caption copy shape behind the same linter. No
video pipeline will be built here.

*TikTok finding (Step 3b of the audit): publishing a reel asset to TikTok is
already a website scheduler concern — `publishTikTok` exists (draft-push via
/inbox by design, `src/studio/publishers.ts:15-19, 388+`), and reels map to
TikTok in `FORMAT_PLATFORMS`. Nothing in this repo needs to change for TikTok
beyond the performance log, which already records surface per row. The copy
rules apply unchanged — they are what keeps a health account safe there.*

## 4. Build the promised questions feed (or retire the promise)

**Problem.** The Sunday Step 0 (idea mining) is supposed to read real WhatsApp
customer questions. `WHATSAPPCONTENTRUNBOOK.md` §4 documents
`GET /api/content/questions?days=7` — but no such route exists in
`src/server.ts` (verified against the full route table). The flywheel's best
input is currently unreachable.

**Smallest change.** Expose the documented route: PII-free view
(`whatsapp_questions`), same ingest auth, `days` + `include_unknown` params as
specced.

**This repo's part once accepted.** Step 0 reads it weekly; mined questions
feed MYTH/FACT_HEAD candidates with a source tag.

## 5. Doc drift on your side — two corrections

- `docs/CONTENT-MACHINE-BRIEF.md:219-224` still describes the duplicate-insert
  race as an open caveat; `src/studio/content.ts:213-238` and your own §269-280
  say it was fixed 2026-08-09. Please delete the stale caveat — this repo has
  now updated its own timeout guidance on the strength of the fixed code, so a
  stale doc re-teaching the old fear will cause drift. Also please confirm the
  deployed worker includes that fix (merge `86e1fc5`).
- `docs/CONTENT-INGEST.md:36` and `docs/CONTENT-MACHINE-BRIEF.md:205` still say
  "send PNG". As of 2026-08-14 this repo renders both formats and **sends
  JPEG** (Instagram refuses `.png` paths — your `publishers.ts:212-217`; your
  ingest sniffs bytes and derives the extension, so no change is needed in your
  code). Update the two doc lines to "send JPEG". Historical issues 1-3 are
  stored as PNG; if IG re-publishing of old cards ever matters, this repo can
  re-send them (supersedes in place) rather than you building conversion.

## 6. Operational asks

- **Rotate `CONTENT_INGEST_SECRET`** (`npx wrangler secret put`) — a previous
  value appeared in a chat transcript (recorded in this repo's README). The
  founder sets the new value in their shell; nothing is written to any file.
- The one-line RLS fix on `audit_log_default` (carried in this repo's README
  open items) is website-side Supabase work — taking it off this repo's list
  and handing it to you.

## 7. Addendum 2026-08-14 — full site brand + funnel review

`BRAND_REVIEW_2026-08.md` (same folder) contains a file:line review of the
whole website against the Brand Building Playbook. The website-side work it
identifies, in priority order:

1. **Regulatory-language sweep, site-wide** — pending the founder + counsel
   decision (§1 of the review). Footer, `/`, `/science` (+ meta description),
   `/preorder` (+ FAQ), `/partners`, `/inside`, `/terms`, `/founder`
   ("certified" ×3), `PresellSections.tsx` trust badges, and the dormant
   badge template comment. Also update `src/operator/charter.ts:45-48`,
   which still teaches the pre-ban rule.
2. Reading-interpretation copy → pattern-vs-baseline language (preorder:169,
   index FAQ mock, inside thresholds + classification column, partners:98,
   app.tsx:68, the repeated "in pattern" verdict blocks).
3. Scarcity: `FOUNDER_REMAINING` hand-edited constant rendered as live stock,
   "of 30" vs "20" inconsistency.
4. Step-1 email says "reserved" pre-payment and never sends the promised
   `/reserve/complete` link; add abandoned-lead recovery email.
5. Delivery terms on `/reserve` + `/reserve/complete` (they exist only in
   `wa/facts.ts:45` today); FAQ gaps (sizing, battery, delivery, payment) +
   FAQ presence on `/reserve`.
6. Homepage/funnel coherence (USD homepage → naira-only checkout dead end);
   instrument `/` and `/preorder`; WhatsApp-door standard event.
7. Gifting bundle + post-purchase second-unit offer; comparison table;
   education advertorial page (this repo supplies linted copy on request).
8. Drip promises with no on-site backing (`templates.ts:55-57`); `/partners`
   referral program described but unimplemented (USD, against naira).
9. Hygiene: **`.env.production` is git-tracked and not ignored — audit,
   rotate, purge history, ignore `.env*`**; confirm RLS behind the hardcoded
   publishable key in `src/lib/supabase.ts`; minor: hero SVG hydration
   shift, unwrapped table in `inside.tsx:152`, dead `ui/sidebar.tsx`.
