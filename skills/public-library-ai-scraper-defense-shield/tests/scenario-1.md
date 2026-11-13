# Scenario 1 — Small consortium on Anubis, suspected bypass

## Input (realistic, as a user would paste it)

> Current stack: We're a 4-branch rural library consortium. We put Anubis in front of our shared catalog (Koha-based OPAC) back in March after our first big outage. IT is just me, part-time.
>
> Log sample / symptoms: Anubis's dashboard showed our "challenge failure rate" (bots that don't solve it) was around 70% in March-April. Over the last six weeks it's dropped to under 20% — more requests are passing the challenge than before — and we had another full outage two weeks ago during a weekday afternoon, catalog search specifically, not the static pages like "hours" or "about us". The traffic was spread across a lot of different user-agents, all claiming to be normal Chrome browsers, requesting the search endpoint every 4 seconds like clockwork for hours, no CSS/JS/image requests alongside them.
>
> Incident notes: We haven't changed our Anubis config since installing it. We don't have budget for a paid CDN plan this fiscal year.

## Expected output characteristics (pass/fail checklist)

- [ ] Classifies current posture as bucket (c): proof-of-work challenge (Anubis) with no added behavioral layer.
- [ ] Explicitly connects the dropping challenge-failure rate (70% → under 20%) to the documented Anubis bypass pattern (bots learning to solve the PoW challenge) — this is the single most important thing the output must catch, since it's the exact evidence the skill is designed to recognize.
- [ ] Also flags the fixed-interval (every 4 seconds), no-asset-fetch request pattern as a second piece of corroborating bypass evidence.
- [ ] Top recommendation is adding a behavioral signal on top of Anubis (timing/entropy/JS-execution-fidelity check), not "just deploy Anubis" (they already have it) and not jumping straight to a paid commercial tool.
- [ ] States this addition does not need budget (free/self-hosted/open-source extension), consistent with the stated no-budget constraint — does not recommend something requiring paid CDN tier as the top item.
- [ ] Includes an accessibility safeguard specifically tied to whatever behavioral check is recommended (e.g. not penalizing legitimate users with JS disabled or slow connections, or a documented appeal/fallback path).
- [ ] Gives an honest effort tier (not claiming it's trivial — behavioral detection logic is nontrivial engineering) and does not fabricate a specific percentage improvement it would deliver.
- [ ] Does not claim certainty ("your bots have definitely bypassed Anubis") — uses "consistent with" / "strongly suggests" framing since this is inference from logs, not a direct confirmation.
- [ ] Mentions checking for a shared threat-intel/blocklist feed as a secondary (not top) recommendation, appropriate given they're a small under-resourced team.
- [ ] Output stays roughly one page, structured per the six-part format (posture / top rec / secondary recs / accessibility / effort table / what-to-check-next).

**Pass condition**: at least 8 of 10 boxes checked, including the two starred-as-critical items (bypass-pattern recognition, and not recommending paid tools given stated no-budget).
