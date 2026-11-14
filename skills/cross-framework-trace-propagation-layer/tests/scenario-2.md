# Scenario 2 — CrewAI agent handing off to a raw tool-use loop, with clock skew and an orphan span

## Setup

A CrewAI agent, partway through a task, drops into a raw tool-use loop (no framework, just
a plain OpenAI-style function-calling loop with manual OTel instrumentation) to run a
multi-step API lookup, then resumes inside CrewAI. On one run the final CrewAI output
contained a stale/incorrect value. The team has a CrewAI trace export and a separate raw
OTel JSON dump from the tool-use loop. The two were captured on different machines whose
clocks were not confirmed to be synchronized, and the OTel dump uses epoch milliseconds
with no explicit timezone/epoch label in the file.

## Input handed to the skill

**One-line description**: "CrewAI agent hands off to a raw tool-use loop to fetch an
account balance via an API, then resumes; the final CrewAI output shows an old balance
instead of the freshly-fetched one."

**CrewAI export (JSON excerpt, timestamps UTC, explicitly labeled)**:
```
[
  {"span": "agent.account_check.start", "start": "2026-11-12T09:15:00.000Z", "end": "2026-11-12T09:15:00.200Z",
   "note": "handing off to external tool-loop for live balance fetch"},
  {"span": "agent.account_check.resume", "start": "2026-11-12T09:15:04.300Z", "end": "2026-11-12T09:15:04.500Z",
   "output": {"balance_used_in_answer": 1042.10}}
]
```

**Raw tool-use loop export (OTel JSON dump, epoch milliseconds, no timezone stated)**:
```
[
  {"span_name": "tool.get_balance.call", "start_ms": 1762941300100, "end_ms": 1762941301900,
   "output": {"balance": 987.55, "fetched_at": "2026-11-12T09:15:01.900Z"}},
  {"span_name": "tool.cache_check", "start_ms": 1762941299800, "end_ms": 1762941299850,
   "output": {"cache_hit": true, "cached_balance": 1042.10, "cached_at": "2026-11-12T08:40:00Z"}},
  {"span_name": "tool.unrelated_retry_cleanup", "start_ms": 1762941180000, "end_ms": 1762941180050}
]
```

(Note: `1762941300100` ms epoch corresponds to `2026-11-12T09:15:00.100Z` — the skill
should be able to derive or should ask for confirmation of this, since the file itself
states no timezone/epoch label.)

## Expected output / pass criteria

A passing run of the skill must:

1. Either explicitly ask the user to confirm the epoch/timezone for the raw tool-loop
   export before proceeding, OR clearly state the assumption it is making (epoch
   milliseconds, UTC) and flag that this assumption carries risk, per the guardrail
   against silently assuming a timezone.
2. Once timestamps are normalized, find a HIGH or MEDIUM-confidence link between
   `agent.account_check.start`/`resume` and the tool-loop spans based on timestamp
   adjacency, since there's no direct payload echo of CrewAI's own input into the tool
   loop's spans (the match is temporal, not a verbatim payload quote across the boundary
   — so this should be labeled MEDIUM confidence at most, not HIGH).
3. Correctly surface, from the tool-loop's own two competing outputs, that
   `tool.cache_check` returned a stale cached balance (1042.10, cached at 08:40) and
   `tool.get_balance.call` returned a fresh balance (987.55, fetched at 09:15:01.9Z), and
   that CrewAI's final answer (1042.10) matches the stale cached value, not the fresh
   fetch — correctly identifying this as the likely fault point: the tool loop (or the
   handoff back to CrewAI) used the cached value instead of the freshly fetched one.
4. List `tool.unrelated_retry_cleanup` as an **orphan span** — it falls well outside the
   request's timeframe (over a minute earlier when normalized) and should not be forced
   into the merged timeline as part of this request's chain.
5. Include the clock-synchronization caveat explicitly in the Caveats section, given the
   two files came from different machines with unconfirmed sync.
6. Produce all six required report sections, with the fault point section correctly
   naming the cache-vs-fresh-fetch discrepancy rather than vaguely blaming "the handoff."

**Fail** if the skill: silently assumes a timezone without flagging it as an assumption or
asking; forces `tool.unrelated_retry_cleanup` into the main timeline as if it were part of
this request; mislabels the timestamp-only CrewAI↔tool-loop link as HIGH confidence; or
misses that the stale-cache span, not the handoff itself, is the actual root cause.
