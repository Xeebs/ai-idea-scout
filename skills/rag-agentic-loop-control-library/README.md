# Agentic RAG Loop Audit

A paste-in prompt for any AI chat tool. It reviews a hand-rolled agentic retrieval loop — the kind where code plans a query, retrieves documents, critiques whether the retrieval was good enough, and either answers or rewrites the query and tries again — and checks it against three failure modes that recur across real practitioner write-ups of this exact pattern: a missing retry cap, a stopping criterion that isn't actually calibrated to anything, and unhandled malformed JSON from the underlying model's tool calls.

It is scoped for solo developers and small teams building an internal or early-stage retrieval tool over roughly hundreds to low-thousands of documents — not a claim to fix million-document retrieval infrastructure. If your system is at that scale, this audit will say so rather than pretending to help.

## When to use this

Use it the moment you're about to ship a custom agentic-retrieval loop and want it checked before it hits real traffic, or after it's already hung, looped forever, quit after a single pass when it shouldn't have, or crashed on a malformed response from the model mid-loop.

## What to paste in

Copy this whole prompt into your AI chat tool, then paste your actual code or a close description of it where indicated.

```
You are auditing my hand-rolled agentic RAG retrieval loop (retrieve -> critique -> re-query -> stop) for three known failure modes. This is a code review, not an architecture redesign — patch my existing loop, don't tell me to adopt a different framework.

My loop code / description (paste below):
<PASTE YOUR LOOP CODE OR A STEP-BY-STEP DESCRIPTION HERE>

Optional context:
- Corpus size / scale: <e.g. "about 800 internal docs" or "unknown">
- Any failure I've already hit: <e.g. a stack trace, a hang description, a sample of malformed JSON the model returned, or "none yet, pre-ship review">

Please do the following:

1. Parse my loop into its five pieces: the retrieve call, the critique/evaluate step, the re-query/rewrite step, the loop's exit condition(s), and how it handles the model's tool-call/structured output. If a piece is genuinely missing from what I pasted, say so rather than guessing.

2. Check failure mode 1 - missing retry cap. Flag CRITICAL if there's no hard maximum iteration count (e.g. "while True" or unbounded recursion). Flag WARNING if a cap exists but is unreasonably high (>10) with no stated reasoning. Otherwise OK.

3. Check failure mode 2 - uncalibrated stopping criterion. Flag CRITICAL if the only way the loop stops is hitting the retry cap (no quality signal at all). Flag WARNING if a threshold exists but is a vague instruction rather than a checked numeric value. Otherwise OK.

4. Check failure mode 3 - unhandled malformed tool-call JSON. Flag CRITICAL if there's no error handling around parsing the model's structured output at all. Flag WARNING if handling exists but has no bounded retry of its own (so persistent malformed output could still loop forever). Otherwise OK.

5. Bonus check - does the loop log *why* it exited (answered / max-iterations-hit / low-marginal-gain / parse-failure-exhausted)? If not, flag INFO and explain why this matters for seeing these failure classes in production.

6. If my described scale sounds like it's actually a million-document-scale retrieval system, say so explicitly and tell me this audit addresses loop logic only, not retrieval infrastructure.

7. For every CRITICAL and WARNING, give me the actual code to add or change, in my language/framework if you can tell what it is from what I pasted. If you can't confirm the exact API, say so and give me the framework-agnostic version instead of guessing syntax.

8. List anything you genuinely can't verify from what I pasted (e.g. whether my retrieve() function is idempotent across retries) as residual risk — don't assume it's fine.

Give me the result as:
- Loop structure summary (2-3 sentences)
- Findings table: Failure Mode | Severity | What was found | One-line fix summary
- Drafted fixes (actual code, one per CRITICAL/WARNING)
- Exit-reason logging recommendation (only if that check was INFO)
- Residual risk (bullet list)

Do not declare my loop "safe" or "production-ready" overall - only report against the three named failure modes and the logging check. Do not tell me to switch frameworks. Do not cite a specific retry count as an industry standard - present it as a tunable starting point. If you can't evaluate one of the failure modes because a piece is missing from what I pasted, say so instead of guessing a verdict.
```

## What you get back

A single report: a short summary of what loop pieces were found, a findings table rating each of the three failure modes (plus the exit-logging bonus check) as CRITICAL / WARNING / OK / INFO, the actual code fix for every CRITICAL or WARNING, and a residual-risk list of anything that couldn't be verified from what you pasted. Nothing in the report claims your loop is now "safe" in general — it's a targeted check against three specific, well-documented failure modes, not a full code review.

## Guardrails this prompt enforces

- No framework-migration advice — it patches your loop, it doesn't tell you to rewrite it in LangGraph or LlamaIndex.
- No invented API calls — if the exact method name for your framework can't be confirmed from what you pasted, it says so and gives you the generic fix.
- No "industry standard" number-dropping — retry counts and thresholds come back as reasoned starting points to tune, not settled facts.
- No silent gap-filling — if your pasted loop is missing a piece entirely (e.g. there's no critique step at all), it tells you which failure mode it couldn't assess rather than inventing a verdict.
