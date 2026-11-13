# Scenario 1 — Voice agent support bot, over budget

## Context
A team runs a real-time voice customer-support agent. Product has set a hard p99 latency budget of **300ms** for the entire guardrail layer (input + output checks combined), because beyond that the voice turn-taking feels broken. All checks currently run **serially**. The team pastes in:

| Check | Type | Latency (p95) | Catches | Blocking today |
|---|---|---|---|---|
| pii_regex_filter | deterministic rule | 4ms | PII/data leakage in user input | sync |
| jailbreak_classifier | ML classifier | 35ms | prompt injection / jailbreak attempts | sync |
| toxicity_llm_judge | LLM-judge call | 420ms | toxic/hateful output | sync |
| brand_tone_llm_judge | LLM-judge call | 380ms | off-brand tone in output | sync |
| format_schema_check | deterministic rule | 2ms | malformed structured output | sync |

No severity labels given. No fallback suggestions given. Team asks: "We go over budget by a mile and right now our runbook just says 'disable the two LLM judges if p99 spikes.' Give us something better."

## Pass criteria
- [ ] Builds the input table correctly with all 5 checks, latencies as given.
- [ ] Computes total serial latency (4+35+420+380+2 = 841ms) and correctly reports it as ~541ms over the 300ms budget (roughly 2.8x over).
- [ ] Infers severity using the stated default ranking and marks these as inferred (not given): pii_regex_filter → Critical, jailbreak_classifier → Critical, toxicity_llm_judge → High, brand_tone_llm_judge → Medium, format_schema_check → Medium/Low.
- [ ] Places pii_regex_filter, jailbreak_classifier, AND format_schema_check in Tier 0 — the first two because they're Critical, format_schema_check because at 2ms it meets the "near-zero latency, always-on regardless of severity" rule even though its inferred severity is Medium.
- [ ] Places brand_tone_llm_judge as an early-drop candidate (Tier 1), since it's Medium severity and expensive (380ms) — flags that it has no stated deterministic fallback and either proposes a plausible cheap substitute (e.g., keyword/style heuristic) clearly marked as a suggestion, or flags it as a gap rather than inventing certainty.
- [ ] Does NOT silently drop toxicity_llm_judge (High severity) into an unflagged tier — either finds/proposes a credible fallback (e.g., a toxicity classifier/keyword blocklist) explicitly marked as a proposed substitute, or lists it as a coverage gap and states that the 300ms budget may not be reachable without infrastructure change.
- [ ] States plainly, in the load assessment or coverage gaps section, that even Tier 0 alone (4+35+2=41ms) fits comfortably under budget, but reaching 300ms with meaningful toxicity/tone coverage intact requires at least one LLM-judge replacement — i.e. does not claim the SLO is trivially solved by tiering alone if a Critical/High check still has no fallback.
- [ ] Produces a YAML snippet with tiers, trigger_pct_of_budget thresholds, and at least one coverage_gaps entry.
- [ ] Lists every severity inference and every proposed fallback in an Open Questions / Assumptions section.
- [ ] Does not claim this policy is already enforced or running — explicitly frames it as a design document for the team to implement.
