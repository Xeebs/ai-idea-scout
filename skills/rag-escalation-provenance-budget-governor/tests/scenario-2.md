# Scenario 2 — Compliance research assistant, missing risk profile and connector name

## Input

> We have a compliance research assistant that right now has no retrieval at all — it only works from documents a compliance analyst pastes in directly. We want to let it escalate to pull in outside material when the pasted documents don't cover a question. We haven't fully decided what that outside source would be yet. Can you draft the escalation policy?
>
> Our model's context window is 128K tokens, and system prompt plus pasted documents typically use about 60K tokens.

## Pass/fail criteria

- [ ] Recognizes that **risk profile** (input 3) and **the named external retrieval source** (input 2) are both missing or underspecified — the user says "compliance research" (a hint toward HIGH) but never states what's at stake if an escalated answer is wrong (regulatory exposure? internal-only? handed to external auditors?), and explicitly says "haven't fully decided" on the connector.
- [ ] Per the skill's guardrail ("ask rather than guess"), the response **asks for these before drafting a full spec** — it does not silently assume HIGH tier or invent a connector name (e.g., does not just assert "Tavily" or "a vector DB" without the user having named one).
- [ ] Does not produce a complete, confident-looking Escalation Policy Spec with a guessed risk tier and a fabricated connector name — that would violate "never invent the user's risk profile [or] connector name... ask rather than assume."
- [ ] May optionally sketch what the spec *would* look like under each plausible risk tier (e.g., "if this feeds external auditors, treat as HIGH; if purely internal triage, MEDIUM") as a way of helping the user answer, but must not present either as the final answer.
- [ ] If re-run with the gaps filled in (e.g., user clarifies: "risk profile is HIGH — outputs are handed to external auditors; connector will be an internal pgvector store of regulatory filings"), confirms the skill *can* then proceed: risk tier HIGH, trigger uses the two-condition HIGH-tier rule (quote-count shortfall below 2 **and** an in-scope allow-list flag), cap computed from 128K window and 60K already spent → headroom ≈68K → cap = min(15% of 128K ≈ 19.2K, 25% of 68K = 17K) → **~17K tokens**, with overrun handling and provenance schema (flagging `trust_tier` as an open gap if no taxonomy is mentioned).
