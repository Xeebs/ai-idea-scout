# Guardrail Architecture Reference Adoption Kit

A paste-in prompt template that takes whatever you can describe about your LLM or agent app's current safety/guardrail checks and maps them against the four-point reference pattern that's converged across the industry in 2026: **pre-inference, retrieval-time, post-inference, and tool-call-time**. It tells you which of the four points you actually cover, which are informal/partial, which are missing entirely, and names concrete, real models or techniques to close each gap — instead of you re-deriving the architecture from scratch or guessing whether your current setup is complete.

## When to use this

Use this before you invest time redesigning or documenting your guardrail layer — when you're writing an architecture doc, opening a "how should we structure our guardrails" ticket, doing a pre-launch safety review, or you simply inherited a guardrail setup that was "duct-taped together over time" and want to know what's actually there. It is not for picking the rules inside a single content-moderation policy, and it is not a certified compliance audit — there's no official NIST/OWASP standard for this yet, just a pattern that's converged independently across multiple vendors and the open-source FMS/TrustyAI Guardrails Orchestrator project.

## What to hand over

**Data source: Manual.** Paste or describe your current (or planned) guardrail setup, covering as much of the following as you can:
- What runs on the user's input *before* it reaches the model (if anything) — injection detection, jailbreak classifiers, topic filters.
- What runs on retrieved content *before* it's added to the prompt, if you do RAG — scanning for injected instructions in retrieved documents.
- What runs on the model's *output before it reaches the user* — PII leak checks, harmful-content classifiers, system-prompt-leak detection.
- What runs *around tool/function calls* the model triggers — argument validation, allow-lists, rate limits, scanning tool results before they go back into context.

A code snippet, a config file, a Slack message describing your setup, or a rough bullet list all work. If you only describe one or two of the four points, that's fine — the assessment will just mark the rest `MISSING` and tell you what to add.

## What you'll get back

1. **A Coverage Map** — a 4-row table, one row per insertion point (pre-inference, retrieval-time, post-inference, tool-call-time), each marked `COVERED`, `PARTIAL`, `MISSING`, or `N/A` (for retrieval-time if you don't do RAG), with what you currently have at that point and — for every gap — a named, real option to fill it (e.g., Meta Llama Guard, Prompt Guard, IBM Granite Guardian, Azure AI Content Safety Prompt Shield, argument-schema validation for tool calls). No generic "add more guardrails" advice — every gap gets a specific, real answer.
2. **The biggest gap, named explicitly** — one or two sentences on the single most consequential hole in your coverage (the most common pattern across real setups is strong input/output checking with nothing around tool calls — if that's what shows up in yours, it'll say so).
3. **An honesty caveat** — one line making clear this compares you against a converged-but-unofficial industry pattern, not a certified standard, so you don't walk away thinking you passed or failed an audit that doesn't exist.

## How to use this prompt

Paste the following into any AI chat tool, then paste your guardrail setup description right after it:

> You are assessing my LLM/agent application's guardrail architecture against the four-point reference pattern that's converged across the industry: pre-inference (checks on raw user input before the model), retrieval-time (checks on retrieved context before it's added to the prompt, if applicable), post-inference (checks on the model's output before the user sees it), and tool-call-time (checks before/after any tool or function call the model triggers).
>
> Here is my current setup: [paste your description, config, or code here]
>
> For each of the four points: classify it as COVERED (a dedicated, purpose-built check exists), PARTIAL (something exists but is informal or narrow — e.g. a regex instead of a classifier), MISSING (nothing touches this point), or N/A (only for retrieval-time, if I don't do RAG — ask me first if it's unclear whether I do). For every PARTIAL or MISSING point, name at least one specific, real model or technique that would typically fill it (e.g., Llama Guard, Prompt Guard, IBM Granite Guardian, Azure Prompt Shield for input/output checks; argument-schema validation, allow-lists, or least-privilege scoped credentials for tool-call checks) — never generic advice. Then call out the single biggest asymmetry in my coverage by name, and explicitly note that this compares against a converged industry pattern, not a certified NIST/OWASP standard, since no such standard exists yet. Do not produce a full redesign, deployment plan, or infrastructure code unless I explicitly ask for one as a follow-up.

## A worked example (abbreviated)

If you say: *"We run OpenAI's moderation endpoint on user messages before sending to GPT-4, and we scrub PII from the model's response with a regex before returning it. We don't do RAG. The model can call three internal APIs directly with no validation on the arguments."*

You'd get back something like:

| Point | Status | What exists today | Option to close the gap |
|---|---|---|---|
| Pre-inference | COVERED | OpenAI moderation endpoint on raw input | — |
| Retrieval-time | N/A | No RAG | — |
| Post-inference | PARTIAL | Regex-based PII scrub, not a dedicated classifier | IBM Granite Guardian (output mode) or a proper PII-detection library (e.g., Presidio) in place of the regex |
| Tool-call-time | MISSING | No validation on the three internal API calls | Argument-schema validation plus an explicit allow-list per API, or least-privilege scoped credentials per call |

**Biggest gap**: your model can call three internal APIs with zero argument validation — this is the point where a successful prompt injection stops being a content problem and becomes an actual unauthorized action. This is the most common and highest-stakes gap in real-world setups.

**Caveat**: this compares you against a converged-but-unofficial industry pattern (visible across multiple vendor write-ups and the open-source FMS/TrustyAI Guardrails Orchestrator project), not a certified NIST/OWASP standard — none exists yet.

## Limits

This is a one-time, point-in-time assessment based entirely on what you describe — it does not read your actual running infrastructure, so an inaccurate or incomplete description produces an inaccurate map. It also does not replace a security review: a `COVERED` rating means a dedicated check exists at that point, not that the check's own rules or thresholds are well-tuned.
