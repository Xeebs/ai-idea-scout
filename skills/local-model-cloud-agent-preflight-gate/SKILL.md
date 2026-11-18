---
name: local-model-cloud-agent-preflight-gate
description: Drafts a tailored pre-send/post-receive checklist (plus ready-to-paste local-model prompts) for gating a cloud coding-agent CLI's calls with a local small model, before anyone writes the middleware. Use when a developer wants the actual gate rules for their workflow, not the interceptor code.
---

# Local-Model Preflight Gate Designer

## When to use this
Use this when a developer or small team already runs (or is about to build) a local small model as a quality gate in front of a cloud coding-agent CLI — Codex CLI, Claude Code, Cursor's agent mode, or a raw OpenAI/Anthropic API call — and needs the actual **rule content**: what the gate should check for before a request is sent (to avoid wasting a paid call) and what it should check for after a response comes back (to avoid trusting an obviously-wrong answer). This is a one-time design task. It does not write the interceptor/middleware code that hooks the CLI's call lifecycle — that is a separate infrastructure build. Reach for this skill the moment someone says something like "I want a local model to catch bad calls before/after they hit [Codex/Claude Code/Cursor]" or "my local model gate keeps letting bad stuff through, help me fix the checklist."

## Inputs
**Data source**: Connected — ideally reads the target CLI's own local session/call logs (Codex CLI session JSONL, Claude Code transcript files, Cursor's local history, or any exported call log) to mine real failed/wasted calls instead of guessing; this is local filesystem log access, already mature today, not a third-party API. If no log file is available or the user doesn't want to share one, fall back to Manual — the user directly describes 3-5 example calls (what was sent, what came back, why it was wasteful or wrong) in chat instead of a log file. Either path is acceptable; state in the output which path was used.

Beyond the log/examples, the user must also hand over:
- Which CLI/tool and language/stack (e.g., "Codex CLI, TypeScript monorepo" or "Claude Code, Python/Django").
- In their own words, what kinds of outgoing requests tend to fail or waste a call for them (missing context, vague instructions, repeated questions, etc.).
- In their own words, what a "bad response" looks like for their codebase (references a symbol that doesn't exist, skips a required tool call, wrong output format, etc.).

## Procedure
1. **Collect the workflow profile.** If the user hasn't already supplied the four inputs above, ask for them directly — do not proceed on vibes. If they offer a log file, read it; if not, treat their described examples as the dataset.
2. **Mine or elicit concrete failure examples.** From the log (or the user's description), pull out at minimum 2 real/realistic examples of a wasteful outgoing request and 2 real/realistic examples of a bad incoming response, specific to their stack. Never invent an example that isn't grounded in what the user gave you — if they gave too little to find a second example of a category, say so instead of fabricating one.
3. **Build the Pre-Send Checklist.** Group checks under three fixed categories: (a) Context completeness — is every file/symbol/path the request depends on actually included or referenced; (b) Instruction specificity — does the request state a concrete, checkable goal rather than an open-ended one; (c) Duplicate/redundant detection — does this request re-ask something already answered this session. For each category, write one concrete, binary-ish check (something a small local model can actually evaluate, not a vague "is this good") and assign a decision: HOLD (block, ask user to fix), FLAG (send anyway but warn), or PASS.
4. **Build the Post-Receive Checklist.** Group checks under: (a) Structural validity — does the response parse/compile for the target language, are all referenced symbols/files real; (b) Required-action compliance — if the request implied a specific tool call or file edit, did the response actually do it; (c) Format compliance — does the response match whatever output contract the workflow expects (diff format, specific file structure, etc.). Same HOLD/FLAG/PASS decision per check.
5. **Attach a worked example to every check** — one case from step 2 that would PASS and one that would HOLD/FLAG, phrased in the user's own stack and terms.
6. **Write two ready-to-paste local-model prompt templates** — one for the pre-send scorer, one for the post-receive scorer — that take the request (or response) plus the checklist as input and return a structured verdict (decision + which check failed + why). These are prompts for whatever local model the user already runs (Ollama/llama.cpp), not new infrastructure.
7. **Flag subjectivity risk.** For any check from steps 3-4 that depends on judgment calls rather than a structural/mechanical test (e.g., "is this instruction specific enough" vs. "does this symbol exist in the codebase"), explicitly mark it LOW-CONFIDENCE and recommend it carry less weight than the structural checks, or be dropped until the user has calibration data showing it doesn't produce false holds.
8. **Close with a calibration suggestion**: if the user has or can get a labeled set of past calls (known-good vs. known-wasted/bad), suggest running the two prompt templates against that set before trusting the HOLD decisions live, and name roughly how many examples (20-50) would be a reasonable first calibration batch.

## Output format
A single Markdown document with these sections, in order:
1. **Workflow Profile** — CLI/tool, stack, and whether log-mining or manual description was the data source.
2. **Pre-Send Checklist** — a table: `Check | Category | Decision if triggered | Example that PASSES | Example that HOLDS/FLAGS`.
3. **Post-Receive Checklist** — same table structure, for response-side checks.
4. **Local-Model Prompt Templates** — two fenced code blocks, one labeled "Pre-send scorer prompt" and one "Post-receive scorer prompt", each a complete prompt ready to paste into the user's local-model call.
5. **Calibration Notes** — the LOW-CONFIDENCE checks from step 7, and the suggested calibration batch from step 8.
6. **Explicitly out of scope** — one line stating this document is the rule set only; wiring it into the CLI's call lifecycle (the interceptor/middleware) is a separate build.

## Guardrails
- Never write or suggest specific interceptor/middleware code for hooking a CLI's call lifecycle — that's the project-infrastructure half of this idea, not this skill's job. If asked for the hook code, say so explicitly and stop at the rule set.
- Never invent failure examples, call counts, or percentages not grounded in what the user supplied (log contents or their own description) — fabricated examples make the checklist look validated when it isn't.
- Never present a subjective/judgment-based check with the same confidence as a structural one; always separate them per step 7.
- Never claim this checklist will catch a specific percentage of bad calls — no evaluation has been run yet; only the calibration step in the output can produce that number, and only on the user's own data.
- If the user's inputs are too thin to build a real checklist (e.g., no stack named, no failure description, no log), do not fabricate one — ask for the missing specific input instead of shipping a generic placeholder checklist.
