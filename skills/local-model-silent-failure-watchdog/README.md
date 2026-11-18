# Local-Model Silent-Failure Watchdog — One-Time Detectability Audit

Paste this whole file (or just the prompt block near the bottom) into any AI chat tool — Claude, ChatGPT, Copilot Chat, whatever you have open — along with the information it asks for. No installation, no Claude Code required.

## What this is for

You're running a local model (Ollama, llama.cpp, or similar) in a scheduled, unattended job — a content-generation pipeline, a data-enrichment or ETL step, a batch process — and nobody watches every run's output. The dangerous failure mode for local models isn't a crash or an API error; it's **wrong output with no error at all**: truncated text, a repetition loop, a response that silently violates your expected format, or output that's confidently wrong while looking perfectly normal. Those slip downstream until something else breaks, and by then the debugging cost can exceed whatever you saved by running local in the first place.

This is a **one-time audit**, not a monitoring tool you install. You give it a description of your job (and ideally some real recent outputs), and it hands back:
- a map of exactly where your job can fail silently today,
- specific anomalies it finds in the samples you give it,
- a prioritized, concrete plan for the cheapest checks to add first,
- an honest answer on whether building that monitoring is even worth it yet,
- and an explicit statement of what no amount of this kind of monitoring will ever catch.

It produces a written plan. It does not write the monitoring code for you (that's a separate follow-on task if you want it) — it tells you exactly what to build and in what order.

## What to hand over

This only works from what you paste in below — it has no way to read your logs, your database, or your model's actual runs. Give it:

1. **Job description** (required): which local model/runtime you're using (e.g. "Ollama, llama3.1:8b"), what the job produces, how often it runs, and whether any human currently looks at each run's output.
2. **Output contract** (required, or say "none"): any schema, expected fields, or length range the output is supposed to follow.
3. **Sample outputs** (strongly recommended): paste 5–10 real, recent outputs verbatim. This is the single most useful thing you can provide — the audit can spot real problems in these, not just theoretical gaps. If you don't have samples handy, say so; the audit still runs, just note it's description-only.
4. **Downstream consumer** (required): what happens to the output (a file write, a database row, a queue message, published content) and how costly a bad one slipping through would be.
5. **Known incidents** (optional but valuable): any specific "it was wrong but nothing errored" case you've already hit, pasted verbatim if you have it.
6. **Existing downstream validation** (optional): does anything already check the output on the way in (a schema check on write, etc.)? Helps avoid recommending something redundant.

## The prompt

Paste everything below this line into your AI tool, filling in the bracketed sections with your actual information:

---

You are auditing a scheduled, unattended local-model automation job for where it can produce wrong-but-not-erroring output with nothing flagging it. This is a one-time audit producing a written report and plan — do not write monitoring code, just the audit.

**Job description**: [what local model/runtime, what it produces, how often it runs, whether anyone reviews each run]

**Output contract**: [any declared schema/format/length expectation, or "none"]

**Sample outputs** (5-10 real recent ones, verbatim, or state "none available"):
[paste here]

**Downstream consumer**: [what happens to the output, and how costly a bad one slipping through would be]

**Known incidents** (optional): [any specific wrong-but-no-error case already observed, or "none"]

**Existing downstream validation** (optional): [anything that already checks output on the way in, or "none"]

Now produce the audit in this exact structure:

1. **Job summary** — one line restating what's being audited.
2. **Detectability matrix** — a table across these four dimensions: Length/shape, Schema/structural conformance, Repetition/degeneration, Semantic correctness. For each, mark CONFIRMED-DETECTABLE, PARTIALLY-DETECTABLE, or BLIND SPOT, with the reasoning. Never assume a check exists that wasn't described — an unstated hop is a BLIND SPOT. Mark Semantic correctness BLIND SPOT by default unless I explicitly described a working secondary check for it. Watch for two traps that look like coverage but aren't: (a) a **misused proxy** — an existing check used as a stand-in for a dimension it doesn't actually measure (e.g. "drafts over 800 words skip human review" treating length as a stand-in for correctness); (b) a **silent safeguard** — a mechanism that already catches or masks a problem internally (an exception handler, a fallback to a default value) but never surfaces that it fired to any human. Neither earns CONFIRMED-DETECTABLE — mark BLIND SPOT or PARTIALLY-DETECTABLE and say explicitly why.
3. **Findings from sample outputs** — if I gave you real samples, analyze them directly for repetition loops, truncation, schema violations against my stated contract, or boilerplate/refusal text standing in for real output. Flag anything found as already happening right now, unflagged — this is stronger evidence than any theoretical gap. If I gave no samples, say the audit is description-only.
4. **Recommended baseline-tracking plan** — a prioritized list (cheapest-and-highest-risk first) of specific checks: for length/shape, a rolling mean/stdev band on a stated metric; for schema, a deterministic validation pass; for repetition/degeneration, an n-gram repetition ratio or compression-ratio heuristic with a stated threshold. For each, give a rough build cost (S/M/L).
5. **Baseline maturation timeline** — estimate roughly how many historical runs (e.g. 20-30 as a floor) a trustworthy statistical baseline needs, and translate that into wall-clock time given my stated run frequency. If that ramp-up is long relative to the risk, recommend a conservative static threshold as an interim measure instead of waiting on the baseline.
6. **Immediate zero-cost fix** — if step 2 found a misused proxy or a silent safeguard, state the specific, nearly-free fix you'd recommend right now (tighten/remove the proxy threshold; add a log/alert on the existing fallback path), independent of whether any monitoring ever gets built. If none was found, say so in one line.
7. **Build-vs-don't-build verdict** — one explicit sentence: is building this monitoring worth it right now, or not yet — and name the specific condition that would flip that answer.
8. **Ceiling** — one explicit paragraph: state plainly that none of the above (length, schema, repetition checks) will ever catch output that's confidently wrong but well-formed — that needs a secondary check (a cheap classifier, a deterministic business-rule check, or an optional cross-check call to a second model) or accepted residual risk. Say this even if everything else in the audit looks clean.

Rules you must follow while doing this: never invent sample outputs, incidents, or a schema I didn't give you — mark anything I didn't describe as a BLIND SPOT, not a best-case assumption. Never claim a statistical/structural check catches semantically-wrong-but-well-formed output. Don't write the actual monitoring code — stop at the plan. Don't recommend day-one alerting off an empty baseline — alert fatigue from a too-eager threshold is exactly the kind of thing that gets the whole system tuned out and ignored.

---

## What good output looks like

A complete answer fills all eight sections above, in order, with the detectability matrix as an actual table (not prose), at least one concrete recommended check per BLIND SPOT or PARTIALLY-DETECTABLE dimension found, an explicit yes-or-no build verdict (not a hedge like "it depends"), and the semantic-correctness ceiling stated as its own clearly separated paragraph — not buried in a caveat at the end.

## What this is not

This is not a monitoring tool, a cron wrapper, or working code. It doesn't connect to Ollama, your database, or your log files — it only reasons from what you paste in. If you want the baseline tracker, schema validator, and alert wiring actually built, treat that as a separate follow-on task once you have this audit's plan in hand.
