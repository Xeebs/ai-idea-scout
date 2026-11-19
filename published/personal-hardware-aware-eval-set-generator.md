# Personal Bench: A Hardware-Aware Eval Set Generator Built From Your Own Task Samples

Published leaderboards tell you how a model does on someone else's benchmark, on someone else's hardware, on tasks that aren't yours. Enough people have noticed this that they've started quietly rebuilding the same thing from scratch, alone, over and over — and nobody has packaged the obvious fix.

## The Gap

Two independent authors, in the same 30-day window, arrived at the identical conclusion by hand. A dev.to post titled "Your local LLM benchmark is probably lying to you" (bmdpat.com) makes the case directly: published leaderboard numbers lack the context of any one person's hardware or workload — a score with no denominator attached to it. A second author, writing separately on dev.to/llm_ops under the title "Your smallest local model might be your best one — I measured 4 of mine," states the fix plainly: "I wrote my own small benchmark, tuned to exactly my laptop." An Ask HN thread ("What is the best LLM for consumer grade hardware?") and a community roundup on local-llm.net both frame this the same way — as scattered anecdotal field reports, not a repeatable process anyone has turned into a tool.

What's missing isn't benchmarking tools generally — there are plenty. It's the specific, obvious-in-hindsight combination: take a handful of a person's *actual* task examples, run them against the models that actually fit on their *actual* hardware, and hand back a score they can trust and re-run. Every existing option misses this by being one half of the equation. BenchLoop ships a frozen YAML task suite. PipelineScore locks in a fixed 25-task suite. InferBench only measures tokens/sec, not output quality. whichllm and llmfit solve the hardware-matching half well — they map a device to published generic benchmark scores — but never touch the user's real task. None of them close the loop a bmdpat.com or dev.to/llm_ops reader actually wants closed.

## The Project

Personal Bench is a CLI and library that takes a small set of a user's own real task examples — a prompt plus a reference-quality answer, or a pass/fail rubric when there's no single right answer — and a detected local hardware profile, and turns them into a durable, versioned personal benchmark. It runs a slate of candidate small/local models (whatever's already installed via Ollama, plus suggested downloads that fit the detected VRAM/RAM budget) against those examples, scores each with a configurable method (exact match, rubric match, or an LLM-judge pass for open-ended output), and stores the result so the next time a new model drops, the question "does this actually help my task" is a 10-minute re-run instead of a fresh investigation.

The pieces are deliberately small: an example-set manager to add, edit, and version the user's own task samples; a hardware prober reusing the same local-introspection pattern (`nvidia-smi`/`rocm-smi`/platform APIs) that llmfit and similar tools already rely on; a model-candidate runner against installed or Ollama-discoverable models; a pluggable scorer; and a persisted score-history store that turns "did the new model help" into a tracked trend instead of a one-off printout that gets thrown away after a single comparison — which is exactly what happens today, repeatedly, according to the people describing this workflow in public.

## Tangible Impact

**Population**: Hobbyists and indie developers running local models for a specific recurring personal or small-team task (a dictation cleanup rewrite, a narrow classification rule, a personal coding-assistant workflow) who today either trust a published leaderboard that doesn't reflect their task or hardware, or hand-roll a throwaway benchmark script for a single comparison and then discard it. r/LocalLLaMA's 680k+ members are the proxy population for self-hosted model experimentation at this scale; the specific pain — leaderboard numbers don't predict my hardware/workload — is independently voiced by multiple blog authors and an Ask HN thread in the same 30-day window.

**Mechanism**: Replaces "guess from a published number, download, try it, discover it's wrong for my task, repeat" with a durable, reusable personal eval set built from the user's own examples, so picking between two local models for a specific task becomes a quick re-run against stored criteria rather than a fresh investigation every time a new model ships.

**Measure**: (1) time from "a new model is released" to "I know if it helps my specific task" — target under 15 minutes via a re-run, versus the multi-hour manual comparisons the cited blog posts describe; (2) correlation between a model's score on the personal benchmark and the user's own stated real-world satisfaction, to confirm the benchmark actually predicts usability, which is the exact thing published leaderboards were accused of failing to do; (3) how many distinct personal eval sets get created *and re-run more than once* — the signal that the tool is being kept, not discarded like the scripts it replaces.

## Why Now

Small/local models now ship often enough that "which one is actually best for my task" has become a recurring question rather than a one-time decision — which is exactly why multiple independent people built throwaway personal benchmarks in the last 30 days. Nobody has taken the obvious next step of making that personal benchmark durable and re-runnable instead of a script you write once and lose.

## Try It

A companion Claude Code skill, [`personal-hardware-aware-eval-set-generator`](../skills/personal-hardware-aware-eval-set-generator/), is already written: *"Designs a reusable personal eval-set structure (scoring method per example, sample-size check, missing edge cases, ready-to-use LLM-judge rubric) from a handful of a user's own real task examples, before they build or run any model-comparison tooling."* It's a one-time design review, not the runtime tool itself — use it when you have a pile of example prompts and "good" answers but no structured eval set yet, and want help turning them into something a ranking could actually be trusted against.

To use it: drop the `skills/personal-hardware-aware-eval-set-generator/` folder into `~/.claude/skills/` for Claude Code, or paste the contents of its `README.md` into any AI chat tool along with your own task examples.

## Risks & Open Questions

LLM-judge scoring for open-ended tasks inherits the same judge-calibration problems documented elsewhere in this pipeline's own eval-observability research — any version of this needs an honest confidence caveat, not a false sense of rigor. A sufficiently motivated user could just keep doing this by hand in a spreadsheet; the entire value proposition rests on re-run/versioning/drift-tracking being meaningfully less friction than that, which needs validating with real users early. And ten examples may simply be too few to reliably rank models for some task types — worth treating as an open question rather than assuming the sample sizes people actually have on hand are sufficient.

---

Surfaced from `research/2026-11-18-small-and-local-models.md`, pattern `P3`.
