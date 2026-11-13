# Technical-Content Guardrail False-Positive Reducer

A prompt template for diagnosing why your AI safety guardrail is blocking legitimate technical/developer queries — and for drafting the starter labeled data you'd need to fix it. Paste this into any AI chat tool (ChatGPT, Claude, Gemini, etc.) along with your sample of flagged queries.

## When to use this

You're running an AI coding assistant, DevOps/SRE copilot, or security-research tool behind a safety guardrail (NeMo Guardrails, Guardrails AI, LLM Guard, a vendor gateway, or a foundation model's built-in moderation). Legitimate requests are getting blocked because the vocabulary overlaps with violence, hacking, or weapons categories — things like "write a script to kill this process," "craft a payload to test our rate limiter," or "explain how this CVE exploit works for an internal writeup." You have, or can quickly export, a sample of these false-positive queries and want to know *why* they're being blocked and what to actually do about it, before investing in a custom classifier.

This gives you a diagnosis and a starter dataset — not a trained model. It's the step that comes before building a fix.

## What you need to provide

**Data source: Manual.** You paste in a sample of queries your current guardrail has incorrectly blocked. For each one, provide:

1. **The query text** — verbatim, exactly what the user/developer typed.
2. **The guardrail's verdict** — what category or label it assigned (e.g., "Violence," "Hacking," "Weapons," or just "Blocked" if your gateway doesn't report a category). Say explicitly if you don't have this.
3. **A ground-truth label, if you have one** — was this actually benign or actually malicious, per a human who understands the technical context? If you haven't labeled it yet, say so — don't guess at this stage.
4. **Optional context** — what kind of product this is (DevOps copilot, pentest-support tool, general coding assistant) sharpens the diagnosis.

You need at least 10 queries for the diagnosis to be useful. Fewer than that, and the tool should tell you to come back with more rather than force a verdict on thin data.

(There's no live connector for this today — most guardrail gateways log every block decision in an audit trail or webhook, but pulling that automatically isn't built yet. Manual export is the honest way to use this right now.)

## What it does

Paste the sample and this prompt:

> I'm going to give you a sample of queries that my AI guardrail incorrectly flagged as unsafe. For each query I'll give you the text, the guardrail's verdict/category (or say if I don't have one), and whether I know it to be benign or malicious (or say if I haven't labeled it). I want you to:
>
> 1. For each query, identify the specific trigger vocabulary likely responsible for the flag (words like "kill," "exploit," "payload," "inject," "bypass," "attack," "crash," "backdoor," "exfiltrate").
> 2. Infer which guardrail category that vocabulary likely maps to (Violence, Hacking, Weapons, etc.), and flag if that doesn't match the verdict I gave you.
> 3. Classify each query's real intent as benign-technical, genuinely-malicious, or ambiguous-needs-human-review, using the full context of the query — not just the trigger word. If I gave you a ground-truth label, use it, but if your own read disagrees, say so explicitly rather than silently going with mine or silently overriding it.
> 4. For every benign-technical query, draft a matched "eval pair": the real benign text, next to a structurally similar but genuinely malicious counterpart using the same trigger vocabulary. Keep the malicious side abstract and intent-only — describe the harmful intent in general terms, never write actual working exploit code, real payloads, or step-by-step attack instructions, even as an example.
> 5. Aggregate the false-positive root causes by category, ranked by how often each shows up in my sample.
> 6. For each top category, tell me whether this looks like a quick vocabulary-overlap fix (an allowlist or context rule) or a genuinely hard semantic distinction that needs a trained classifier — and in either case, note that a human needs to sign off before deploying the change. Never recommend just turning a guardrail category off.
> 7. Tell me how many more labeled examples I'd need to reach a usable eval-set size (200-300 pairs), and who should review the ambiguous ones.
>
> Here is my sample: [paste queries, verdicts, and labels here]

## What you get back

A report with five sections:

1. **Diagnostic Summary** — sample size, split of benign-technical vs. genuinely-malicious vs. ambiguous, and the top root-cause categories.
2. **Per-Query Breakdown** — a table of each query, its guardrail verdict, trigger vocabulary, and inferred intent.
3. **Draft Eval-Set Pairs** — a CSV-style block (`id,benign_text,malicious_text,vocabulary,domain`) seeding the labeled dataset you'd need for a full fix. This is a starting seed (you'll need 200-300 pairs eventually), not a finished dataset.
4. **Root-Cause Recommendations** — ranked categories with a tune-it vs. train-a-classifier call for each, and the human sign-off step required.
5. **Next Steps** — how much more labeled data you need, and who should review the unclear cases.

## Guardrails on this skill itself

- It will never write real exploit code, working payloads, or attack instructions for the "malicious" side of a draft pair — only abstract, intent-level descriptions. Don't ask it to go further than that; it's designed to refuse.
- It will never silently overrule a ground-truth label you provide — if its read disagrees with yours, it says so and explains why, and leaves the call to you.
- It will never tell you to just disable a guardrail category — only to tune, exempt specific patterns, or invest in a classifier, always with a human-review step named.
- If you give it fewer than 10 queries, or none with ground-truth labels, it should tell you the read is provisional and ask for more data rather than hand you a confident-sounding verdict on thin evidence.
- It does not train or deploy anything — it's the diagnostic and seed-data step that comes before that project.
