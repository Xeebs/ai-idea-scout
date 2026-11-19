---
name: vision-modality-router-hook
description: Audits whether a text-reasoning agent's vision-tool-calling is LLM-initiated (and therefore prone to missing attached images), then drafts a pre-reasoning routing hook and framework-specific adapter config to fix it. Use when a multimodal agent/support bot seems to answer without actually looking at an attached screenshot or image.
---

# Vision Modality Router Hook — Architecture Review & Hook Drafter

## When to use this
Someone is building or operating a multimodal agent (commonly an AI customer-support widget, but also any LangChain/OpenAI-Assistants/custom agent loop that accepts image attachments) and either: (a) has noticed the agent sometimes answers a ticket or question while ignoring an attached screenshot, image, or photo; or (b) wants to proactively check, before shipping, whether their vision-tool-calling setup relies on the text model *deciding* to look at an image rather than being guaranteed to look. The trigger phrase is usually some version of "my agent didn't look at the screenshot" or "how do I make sure the vision tool always runs when there's an attachment."

## Inputs
**Data source**: Connected — the skill reviews the user's own agent configuration and conversation traces directly: in a coding-capable environment (e.g. Claude Code) it reads the agent's source via Read/Grep; in a plain chat tool with no file access, the same material is pasted in. There is no third-party API call involved in running the skill itself. This is distinct from the parent project's own runtime Data Sources (the always-on middleware reads live Zendesk/Intercom conversation APIs or the host framework's message store at runtime) — this skill is a one-time design-and-review aid that operates on the user's design artifacts, not on live ticket data.

The user needs to hand over:
1. **The system prompt** (or the tool-calling-relevant excerpt) given to the reasoning model.
2. **The vision tool's definition** as registered with the model — function name, description, and parameters schema.
3. **3–5 example traces**, each showing: the user's message, whether an image was attached, whether/when the vision tool was called (before the final answer, not at all, or mid-reasoning), and the agent's final response text.
4. **The integration target** — LangChain, OpenAI Assistants API (threads/runs), a raw webhook pre-processor in front of Zendesk/Intercom, or a custom agent loop — so the drafted adapter matches their actual stack. If unstated, ask.

If fewer than 2 traces with an attached image are provided, ask for more before diagnosing — a verdict without trace evidence is a guess, not a review.

## Procedure
1. **Classify the current architecture.** Read the tool definition and system prompt. Determine: is the vision tool's invocation left entirely to the model's own judgment (the default in virtually every tutorial stack), or does the prompt already contain an explicit instruction like "always inspect any attached image before responding"? Note which.
2. **Score the traces.** For each trace with an attached image, mark one of: VISION-CALLED-FIRST (tool ran before the final answer was composed), VISION-CALLED-LATE (ran but answer was already drafted/contradicts it), or VISION-NOT-CALLED. Also note whether the image was plausibly relevant to the user's question or a decoy (e.g. an attachment that has nothing to do with what's being asked) — a NOT-CALLED trace on a decoy image is not a miss, since skipping an irrelevant image is correct behavior; call this out explicitly rather than folding it silently into the headline number. Compute the miss rate = (NOT-CALLED + LATE among plausibly-relevant image traces) / (total plausibly-relevant image-attached traces), and report the decoy traces separately.
3. **Check for a non-architectural cause first.** Before recommending a hook, check whether any NOT-CALLED/LATE trace shows the image arriving as a placeholder, an expired URL string, or empty content instead of actual image data — if so, flag this as a tool-execution/data-plumbing bug, not a decision-architecture problem, and recommend fixing attachment delivery before building a routing hook on top of broken input.
4. **Render a verdict:**
   - Any trace flagged in step 3 as a plumbing/delivery bug (placeholder, expired URL, empty content reaching the tool) → verdict is **fix-the-plumbing-first**, regardless of miss rate — do not draft a routing hook on top of broken attachment delivery. Name the specific broken pattern found and recommend fixing it (resolve URLs server-side, fetch bytes directly, etc.) before anything else. If the vision tool was already being called correctly in every trace (i.e. the architecture is fine and only the data reaching the tool is broken), say so explicitly and skip steps 5–6.
   - Otherwise, miss rate 0% across all provided traces AND an explicit always-inspect instruction already exists → hook not warranted yet; recommend only tightening the instruction wording and expanding the trace sample before concluding it's solid.
   - Otherwise, miss rate > 0%, or no explicit instruction exists at all (even if traces happened to pass) → hook warranted; proceed to step 5.
5. **Draft the routing policy** in plain language, choosing among: always-run (every attachment triggers vision inspection — simplest, costs one extra call per attachment), confidence-threshold (a cheap relevance check first: attachment type is image AND user message or recent context plausibly references visual content → then run vision), or ask-the-user (when ambiguous and cost-sensitive, surface a quick "want me to look at the image?" instead of auto-running). Recommend confidence-threshold as the default unless the user's traces show attachments are rare enough that always-run's extra cost is negligible.
6. **Draft the adapter skeleton** matching the stated integration target:
   - *LangChain*: a pre-processing function/Runnable that inspects the input messages for image content before the main chain invokes the reasoning LLM, injecting the vision tool's output as a prior AI/system message.
   - *OpenAI Assistants API*: a wrapper around thread-run creation that scans the thread's messages for `image_file`/`image_url` content blocks before calling `runs.create`, and if found and unprocessed, calls the vision tool and adds its result as a message before the run starts.
   - *Webhook (Zendesk/Intercom)*: a pre-processor in the ticket-received webhook handler that checks the payload for attachments via the platform's attachment field/API, runs vision inspection synchronously (or queues it) before the ticket is handed to the reasoning agent.
   - *Custom loop*: a function inserted immediately after message ingestion and before the first reasoning call, operating on whatever context object the loop already uses.
   Each skeleton is pseudocode/skeleton-level — enough to adapt into the user's actual codebase, not a finished library.
7. **Attach a validation plan**: recommend re-running the same trace set (plus at least 5 new ones, including some "decoy" attachments that are irrelevant to the question) through the drafted hook before shipping, and checking both that relevant images get inspected and that irrelevant ones don't add needless latency/cost.
8. **Set honest expectations.** Note that published research on pre-invocation perceptual gating (e.g. ToolGate, arXiv 2606.03054) found such gating actually changed the final answer in only a minority of cases where it fired — the hook mainly prevents a specific failure mode (ignoring a relevant image), it is not a general accuracy multiplier. Don't oversell the lift.

## Output format
A single structured report with five sections, in this order:
1. **Diagnosis** — current architecture classification, the trace-by-trace scoring table, and the computed miss rate.
2. **Verdict** — hook warranted / not yet / fix-the-plumbing-first, with the one-line reason.
3. **Routing Policy** — the recommended policy (always-run / confidence-threshold / ask-the-user) and why, given the traces provided.
4. **Adapter Draft** — a code/pseudocode block for the stated integration target.
5. **Validation Plan** — the concrete before-shipping test the user should run.

## Guardrails
- Never render a verdict from zero or one trace — ask for more real examples first.
- Never recommend always-run as a default without naming the latency/cost tradeoff it introduces on every attachment, relevant or not.
- Never claim a specific Zendesk/Intercom rate limit or API field without flagging that current platform docs should be checked — these change and vary by plan tier.
- Never hand back a "finished middleware package" — this skill drafts an adapter skeleton sized for the user's own codebase, not a pip-installable library that doesn't exist.
- Never skip the plumbing-bug check (step 3) — a routing hook built on top of broken attachment delivery (placeholder/expired-URL images) will not fix the actual symptom.
- Never overstate the hook's expected accuracy lift — cite that gating primarily prevents ignored-image misses, not a general quality improvement, per the cited research's own modest findings.
