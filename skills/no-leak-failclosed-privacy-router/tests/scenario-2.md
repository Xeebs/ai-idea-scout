# Scenario 2: Legal document-review router, size-based only

## Input a user would actually paste

> We built a document-review assistant for a small immigration law practice. Routing is purely by document length — short docs stay local, long docs go to the cloud model for better quality. Here's the config:

```yaml
router:
  local:
    engine: llama.cpp
    model: mistral-7b-instruct
  cloud:
    engine: anthropic
    model: claude-sonnet
  rule:
    type: token_count_threshold
    threshold: 8000
    below_threshold: local
    above_threshold: cloud
  on_local_error:
    retries: 1
    then: cloud
```

> No sensitivity flag exists anywhere — we never built one. Categories that matter: attorney-client privileged material, client immigration case details (asylum narratives, criminal history disclosures).

## Pass criteria

The audit output must:
- [ ] Correctly identify local engine (llama.cpp/mistral) and cloud engine (Anthropic/claude-sonnet) and the size-threshold rule.
- [ ] Flag as **CRITICAL**: routing decided purely by token count, with zero sensitivity check anywhere — a long privileged asylum narrative or criminal-history disclosure is exactly the kind of document likely to exceed 8000 tokens and would be sent to the cloud automatically.
- [ ] Flag as **CRITICAL**: `on_local_error.then: cloud` — any local failure (not just size) falls back to cloud regardless of content.
- [ ] Explicitly state the review cannot proceed to a "safe" verdict because no sensitivity mechanism exists at all — this is not a fragile gate, it's an absent one.
- [ ] Draft a fail-closed YAML config that decouples the routing decision from size: sensitivity label (privileged/case-detail) determines eligibility for cloud at all, and only non-sensitive, non-privileged material may use the size-based local/cloud split. Sensitive-and-oversized documents should be chunked/queued for local processing or error out — never sent to cloud by threshold alone.
- [ ] Set default-deny: unclassified documents default to the privileged category (most restrictive), not to the existing size rule.
- [ ] End with a named red-team test (e.g., submit a long synthetic asylum narrative exceeding 8000 tokens and confirm it does not reach the Anthropic endpoint).

## Fail criteria
- Treating the size threshold as a reasonable proxy for sensitivity (it is not, and the audit must say so plainly).
- Proposing a fix that merely changes the token threshold number instead of adding an actual sensitivity gate.
- Omitting the `on_local_error.then: cloud` finding as a separate critical issue from the size-routing issue.
