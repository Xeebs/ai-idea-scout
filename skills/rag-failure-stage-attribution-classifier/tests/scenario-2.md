# Scenario 2 — Generation failure (fabricated number despite sufficient context), plus a low-confidence check

## Context
A developer-tools startup runs a RAG-powered docs chatbot for its API. A developer reported the bot quoted a rate limit that doesn't match the published docs, and filed it as "the bot is lying." The on-call engineer pastes the interaction to find out if it's a hallucination (fix the generator/prompt) or whether the docs chunk itself is stale (fix the corpus).

## Input to the skill

**Query**: "What's the rate limit for the free tier of the Widgets API?"

**Retrieved chunks**:
- Chunk 1 (source: `api-docs/rate-limits.md`, section "Rate Limits", chars 0–310):
  > "The Widgets API enforces the following rate limits per API key: Free tier — 100 requests per minute, burst up to 150 for 10 seconds. Pro tier — 1,000 requests per minute, burst up to 1,500 for 10 seconds. Enterprise tier — custom limits negotiated per contract."

**Generated answer**: "The free tier for the Widgets API allows 500 requests per minute, with no burst allowance."

**Correct answer / gold passage**: not available (the engineer trusts the retrieved chunk is correct and current, but hasn't independently verified against the live API gateway config).

**Adjacent chunks**: not available.

## Expected handling
- Sufficiency check: no gold passage given, so this runs as a best-effort judgment — but the retrieved chunk directly and unambiguously states the free-tier limit (100 req/min, burst 150), which is exactly on-topic for the query. A reasonable judgment call is sufficiency CONFIRMED (the chunk plainly contains the answer to this specific query), while still noting the LOW-confidence caveat applies if there's any possibility the doc itself is stale relative to production config.
- Chunking check: not applicable / unavailable — no adjacent chunks given, and there's no visible truncation in the chunk (the sentence completes cleanly with a period before the next tier).
- Claim-support check: break down the answer's claims — "500 requests per minute" is Contradicted (chunk says 100), "no burst allowance" is Contradicted (chunk says burst up to 150 for 10 seconds). Both claims traceable only to the generator, not the retrieved text.
- Verdict should be **GENERATION FAILURE**, confidence should be MEDIUM-to-HIGH on the generation call itself (the contradiction is clean and directly quotable) even though no external gold passage was supplied — the "gold" comparison here is the retrieved chunk against the answer, which is self-contained evidence, not a judgment call about the world.
- The report should still flag that it cannot verify whether the doc chunk itself (100 req/min) matches the actual live API gateway config, since no gold source beyond the pasted chunk was given — but this is a secondary caveat, not a blocker to the generation verdict.

## Pass/fail criteria
- PASS if the verdict is GENERATION FAILURE with evidence quoting both the chunk's actual numbers ("100 requests per minute, burst up to 150 for 10 seconds") and the answer's contradicting numbers ("500 requests per minute... no burst allowance"), the chunking check is reported as unavailable/not applicable rather than silently skipped, and the output does not claim retrieval or chunking is at fault.
- FAIL if the tool reports RETRIEVAL FAILURE or CHUNKING FAILURE, if it fails to quote the specific contradicting numbers from both chunk and answer, or if it claims full certainty that the chunk's 100 req/min figure matches production without flagging that no independent gold source was provided for that narrower claim.
