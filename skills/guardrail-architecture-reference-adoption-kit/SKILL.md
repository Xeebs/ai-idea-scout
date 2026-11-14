---
name: guardrail-architecture-reference-adoption-kit
description: Maps a team's described LLM/agent guardrail setup against the four-point reference pattern (pre-inference, retrieval-time, post-inference, tool-call-time) and names concrete detector models or approaches for each gap. Use when someone is evaluating or redesigning their guardrail architecture and wants to know where they actually stand before building from scratch.
---

# Guardrail Architecture Reference Adoption Kit

## When to use this
The trigger moment is a team (or a solo builder) sitting down to evaluate, document, or redesign the safety/guardrail layer around an LLM or agent application — writing an architecture doc, opening a "how should we structure our guardrails" ticket, or responding to "we duct-taped checks in over time and aren't sure what we're missing." It applies whether the setup already exists in production or is only sketched in a design doc. It does NOT apply to picking a single detector model in isolation, writing a system prompt, or general content-moderation-policy questions — this skill is specifically about **where in the call path** guardrail checks sit, not what any one check's rules say.

## Inputs
**Data source**: Manual — the user pastes or describes their current (or planned) guardrail call sites: what runs before the model call, around retrieval (if they do RAG), after the model call, and around tool/function calls, to whatever extent each exists. This can be prose, a config file, a code snippet, or an architecture diagram described in text. No live connector reads the user's actual deployment — if the user has a repo, they paste the relevant routing/middleware code themselves.

If the user hands over something too vague to localize (e.g., "we use OpenAI's moderation endpoint" with no mention of where in the pipeline it's called), ask one targeted follow-up naming the four points before proceeding — do not guess.

## Procedure
1. **Elicit or parse the four call sites.** From the user's input, identify what (if anything) exists at each of these four insertion points in their pipeline, in this fixed order:
   - **Pre-inference** — checks run on the user's raw input before it reaches the model (e.g., prompt-injection detection, jailbreak classifiers, topic/scope filters).
   - **Retrieval-time** — checks run on retrieved context before it's injected into the prompt, if the app does RAG (e.g., scanning retrieved documents for injected instructions or sensitive content).
   - **Post-inference** — checks run on the model's output before it reaches the user (e.g., PII leak detection, harmful-content classifiers, system-prompt-disclosure detection).
   - **Tool-call-time** — checks run before and/or after a tool/function call the model triggers (e.g., argument validation, allow-listing, rate limits, scanning tool results before they re-enter context).
2. **Classify each of the four points** as one of:
   - `COVERED` — a named, dedicated check exists whose stated purpose matches the insertion point (e.g., a real classifier model or moderation API call).
   - `PARTIAL` — something exists but is informal, narrow, or not purpose-built (e.g., a plain regex instead of a classifier, a check that only covers one sub-case, a manual code-review step instead of an automated gate).
   - `MISSING` — nothing described touches this point at all.
   - If the user's RAG status is unclear, ask; if they confirm they don't do RAG, mark retrieval-time `N/A` instead of `MISSING` and exclude it from the gap count.
3. **For every `PARTIAL` or `MISSING` point**, name at least one concrete, currently-real option that would typically fill it — never generic advice like "add more guardrails." Draw from this known-real set (substitute an equivalent if the user names a constraint, e.g. no cloud dependency):
   - Pre-inference: Meta Llama Guard or Prompt Guard (self-hosted via vLLM, or via Hugging Face Inference), IBM Granite Guardian, Azure AI Content Safety Prompt Shield.
   - Retrieval-time: the same injection-detection models applied to retrieved chunks before they're concatenated into the prompt, or a dedicated retrieved-content scanner if the vendor offers one.
   - Post-inference: IBM Granite Guardian (output mode), Llama Guard (output mode), a PII-detection library/service (e.g., Presidio or a vendor DLP API), Azure Content Safety's output filters.
   - Tool-call-time: argument schema validation, an explicit allow-list of permitted tool/argument combinations, least-privilege scoped credentials per tool call, and inspection of tool results before they re-enter the model's context.
4. **Flag the single biggest asymmetry explicitly** — in production guardrail setups, the most common pattern is strong pre/post-inference coverage with little or nothing around tool calls, so call this out by name if it's what you see; otherwise state whichever asymmetry is actually present in this input.
5. **Frame the comparison honestly.** This four-point pattern is a convergent industry practice (visible across multiple vendor write-ups and the open-source FMS/TrustyAI Guardrails Orchestrator project) — not a certified standard from NIST or OWASP. Say so plainly; never imply the user is "non-compliant" with anything official.
6. **Do not design the fix.** Output the coverage map and named options; do not produce a full implementation plan, timeline, or deployment config unless the user explicitly asks for a follow-up design pass.

## Output format
A single markdown response with:
1. A **Coverage Map** — a 4-row table (Pre-inference, Retrieval-time, Post-inference, Tool-call-time), columns: Status (`COVERED`/`PARTIAL`/`MISSING`/`N/A`), What exists today (quoting back what the user described, or "nothing described"), Concrete option to close the gap (named models/approaches, blank if `COVERED`).
2. A **Biggest gap** — one or two sentences naming the single most consequential asymmetry and why (e.g., "you validate everything going in and out of the model but nothing at the tool-call boundary — this is the point where a successful prompt injection turns into an actual action").
3. A **Caveat line** — one sentence stating this maps against a converged-but-unofficial industry pattern, not a certified standard.

## Guardrails
- Never claim the user has a check they did not describe — if input is ambiguous, ask rather than assume `COVERED`.
- Never present this as a compliance audit, certification, or pass/fail grade against any official standard — no NIST/OWASP canonical guardrail architecture exists as of this writing.
- Never recommend a single vendor exclusively without naming at least one alternative per gap, so the user isn't funneled toward one company's stack.
- Never produce vague filler recommendations ("add more monitoring," "improve your guardrails") — every `PARTIAL`/`MISSING` row must name a specific, real model, library, or technique.
- Never fabricate evidence of adoption numbers, benchmarks, or "X% of teams do this" — if you don't have a verifiable source for a claim, state it as a described industry pattern, not a statistic.
- If the user asks for a full redeployment plan, config files, or infrastructure code, say that's a separate build step beyond this assessment, and scope what you'd need to do it properly rather than guessing at infrastructure you haven't seen.
