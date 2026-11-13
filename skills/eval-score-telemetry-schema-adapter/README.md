# Eval-Score Telemetry Schema Adapter

A paste-into-any-AI-chat prompt that produces a field-by-field feasibility report for moving or duplicating LLM eval-score telemetry (Datadog, Arize, Langfuse, New Relic AI Evaluation) between vendors, or mapping it onto the draft OpenTelemetry GenAI evaluation attributes. If your team emits eval scores (faithfulness, toxicity, groundedness, task-success, etc.) into one vendor and is weighing a switch or a side-by-side second vendor, this tells you, concretely, how much of your current instrumentation survives and what breaks — before anyone commits engineering time.

## Why this exists

Trace/span telemetry converged on OpenTelemetry years ago. Eval-score telemetry did not: Datadog ships its own `ml_obs.evaluation.*` fields, Arize uses an OpenInference `eval.<name>.label/score/explanation` span-attribute convention, Langfuse has its own `scores` object, and New Relic's AI Evaluation feature is still in preview with no stable field names. A canonical OTel GenAI evaluation attribute set exists on paper but is an unreleased draft. None of this is portable today, and because these specific sub-schemas are newer than core tracing, they also drift faster — a mapping done six months ago may already be stale.

This is a one-time assessment tool, not a running piece of software. It will not call any vendor's API for you and it has no live access to your observability stack. You give it a real sample of how you emit eval scores today; it gives you back a mapping report and a draft config you (or an engineer) can act on.

## What to give it

Before asking for a report, have ready:

1. **Your current vendor** and an **actual sample** of how you emit eval scores today — a real code snippet (the actual SDK call you make, e.g. a `submit_evaluation(...)`, `langfuse.score(...)`, or `log_evaluations(...)` call) or a real exported row/JSON payload with the field names and example values as they actually appear. A vendor name by itself is not enough — field-name drift is exactly the problem this tool exists to catch, so it needs to see your real fields, not just know your vendor's name.
2. **Your target vendor(s)** — one or more of Datadog, Arize, Langfuse, New Relic — or say "OTel GenAI canonical" if you just want to future-proof against the draft spec rather than target a specific vendor.
3. *(Optional)* Roughly how many scores per day you emit, and whether you need historical scores backfilled or only new ones going forward — this changes the effort estimate, not the mapping itself.

If you have no eval scores emitted anywhere yet (pre-instrumentation), this tool isn't useful yet — come back once you have at least one real emitted score to anchor against.

## The prompt

Paste this into your AI chat tool, filling in the bracketed parts:

> I need a migration-feasibility report for moving LLM eval-score telemetry from one observability vendor to another (or onto the draft OTel GenAI evaluation attributes). Here is my current vendor and an actual sample of how I emit eval scores today:
>
> Current vendor: [Datadog / Arize / Langfuse / New Relic]
> Sample (real code snippet or exported payload, with actual field names and example values):
> [paste it here]
>
> Target vendor(s): [name one or more, or "OTel GenAI canonical"]
>
> Please:
> 1. List every field actually present in my sample, verbatim — don't infer fields that aren't there just because the vendor's docs mention them elsewhere. If my vendor embeds the metric name inside the field name itself (e.g. Arize/OpenInference's eval.<name>.label / eval.<name>.score / eval.<name>.explanation convention), group every field sharing the same <name> into its own separate evaluation record before mapping.
> 2. Map each field to this canonical intermediate schema, which tracks the draft OTel GenAI evaluation attributes: eval.name, eval.score.value, eval.score.label, eval.explanation, eval.target_ref (trace/span/request id), eval.evaluator.type, eval.evaluator.id, eval.timestamp, eval.metadata (catch-all). For each mapping, mark it CONFIRMED (exact documented match), INFERRED (close but not an exact match — flag it), or UNRECOGNIZED (ask me what it means rather than guessing).
> 3. Map each canonical field onward to my target vendor's known field, marking each CLEAN (no information lost), LOSSY (needs a type/precision transform — say what's lost), or NO EQUIVALENT (target vendor has no slot for it).
> 4. If New Relic is in scope anywhere, flag that row LOW CONFIDENCE — it's a preview product and its field names are the least stable of the group; tell me to verify against current docs rather than trusting the table.
> 5. Give me a translation-completeness verdict: HIGH (≥80% of my fields map CLEAN end-to-end), MEDIUM (50-79%), or LOW (<50%), with the percentage shown.
> 6. Draft a declarative adapter config — source_field -> canonical_field -> target_field, YAML, with a one-line transform note on every LOSSY field. This is a planning artifact for a human to implement, not working code that calls either vendor's API with my credentials.
> 7. Give me a doc-verification checklist: the 2-4 exact vendor doc pages/API references I should open right now to confirm the field names in your mapping table haven't moved, since this exact area (eval-score sub-schemas) is newer and less stable than core tracing.
> 8. Give me an effort estimate in hours-vs-weeks, driven by how many fields are LOSSY/NO EQUIVALENT and whether you can confirm the target vendor's API even accepts externally-submitted eval scores at all — if that's unverified, say so and widen the estimate.
>
> Rules: never map a field without it actually appearing in my sample. Never call a field CLEAN unless it's clean on both hops (source-to-canonical and canonical-to-target) — anything less is LOSSY. Never produce or imply working, credentialed code that calls a live API — only the mapping table and the YAML config artifact. If a field in my sample matches nothing you recognize, mark it UNRECOGNIZED and ask me, don't force it into the nearest-sounding slot.

## What you get back

A report with these sections, in this order:

1. **Translation completeness verdict** — HIGH/MEDIUM/LOW with the percentage of your fields that map cleanly end-to-end.
2. **Field mapping table** — source field, canonical field, mapping confidence (CONFIRMED/INFERRED/UNRECOGNIZED), target field, translation status (CLEAN/LOSSY/NO EQUIVALENT), and a note.
3. **Lossy / no-equivalent fields** — a plain list of what breaks and why, so you know exactly what to expect before you start.
4. **Draft adapter config** — a YAML mapping artifact for a human (or your own build) to implement — not live code.
5. **Doc-verification checklist** — the exact doc pages to check before you trust any of this, because this specific area of vendor schemas moves faster than core tracing does.
6. **Effort estimate** — hours vs. weeks, and what's driving that number.
7. **Disclaimer** — this is a one-time assessment from a pasted sample and public docs as understood at report time, not a guarantee the vendor hasn't changed something since, and not a running adapter.

## What this is not

This does not build, install, or run a continuously-operating translation layer that watches your live telemetry and rewrites it on the fly — that's a genuinely separate, longer-lived engineering project (a library with per-vendor adapter classes and a replay CLI), not something a chat prompt can responsibly claim to deliver. This tool answers "how much work is this, concretely, for my actual fields" so you can decide whether that larger project is worth building.
