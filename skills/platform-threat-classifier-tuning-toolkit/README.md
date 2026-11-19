# Threat Tune Feasibility Diagnostic

A self-contained prompt template for deciding whether it's worth building a custom-tuned abuse/content classifier for your platform — before you spend engineering time on the actual training pipeline. Paste the prompt below into any AI chat tool (Claude, ChatGPT, etc.) along with your data, and you'll get a structured go/no-go read in one pass.

## When to use this

Use this when your trust-and-safety or platform-engineering team suspects your current content-moderation guardrail (a generic foundation-model guardrail — NeMo Guardrails, Guardrails AI, LLM Guard, or a vendor API) is misfiring on language specific to your own community, and you have a backlog of past human-moderator decisions you could learn from — but you don't yet know if that backlog is good enough to justify building a custom active-learning fine-tuning pipeline. This tool answers "is this worth doing" in one pass, before you commit to the real build.

This is a feasibility diagnostic, not the classifier itself. It will not train a model or give you deployment-ready code — it tells you whether your own data supports building one, and what to fix first if it doesn't.

## What you need to provide

**Data source: Manual.** You paste or upload the data directly into the chat — this tool does not connect to any moderation system or database on its own (every platform's mod-queue schema is different enough that no universal connector exists). You need:

1. **A sample export of 100-1,000+ recent human-moderator decisions**, as CSV or JSON, with one row per decision containing: the content/text that was reviewed, the action taken (e.g., removed, warned, allowed, escalated), a reviewer identifier if you have one, and a timestamp. **Anonymize usernames and any personally identifying details before pasting — moderation logs routinely contain real user data.**
2. **A written description of your current guardrail's known false positives and false negatives**, with at least 3-5 concrete examples (not just "it's not great" — actual content snippets or categories of content it got wrong).
3. **Optional but helpful**: what kind of platform this is (forum, marketplace, dating app, gaming community, etc.) and the name of your current guardrail/vendor.

If you can't provide at least 3 concrete failure examples in item 2, stop and gather those first — the whole diagnostic depends on having real examples to analyze, not a vague complaint.

## The prompt to paste

Copy everything below, then attach or paste your moderation-log sample and guardrail-failure description where indicated.

---

> You are running a feasibility diagnostic for whether I should build a custom-tuned abuse/content classifier from my own moderation history, instead of continuing to rely on my generic guardrail. Here is my data:
>
> **Moderation log sample:** [paste CSV/JSON export of 100+ anonymized moderation decisions: content, action taken, reviewer id if available, timestamp]
>
> **Current guardrail failure examples:** [list at least 3-5 concrete examples of content the current guardrail got wrong — flagged something that shouldn't have been, or missed something that should have been — and briefly what action a human moderator actually took on similar content]
>
> **Platform type / current guardrail (optional):** [e.g., "gaming community forum, using a generic vendor API" or "dating app, using NeMo Guardrails"]
>
> Please do the following, in order, and give me a structured report:
>
> 1. **Sample Summary** — count the total rows, the balance between action categories, the approximate time range covered, and flag explicitly if the total sample is under ~100 rows or under ~20 rows in the minority (flagged) category — that's a sample-size blocker, not something to gloss over.
> 2. **Label consistency check** — look for content that's similar or repeats (same phrase, slang, or scam pattern) but received inconsistent actions across different decisions. Call out a high rate of this explicitly as a ceiling on how good any classifier trained on this data can get — it's a real constraint, not a reason to abandon the idea.
> 3. **Guardrail Failure-Mode Breakdown** — sort each failure example I gave you into one of three buckets, with a one-line reason for each:
>    - **Platform-vocabulary-driven** (slang, in-group terms, or domain-specific phrasing the generic guardrail doesn't recognize) — the best target for tuning.
>    - **Context-dependent ambiguity** (sarcasm, reclaimed language, genuinely borderline cases) — tuning helps less here.
>    - **Rare/edge-case** (one-off incidents, not a recurring pattern) — too sparse to target yet.
> 4. **Opportunity Estimate** — rate HIGH / MEDIUM / LOW based on whether most of my failure examples are platform-vocabulary-driven AND my sample actually contains enough of that category to learn from. State your reasoning in plain language. Do not invent a precision, recall, or F1 number — no model has actually been trained or evaluated yet, so only give a qualitative band with reasoning.
> 5. **Verdict** — GO, CONDITIONAL-GO (and name exactly what gap to close first, e.g. "collect 50 more examples of X"), or NO-GO (and name exactly why).
> 6. **Recommended Next Step** — one concrete action I should take next, regardless of verdict.
>
> Before anything else, remind me that moderation-log content often contains real user data and should be fully de-identified before being shared with any AI tool, if I haven't already confirmed that.

---

## What you'll get back

A structured report in five parts: a summary of your sample's size/balance/consistency, a breakdown of your described guardrail failures into three categories, a qualitative HIGH/MEDIUM/LOW opportunity estimate with reasoning (never a made-up accuracy number), a GO/CONDITIONAL-GO/NO-GO verdict, and one concrete next step.

## What this does not do

This diagnostic does not train, tune, or deploy a classifier. It does not connect to your moderation system directly. It will not give you a real F1 score or confusion matrix — that only comes from actually building and evaluating a tuned model, which is a separate, larger project this diagnostic exists to help you decide whether to start. If the verdict is GO, the next step is building (or commissioning) the actual active-learning labeling and fine-tuning pipeline — a distinct effort from this one-shot read.
