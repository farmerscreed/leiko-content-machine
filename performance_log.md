# Leiko performance log — scoreboard + lessons

One line per published card, one lesson per issue. Numbers come from Meta
Business Suite (and TikTok analytics for TikTok posts) — the founder exports
them weekly, or reads them out and `perf_log.py` appends the row.

Rules (README_v3 Step 1 / TWO_MARKET_RESEARCH_SETUP §2):
- **WINNER** = reach ≥ 2× the running average → remixable after ~90 days
  (same idea, fresh wording, never identical copy).
- **retire** = reach < ½ the running average → drop that angle for that market.
- Averages are computed **per market and per surface** — NG and US numbers are
  not comparable, and neither are Instagram and TikTok numbers.
- `perf_log.py` suggests the verdict once a market+surface has 3 rows of
  history; before that it writes `–`. The founder can overrule by editing this
  file — it is a text file, not a database.

## Scoreboard

| date | issue | card | market | surface | angle | reach | saves | shares | taps | verdict |
|---|---|---|---|---|---|---|---|---|---|---|

## Lessons

<!-- one line per issue, appended by: python perf_log.py lesson <issue> "…" -->
