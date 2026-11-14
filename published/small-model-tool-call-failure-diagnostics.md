# ToolCause: A Cross-Runtime Root-Cause Classifier for Small-Model Tool-Calling Failures

Your tool-calling accuracy score just dropped, and you have no idea why — was it the model, the chat template, or the parser you wrote? That single number flattens three completely different bugs into one shrug, and right now the only way to tell them apart is to read raw model output by hand and hope you recognize the pattern.

## The Gap

Three independent writeups surfaced in the same 30-day window, all circling the same frustration: an r/LocalLLM post arguing that a bare tool-calling accuracy number hides which of several distinct failure modes actually occurred, a dev.to piece titled "Why Small LLMs Fail at Tool Calling," and a personal blog ("in the trenches with small llms... we need a prompt hero") describing the same manual-debugging slog. The r/LocalLLM thread traced a concrete, embarrassing example: Qwen2.5's own chat template renders its tool-call example with doubled braces, and small models dutifully copy that formatting mistake literally — producing a "failure" that looks like the model is bad at tool calling when it's actually just following a buggy template correctly.

Someone has already tried to fix this, and it's instructive that they stalled. `Code-byte404/toolhound` classifies exactly this — template bug, parser gap, model format, model decision — but it's MLX/Apple-Silicon-only, sitting at 7 stars and 1 fork, last pushed four months ago. `SoHarshh/ToolFailBench` is a real academic benchmark (ICML 2026 workshop, arXiv 2607.04686) with a different taxonomy, also gone quiet since July. Both prove the classification idea is buildable. Neither is something a developer running Ollama or vLLM today can actually install and use across their stack.

## The Project

ToolCause is a lightweight proxy that sits in front of Ollama, llama.cpp's server, and vLLM's OpenAI-compatible endpoint, watching every tool-calling request and response pass through. When one fails, it doesn't report a number — it names the cause: a chat-template rendering bug, a parser/extraction gap, malformed-but-recoverable model output, or a genuine model reasoning failure. Each classification comes with the receipts — the raw string, the specific template fragment, the exact point the parser choked — plus a suggested fix: patch the template, widen the parser's tolerance, or accept that this is a capability ceiling and consider a bigger model.

Four pieces do the work: thin per-runtime capture adapters (not a rewrite of any server), a rule-based-plus-small-classifier triage layer trained on the four-bucket taxonomy, a fix-suggestion library keyed to known template bugs across the popular tool-calling model families (Qwen, Llama, Mistral, Hermes), and a CLI/dashboard that turns a run's worth of failures into a bucketed report instead of one flat accuracy percentage.

## Tangible Impact

**Population**: developers building agentic/tool-calling applications on small, open-weight local models (sub-8B, the class most prone to template/parser brittleness) across the three dominant self-hosted serving stacks — Ollama, llama.cpp, and vLLM. r/LocalLLaMA alone has 480k+ members, and Ollama reports hundreds of thousands of weekly active installs; a meaningful fraction of that community is building tool-using agents on exactly this class of model, per the digest's own corroborating threads.

**Mechanism**: today, a developer who sees a tool call fail has to manually re-read the raw model output, the Jinja chat template, and the parser code to figure out which of three completely different fixes applies — a process each cited writeup turned into its own multi-paragraph blog post. ToolCause automates that triage into one classified report per failure, so the developer acts on the actual cause (patch a template, loosen a regex, or switch models) instead of guessing or assuming "the model is just bad at this."

**Measure**: (1) median time from "tool call failed" to "root cause identified" — target: minutes, not the hours implied by the existing one-off debugging posts; (2) percentage of failures in a sampled corpus that are template/parser bugs vs. genuine model limitations, made visible and trackable per model/template pair instead of invisible; (3) adoption proxy — GitHub stars/installs crossing toolhound's stalled 7-star baseline within 3 months as a sign the gap was real.

## Try It

A companion Claude Code skill, [`skills/small-model-tool-call-failure-diagnostics/`](../skills/small-model-tool-call-failure-diagnostics/), is already written: *"Diagnoses a single failed tool call from a small/local LLM (Ollama, llama.cpp, vLLM) by classifying the root cause into one of four buckets — chat-template rendering bug, parser/extraction gap, malformed-but-recoverable output, or genuine model reasoning failure — with cited evidence and a concrete fix. Use when a user pastes a raw failed tool-call trace and asks why it broke, instead of guessing 'the model is just bad at this.'"*

It's the zero-install counterpart to the always-on proxy above — a one-shot triage for a single failure, not a running wrapper watching your whole stack. Paste the raw failed model completion, the chat template that was applied, and the tool schema that was sent, and it comes back with a classified diagnosis and a specific fix. To use it: drop the `skills/small-model-tool-call-failure-diagnostics/` folder into `~/.claude/skills/` if you're on Claude Code, or paste its `README.md` into any AI chat tool as a standalone prompt — it stands on its own without Claude Code installed.

## Risks & Open Questions

Worth saying plainly: `toolhound` already exists, and the strongest version of this project might honestly be "revive and generalize toolhound" rather than a clean-room build — reaching out to its original author before starting is worth doing. Chat-template bugs also get patched upstream fast once noticed, which makes staying current an ongoing maintenance cost, not a one-time build. The four-bucket taxonomy may need to grow (multi-tool-call ordering failures are an obvious gap) as more real traces get classified, risking drift in what "the same bucket" even means over time. And the hardest bucket — telling a genuine model reasoning failure apart from a subtle parser edge case — is exactly the one rules alone are least likely to get right, which is why this leans on a trained classifier rather than pure heuristics for that call.

Surfaced from `research/2026-11-13-small-and-local-models.md`, pattern `P2`.
