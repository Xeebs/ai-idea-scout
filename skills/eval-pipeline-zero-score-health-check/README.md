# Eval Pipeline Zero-Score Health Check

A paste-and-run prompt template for auditing an LLM evaluation pipeline (promptfoo, deepeval, or a custom OTel-GenAI-instrumented setup) for the specific failure mode where the pipeline runs without error but silently produces no usable score signal — the "I switched on production evals and they scored nothing" problem. No installation, no SDK, no ongoing monitoring required: this is a one-time diagnostic you run by pasting text into any AI chat tool.

## When to use this

Use this before trusting a new eval pipeline, right after an on-call incident that turned out to involve a flat/dead eval dashboard, or as a periodic sanity check on a pipeline that's been running quietly for a while. It is not a replacement for always-on monitoring — it's a point-in-time audit that tells you whether your current config and recent runs show signs of the silent-zero failure, plus the specific code change to fix it if they do.

## What to paste in

Hand the AI all of the following, verbatim:

1. **Your eval pipeline's config file** — the promptfoo `promptfooconfig.yaml`, the deepeval Python test file that defines your metrics/assertions, or your OTel exporter config, whichever applies.
2. **The JSON (or SQLite-exported JSON) output of your last 2-3 eval runs**, verbatim. One run is enough to get a partial audit, but 2-3 lets the AI check for score collapse across runs with more confidence.
3. **(Optional) Your schedule definition** — the cron line or CI workflow YAML that triggers the eval on a schedule, if it runs on a schedule rather than only on-demand or per-PR.

If you're missing any of these, say so up front — the audit will tell you what it can't check without them rather than guessing.

## The prompt

Paste this along with your files:

> I'm running an LLM evaluation pipeline and I want you to audit it for the "silent zero-score" failure mode — where the pipeline runs with no error but produces no usable score signal, and nobody notices until much later. Here is my eval config and my last few run outputs (and my schedule, if applicable — see below). Please:
>
> 1. Identify which framework this is (promptfoo, deepeval, OTel GenAI, or something else) from the config shape.
> 2. Parse the run output into per-sample scores and check: (a) whether ≥90% of samples in any run have a null/missing/undefined score (not a low numeric score — a genuinely absent one), (b) whether every score in a run is numerically identical across ≥10 samples (a collapse, not a coincidence), and (c) if I gave you a schedule, whether the most recent run is more than 2x overdue versus the expected cadence.
> 3. Look at the config itself for code that could cause a silent null: a custom scorer or assertion that catches an exception and returns 0/null/False instead of re-raising or logging it, or a scorer whose failure path looks identical to its "legitimately scored zero" path.
> 4. For every finding, tell me explicitly whether it's a "legitimately low/zero score because the thing being tested actually failed" or a "the scorer never ran to completion" case — and say so if you genuinely can't tell from what I gave you.
> 5. Give me a findings table (signature, severity High/Medium/Low, the exact quoted evidence from what I pasted, and the legitimately-zero-vs-didn't-compute verdict), then one concrete fix per High/Medium finding — an actual code or config change, not "investigate further" — and finally a list of which checks came back clean.
>
> Do not invent any score, sample ID, timestamp, or line of config that isn't literally in what I pasted. Do not flag score collapse on fewer than ~10 samples. Do not claim my schedule has stopped firing unless I actually gave you a schedule definition. Do not recommend buying a monitoring product — just tell me what to change in what I gave you.
>
> My config:
> [paste config here]
>
> My last 2-3 run outputs:
> [paste run JSON here]
>
> My schedule (if applicable):
> [paste cron/CI schedule here, or write "not scheduled"]

## What you get back

A short markdown report with:
- **Detected framework** and what gave it away.
- **Run data summary** — sample counts and date range from what you provided.
- **Findings table** — each finding tagged with severity, the literal evidence quoted from your paste, and whether it's a real-zero or a didn't-compute case.
- **Recommended fixes** — one specific, actionable fix per real finding (e.g. "re-raise the exception on line N of your custom metric instead of returning 0").
- **Clean checks** — what was checked and came back fine, so you know the audit's actual coverage given what you supplied.

## Limits

This is a one-shot audit of what you paste, not a live monitor — it can only see the runs and config you give it, and it will say explicitly when it doesn't have enough data (e.g. fewer than ~10 samples for the collapse check, or no schedule for the schedule check) rather than guessing. If you want always-on protection against this failure mode going forward, that's a separate, bigger project (an always-running sidecar watching every run) — this skill is specifically the fast, no-install check you can run today before that exists.
