# Scenario 1: Dictation cleanup rewriter

## Context
A developer runs a local LLM (currently comparing `llama3.1:8b` and `qwen2.5:14b` via Ollama on a 16GB VRAM laptop) to clean up raw dictation transcripts into readable prose for their engineering notes. They've been eyeballing outputs and want a real eval set before picking a model to stick with.

## Input handed to the skill

Task: "Take a raw dictated transcript (from talking out loud while coding) and rewrite it into clean, grammatically correct prose, keeping all technical terms and filenames exactly as spoken, removing filler words ('um', 'so yeah', 'like'), and keeping roughly the same length (+/- 20%)."

Examples:
1. Input: "so yeah i think the bug is in um the auth middleware like the token refresh logic it's not checking expiry right" / Good answer: "The bug is in the auth middleware's token refresh logic — it's not checking expiry correctly."
2. Input: "okay next thing i want to fix the database connection pool because like it's leaking connections under load" / Good answer: "Next, I want to fix the database connection pool because it's leaking connections under load."
3. Input: "um the api endpoint slash users slash id is returning a 500 when the id is like not a valid uuid" / Good answer: "The /users/:id API endpoint returns a 500 when the ID is not a valid UUID."
4. Input: "so basically what i'm thinking is we refactor the payment service to use stripe's new idempotency keys api" / Good answer: "I'm thinking we refactor the payment service to use Stripe's new idempotency keys API."

Candidate models: llama3.1:8b, qwen2.5:14b (context only).

## Pass criteria
- Classifies all 4 examples as open-ended (not exact-match), since phrasing varies even with a reference — rubric-match or LLM-judge, not strict exact-match.
- States sample-size verdict as "too few to trust a ranking" (4 < 5) and recommends growing toward 8-15.
- Names at least 2 concrete missing edge cases, e.g.: no example with a technical term/filename that must survive verbatim under heavier filler, no example testing the length-preservation constraint being violated, no malformed/very short or very long transcript tested, no example where filler removal could accidentally drop real content.
- Produces a rubric with dimensions tailored to this task specifically (e.g., filler-word removal completeness, technical-term/filename fidelity, grammaticality, length adherence within 20%) — not generic "quality/helpfulness."
- Produces a ready-to-paste LLM-judge prompt template with {input}/{reference_or_rubric}/{model_output} placeholders.
- Includes the mandatory LLM-judge calibration limitation line.
- Does not recommend llama3.1:8b vs qwen2.5:14b as a pick, does not probe or mention VRAM/hardware as a driver of the review, does not simulate running either model.
- Includes the "Not Covered By This Review" closing note.

## Fail criteria
- Treats this as exact-match scoreable (it isn't — phrasing legitimately varies).
- Silently proceeds without flagging the sample size as too small.
- Gives generic edge-case advice not grounded in the actual 4 examples shown.
- Picks a model or discusses VRAM/hardware fit.
- Fabricates a model output or score instead of only designing the eval set.
