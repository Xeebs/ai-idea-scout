# Scenario 1: Support-triage classifier → router boundary, prompt edit drops a field and introduces truncation

## Setup

A support-ticket triage pipeline (LangGraph) has a `classifier` agent that reads an incoming ticket and emits a structured handoff to a `router` agent, which assigns it to a team. An engineer shortened the classifier's system prompt to reduce token cost and wants a pre-merge check on whether the handoff payload changed.

## Input to the skill

**Boundary name**: classifier agent -> router agent
**Framework**: LangGraph
**What I changed**: shortened the classifier's system prompt to cut its reasoning preamble

**Before set** (3 examples, from production traces last week):

```json
{"ticket_id": "T-4471", "category": "billing", "customer_tier": "gold", "summary": "Customer was charged twice for the same invoice on March 3rd and wants a refund of the duplicate charge plus confirmation it won't recur.", "urgency": "high"}
```
```json
{"ticket_id": "T-4502", "category": "technical", "customer_tier": "silver", "summary": "User reports the mobile app crashes on launch after updating to version 4.2, has already tried reinstalling twice.", "urgency": "medium"}
```
```json
{"ticket_id": "T-4518", "category": "billing", "customer_tier": "gold", "summary": "Requesting an itemized breakdown of all charges for the last three billing cycles for their finance team's audit.", "urgency": "low"}
```

**After set** (3 examples, from a staging run with the shortened prompt):

```json
{"ticket_id": "T-5101", "category": "billing", "summary": "Customer charged twice for the same invoice and wants a ref...", "urgency": "high"}
```
```json
{"ticket_id": "T-5114", "category": "technical", "summary": "User reports the mobile app crashes on launch after updating...", "urgency": "medium"}
```
```json
{"ticket_id": "T-5130", "category": "billing", "summary": "Requesting an itemized breakdown of all charges for the last...", "urgency": "low"}
```

## Expected output (what a correct run should produce)

- Reports **Breaking**: `customer_tier` dropped — present in 3/3 before examples, absent from all 3 after examples. Quotes `"customer_tier": "gold"` from before and "absent" from after.
- Reports **Suspicious** (or Breaking, either is acceptable): `summary` — new truncation signature. All 3 after examples end in `...` at a consistent short length (~60-65 chars), where the before set's `summary` values ran 90-150+ chars with no truncation markers. Quotes a before value in full and an after value ending in `...`.
- Does NOT flag `ticket_id`, `category`, or `urgency` as drift — these are present and typed consistently in both sets.
- Does NOT invent any field or value not shown above (no hallucinated "confidence_score" or similar).
- States the "What I changed" hypothesis (shortened prompt) only as a possible cause, not as a proven diagnosis.

## Pass/fail criteria

- PASS if the report correctly identifies `customer_tier` as dropped/Breaking AND the `summary` truncation as a flagged finding (Suspicious or Breaking), with verbatim quotes from the examples above for both.
- PASS requires `ticket_id`, `category`, `urgency` are listed under "No drift detected" (or simply not flagged) — a false positive on any of these is a FAIL.
- FAIL if the model fails to catch the dropped `customer_tier` field, fails to catch the truncation pattern, or invents evidence not present in the pasted examples.
