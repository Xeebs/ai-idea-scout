# Vision Modality Router Hook — Architecture Review & Hook Drafter

Paste this whole prompt into any AI chat tool (Claude, ChatGPT, etc.) along with your agent's details, and it will diagnose whether your vision-tool-calling is reliable and draft a fix.

## What this is for

If you're building a multimodal agent — most commonly an AI customer-support widget that accepts screenshot attachments, but also any LangChain/OpenAI-Assistants/custom agent that can call a vision tool — there's a common, mostly-invisible failure mode: the text-reasoning model decides *for itself* whether to call the vision tool, and a text-only model often can't reliably judge that it needs to look at an image it hasn't seen yet. The result is an agent that sometimes answers a ticket or question while completely ignoring an attached screenshot.

This prompt reviews your actual setup (not a generic checklist) and, if warranted, drafts a "pre-reasoning hook" — a routing step that inspects attachments *before* the main model reasons, instead of waiting for the model to decide to look.

## What you need to provide

**Data source: Connected (to your own files/config), not a third-party API.** This skill works entirely on material you already have — either paste it directly into the chat, or, if you're using a coding-capable tool like Claude Code, let it read the files directly from your repo. Nothing needs to be built or connected for this to work; it reads your own agent's configuration and conversation traces, not a live third-party service.

Hand over:

1. **Your system prompt** — or at least the part that mentions the vision tool or how to handle attachments.
2. **Your vision tool's definition** — the function name, description, and parameters schema exactly as you registered it with the model.
3. **3–5 real example traces** — for each one: what the user sent, whether an image was attached, whether and when the vision tool got called (before the answer, after/alongside it, or never), and what the agent's final response said. Use real traces, not hypotheticals — the diagnosis is only as good as the evidence.
4. **Your integration target** — LangChain, OpenAI Assistants API, a webhook in front of Zendesk/Intercom, or a custom agent loop. If you don't say, it'll ask.

If you only have 0–1 traces with an image attached, gather a couple more first — a verdict without evidence is just a guess.

## What it does with that

1. **Classifies your current setup** — is the vision tool left entirely to the model's judgment, or does your prompt already say something like "always look at any attached image first"?
2. **Scores each trace** as vision-called-first, vision-called-late, or vision-not-called, and computes a miss rate across your image-attached traces.
3. **Checks for a plumbing bug first** — before blaming the architecture, it checks whether any missed trace actually shows the image arriving broken (a placeholder, an expired URL string, empty content) rather than a genuine decision failure. Broken attachment delivery gets flagged and fixed before anything else.
4. **Renders a verdict**: hook warranted, not needed yet, or fix the plumbing first.
5. **If warranted, drafts a routing policy** — always-run every attachment through vision, a cheap confidence-threshold pre-check, or ask-the-user — recommending whichever fits your attachment volume and cost sensitivity, with confidence-threshold as the default unless your traces show attachments are rare.
6. **Drafts an adapter skeleton for your specific stack** — LangChain middleware, an OpenAI Assistants thread-run wrapper, a Zendesk/Intercom webhook pre-processor, or a custom-loop insertion point. This is a skeleton to adapt into your own code, not a finished package to `pip install`.
7. **Gives you a validation plan** — re-run your traces plus some new "decoy" attachments (irrelevant images) through the drafted hook before shipping, checking both that relevant images get inspected and that irrelevant ones don't add needless cost.
8. **Sets honest expectations** — pre-invocation vision gating mainly prevents the specific failure of ignoring a relevant image; published research on this exact pattern (ToolGate, arXiv 2606.03054) found it only changed the final answer in a minority of the cases where it fired. This isn't a general accuracy multiplier — treat it as a targeted fix for a specific miss, not a universal upgrade.

## Output you'll get

A report with five sections in this order:

1. **Diagnosis** — architecture classification, trace-by-trace scoring, miss rate.
2. **Verdict** — hook warranted / not yet / fix the plumbing first, with the one-line reason.
3. **Routing Policy** — the recommended policy and why.
4. **Adapter Draft** — code/pseudocode for your specific integration target.
5. **Validation Plan** — the concrete test to run before shipping.

## Rules this follows

- It will not render a verdict from zero or one trace — it will ask you for more real examples first.
- It will not recommend "always run vision on everything" without naming the latency/cost tradeoff that introduces.
- It will not assert specific Zendesk/Intercom API rate limits or fields as fact — it'll flag that you should check current platform docs, since these vary by plan and change over time.
- It will not hand you a "finished middleware library" — only an adapter skeleton sized to drop into your own codebase.
- It will always check for broken attachment delivery (placeholder images, expired URLs) before concluding the problem is architectural.
- It will not oversell the hook's impact — it prevents a specific class of miss, it is not a general quality upgrade.

## Example prompt to paste

> Here's my support bot's system prompt: [paste]. Here's my vision tool definition: [paste]. Here are 4 traces where a user attached a screenshot: [paste traces]. I'm using LangChain. Review whether my vision-tool-calling is reliable, and if not, draft a pre-reasoning hook for me.
