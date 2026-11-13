# Bypass Triage: Guardrail Micro-Bounty Submission Reviewer

A self-contained prompt template for triaging a single red-team bounty submission against a self-hosted LLM guardrail (NeMo Guardrails, Guardrails AI, LLM Guard, or a custom webhook). Paste this whole document into any AI chat tool (Claude, ChatGPT, Gemini, etc.) along with your submission details, and it will tell you whether to pay, reject, or ask for more evidence — plus draft the message to send back.

## When to use this

Use this when you're a solo developer or small team running a self-hosted LLM guardrail and someone submits a claim — via a GitHub issue, a Discord DM, an email, or a bounty-board form — that they found an adversarial payload that bypasses your guardrail (gets flagged as "clean" when it should have been caught as prompt injection, jailbreak, PII leakage, etc.), and you need to decide whether to pay out, reject, or ask for more info. This fits the pattern of a solo-run micro-bounty (think: a GitHub issue titled "[BOUNTY] $5.00+ USDC: Adversarial Prompt Injection Bypass") triaged entirely by hand, with no automated pipeline behind it.

This is a one-shot judgment-and-drafting task for **one submission at a time**. It does not run an ongoing bounty program, hold escrow, process payment, or maintain a leaderboard — you (the builder) still own those decisions and that infrastructure. This just does the judgment call on whether a given submission is legitimate.

## Data source

**Manual or Connected, your choice per session.** Best case: you give the AI tool live access to your guardrail's HTTP endpoint (URL, auth header, request/response shape) so it can replay the submitted payload itself and get a fresh, authoritative verdict — this works today against NeMo Guardrails, Guardrails AI, LLM Guard, or any custom webhook, since all of them already expose a "submit payload, get back verdict" API; there's just no single standardized connector across them, so you describe your specific request/response shape and the tool adapts.

If you're using a plain chat interface with no tool-calling/API access in that session (e.g. pasting into a chat box with no browsing or execution), fall back to manually re-running the payload against your own guardrail yourself first, then **paste** the fresh verdict output instead. Either way, you must say explicitly which mode you used — a pasted verdict is weaker evidence than a live replay, and the output must reflect that.

## What to hand over

Before running this, gather:

1. **The submission** — the exact adversarial payload text, the submitter's claimed bypass description (what category it should have been flagged under and wasn't), and the submitter's claimed verdict or screenshot from your guardrail, pasted verbatim.
2. **Either** your guardrail endpoint (URL + auth + request format) for a live replay, **or** a pasted fresh verdict output if you can't replay this session.
3. **Your guardrail's stated detection scope** — what categories/policies it claims to cover (e.g. "prompt injection, PII leakage, jailbreak attempts"), pulled from its config or docs, pasted or linked.
4. **Your prior submission history** — a pasted list or log of previously accepted and rejected bypass reports (payload summary, technique family, date, outcome). If this is your very first submission ever, that's fine — say so explicitly rather than skipping the dedupe step.

## The procedure (paste this prompt, with your four inputs above, into any AI chat tool)

> You are triaging a single red-team bounty submission against my self-hosted LLM guardrail. Here is what I have:
>
> **Submission**: [paste the payload, the claimed bypass, and the submitter's claimed verdict]
> **Evidence available**: [either "I can give you live endpoint access: <URL, auth, request/response format>" or "Here is a fresh pasted verdict I ran manually: <paste>"]
> **Guardrail's stated detection scope**: [paste or describe the categories it claims to cover]
> **Prior submission history**: [paste a list of past accepted/rejected submissions with technique family, date, outcome — or state "this is our first submission, history is empty"]
>
> Follow this exact procedure:
> 1. **Replay or verify the verdict.** If I gave you live endpoint access, replay the exact payload now and record the fresh verdict. If I only gave you a pasted verdict, use it but flag the result `UNVERIFIED (no live replay)` throughout. If neither is available, stop and tell me you need one — never guess at what the guardrail would have said.
> 2. **Check reproducibility.** Compare the fresh (or pasted) verdict against the submitter's claim. If the guardrail now correctly flags the payload, contradicting the claim, this does not reproduce.
> 3. **Check scope.** Confirm the claimed bypass category actually falls within what my guardrail's stated detection scope claims to cover. A payload that slips through a category never claimed is out of scope, not a bypass.
> 4. **Dedupe by technique family, not exact string.** Identify the underlying technique (e.g. "unicode homoglyph obfuscation," "nested-roleplay jailbreak template," "base64-encoded instruction smuggling") and compare it against technique families already present in my submission history — not a literal text match. Cosmetic rewording of a known family is still a duplicate; a genuinely different technique with a similar surface effect is not.
> 5. **Classify into exactly one of**: `PAY — GENUINE NOVEL BYPASS`, `REJECT — DUPLICATE`, `REJECT — NOT REPRODUCED`, `REJECT — OUT OF SCOPE`, or `NEEDS MORE INFO`.
> 6. **Flag abuse/scope risk separately** from the classification — note explicitly (don't skip this even on a clean `PAY`) if the submission shows signs of unauthorized testing against a production system, or targets something outside what this bounty covers.
> 7. **Draft a ready-to-send response** to the submitter matching the classification, thanking them and explaining the outcome. For a `PAY` verdict, explicitly note that the actual payout amount and release are my decision, not something you are authorizing.
>
> Produce your answer in exactly this format:
>
> ```
> ## Bypass Triage Report
>
> **Submission**: <one-line summary>
> **Evidence mode**: LIVE REPLAY | UNVERIFIED (pasted verdict only)
> **Verdict**: PAY — GENUINE NOVEL BYPASS | REJECT — DUPLICATE | REJECT — NOT REPRODUCED | REJECT — OUT OF SCOPE | NEEDS MORE INFO
>
> ### Reproduction check
> <details>
>
> ### Scope check
> <details>
>
> ### Dedupe check
> <technique family identified, and the specific prior entry it matches, or confirmation none matches — note explicitly if history was empty>
>
> ### Abuse/scope risk flag
> <NONE, or a specific concern>
>
> ### Draft response to submitter
> <ready-to-send message>
>
> ### Caveats
> <e.g. "verdict is unverified — recommend a live replay before finalizing," or "payout amount/release is your own decision; this report only establishes eligibility">
> ```
>
> Rules you must follow:
> - Never fabricate or assume a guardrail verdict. If you have neither a live replay nor a usable pasted verdict, classify as `NEEDS MORE INFO` and ask for one.
> - Never treat exact-string novelty as enough for `PAY` — always run the technique-family dedupe check.
> - Never state or authorize a specific payout amount — that decision belongs to the builder.
> - Never classify as `REJECT — DUPLICATE` without naming the specific prior entry or technique family it matches.
> - Never drop the abuse/scope risk flag, even on a clean `PAY` — classification and authorization-to-test are separate questions.
> - Do not behave like a running bounty platform, escrow system, or leaderboard — you are reviewing one submission and producing no persistent state.

## What you get back

A single "Bypass Triage Report" (format shown above) covering: the evidence mode used, a final classification, the reproduction/scope/dedupe reasoning behind it, a standalone abuse/scope-risk flag, a ready-to-send draft response to the submitter, and caveats about what's unverified or still the builder's own call.

## Guardrails

- Never pay out, or tell the submitter they'll be paid a specific amount, based on this skill's output alone — it establishes eligibility and drafts a message only.
- Never accept a classification of `PAY` when the evidence mode is `UNVERIFIED (no live replay)` without flagging that explicitly as a caveat — unverified evidence should push toward re-testing before payout, not toward treating it as equivalent to a live replay.
- Never skip the technique-family dedupe step just because the submitted payload string looks new — check the underlying technique against history every time.
- Never run this as a substitute for an actual bounty platform — it has no memory between sessions; you must bring the prior-submission history yourself each time.
