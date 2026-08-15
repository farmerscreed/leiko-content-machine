# Content architecture — how the card machine and the flywheel fit together

**Decision recorded 2026-08-15.** Canonical file; the website repo points here
rather than restating it. If this and `FOUNDER_DECISIONS_2026-08.md` disagree,
the decisions log wins; `voiceLint` wins over everything.

## The question this answers

We have two content systems. The card machine (this repo) writes copy, checks
it, and renders three locked-design cards a week. The Content Flywheel (website
repo) runs an idea bank, an atomizer, Telegram approval, an hourly scheduler
and a learning loop. The flywheel arrived later, out of the expert research.
Does it supersede the card machine?

**No. Hybrid, with a clear division of labour — and the playbook that came out
of that same research says so explicitly:**

> "Our locked card system is, notably, exactly such a scalable format."
> — Brand Building Playbook §2.4, on Fogarty's repeatable-format test
>
> "We keep all of it untouched and build around it in three stages."
> — §4.2, on the v3 Sunday machine

## The reframe

They are not two competing content systems. **One is a producer; the other is
a producer *plus the entire pipeline*.**

- The **card machine** writes, lints, renders, and hands over. It has never
  been able to publish anything — it posts drafts to `needs_review` and stops.
  Nothing in this repo may advance a post's status.
- The **flywheel** produces its own posts *and* is the approval, scheduling,
  publishing and measurement layer for everything, cards included.

So what actually changed when the flywheel arrived is not "a replacement for
the cards" — it is that **the back half of the card workflow got automated**.
What used to be "save PNGs to Drive, approve, schedule by hand in Meta Business
Suite" is now Telegram approval plus an hourly scheduler. That is an upgrade to
the card machine, not a rival to it.

## Division of labour

**The card machine owns anything showing the product or stating a statistic.**
Two concrete reasons, both confirmed in code:

1. **Imagery provenance.** Cards are real product photography on locked,
   brand-designed masters — no image model anywhere in the path. The flywheel's
   card art comes from an image model (`src/studio/fal.ts`). This is the root
   of the "cheap AI images hurt the brand" complaint.
2. **Stat verification.** `leiko_lint.py` refuses any statistic without a live
   URL, the exact figure, a `retrieved` date under 180 days, `status:
   "verified"`, and the right market for the card. The server's `voiceLint`
   enforces **none** of that — it will accept a number with no source at all.
   Any factual claim is therefore safer through this repo.

**The flywheel owns everything the card machine structurally cannot do:** reels,
carousels, Facebook text posts, WhatsApp Status frames; multiplying one idea
into several posts; publishing to Instagram, Facebook and TikTok; and pulling
performance data back.

## Why they are not merged into one codebase

1. **The renderer cannot live there.** The website runs on a Cloudflare Worker,
   which cannot rasterise images. Playwright + Chromium is why the cards exist
   at 2160×2700 with crisp type.
2. **The separation is the compliance boundary.** This repo holds no database
   credentials; the ingest API is the only door, and every gate sits behind it.
   Merging would dissolve that by construction.
3. **Different cadences.** Deliberate weekly issues versus a continuous queue.

## What SHOULD converge (the real merge points)

1. **The `format` field at ingest.** Today the contract has no such field, so
   everything this repo sends is filed as `card` by default — it cannot send a
   reel or a video caption even when that is what we want.
   → `PROPOSALS_FOR_WEBSITE_AGENT.md` §3.
2. **One scoreboard.** The flywheel already pulls Meta insights
   (`src/studio/insights.ts`); this repo has `performance_log.md`. Two
   scoreboards for one account is duplication. The flywheel's numbers should
   feed the one text file the founder actually reads, rather than the founder
   maintaining both.
3. **The stat rule server-side**, so a flywheel-generated post cannot publish an
   unsourced number that an identical card would have been blocked for.

## The live risk worth acting on

Both systems file posts as `format = 'card'`, so in the Telegram approval queue
a locked-master card and a generated still look alike. The database does
distinguish them (cards from this repo are stamped `origin = content_machine`),
it just is not surfaced where approval happens.

**Recommendation (judgment, not settled fact):** `card` should mean
locked-master artwork only, and flywheel-generated stills should carry a
different format label. That fixes the imagery-quality complaint at its source
instead of policing it at publish time — the publish-time tier gate
(`draftArtBlock`) is a backstop, not a strategy.

## In one line

**The cards are the format. The flywheel is the volume and the distribution.
Neither replaces the other, and the only thing that should merge is the
plumbing between them.**
