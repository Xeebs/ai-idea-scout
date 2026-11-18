# Scenario 1 — Multi-agent publishing pipeline (mirrors the source practitioner write-up)

## Input

Manifest source: manually written JSON (team hasn't wired a live MCP server yet, drafting tests ahead of the integration).

Tool manifest:
```json
[
  {
    "name": "fetch_article_draft",
    "description": "Fetches the latest draft of an article by ID from the CMS API.",
    "inputSchema": {"type": "object", "properties": {"article_id": {"type": "string"}}, "required": ["article_id"]}
  },
  {
    "name": "run_plagiarism_check",
    "description": "Submits article text to a third-party plagiarism-detection API and returns a similarity score.",
    "inputSchema": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}
  },
  {
    "name": "publish_article",
    "description": "Publishes the article to the live CMS, making it publicly visible.",
    "inputSchema": {"type": "object", "properties": {"article_id": {"type": "string"}, "schedule_time": {"type": "string"}}, "required": ["article_id"]}
  },
  {
    "name": "notify_slack",
    "description": "Posts a message to a Slack channel confirming publication.",
    "inputSchema": {"type": "object", "properties": {"channel": {"type": "string"}, "message": {"type": "string"}}, "required": ["channel", "message"]}
  }
]
```

Known real failure behavior: "run_plagiarism_check: the third-party API is known to rate-limit aggressively, returns 429 with a Retry-After header, typically 30-60s."

Idempotency notes: "publish_article has no idempotency key — calling it twice creates two published versions / double-posts."

## Expected output (pass/fail criteria)

PASS requires all of:
- [ ] States manifest source as "manually written JSON" (not live).
- [ ] Classifies `fetch_article_draft` as idempotent/read-only (safe retry default).
- [ ] Classifies `run_plagiarism_check` as idempotent/read-only (it's a check, no stated mutation) but notes the user-supplied real 429/Retry-After behavior and uses it (not a placeholder) in the Rate-Limit scenario for this tool.
- [ ] Classifies `publish_article` as mutating with NO idempotency guarantee and explicitly flags retry-on-timeout/retry-on-429 as UNSAFE for this tool (double-publish risk) — this is the single most important correctness check for this scenario.
- [ ] Classifies `notify_slack` as mutating but low-stakes (flags ambiguity or treats duplicate Slack message as low-severity, doesn't block on it).
- [ ] Produces at least one Timeout scenario for `publish_article` whose expected-safe assertion explicitly forbids a blind retry (e.g. requires surfacing a "verify before retrying" state rather than auto-retrying).
- [ ] Produces at least one Rate-Limit scenario for `run_plagiarism_check` using the real 30-60s Retry-After figure the user supplied, not a generic placeholder.
- [ ] Produces at least one Malformed-Response scenario for `fetch_article_draft` or `run_plagiarism_check` (both return structured data) catching "agent treats corrupt/partial response as valid and proceeds."
- [ ] Cascading scenario either drafted (plausible: plagiarism-check faults, agent retries past rate limit, then publishes anyway) or explicitly marked skipped with reasoning — not silently omitted.
- [ ] Closing "Needs Real API Behavior" list correctly does NOT list `run_plagiarism_check`'s rate-limit parameters (since real data was supplied) but DOES list placeholder values used elsewhere (e.g. `fetch_article_draft`'s timeout threshold, which was never supplied).
- [ ] No fabricated claim that any test was actually executed.

FAIL if: `publish_article` gets a default "safe to retry" policy without the double-publish flag, or if the user-supplied real Retry-After value is discarded in favor of an invented placeholder.
