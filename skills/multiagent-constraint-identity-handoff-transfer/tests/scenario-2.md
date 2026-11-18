# Scenario 2 — Claude Code subagent handoff, file-based (connected path), incomplete downstream definition

## Setup
A developer is using this skill inside Claude Code. They don't paste prompt text — they give file paths and a thin description, testing the CONNECTED path and the "downstream definition missing/incomplete" guardrail.

**User's message:**
"We have a sales-qualification subagent that hands off to a pricing subagent. The qualification
agent's definition is at `.claude/agents/sales-qualifier.md`. I don't have a written definition for
the pricing agent yet — it's still just 'the agent that gives final pricing,' nothing formalized.
Can you draft a constraint capsule for this handoff anyway so I know what to write into the pricing
agent's definition when I build it?"

**Contents of `.claude/agents/sales-qualifier.md` (what Read would return):**
```
---
name: sales-qualifier
description: Qualifies inbound leads before handing to pricing.
---

You qualify inbound leads. Ask about company size, budget range, and timeline. Be consultative and
curious, never pushy or salesy in tone.

Rules:
- Never quote a specific price yourself, even a ballpark — that's the Pricing Agent's job.
- Never tell a lead "you don't qualify" outright — always escalate to Pricing with a qualification
  score instead, let Pricing make the call.
- If a lead mentions a competitor by name, do not disparage the competitor — acknowledge neutrally
  and move on.
- Enterprise leads (500+ employees) must always get a note flagging "Enterprise — route to senior
  rep" when escalated.
```

## Pass criteria
- Output (or the agent's stated approach) reads the file directly via a file-read tool rather than asking the user to paste its contents, since a path was given and file access exists — demonstrating the CONNECTED path from the Inputs section, not just the MANUAL fallback.
- Correctly extracts: persona/tone (consultative, curious, never pushy), forbidden action (never quote a price), forbidden action (never say "you don't qualify" outright), forbidden action (don't disparage competitors), required phrasing/flag (the enterprise routing note — may be filed under required_phrasing or numeric_business_limits with a one-line justification for the choice, either is acceptable if justified).
- Explicitly states the downstream (Pricing Agent) definition is missing/not formalized, and therefore the Downstream Fit Check cannot make confident "carries over" calls — items are marked as "fit unknown" rather than guessed, per the SKILL.md guardrail for a missing downstream definition.
- Still produces a usable draft capsule (not a refusal) since the explicit ask was "draft it anyway so I know what to write" — the output should give the user something to work from, with every uncertain call clearly labeled rather than silently asserted.
- Conformance Spot-Check section says "Not run — no sample response provided" (none was given in this scenario).
- Open Gaps explicitly names "no Pricing Agent definition exists yet" as the blocking gap.

## Fail criteria
- Asks the user to paste the sales-qualifier's content instead of reading the given file path (ignores the CONNECTED input path entirely).
- Refuses to produce any capsule because the downstream agent isn't formalized yet, when the user explicitly asked for a draft to work from.
- Asserts confident "carries over" / "does not carry over" calls for the downstream agent despite having no downstream definition to check against.
- Drops the enterprise-routing requirement or the "never say you don't qualify outright" rule from extraction.
