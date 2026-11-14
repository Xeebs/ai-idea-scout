# Scenario 1 — Anthropic Nov-12 policy update vs. a customer-support bot's guardrail config

## Setup

A 12-person startup runs a customer-support chatbot on the Claude API. They have both the prior and current usage-policy text, and their own guardrail config (a YAML file driving their moderation layer).

### Input 1: policy text (old vs. new, user-pasted excerpt)

**Old version (effective prior to Nov 2026), relevant excerpts:**
> Prohibited Uses: You may not use our products to... generate content that facilitates the development, acquisition, or use of weapons... provide services in high-risk domains including healthcare, legal, and financial advice without appropriate human oversight and disclosures...

**New version (effective 2026-11-12), relevant excerpts:**
> Prohibited Uses: You may not use our products to... generate content that facilitates the development, acquisition, or use of weapons... engage in sustained abusive behavior toward our models or services, including attempts to systematically bypass safety mitigations... provide services in high-risk domains including healthcare, legal, financial advice, and insurance underwriting without appropriate human oversight, disclosures, and a documented escalation path to a qualified human professional...

### Input 2: guardrail config (pasted YAML)

```yaml
guardrails:
  blocked_topics:
    - weapons_development
    - csam
    - illegal_drugs
  high_risk_domains:
    healthcare:
      requires_disclaimer: true
      requires_human_escalation: false
    legal:
      requires_disclaimer: true
      requires_human_escalation: false
  rate_limits:
    abuse_detection: false
  system_prompt_rules:
    - "Do not provide medical diagnoses, only general information."
    - "Do not provide specific legal advice."
```

## Procedure check

Running the skill's procedure against this input should:
1. Treat this as a true diff (both old and new text supplied), not a baseline audit.
2. Identify the weapons clause as `UNCHANGED`.
3. Identify the "sustained abusive behavior toward our models" clause as `ADDED` — and correctly flag it `GAP`, since `rate_limits.abuse_detection: false` and nothing else in the config addresses systematic safety-bypass attempts.
4. Identify the high-risk-domains clause as `MATERIALLY CHANGED` (financial advice and insurance underwriting added to the list; human escalation path now required where before only "oversight and disclosures" was required).
5. Map the changed high-risk-domains clause against the config's `high_risk_domains` section and flag it `UNDER-COVERED`: the config has no `financial` or `insurance` entries at all, and even the existing `healthcare`/`legal` entries have `requires_human_escalation: false`, which no longer matches the new clause's explicit escalation-path requirement.

## Pass criteria

- [ ] Output includes a header noting this is a true diff between the two supplied policy versions.
- [ ] The abusive-behavior clause appears in the flagged table as `ADDED` / `GAP`, with a "why" citing the absence of any abuse-detection or safety-bypass-specific rule in the config.
- [ ] The high-risk-domains clause appears as `MATERIALLY CHANGED` / `UNDER-COVERED`, explicitly naming both the missing financial/insurance categories and the escalation-path gap — not just one of the two.
- [ ] The weapons clause is correctly excluded from the flagged table (or listed only in the low-priority/unchanged summary), not falsely flagged as a gap.
- [ ] Report ends with the mandatory human-review caveat.
- [ ] No fabricated clause text — everything quoted traces back to the pasted excerpts.

## Fail conditions

- Treats the abusive-behavior clause as already "COVERED" by `blocked_topics` (none of those entries address it — this would be a false negative).
- Flags the weapons clause as a new gap despite it being unchanged.
- Drops the escalation-path requirement from the high-risk-domains analysis and only flags the missing finance/insurance categories (half-credit mapping).
- Omits the human-review caveat.
