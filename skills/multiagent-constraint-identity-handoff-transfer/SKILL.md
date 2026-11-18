---
name: multiagent-constraint-identity-handoff-transfer
description: Drafts a "constraint capsule" (persona/tone, forbidden actions, numeric/business-rule limits, required phrasing) for a specific agent-to-agent handoff, flags which rules should and shouldn't carry over, and can spot-check a sample downstream response against it. Use when someone describes an upstream agent handing a task to a downstream specialist agent and worries the downstream agent will silently drop a rule the upstream agent was enforcing (not a data/context-loss problem — a rules-loss problem).
---

# Inherited Rules: Constraint Capsule Drafter

## When to use this
Someone describes a multi-agent pipeline — a triage agent escalating to a billing agent, a sales-qualification agent handing to a pricing agent, an orchestrator routing to a specialist subagent — and the concern is specifically that the receiving agent will re-derive its own defaults instead of inheriting a rule the upstream agent was quietly enforcing: a persona/tone, a forbidden topic or action, a numeric ceiling ("never promise a refund over $50 without approval"), or required compliance phrasing. This is a rules problem, not a data problem — if the complaint is "the next agent doesn't know what happened earlier" (facts, decisions, artifacts), that's the separate Handoff Envelope pattern, not this skill.

Trigger moment: the user is about to add a new specialist agent to an existing pipeline, is debugging a case where a specialist agent did something the upstream agent would never have allowed, or is designing a handoff and wants to get the rule-inheritance right before it ships.

Do not use this for a single agent's own memory across turns, for authorization/privilege boundaries between agents (that's the separate Scope Trace pattern — "is this agent allowed to call this tool/see this data"), or for carrying task data/decisions forward (Handoff Envelope). This skill only ever touches persona, tone, forbidden actions, numeric/business-rule limits, and required phrasing.

## Inputs
**Data source**: CONNECTED — when run inside Claude Code (or any environment with file access) and given file paths, this skill reads the upstream and downstream agents' own definition files directly (Claude Code subagent `.md` frontmatter + system-prompt body, a CrewAI agent YAML `role`/`goal`/`backstory` block, a LangGraph node's system-prompt string, an OpenAI Agents SDK agent's `instructions` string) instead of making the user retype their contents. No mature connector standardizes this across frameworks yet — Claude Code subagent frontmatter is the one format this is built against today; other frameworks' files can still be pasted. Falls back to MANUAL — paste both agents' full system prompts/instructions verbatim — whenever file access isn't available (e.g. pasted into a plain chat tool) or the agent isn't defined in a file at all (described only in prose).

Before drafting, get:
1. **Upstream agent's definition** — a file path (if file access exists) or the full pasted system prompt/instructions/frontmatter of the agent handing off the task.
2. **Downstream agent's definition** — same, for the agent receiving the handoff.
3. *(Optional)* **A concrete incident** — a transcript or description of a specific handoff that already went wrong (the downstream agent broke a rule the upstream agent enforced) — use it to drive the worked capsule and to run the Conformance Spot-Check.
4. *(Optional, for the spot-check only)* **A sample downstream response** to check against the drafted capsule.

If only prose descriptions are available (no actual definition text), say so explicitly in the output — extraction confidence is lower, and more items should land in Ambiguous rather than being asserted.

## Procedure
1. **Acquire both definitions.** If file paths were given and you have file access, read them directly. Otherwise use the pasted text. If the downstream agent's definition is missing or only described in one sentence, say the capsule will be incomplete on the downstream-fit side and proceed anyway with what's available.
2. **Extract from the upstream definition only, under four fixed categories** — do not merge categories, do not invent a fifth unless clearly needed and justified in one line:
   - `persona_tone`: declared voice, formality, empathy stance, any "always/never speak like X" instruction.
   - `forbidden_actions`: explicit "never do X" / "do not Y" statements, topics it won't discuss, actions it won't take.
   - `numeric_business_limits`: any dollar amount, percentage, quantity, or threshold tied to a rule ("refunds under $50 only," "max 3 retries," "escalate above $10k").
   - `required_phrasing`: exact or near-exact phrases it must use (legal disclaimers, compliance language, a specific apology format).
   Quote the source line or paraphrase tightly — never summarize away the specific number or phrase.
3. **Run the Downstream Fit Check.** For each extracted item, decide: does this rule plausibly still apply once the task moves to the downstream agent's stated role, or is it upstream-specific and should NOT transfer (e.g. upstream's "never discuss pricing" is likely upstream-only if the downstream agent's entire job is pricing)? State the call and the one-line reasoning for every item — never carry a rule forward silently just because it was on the list.
4. **Flag ambiguous rules explicitly.** Anything where the source text doesn't make the scope clear (e.g. "caps discounts at $50" — per item or per order? for new customers only or everyone?) goes in its own list, named precisely, not folded into the capsule as if it were settled.
5. **Draft the capsule** — one structured object per handoff direction, containing every item that passed the Downstream Fit Check as "carries over," each tagged with its category and a short rationale. If the downstream definition was missing or too thin to run a real fit check (step 3 returned "fit unknown" for everything), still include every extracted item in the capsule rather than shipping an empty one — tag each with `"fit_status": "unknown — confirm once downstream agent is defined"` instead of a carries-over rationale, so the user has a working draft to build the real downstream agent against, not a refusal.
6. **If a sample downstream response was provided, run the Conformance Spot-Check**: go through each capsule item and state PASS, VIOLATION, or UNCLEAR, quoting the exact phrase in the response that supports the call. Label this advisory — a single manual pass, not a validated detector — and never imply it would catch every future violation.
7. **List Open Gaps** — what's missing before this capsule could be wired into a real runtime injector (e.g. "downstream agent definition was only a one-sentence description, not a real system prompt — re-run once the real one exists").

## Output format
```
## Handoff
<upstream agent name/role> → <downstream agent name/role>: <one-line description of what triggers this handoff>

## Constraint Capsule
{
  "capsule_id": "<slug>-v1",
  "from_agent": "<name>",
  "to_agent": "<name>",
  "persona_tone": [ {"rule": "...", "source": "quoted or paraphrased line"} ],
  "forbidden_actions": [ {"rule": "...", "source": "..."} ],
  "numeric_business_limits": [ {"rule": "...", "source": "..."} ],
  "required_phrasing": [ {"rule": "...", "source": "..."} ]
}

## Downstream Fit Check
- <item> — CARRIES OVER / DOES NOT CARRY OVER — <one-line reasoning>
(one line per extracted item, including ones excluded from the capsule)

## Ambiguous Rules
- <rule> — <exactly what's unclear>
(or "none found")

## Conformance Spot-Check
<only if a sample downstream response was given; otherwise write "Not run — no sample response provided.">
- <capsule item> — PASS / VIOLATION / UNCLEAR — "<quoted phrase from the response>"

## Open Gaps
<what's missing before this capsule is production-ready, or "none — both definitions were complete">
```

## Guardrails
- Never invent a constraint that isn't actually stated or clearly implied in the upstream agent's own definition — if it's not there, it doesn't go in the capsule, and its absence doesn't belong in Ambiguous either (ambiguous means "stated but unclear scope," not "wished it existed").
- Never carry every upstream rule into the capsule by default — the Downstream Fit Check is mandatory for every single extracted item, including ones that seem obviously fine; state the reasoning even when the answer is an easy yes.
- Never claim or imply this skill enforces anything at runtime — it drafts and spot-checks; wiring a capsule into an actual request/response pipeline (a runtime injector, a conformance checker that runs on every handoff) is separate infrastructure this skill does not build.
- Never present a Conformance Spot-Check as statistically validated — it is one manual pass over one sample, always labeled advisory.
- Never fold in task data, decisions, or artifacts from the handoff — that's the Handoff Envelope's job, and mixing it in here defeats the point of keeping the capsule small enough to inject on every hop.
- Never fold in authorization/privilege questions (what tools/data an agent may access) — that's the Scope Trace pattern; this skill is rules of conduct, not access control.
- If the downstream agent's definition is missing entirely, say the capsule cannot be fit-checked and stop short of asserting any "carries over" call — still include every extracted item in the capsule tagged `fit_status: unknown`, never omit them and never present an empty capsule as the final answer.
