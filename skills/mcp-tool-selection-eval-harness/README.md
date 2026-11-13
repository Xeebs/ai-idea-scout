# MCP Misroute Forensics

A paste-in prompt for diagnosing a single tool-selection failure in an agent that has multiple MCP (or other function-calling) tools registered — the case where every tool works fine on its own, but the agent picked the wrong one for a specific request. Works in any chat tool; no installation needed.

## When to use this

Use this the moment you have a concrete misroute to diagnose: your agent had several tools available, a user request came in, and the agent called the wrong tool even though that tool (and the right one) each pass their own individual tests. This is a one-shot forensic review of a single incident, not a test suite you run continuously — it will, however, hand you the first couple of regression test cases to start one.

Don't use this if you don't yet have a specific failing example in hand — it needs a real transcript, not a hypothetical.

## What to hand over (copy this into the chat)

**Data source**: Manual. You paste this in yourself — there's no automatic connector that pulls MCP tool registries or agent logs for you today. Gather:

1. **The original user request**, word for word.
2. **The tool that got called instead**, with its full description text exactly as registered (not paraphrased).
3. **The other tools the agent had available**, each with its full description text — especially the one that *should* have been picked, if you know which one that is.
4. *(Optional)* Any system prompt or routing instructions given to the agent.

If you're missing any of #1-#3, gather it before using this — a diagnosis built on a guessed-at tool description will sound confident and be wrong.

## The prompt

Paste the following into any AI chat tool, then paste your incident details (request, tool called, full candidate tool list with descriptions, optional system prompt) right after it:

```
You are diagnosing a single MCP/agent tool-selection failure (a "misroute"): the agent had multiple tools registered and picked the wrong one for a request, even though the tool it picked passes its own unit tests fine on its own.

I will give you: the original user request, the tool that got called instead, the full list of candidate tools (with their exact descriptions), and optionally a system prompt. Do not invent or paraphrase any tool description — work only from what I give you, and if something critical is missing, ask me for it before continuing.

Walk through this procedure and give me back a structured report:

1. State the incident in one line: "User asked for X, the agent called tool A (should have called tool B)." If I haven't told you which tool was correct, infer the most plausible one from the list but mark it clearly as an inference, not a stated fact.
2. Diff the descriptions of the tool that got called against the tool that should have been called (and any other tool with real overlap). Quote the exact overlapping words, verbs, or phrases from each description that make both look like valid matches for my request — don't just say "they're similar."
3. Name the missing boundary: what does neither description rule out that would have disambiguated them? Tool descriptions usually say what a tool does but not when NOT to use it — find that gap.
4. If I gave you a system prompt, check it for keyword-triggered rules (like "always use X when the user mentions 'report'") that could override good tool descriptions on their own. Call this out separately from the description-overlap cause, since the fix is different (edit the system prompt, not the tool description).
5. Write a concrete rewrite of the offending tool's description (and the correct tool's, if it also needs one) that adds an explicit "use this for / do NOT use this for" boundary. Keep it short enough to still work as a real function-calling schema description — 1 to 3 sentences, not a paragraph.
6. Generate 2 to 3 new regression test cases in the format "intent -> expected tool" that would have caught this exact failure. Include at least one deliberate near-miss distractor (phrased close to my original failing request but genuinely belonging to a different tool) and one that confirms the fix doesn't break a request that was previously routed correctly.
7. Tell me your confidence level. If the descriptions already look well-bounded and distinct and don't fully explain the misroute, say so instead of forcing a root cause — name the likelier alternative (too many tools in context, model-specific tool-calling quirks, a system-prompt conflict) instead.

Give me your answer in this exact structure:

## Incident Summary
## Root Cause: Description Overlap
## System Prompt Interference (only if I gave you a system prompt; otherwise omit)
## Suggested Description Rewrite
## Regression Scenarios to Add (as a yaml-style list: intent -> expected_tool)
## Confidence & Limits

Here is my incident:
[paste: the user request, the tool called with its full description, the full candidate tool list with descriptions, and optionally the system prompt]
```

## What you get back

A short markdown report in the six sections above: what happened, which exact phrases in the two tool descriptions overlap, whether a system prompt made it worse, a drop-in rewrite for the offending description, 2-3 regression test cases you can paste straight into whatever test file or suite you maintain, and an honest statement of what this diagnosis is and isn't sure of.

## What this does not do

This is a single-incident diagnostic, not a CI-gating regression suite. It will hand you the first few test cases for one, but it doesn't run them, store them, or re-check them on every future tool change — that's a separate, bigger piece of infrastructure (sometimes called a "tool-selection eval harness") that you'd build and wire into CI yourself if misroutes keep recurring across your toolset.

## Guardrails this prompt follows

- It will not invent a tool's description or behavior beyond what you paste in.
- It will not state a root cause with false certainty when the evidence is genuinely ambiguous.
- It will not recommend removing or merging tools as the fix unless you ask for that explicitly — a description rewrite plus a regression case is the smallest fix, not an architecture change.
- It will not give you only one exact-duplicate regression case — it always includes a near-miss distractor, because a single exact-phrase test is trivially satisfied without actually fixing the ambiguity.
- It will mark any inferred detail (like a guessed "correct tool") clearly as inferred, not stated fact.
