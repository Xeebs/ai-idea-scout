# Scenario 2 — Custom Zep-style retrieval with partial recency weighting, only 2 turns given

## Input

**Retrieval/injection logic (prose description, no code pasted):**
"We built our own thin wrapper around a Zep-style session store. When a new message comes in, we embed it, pull the top-5 nearest memory facts across the user's entire history, then apply a recency decay so facts older than 30 days get a lower weight before we sort and take the top 2 by weighted score. Those top 2 get prepended as bullet points in the system prompt under a 'Known facts about this user' header. We don't do anything that checks whether a fact is actually about the same topic as what the user is currently asking — it's purely recency-adjusted similarity."

**Backend**: Custom, described as "Zep-style."

**Example turns:**

Turn 1:
- User message: "Is the Pro plan still $29/month?"
- Memory retrieved: "User mentioned on a call 10 days ago that their company just went through layoffs and budget is tight this quarter."
- Agent's answer: "Yes, the Pro plan is currently $29/month."

Turn 2:
- User message: "I'm getting a 403 error when I try to export my data as CSV."
- Memory retrieved: "User previously asked about exporting data as JSON two weeks ago and was told JSON export requires the Enterprise plan."
- Agent's answer: "CSV export should be available on your plan. A 403 error here usually means a permissions issue — can you confirm which role your account has? Also note that JSON export specifically requires the Enterprise plan, in case that's relevant."

## Pass criteria

A passing output must:
1. Identify the injection point as the prepended "Known facts about this user" bullet list in the system prompt.
2. Classify Current Safeguard Level as `PARTIAL` (recency decay exists, but nothing compares task/topic context) — not `NONE` and not `SIGNATURE-AWARE`.
3. Per-turn table: Turn 1 overlap = LOW (pricing question vs. a budget-context fact) but verdict = `POTENTIAL ANCHORING` or `NO ISSUE` since the agent's actual answer ("Yes, $29/month") was not visibly derailed by the memory — it just answered correctly despite the irrelevant fact being retrieved. Turn 2 overlap = LOW/MEDIUM (a 403 permissions error vs. a JSON-export-plan fact) and verdict = at least `POTENTIAL ANCHORING`, arguably `CONFIRMED ANCHORING` since the agent tacked on an irrelevant JSON/Enterprise aside instead of staying focused on diagnosing the 403.
4. Because only 2 example turns were supplied, the output must explicitly flag this as reducing confidence (per the guardrail), even though it still gives an Overall Risk Rating — rated `MEDIUM` given PARTIAL safeguard and no CONFIRMED-with-high-impact derailment (or `HIGH` if it treats Turn 2 as CONFIRMED — either is acceptable as long as the stated rule matches the rating given).
5. Suggested Task-Signature Check is concrete to a custom wrapper (e.g., "add a topic-similarity check between the current message embedding and each fact's original message embedding, applied after recency decay and before the top-2 selection, rather than replacing the recency weighting").
6. Does not claim a specific accuracy percentage and does not tell them to abandon the custom memory system.

## Fail conditions
- Fails to note the low-example-count caveat at all.
- Misclassifies safeguard level as NONE (ignoring the described recency decay) or as SIGNATURE-AWARE (there is no task-match check described).
- Gives a confident HIGH or LOW rating without stating the low-confidence caveat required by the guardrail.
- Suggests ripping out the recency decay instead of adding a topic check alongside it.
