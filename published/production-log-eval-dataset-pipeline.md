# Trace to Gold: An End-to-End Privacy-Safe Production-Log-to-Eval-Dataset Pipeline

Every team running an LLM feature in production is sitting on the best eval dataset they'll ever have — thousands of real traces showing exactly how the model fails in the wild — and almost none of them use it. Building a golden eval set from that traffic means clustering it, scrubbing it for PII, deduping near-identical cases, and labeling what's left, and right now that's four separate problems with three different half-finished answers scattered across the industry. So teams skip it and hand-write a dozen examples instead, leaving their eval suite blind to the failure modes their own production traffic is actually producing.

## The Gap

Fireworks AI's blog on "Turning Production Logs into Evaluation Datasets" lays out the first half of the pipeline cleanly: pull traces from Langfuse or Braintrust, cluster them by meaning using their open-source Eval Protocol x Lilac integration (embeddings, UMAP, HDBSCAN), sample representative cases per cluster — and then stop. There's no privacy scrubbing step, no labeling step. A dev.to post titled "Your LLM traces are write-only" tells the other half of the story from the opposite direction: a solo developer built `toad-eye`, a CLI that exports a Jaeger trace straight into a YAML eval dataset with generated assertions, but the author's own README flags the inline-scoring mode as "still in progress." And OneUptime's guide "How to Build a Golden Evaluation Dataset from Real LLM Production Failures" is explicit that privacy review, reproducibility checks, and rubric calibration are steps *the reader* performs by hand — it's a checklist, not a tool.

Three independent sources, three different stopping points in the same pipeline. A re-verification search for "turn production LLM traces into evaluation dataset tool github" turned up nothing that closes the loop — Braintrust and Microsoft Foundry both ship commercial trace-to-dataset features, but neither advertises an integrated privacy-review step. Nobody has wired sampling, PII scrubbing, deduplication, and labeling into one tool. Each piece exists; the connective tissue doesn't.

## The Project

The idea is to take a connected trace source — Langfuse, Braintrust, or raw OpenTelemetry GenAI spans straight from a team's own collector — and emit a versioned, labeled eval dataset in a single run, instead of three separate manual hand-offs between tools and people.

The pipeline clusters traces by semantic similarity to surface representative failure modes, deduplicates near-identical cases within each cluster so a reviewer isn't shown the same bug fifty times, runs a deterministic PII/secret scrubber on every surviving example (with a flagged-for-review fallback rather than a silent guess on ambiguous spans), and then hands each cluster to a human with an auto-drafted assertion or rubric suggestion already attached — so the human is approving and editing, not authoring from a blank page. The output is a versioned JSONL/YAML export with a changelog tracing every example back to the exact production trace it came from. The connector layer, the clustering/dedup stage, the scrubber, and the labeling UI are each individually unremarkable — the point is that nobody has put all four in one pipeline instead of leaving them as three vendors' and one hobbyist's unfinished pieces.

## Tangible Impact

**Population**: ML/eval engineers at companies running production LLM features who already use a tracing platform (Langfuse, Braintrust, or OTel-based observability) but have no eval dataset beyond a handful of hand-written examples — per LangChain's 2024 State of AI Agents survey, roughly 51% of surveyed companies run agents in production, and tracing-platform usage among that group implies thousands of teams with raw trace data sitting unused for evaluation.

**Mechanism**: Today, building a golden eval set from real traffic requires a team to separately solve clustering, deduplication, privacy review, and labeling — most teams simply skip it and hand-write a dozen examples instead, leaving their eval suite blind to the failure modes production traffic actually contains. A single pipeline that produces a privacy-safe, deduplicated, pre-labeled candidate set turns "build an eval set from logs" from a multi-week cross-functional project into an hours-long review pass.

**Measure**: time from "we have traces" to "we have a reviewed N-item eval dataset" (baseline: weeks per OneUptime's manual-steps framing; target: under a day); number of real production failure modes represented in the resulting eval set versus a hand-written baseline set from the same team; PII/secret leakage rate in the output dataset (target: zero on a seeded-PII test corpus).

## Try It

No companion Claude Code skill has been written for this idea yet — it's tagged `Format: BOTH`, still awaiting a skill-synthesis pass. The idea file already sketches what that skill would do, though: a user pastes a small batch of raw trace JSON (a few dozen to a few hundred records) and gets back a clustered summary of distinct failure patterns, a deduplicated candidate list per cluster with any detected PII redacted inline, and a drafted assertion per candidate ready for a human edit — a one-shot, paste-in preview of what the full connected pipeline would eventually surface automatically, not the always-on pipeline itself. Watch this repo's `skills/` directory for when that lands.

The project's own data-sourcing posture is worth being upfront about too: the core pipeline is CONNECTED, reading directly from Langfuse's and Braintrust's existing trace-export APIs (both mature and already shipping today) or raw OTel GenAI spans — no manual log paste required to run it for real. The future skill preview above is the one MANUAL exception, by design, since a quick sanity check shouldn't require standing up the full connector first.

## The honest caveat

This is a PARTIAL gap, not a wide-open one, and it's worth saying so plainly. Clustering quality depends heavily on embedding choice and traffic diversity — a low-diversity sample of traffic could produce clusters that miss rare but important failure modes entirely. PII scrubbing that's tuned too aggressively destroys eval signal outright (redacting the one name that's the actual test subject of a support-bot eval is a real failure mode, not a hypothetical one), so the review-fallback design needs real tuning against its false-positive rate before anyone trusts it on sensitive data. And there's a live platform-risk: if Langfuse or Braintrust ship this exact integrated feature themselves in the next few cycles — plausible, since Fireworks' integration already does half of it — a standalone tool's value narrows fast to teams running other or self-hosted tracing stacks. Teams with no tracing platform in place at all get nothing from this until they adopt one first, which keeps the immediately addressable population to teams already one step into the observability stack, not everyone running an LLM feature in production.

---

Surfaced from `research/2026-11-20-llm-evaluation-observability-ii.md`, pattern `P1`.
