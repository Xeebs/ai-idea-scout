# Real Traffic: A Production-Log Distillation Pipeline for Small Local Models

- **Status**: PROPOSED
- **Date**: 2026-11-20
- **Topic**: Small & local models
- **Source**: research/2026-11-20-small-local-models.md · P5
- **Maturity verdict**: PARTIAL — `OpenPipe` (OpenPipe/OpenPipe, 2,838 stars) logs real production request/response pairs and fine-tunes smaller models from them (closest existing match), but its GitHub repo has had no push since 2024-05-25 (18+ months stale, effectively abandoned per the rubric); commercial equivalents (CoreWeave Model Distillation, Azure Stored Completions) are in private preview or unconfirmed open availability; the NeurIPS 2026 paper describing this exact pattern ("Iterate on an LLM, Serve on an SLM") has no linked code. A maintained, evaluated, open pipeline specifically for this pattern does not exist.
- **Format**: BOTH — the log-ingestion/fine-tuning/evaluation pipeline is runtime infrastructure; a one-time "is your traffic distribution clean enough to distill, and with what filter" judgment on a sample is a separable advisory task.
- **Data Sources**: CONNECTED — reads production request/response pairs from the team's existing LLM observability platform (Langfuse or Helicone, via their export/query APIs — both mature, widely deployed today) or directly from the application's own request-log database table via a lightweight adapter. No external data is pasted for the running pipeline; the companion skill (below) uses a small MANUAL paste of sample logs for a lighter-weight, pre-connection advisory pass.

## The Gap
A NeurIPS 2026 paper, "Iterate on an LLM, Serve on an SLM," proposes distilling a small student model directly from a large model's *logged production outputs* via SFT — not synthetic imitation data generated for the purpose — as a cheaper, more faithful way to shrink a narrow-task workflow. The same WebSearch turned up only the older, standard practitioner pattern elsewhere ("a strong teacher labels training data, and a small student learns to imitate it"). The paper has no linked code, and the one open-source project that already does something close, OpenPipe, has been unmaintained for over 18 months.

## The Project
An open pipeline that connects to a team's existing LLM observability/logging platform, pulls real production request/response pairs, filters them by an implicit quality signal (no retry within a time window, no user edit, a thumbs-up, or a downstream action that succeeded), formats the survivors as SFT training examples that preserve the team's actual input distribution, LoRA/QLoRA fine-tunes a small open base model, and evaluates the resulting student against a held-out slice of the *same* production traffic — reporting a faithfulness score against the original large model's real outputs and a cost delta, instead of a synthetic benchmark number.

Components: a log-ingestion adapter (Langfuse/Helicone/direct DB table); a quality-signal filter with a few built-in heuristics; an SFT data formatter; a LoRA fine-tuning job runner on an open base model; a held-out-production-traffic evaluation harness.

## Tangible Impact
**Population**: Engineering teams running an LLM-backed feature in production at meaningful volume who already route calls through an LLM observability platform — a defensible lower bound is the combined job-post-tracked customer base of Langfuse (6,246 companies per Sumble's tracker) and Helicone (130 companies, same tracker); the broader population running LLM features in production without a tracked observability tool is almost certainly larger but not reliably sizeable from public data.
**Mechanism**: Today this population either hand-writes synthetic teacher-labeled training data (expensive, and provably less faithful to their own real input distribution per the NeurIPS paper's framing) or does nothing and keeps paying large-model inference cost on every request. This pipeline lets them point at logs they already have and get a distilled small model with an apples-to-their-own-production-traffic accuracy number, instead of a synthetic-benchmark guess.
**Measure**: (1) inference cost reduction (large-model $/request vs. distilled-model $/request) at a declared accuracy floor, measured on the same held-out production queries; (2) faithfulness gap — the student's output-match rate against the original large model's actual logged production outputs; (3) time from "connect logs" to a usable distilled model with a reported faithfulness number, targeting under a few hours of compute for a pilot dataset.

## Why Now
The NeurIPS 2026 paper just validated that distilling directly from recorded production behavior beats synthetic-teacher imitation for narrow-task workflows, but published no code. Cheap, capable small open base models and mature LoRA fine-tuning tooling (axolotl, Unsloth) already exist, and most candidate teams already have the needed production logs sitting in an observability platform today — the pipeline connecting the three pieces is what's missing.

## Skill Angle
Trigger: a developer is considering distilling their production LLM feature and wants a go/no-go judgment before building any pipeline. Inputs: a pasted sample of 20-50 real request/response pairs, ideally with whatever user-side signal is available (retried? edited? accepted?) — MANUAL for this skill specifically, so someone can get the judgment before connecting any live data source. Output: an assessment of whether the sample's input distribution is narrow/consistent enough to distill well, a recommended quality-signal filter for the full pipeline, and a rough estimate of how many SFT examples would be needed, with reasoning tied to this gap's evidence.

## MVP Sketch
A CLI that takes a Langfuse API key (or a CSV export) and a quality-signal rule (e.g., "no retry within 60 seconds"), pulls 500+ filtered production pairs, formats them as SFT examples, LoRA-fine-tunes a small open model (Llama-3.2-3B or Qwen2.5-3B) via an existing open-source trainer, and runs the resulting student against a held-out slice of the same log stream, reporting cost delta and faithfulness percentage. Experiment: run against one real team's support-reply or classification dataset and confirm the student matches the teacher's actual production outputs at a target rate for a fraction of the cost. 2-4 weeks, 1-2 people.

## Risks & Open Questions
- "No retry/edit" is a noisy proxy for quality — a confidently wrong answer the user didn't notice would get included and faithfully distilled too.
- Small teams' production volume may be too low (under 500-1,000 usable filtered examples) to beat synthetic data meaningfully.
- OpenPipe already attempted close to this exact pattern and went stale after 18 months — worth understanding why before re-building a similar tool (pricing, scope, or developer experience).
- Distilling straight from production behavior risks baking in and amplifying the large model's existing systematic errors, since there's no optional "teacher correction" step the synthetic-labeling approach can apply.
