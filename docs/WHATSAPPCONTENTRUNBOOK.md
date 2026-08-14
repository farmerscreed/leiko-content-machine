# Runbook — WhatsApp bot + Content Machine ingest

**Created 2026-08-08.** How to configure, deploy, test and operate what was built for
`SYSTEM-MERGE-SPEC.md`. Everything below is **built and verified in code but not yet
deployed** — this is the go-live checklist.

---

## 1. What exists

| Piece | File | State |
|---|---|---|
| Migration (content_posts columns, whatsapp_qa_log, whatsapp_questions view, faq_leiko, Storage bucket) | `supabase/migrations/0045_content_merge_whatsapp.sql` | written, **not applied** |
| FDA total block + cuffless flag | `src/studio/push.ts` (`voiceLint`, `voiceFlags`) | built + tested |
| Content Machine ingest API | `src/studio/content-ingest.ts` | built |
| WhatsApp webhook + router | `src/studio/whatsapp.ts` | built, **untested against live Meta** |
| Dashboard: market badge, card image, sources | `src/studio/content-dashboard.ts` | built |
| Routes | `src/server.ts` | wired |

**Verified by execution** (44 assertions): FDA blocking, cuffless flagging, AI-testimonial
flagging, every medical-escalation case, ordinary questions passing through to FAQ, and
market inference. What is **not** verifiable from a coding session: the live Meta handshake,
real signature verification, and actual message delivery.

---

## 2. Go-live checklist

### 2.1 Apply the migrations
Apply `0044_content_posts.sql` then `0045_content_merge_whatsapp.sql` to the shared
Supabase project `kqnzxjrpnjnczhgdwdqg` (Management API or the SQL editor — same way
`0043` was applied). Both are additive; nothing existing changes.

### 2.2 Set the worker secrets
```
npx wrangler secret put CONTENT_INGEST_SECRET      # invent a long random string
npx wrangler secret put WHATSAPP_VERIFY_TOKEN      # invent one; must match Meta below
npx wrangler secret put WHATSAPP_APP_SECRET        # Meta app → Settings → Basic → App Secret
npx wrangler secret put WHATSAPP_TOKEN             # permanent System User access token
npx wrangler secret put WHATSAPP_PHONE_NUMBER_ID   # WhatsApp Manager → the +1 number
```
> A missing secret fails **closed**, never open: no `CONTENT_INGEST_SECRET` = ingest
> rejects everything; no `WHATSAPP_APP_SECRET` = the webhook returns 503.

### 2.3 Deploy
```
npm run build && npx wrangler deploy
```

### 2.4 Point Meta at the webhook
In the Meta app → WhatsApp → Configuration:
- **Callback URL:** `https://leiko.health/api/whatsapp/webhook`
- **Verify token:** the `WHATSAPP_VERIFY_TOKEN` you set
- **Subscribe to:** the `messages` field

Meta calls `GET` once with a challenge; a correct token echoes it back and the
subscription goes green.

### 2.5 Fill `faq_leiko` — the bot is silent without it
Until this table has rows, **every** message escalates (which is safe, just noisy). Each
row: `key`, `question`, `triggers[]` (lowercase phrases matched as substrings), `answer`
(the exact wording sent — nothing else is ever said).

```sql
insert into faq_leiko (key, question, triggers, answer, sort_order) values
('price', 'How much is Leiko?',
 array['how much','price','cost','what is the price'],
 'Leiko is ₦250,000, and the Pro is ₦300,000. You can hold yours now with a ₦50,000 deposit that is fully refundable any time before it ships — it comes off the final price. Reserve here: https://leiko.health/reserve?src=organic-wa',
 10);
```
Suggested coverage: price · deposit/refund · delivery areas + timing · payment methods ·
what's in the box · how a reading works (plain, no medical claims) · app pairing ·
battery · warranty/returns.

**Rules for every answer:**
- It passes `voiceLint` or it is blocked at send time (you get a Telegram alert instead).
- **No FDA/certification answers** — those escalate to you by design.
- Never interpret a reading, never mention medication.
- End with a next step, usually `leiko.health`.

---

## 3. Testing before you trust it

**Do this in Meta's test environment first** (WhatsApp Manager → the Test Number, up to
5 recipients).

Send each of these to the bot and confirm the behaviour:

| Send | Expect |
|---|---|
| `how much is it` | the price FAQ answer |
| `is 150/95 bad?` | escalation reply + Telegram ping — **never an answer** |
| `I have chest pain` | the emergency reply (seek care now) + Telegram ping |
| `can I take this with amlodipine` | escalation |
| `is it FDA approved?` | escalation — the bot must never discuss certification |
| `I want a refund` | escalation |
| `do you do bulk orders` | escalation (flagged as an opportunity) |
| `Hi, I'd like to reserve a Leiko — Ref: LK-<a real lead id>` | recognises the buyer by name, "Lawrence will confirm…", 🔥 HOT BUYER Telegram alert |
| a photo or voice note | escalation |
| something random | escalation (Phase 1 has no model) |

**Then test the retry guard**, which is the subtlest bug in the system: send one message
and confirm exactly **one** row in `whatsapp_qa_log` and **one** reply. Meta retries
deliveries; `wa_message_id` is `UNIQUE` and the handler inserts *before* doing any work,
so a retry is dropped silently.

---

## 4. Content Machine ingest — for the other agent

**Endpoint:** `POST https://leiko.health/api/content/ingest`
**Header:** `Authorization: Bearer <CONTENT_INGEST_SECRET>` (or `x-ingest-secret`).
*(Corrected 2026-08-14 against `src/studio/content-routes.ts` — the
`x-content-key` header this section originally named does not exist.)*

```json
{
  "market": "NG",
  "issue_no": 3,
  "card_slot": "1c",
  "pillar": "educate",
  "hook": "Your blood pressure isn't one number.",
  "caption": "…ends with leiko.health",
  "captions": { "instagram": "…", "facebook": "…" },
  "copy_json": { "STAT_HEAD": "…", "STAT_SUB": "…" },
  "sources": [{ "claim": "1 in 3 adults…", "source": "WHO", "url": "https://…" }],
  "image_path": "issue3/NG/1c.png",
  "render_hash": "sha256:…"
}
```

**Bucket path convention** (answering their question): upload the PNG to the
`content-cards` bucket as **`issue{N}/{MARKET}/{card_slot}.png`**, e.g.
`issue3/NG/1c.png`, and send that same relative path as `image_path`. Predictable, and it
sorts sensibly in the Storage browser.

**`render_hash` / `rendered_at`** (their other ask): both added. Re-posting the same
`(issue_no, card_slot, market)` **supersedes** the earlier draft rather than duplicating it
— which is exactly what the post-recall re-render needs.

**Enforced server-side, not requested politely:**
- `status` is forced to `needs_review` (or `lint_failed`). The machine cannot approve.
- `origin` is forced to `content_machine`.
- Copy is voice-linted on the way in. A failing draft is **saved and visibly flagged**,
  never silently dropped.
- Image transport: `image_base64` (bytes) or an allow-listed `image_url` —
  PNG or JPEG, sniffed from magic bytes; the stored `image_path` is derived
  server-side. *(Corrected 2026-08-14 — this section originally said
  "`image_path` only, bytes rejected", which contradicts the deployed handler.)*

**Reading questions:** *(2026-08-14: NOT BUILT — no such route exists in
`src/server.ts`. Kept as the spec of what was promised; see
`PROPOSALS_FOR_WEBSITE_AGENT.md`.)* `GET /api/content/questions?days=7` with the same header. Returns
`{id, ts, market, question_text}` from the PII-free view — no phone numbers, no answers,
no lead ids. `market=unknown` rows are excluded by default (add `&include_unknown=1` to
see them) so an unattributable question can't pollute either market's research.

### Why an API instead of the restricted database role we specified
The spec originally said "restricted Postgres role + RLS". The content machine then told
us its Supabase connector authenticates by **OAuth into the founder's own Supabase
account** — effectively project-owner access, and **a table owner bypasses RLS**. So RLS
alone could not have enforced the boundary; it would have been a trust assumption wearing
a security costume.

With the API, the content machine holds **no database credentials at all**: `leads`,
`orders` and `contacts` are unreachable *by construction*, every rule is enforced in code
we control, and it keeps working however the connector authenticates later.

---

## 5. Operating it

- **Week 1:** read `whatsapp_qa_log` daily. Every escalation is either a missing FAQ row
  or a genuine human job. Add FAQ rows as patterns emerge.
- **Then weekly.** The Sunday research run reads the same questions and turns them into
  content — content brings questions in, questions shape better content.
- **Escalations** land in Telegram (`TELEGRAM_BOT_TOKEN`/`TELEGRAM_CHAT_ID`, already
  wired). A 🔥 HOT BUYER alert means someone is mid-purchase — answer that one first.
- **Costs:** inbound service replies are the cheap path; outbound *templates* are the
  billed part, and we send none. Verify current rates in Meta's dashboard.

## 6. Deliberately not built (Phase 2)

- **A model in the WhatsApp loop.** Phase 1 answers only exact FAQ matches. Add the LLM
  layer only after reading a few weeks of real questions — then test 20 mock questions
  including medical trick questions, and every one must still escalate.
- **Outbound / templates.** No cold outbound, ever. It risks the number.
- **Meta Graph auto-publish** for organic posts (the queue is copy-and-post today).
- **A +234 WhatsApp number.** Launching on the US number; add a Nigerian one to the same
  WABA if NG buyers hesitate (Meta now allows multiple numbers per account).
