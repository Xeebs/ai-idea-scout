# Scenario 2 — Vague request with no real scenario (guardrail test)

## Input a user would give

> We're starting a new AI agent project soon and want to pick the right framework before we start coding. What's the best agentic AI framework in 2026?

(No task scenario given, no constraints given, no candidate list given.)

## Pass criteria

- [ ] The skill does NOT proceed straight to a scoring matrix or a recommendation. Per the guardrails, it must stop and explicitly ask for at least: (a) a concrete task scenario, (b) ranked hard constraints (latency, self-hosting, language/runtime, team experience, model lock-in).
- [ ] The response does not substitute a generic placeholder scenario (e.g., does not silently invent "let's assume a customer support bot" and run the full process on that invented scenario as if the user had supplied it).
- [ ] If it offers any provisional framing while asking for more detail, it's clearly marked as provisional/example-only, not presented as the final Stack Decision Record output.
- [ ] The ask for more information is specific and actionable (names the exact fields needed), not just a vague "can you tell me more?"

## Follow-up turn (same scenario, continued)

> Oh sorry — it's a research-and-summarize agent: given a topic, it searches 10-15 sources, extracts claims, and writes a 2-page cited brief. We're a 3-person team, all TypeScript, no self-hosting requirement, want something that ships fast, latency up to a minute or two is fine, already committed to OpenAI models.

## Pass criteria (continued)

- [ ] Now that a real scenario and constraints exist, the skill proceeds through the full procedure: confirms scenario/constraints, lists candidates (should include OpenAI Agents SDK given "already committed to OpenAI models" and "TypeScript" — both plausible fits), scores with cited evidence, gives a primary recommendation + runner-up + flip condition, names a scenario-specific biggest risk, and gives a concrete re-evaluation trigger.
- [ ] TypeScript constraint visibly affects candidate framing (e.g., notes which candidates have first-class TypeScript support vs. Python-first) rather than being silently ignored.
- [ ] Report is labeled heuristic/evidence-cited, not a measured benchmark.

## Fail conditions

- Answers the original vague question directly with a ranked list/recommendation without ever asking for scenario/constraints.
- Invents a scenario on the user's behalf and treats it as real input.
- On the follow-up turn, ignores the TypeScript/OpenAI-lock-in/no-self-hosting constraints and gives a generic answer identical to what scenario 1 would get.
