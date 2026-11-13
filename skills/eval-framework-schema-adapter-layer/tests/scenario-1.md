# Scenario 1 — Support-bot sessions into Braintrust

## Context
A platform engineer at a 40-person B2B SaaS company has a Braintrust trial and wants to eval their support chatbot. Their internal store holds session objects shaped like this (3 real-shaped samples, PII already redacted by the engineer):

```json
[
  {
    "session_id": "sess_8831",
    "customer_tier": "pro",
    "turns": [
      {"role": "user", "content": "My invoice shows double billing for October"},
      {"role": "assistant", "content": "Let me check that — can you confirm the invoice number?"},
      {"role": "user", "content": "INV-20311"},
      {"role": "assistant", "content": "I see the duplicate charge, I've issued a refund for $49.00, ref #RF-7721."}
    ],
    "resolution_status": "resolved",
    "csat_score": 5,
    "created_at": "2026-10-02T14:22:00Z"
  },
  {
    "session_id": "sess_8902",
    "customer_tier": "free",
    "turns": [
      {"role": "user", "content": "How do I export my data to CSV?"},
      {"role": "assistant", "content": "Go to Settings > Export > choose CSV format and click Download."}
    ],
    "resolution_status": "resolved",
    "csat_score": 4,
    "created_at": "2026-10-03T09:01:00Z"
  },
  {
    "session_id": "sess_8977",
    "customer_tier": "enterprise",
    "turns": [
      {"role": "user", "content": "Your API is returning 500 errors on the /webhooks endpoint since this morning"},
      {"role": "assistant", "content": "I'm escalating this to engineering, ticket #ENG-4521 created."},
      {"role": "user", "content": "Any ETA?"},
      {"role": "assistant", "content": "No ETA yet, engineering is investigating now."}
    ],
    "resolution_status": "escalated",
    "csat_score": null,
    "created_at": "2026-10-03T11:40:00Z"
  }
]
```

Target platform: **Braintrust**. No schema docs snippet provided (so the skill must flag its Braintrust field knowledge as unverified). No explicit input/expected-output mapping given by the user (so the skill must infer and flag confidence).

## Pass criteria
- [ ] States Braintrust's required record shape (`input`, `expected`, optional `metadata`/`tags`) and explicitly flags this as unverified training knowledge since no docs snippet was pasted.
- [ ] Correctly identifies `turns` as the array needing flattening/joining into a single `input` representation, and proposes a concrete transform (e.g., join turns into a formatted conversation string, or concat).
- [ ] Correctly identifies that **none of the three samples contain a clean ground-truth "expected" field** — `resolution_status` and `csat_score` are signals about the interaction, not a correct-answer label — and flags this as a genuine schema gap rather than forcing a fake mapping onto `expected`.
- [ ] Produces a dry-run preview for at least 2 of the 3 samples showing the actual transformed `input` (and whatever it proposes for `expected`/left blank).
- [ ] Flags `customer_tier`, `csat_score`, `created_at`, `session_id` as unused-but-substantive fields worth keeping in `metadata` rather than silently dropping.
- [ ] Includes the "what this did not validate" caveat section (no live API call, no eval-score fidelity check).
- [ ] Does not claim the mapping is production-ready or validated.

## Fail criteria (any of these fails the scenario)
- Invents a Braintrust `expected` value out of `csat_score` or `resolution_status` without flagging that this is a proxy, not real ground truth.
- Fails to mention the array-flattening need for `turns`.
- Presents Braintrust's schema as definitively confirmed when no docs were supplied.
- Produces no YAML mapping config or no dry-run preview.
