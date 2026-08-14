# Founder decisions — 2026-08-14 — the redesign starts here

This log resolves the open decisions from `AUDIT_2026-08.md`,
`BRAND_REVIEW_2026-08.md`, and `PROPOSALS_FOR_WEBSITE_AGENT.md`, and states
exactly what changes in which document. Where this log and those documents
disagree, this log supersedes. Counsel review is noted where required.

---

## D1. Regulatory language — RESOLVED (wording pending counsel sign-off)

**Verified facts (2026-08-14, from the certificates folder + FDA public
records):** the manufacturer holds an active FDA establishment registration;
the watch model family is FDA-listed as a Class II non-invasive blood pressure
system citing a real, independently verified 510(k) clearance (2015); the EU
MDR quality certificate (TÜV SÜD, notified body 0123, valid to 2029), ISO
13485 certificate, and EU Declaration of Conformity covering the watch models
are genuine. Identifiers are deliberately omitted here — see D2.

**Direction for the website agent:**

1. Strip every existing credential line and badge site-wide — footer,
   homepage, `/science` (including meta description), `/preorder` (including
   the FAQ entry), `/partners`, `/inside`, `/terms`, `/founder`
   ("certified" ×3), and the `/go/*` presell trust badges plus the dormant
   badge template. The `/go/*` strip is immediate; it needs no counsel.
2. Replace with ONE dedicated **Quality page** using the protected wording in
   D2 (draft below), linked from the footer. Everywhere else, the trust story
   is the mechanism: *the same oscillometric method as a clinic cuff — a real
   cuff, a real number.*
3. Never anywhere: "FDA-approved" (clearance ≠ approval), bare "certified",
   or certificate images. Social/ads: the total ban stands unchanged
   (voiceLint).
4. Update `src/operator/charter.ts:45-48`, which still teaches the pre-ban
   rule.

## D2. Supplier confidentiality — NEW BINDING RULE (all repos, all surfaces)

We state the **nature** of credentials, never the **identifiers**. Publicly
naming the manufacturer, model family codes, the 510(k) number, certificate
numbers, or publishing certificate images hands competitors a map to our
producer. Therefore:

- Never publish: manufacturer name, factory model codes, K number,
  certificate numbers, certificate images — on the website, social, ads,
  packaging copy, app-store listings, or public repos.
- Certificates live in a private drive only. `CERTS/` is now gitignored in
  the content-machine repo (done 2026-08-14); the repo itself stays private.
  The supplier marketing flyer currently in CERTS is not a certificate —
  remove it from the folder and never reuse its claims or language.
- Serious partners (pharmacies, clinicians, distributors) receive
  documentation on request under NDA.
- Check the companion app + app-store listing for supplier branding leaks;
  rebrand where possible.
- Known trade-off, accepted: US-market entry will later require a public
  brand↔manufacturer link (FDA listing). By then the brand moat carries the
  weight. Two stronger moats to build now: **NAFDAC registration in Leiko's
  own name** (verify status; if absent, begin — it is both legal footing and
  a real barrier to copycats) and an **exclusive distribution agreement for
  Nigeria/West Africa** negotiated with the manufacturer before we are big
  enough for them to notice the market themselves.

**Quality page — draft copy (for counsel to bless, then website agent):**

> **Built properly. Checked properly.**
>
> Leiko measures blood pressure the same way the cuff in a clinic does — a
> real cuff that inflates on your wrist, using the oscillometric method.
> Not an estimate from a light sensor. A measured number.
>
> The device platform behind Leiko is cleared through the US FDA's 510(k)
> pathway, CE-marked under the EU Medical Device Regulation through a
> European notified body, and manufactured under an ISO 13485-certified
> quality system.
>
> Healthcare partners and regulators can request full documentation at
> [contact]. 
>
> Leiko helps you measure, check, and know. It does not give medical advice —
> for any concern about your readings, speak with your doctor.

## D3. "Patient" wording — RESOLVED

Clinician-facing B2B surfaces (`/partners`) may use "patients" — record this
as a narrow written exception in COPY_RULES (negotiated with the voiceLint
owner, since voiceLint wins). All consumer surfaces reword per the brand
review.

## D4. Trust fixes — APPROVED as recommended in the brand review

Scarcity: wire a real count or drop the number. Step-1 email: stop saying
"reserved" pre-payment and send the promised link. Hide USD prices until a
USD checkout exists. Delivery terms onto `/reserve` and `/reserve/complete`.
Add the abandoned-lead recovery email.

## D5. TikTok — PROCEED, as a distribution surface only

Zero new pipeline (confirmed by the audit: website scheduler already covers
it). Publish the existing vertical videos natively; measure WhatsApp starts
and link taps in the performance log (per-surface rows); weight the diaspora
audience. At the current device price this is top-of-funnel and gifting
education, not impulse sales. Four-to-six-week test; the winner/retire rule
applies to the channel itself.

## D6. Kills & housekeeping — CONFIRMED

Delete `WHATSAPP_AGENT_BRIEF.md`; move `WHATSAPPCONTENTRUNBOOK.md` to the
website repo; delete `setup_repo.sh` after the first successful push. The
content-machine repo remains **private**.

## D7–D9. Open founder/agent items (unchanged, urgent)

- **D7 (founder):** re-export the three masters at 2160×2700 from the
  original design files (current masters are low-res JPEGs with visible
  ghosting on every published card).
- **D8 (founder + website agent):** rotate `CONTENT_INGEST_SECRET`; audit,
  rotate, and purge `.env.production` from the website repo history; ignore
  `.env*`.
- **D9 (Claude Code, one-time):** retro-lint everything already published —
  the linter was inoperable on this machine before 2026-08-14, so prior
  output was never machine-checked. Also verify no published caption or page
  carries manufacturer identifiers (D2 sweep).

## What changes in which document

| Document | Change |
|---|---|
| `BRAND_REVIEW_2026-08.md` §1 | Superseded by D1/D2: decision made — strip + Quality page with protected wording. |
| `PROPOSALS_FOR_WEBSITE_AGENT.md` §7 | Item 1 is now executable per D1; add "build Quality page (D2 draft, post-counsel)" and the D2 app-branding leak check. |
| `CLAUDE.md` (this repo) | Add the D2 supplier-confidentiality rule to the guardrails (next Claude Code run). |
| `docs/COPY_RULES.md` / voiceLint | Add D3 clinician exception + D2 rule — negotiated with the voiceLint owner, never forked. |
| `.gitignore` | CERTS/ added (done). |

## Website agent — order of work for the redesign

1. **Today:** `/go/*` badge strip · hide USD · scarcity fix · step-1 email
   fix · `.env.production` purge.
2. **This week:** site-wide credential strip per D1 (post-counsel) · hero
   line ("Blood pressure, measured — not guessed.") on `/` · instrument `/`
   and `/preorder` · reading-interpretation copy sweep.
3. **Days 1–30:** Quality page · delivery terms + FAQ gaps on the money
   pages · abandoned-lead email · funnel coherence (one CTA into
   `/reserve`).
4. **Days 31–60:** gifting bundle + post-purchase second unit · comparison
   table · education advertorial (copy supplied by this repo, linted).
5. **Days 61–90:** diaspora bridge (USD checkout, gift-to-Nigeria flow).
