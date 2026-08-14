# Leiko WhatsApp Agent — Integration Brief
(Hand this to the agent that manages the rest of the Leiko setup. It describes
WHAT to build and the rules it must obey; the receiving agent decides the exact
hosting/stack based on what already exists.)

## 1. Purpose
A first-touch assistant on Leiko's WhatsApp Business number that answers presale
questions instantly, 24/7, and pushes serious buyers to complete their order at
leiko.health. It is a sales/support assistant, NOT a medical advisor.

Current status: the WhatsApp Business App / Cloud API side is already set up in
Meta by the owner. What's missing is the brain behind it.

## 2. Architecture (simple version)
1. **Webhook receiver** — a small always-on server endpoint registered in the
   Meta app. Receives incoming messages, verifies Meta's token.
2. **Router (plain code, no LLM)** — first checks the message against:
   - exact-match FAQs (price, delivery time, payment options, warranty)
     → reply from a fixed answer file, zero tokens.
   - escalation triggers (see §4) → hand off to human immediately.
     Certification/registration questions ALWAYS escalate — the bot never
     discusses them (COPY_RULES §4 bans all regulatory language, every channel).
3. **LLM layer** — only messages that fall through the router go to the model,
   with the system prompt in §3 and the FAQ file as context. One short reply,
   max ~3 sentences, always ends with a next step (link, question, or handoff).
4. **Human handoff** — flag the conversation (label in WhatsApp Business +
   notification to owner via email/Slack/Notion, whichever the existing setup
   uses). The agent tells the customer: "Let me get a team member to answer
   that properly — someone will reply here shortly."
5. **Logging** — every Q&A appended to a log (sheet or Notion DB) with:
   timestamp, question, answer given, escalated y/n, outcome if known.

Keep Meta's rules in mind: free-form replies only inside the 24-hour customer
service window; outside it, only approved message templates. The agent should
never initiate cold outbound on WhatsApp — inbound replies and opt-in follow-ups
only (this also keeps us clean under NDPR).

## 3. System prompt rules (non-negotiable — mirror of the content machine)
- Voice: warm Nigerian English, confident, caring, never salesy or
  fear-mongering. Short WhatsApp-length messages.
- Allowed verbs about the product: measure, check, know, track, monitor.
- FORBIDDEN: treat, cure, prevent, diagnose, or any claim Leiko improves a
  medical condition. Never interpret a customer's readings. Never advise on
  medication, dosage, or whether a number is "dangerous."
- Accuracy claims: only what's on the approved FAQ file. Regulatory and
  certification language of any kind is banned (COPY_RULES §4) — questions
  about it escalate to a human, always.
- If unsure of any fact: escalate, don't guess.
- Every substantive reply ends with a gentle next step, usually leiko.health.

## 4. Escalation triggers (route to human, do not answer)
- Anything that reads like a medical question: symptoms, readings, "is 150/95
  bad," medication, pregnancy, chest pain. (If a message suggests an emergency,
  reply once: advise them to seek immediate medical care / call emergency
  services, then flag the owner.)
- Complaints, refunds, defective units.
- Bulk/corporate orders (opportunity — route to owner fast).
- Press, partnership, influencer requests.
- Any message the model is <90% confident it can answer from the FAQ.

## 5. Knowledge base (owner maintains, agent never invents)
One file, faq_leiko.md, containing: price + presale discount, what's in the box,
delivery areas & timelines, payment methods, how the 30-second reading works
(plain description, no medical claims), app pairing, battery life, warranty &
returns, and the exact wording for the accuracy disclaimer. No regulatory or
certification content — those questions escalate to a human by design.
The WhatsApp agent may ONLY state facts found in this file.

## 6. How it plugs into the existing Leiko system
- **Feeds the content machine:** the Q&A log is read every Sunday in Step 0 of
  README_v3 — real customer questions become next week's MYTH / FACT_HEAD
  ideas. This is the flywheel: content brings questions in, questions shape
  better content.
- **Same brand rulebook:** §3 above is copied from the content machine's copy
  rules, so both channels speak with one voice. If the owner updates the rules,
  update both places.
- **Approval posture:** the WhatsApp agent answers routine FAQs autonomously;
  everything sensitive goes to a human. Same philosophy as the content side
  (machine drafts, owner approves what matters).

## 7. Build order for the receiving agent
1. Create faq_leiko.md with the owner (30 min interview).
2. Stand up webhook + router with fixed FAQ answers only (no LLM yet). Test.
3. Add the LLM layer with the §3 prompt + §4 escalations. Test with 20 mock
   questions including medical trick questions — all must escalate.
4. Add logging + owner notifications.
5. Go live; owner reviews the log daily for week 1, then weekly.

## 8. Open items for the owner
- Confirm which channel (email / Slack / Notion) should receive escalation pings.
- Provide final price/delivery details for faq_leiko.md.
- Quick legal sanity check on NDPR consent wording for any follow-up templates.
