# Inherited Rules: Constraint Capsule Drafter

Paste this whole prompt into any AI chat tool (ChatGPT, Claude, Gemini, etc.) when you're handing a task between two AI agents and you're worried the receiving agent will silently drop a rule the first agent was enforcing — a persona, a forbidden topic, a dollar-amount ceiling, a required compliance phrase — even though the actual task data transferred fine.

## When this applies

Use this when:
- You have an upstream agent (a triage bot, a sales-qualification agent, an orchestrator) handing a task to a downstream specialist agent (a billing agent, a pricing agent, a refunds agent), and
- The upstream agent enforces some rule — tone, a forbidden action, a numeric limit, required wording — that isn't explicitly re-declared in the downstream agent's own instructions, and
- You want that rule made explicit and checkable instead of hoping the downstream agent "just knows."

Do **not** use this if your actual problem is that the downstream agent doesn't know what already happened (facts, decisions already made, artifacts already produced) — that's a different problem (a handoff context/data schema), not a rules problem. This tool only ever handles four things: persona/tone, forbidden actions, numeric/business-rule limits, and required phrasing. It never touches task data, and it never touches "is this agent allowed to use this tool/see this data" (that's an authorization question, also out of scope here).

## Data this needs from you

**Ideally**: the full system prompt / instructions text of both agents — the upstream agent that's handing off, and the downstream agent that's receiving the task. Paste both in full; don't summarize them yourself, since the exact wording matters for extracting numeric limits and required phrasing correctly.

**If you're running this inside a coding assistant that can read files** (e.g. Claude Code), you can instead just give the file paths to both agents' definition files (a subagent `.md` file, a CrewAI YAML config, a LangGraph node's prompt string, etc.) and ask it to read them directly rather than retyping them.

**Optional but useful**: a specific incident where the downstream agent already broke a rule the upstream agent was enforcing (paste the transcript or describe it), and/or a sample downstream response you want checked against the drafted rules.

## What to paste after this template

1. Upstream agent's full definition/system prompt (required).
2. Downstream agent's full definition/system prompt (required — if you only have a one-sentence description, say so, the output will flag reduced confidence).
3. A known-bad incident, if you have one (optional).
4. A sample downstream response to spot-check, if you have one (optional).

## The procedure to follow

1. **Extract from the upstream agent's definition only**, sorted into exactly four categories — don't invent a fifth without saying why:
   - **Persona/tone**: declared voice, formality, empathy stance, any "always/never speak like X."
   - **Forbidden actions**: explicit "never do X," topics it won't touch, actions it won't take.
   - **Numeric/business limits**: dollar amounts, percentages, quantities, thresholds tied to a rule (e.g. "refunds under $50 only," "escalate above $10k").
   - **Required phrasing**: exact or near-exact required language (disclaimers, compliance text, a specific apology format).
   Quote or tightly paraphrase the actual source line for each — never summarize away a specific number or exact phrase.

2. **Run a Downstream Fit Check on every single extracted item** — for each one, decide whether it plausibly still applies once the downstream agent's own role takes over, or whether it's upstream-specific and should NOT carry forward (classic trap: upstream's "never discuss pricing" is often upstream-only if the downstream agent's entire job is pricing). State the call and a one-line reason for every item, even the obvious ones — never silently assume something carries over.

3. **Flag ambiguous rules on their own list.** If the source text doesn't make the scope clear (e.g. "caps discounts at $50" — per item? per order? new customers only?), name the exact ambiguity instead of guessing or folding it into the capsule as settled.

4. **Draft the capsule** — a structured object containing every item that passed the Downstream Fit Check as "carries over," each tagged with its category and a short reason it belongs. If the downstream agent's definition is missing or too thin to really fit-check (everything came back "fit unknown" in step 2), still include every extracted item in the capsule — tag each one `fit_status: unknown, confirm once downstream agent is defined` instead of leaving it out. Give the user a working draft to build against, not a refusal or an empty capsule.

5. **If a sample downstream response was provided, spot-check it** against every capsule item: PASS, VIOLATION, or UNCLEAR, quoting the exact phrase from the response that supports each call. This is one manual pass over one sample — always label it advisory, never claim it would catch every future violation.

6. **List what's still missing** before this capsule could actually be wired into a live system — e.g. "downstream definition was only a one-sentence description, re-run with the real system prompt once it exists."

## Output format

```
## Handoff
<upstream agent> → <downstream agent>: <what triggers this handoff>

## Constraint Capsule
{
  "capsule_id": "<slug>-v1",
  "from_agent": "<name>",
  "to_agent": "<name>",
  "persona_tone": [ {"rule": "...", "source": "quoted/paraphrased line"} ],
  "forbidden_actions": [ {"rule": "...", "source": "..."} ],
  "numeric_business_limits": [ {"rule": "...", "source": "..."} ],
  "required_phrasing": [ {"rule": "...", "source": "..."} ]
}

## Downstream Fit Check
- <item> — CARRIES OVER / DOES NOT CARRY OVER — <reasoning>
(one line per extracted item, including excluded ones)

## Ambiguous Rules
- <rule> — <exactly what's unclear>
(or "none found")

## Conformance Spot-Check
<"Not run — no sample response provided" if none was given>
- <capsule item> — PASS / VIOLATION / UNCLEAR — "<quoted phrase>"

## Open Gaps
<what's missing before production use, or "none">
```

## Rules this tool follows (don't let it skip these)

- It never invents a rule that isn't actually in the upstream agent's own text — no rule there means no entry, not an "ambiguous" guess either.
- It never carries an upstream rule into the capsule automatically — every single item gets an explicit Downstream Fit Check line, even the ones that seem obviously fine.
- It never claims to enforce anything — this produces a draft capsule and, at most, a one-time spot-check of a sample response. Actually wiring the capsule into a live pipeline (so every real handoff gets checked automatically) is separate infrastructure work this prompt does not do.
- It never treats the spot-check as a validated detector — one sample, one pass, always labeled advisory.
- It never mixes in task data, decisions already made, or artifacts produced — that belongs in a different kind of handoff schema, not this capsule.
- It never mixes in tool/data access permissions — that's an authorization boundary question, not a conduct-rules question.
- If the downstream agent's definition is missing, it says the fit check can't be completed and still includes every extracted item in the capsule tagged "fit unknown" — it never omits them and never hands back an empty capsule.
