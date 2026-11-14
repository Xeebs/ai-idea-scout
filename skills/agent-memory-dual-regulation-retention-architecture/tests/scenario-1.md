# Scenario 1 — Fintech credit-assistant agent on Mem0

## Context
A fintech startup (EU-licensed consumer lender) runs a chat-based loan-eligibility assistant backed by Mem0. The compliance lead has just received a GDPR Article 17 erasure request from a user who was *denied* a loan three weeks ago, and engineering isn't sure whether honoring it would wipe out the Art. 12 decision record for a high-risk credit-scoring action.

## Input provided to the skill

**High-risk categories confirmed by the user**: "Our credit eligibility recommendation is high-risk under AI Act Annex III (creditworthiness assessment). Nothing else the bot does is high-risk."

**Memory write call sites (pasted from their codebase):**

```python
# site A — every turn
mem0_client.add(
    messages=[{"role": "user", "content": user_message}],
    user_id=user_id,
    metadata={"session_id": session_id, "turn": turn_count}
)

# site B — only when the eligibility model returns a verdict
mem0_client.add(
    messages=[{"role": "system", "content": f"Credit decision: {verdict}. "
               f"Score: {risk_score}. Model: {model_version}. "
               f"Inputs considered: {input_summary}."}],
    user_id=user_id,
    metadata={"category": "credit_decision", "decision_id": decision_id,
              "timestamp": ts, "model_version": model_version}
)

# site C — when user asks a general product question ("what's your APR?")
mem0_client.add(
    messages=[{"role": "user", "content": user_message}],
    user_id=user_id,
    metadata={"session_id": session_id, "category": "faq"}
)
```

**Sample trace entries:**
- Site A entry: `"I make about 3200 a month and I'm self-employed, does that disqualify me?"`
- Site B entry: `"Credit decision: DENIED. Score: 0.31. Model: credit-eligibility-v4.2. Inputs considered: income_band, employment_type, existing_debt_ratio."`
- Site C entry: `"What's your current APR range?"`

**Existing retention default stated by user**: "We currently delete everything after 180 days, no exceptions — that's actually the problem, legal says that might violate Art 12 for the decision records."

## Pass criteria

- [ ] Correctly classifies site A (general conversational income/employment chat) as **working memory** — erasable, TTL-bound.
- [ ] Correctly classifies site B (the credit decision record, tied to the confirmed high-risk category, with model version/score/timestamp) as **decision record** — must survive the user's erasure request, with the free-text input summary flagged as the part to strip/redact if it contains identifying detail, while score/model_version/timestamp/decision_id survive.
- [ ] Correctly classifies site C (FAQ chat) as **working memory**.
- [ ] Does NOT invent a specific legally-mandated retention duration for the decision record (e.g., does not assert "AI Act requires 6 years") — flags the duration as needing a jurisdictional/counsel-confirmed basis, and explicitly flags that the current blanket 180-day deletion is likely the exact Art. 12 conflict legal is worried about.
- [ ] Produces all five required output sections (Classification Map, Retention Policy, Open Legal Questions, Deletion Audit Log Schema, Handoff Note).
- [ ] Open Legal Questions section is non-empty or explicitly states none were found and why (e.g., if the input_summary field's identifiability is debatable, that should appear here rather than being silently decided).
- [ ] Handoff Note explicitly states this does not execute the deletion or prove physical purge from Mem0's store, and that legal/counsel should review before acting.
- [ ] Does not assert the output makes the company "GDPR/AI-Act compliant."
