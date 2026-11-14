# Agentic Stack Benchmark Selector

A prompt template for picking an agentic AI framework/SDK (LangGraph, CrewAI, OpenAI Agents SDK, Pydantic AI, Microsoft Agent Framework, or others) tied to your team's own task and constraints — instead of a generic "top 10 frameworks" listicle or whichever one a teammate happened to use last.

Works in any AI chat tool that can browse/search the web (ChatGPT with browsing, Claude with web search, Gemini, Perplexity, etc.). If your tool can't search the web, it can still run this using its own training knowledge, but you should ask it to flag that explicitly in the output (see Guardrails below).

## When to use this

You're choosing a framework/model/tool-calling stack for a new or existing agent project, and someone has asked "which agent framework should we use" or you're mid-debate between two or more candidates. Use this before picking based on a blog post, a forum thread, or inertia.

Not for: picking a base LLM/model (a separate decision), or choosing an orchestration *pattern* (hierarchical vs. peer-to-peer) once you've already committed to a framework — that's narrower and different.

## What you need to provide

This is a **manual-input** tool — there is no live connector to a real benchmark database behind it (nobody has built a service that actually runs your task against every framework's live SDK and measures real cost/latency/success — if one existed, use that instead and skip this). You provide, in your own words:

1. **1–3 representative task scenarios** for the agent you're building. Be concrete: "a support-ticket triage agent that reads an inbox, classifies urgency, and either auto-replies or escalates to a human queue" — not "an agent that does stuff."
2. **Your hard constraints**, ranked if you can: latency budget, expected number of tools/steps per run, self-hosting or data-residency requirement, your team's existing language/runtime (Python-only? TypeScript?), team size/experience with agent frameworks, and whether a model vendor is already locked in.
3. Optionally, the specific candidates you want compared. If you don't name any, the default set is LangGraph, CrewAI, OpenAI Agents SDK, Pydantic AI, and Microsoft Agent Framework.

If you don't have a real scenario yet, go write one first — a vague ask ("help us pick a framework") produces a vague, useless answer.

## The prompt

Paste this into your AI tool, filling in the bracketed parts:

```
You are helping me pick an agentic AI framework/SDK for a real project. Do NOT give me a generic listicle or popularity ranking. Follow this process exactly:

MY SCENARIOS:
[describe 1-3 concrete task scenarios your agent must handle]

MY CONSTRAINTS (ranked most important first):
[list your hard constraints: latency budget, tool/step count, self-hosting/compliance needs, language/runtime, team experience, model vendor lock-in if any]

CANDIDATES TO COMPARE:
[list specific frameworks, or say "use your default set of mainstream agentic frameworks"]

Now do the following:
1. Restate my scenarios and constraints back to me in one short paragraph so I can correct anything before you proceed.
2. List the candidates you'll evaluate, and drop any that flatly violate a hard constraint, stating why.
3. For each remaining candidate, search for or recall dated, specific evidence relevant to MY scenarios: how well it handles the state/workflow management, multi-step tool-calling reliability, multi-agent coordination (if my scenario needs it), self-hosting/deployment story, and current maturity (GA vs beta vs stale/unmaintained). Cite a source (doc page, changelog, GitHub activity, a named article) and its approximate date for every claim you use — no claim based on reputation alone.
4. Score each surviving candidate 1-5 per scenario against my ranked constraints, with a one-line justification citing the evidence from step 3. If two tie, say so.
5. Flag any score built on thin, old (more than ~9 months for a fast-moving framework), or conflicting evidence as low-confidence — don't present it with the same certainty as well-evidenced scores.
6. Give me a primary recommendation and a runner-up, and name the one constraint change that would flip your pick to the runner-up.
7. Name the single biggest risk of your recommended pick for MY scenario specifically — not a generic risk.
8. Tell me what concrete event should make me redo this whole process (a framework reaching GA, my scenario changing materially, a named upcoming migration) — treat today's pick as provisional, not permanent.

Output a single markdown report titled "Stack Decision Record" with these sections in order: Scenarios & Constraints Captured, Candidates Considered, Scoring Matrix (table: candidate x scenario, each cell = score + one-line evidence citation, plus a constraint-weighted total column), Recommendation, Biggest Risk, Confidence & Staleness Notes, Re-evaluation Trigger.

Guardrails — do not violate these:
- Never invent a benchmark number (cost, latency, success rate) as if it came from an actual measured test run. Label the whole report "Heuristic, evidence-cited scoring — not a measured benchmark run" at the top.
- Never score a candidate using "it's popular" or "it's well-documented" alone as the evidence — that's not evidence.
- If you cannot search the web right now, say so explicitly at the top of the report and rely only on your training knowledge, flagging that every score is therefore potentially stale.
- If I haven't given you a real scenario, stop and ask me for one instead of inventing a generic example.
- If you find nothing relevant for a candidate on a given scenario, write "insufficient evidence" in that cell rather than guessing a plausible-looking number.
```

## What you get back

A single "Stack Decision Record" document with:
1. **Scenarios & Constraints Captured** — confirms it understood your situation correctly before scoring anything.
2. **Candidates Considered** — the final list, with anything dropped and why.
3. **Scoring Matrix** — a table scoring each remaining candidate against each of your scenarios, with a cited, dated piece of evidence behind every score, plus a constraint-weighted total.
4. **Recommendation** — a primary pick and a runner-up, with the specific constraint change that would flip the pick.
5. **Biggest Risk** — the one real risk of the recommended pick, specific to your scenario.
6. **Confidence & Staleness Notes** — which scores are shaky and why.
7. **Re-evaluation Trigger** — the concrete event that should make you redo this later, since frameworks in this space change fast.

## Guardrails (why these rules exist)

- **No fabricated benchmark numbers.** This tool does not run your code against anything. Every score is a cited judgment call, not a timed test — the report says so up front so you don't mistake it for lab data.
- **No scenario-less recommendations.** A framework pick made without a real task in mind is exactly the kind of generic listicle advice this tool exists to replace.
- **No silent evidence-gap padding.** If the search turns up nothing specific for a candidate, the report says "insufficient evidence" rather than a confident-sounding guess.
- **No permanent verdicts.** The re-evaluation trigger is mandatory output, not optional — these frameworks are evolving fast enough that a six-month-old pick can already be stale.
