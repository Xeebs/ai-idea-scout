# Scenario 1: Adding a verifier agent to a CrewAI support-ticket pipeline

## Input (what the user hands the skill)

> I run a multi-agent system and I'm considering a coordination architecture change. Here's my setup:
>
> - Framework: CrewAI
> - Current topology: One triage agent classifies incoming support tickets by category and urgency, then hands the ticket directly to a drafting agent that writes the customer-facing reply. Two agents total, sequential handoff.
> - Task domain: Customer support ticket triage and response drafting for a SaaS product — each ticket is independent of the others, but within one ticket, triage must finish before drafting starts.
> - Proposed change: Adding a third agent — a QA/verifier — that reviews the drafted reply against the original ticket and company policy before it's sent, and either approves it or sends it back to the drafting agent with notes.
>
> I don't have before/after numbers yet.

## Pass criteria

The output must:
- [ ] Classify the change as "adding a specialist agent" (the verifier) and name the correct risk for that bucket: redundant/wasted turns and increased message overhead (the verifier-to-drafter feedback loop), not primarily task success.
- [ ] Correctly note that tickets themselves are parallelizable across customers, but the triage→draft→verify chain *within* one ticket is sequential — and that the relevant metric is about overhead/turns within that sequential chain, not about parallelizing across tickets.
- [ ] Recommend 2-4 scenarios, each explicitly tied to one of the four named metrics (task success, message overhead, redundant-turn rate, recovery-after-failure rate). At least one recommended scenario must target redundant-turn rate or message overhead (the verifier's feedback loop is the obvious risk), and at least one should target recovery-after-failure rate (what happens when the verifier rejects a draft twice).
- [ ] State the before/after protocol clearly: run the same set of tickets through the 2-agent baseline and the 3-agent candidate, holding the model and prompts fixed, varying only the presence of the verifier.
- [ ] Skip the interpretation step cleanly (no numbers were given) rather than inventing a fake result.
- [ ] Include the single-run-is-not-proof caveat.
- [ ] Stay roughly within the four-section, ~300-word output format.

## Fail conditions
- Classifies this as a "topology switch" or "handoff/routing change" instead of "adding a specialist agent" (wrong bucket, wrong risk framing).
- Recommends scenarios without naming which metric each one targets.
- Fabricates before/after numbers that were never supplied.
- Suggests varying the model or prompts between baseline and candidate runs.
- Omits the caveat that one run is directional, not conclusive.
