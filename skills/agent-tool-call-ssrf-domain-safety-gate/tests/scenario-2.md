# Scenario 2: Multi-tool support agent with one partially-guarded fetch and one vague request

## Input a user would realistically provide

> Agent task scope: "A customer-support agent for a SaaS product that can look up a customer's linked external documentation URL (pasted into a support ticket) to check whether a referenced screenshot or doc page matches our product, plus a separate tool that calls our own internal webhook-retry endpoint."
>
> Fetch-type tool call sites:
>
> ```python
> def fetch_customer_doc(url: str) -> str:
>     parsed = urlparse(url)
>     if parsed.hostname in BLOCKED_HOSTS:  # a short manual list of a few known-bad hosts
>         raise ValueError("blocked host")
>     return requests.get(url, timeout=5).content
> ```
>
> ```python
> def retry_webhook(webhook_id: str) -> dict:
>     url = f"https://internal.ourcompany.com/webhooks/{webhook_id}/retry"
>     return requests.post(url).json()
> ```
>
> Existing guards already in place: `fetch_customer_doc` has that `BLOCKED_HOSTS` check above; nothing else that I know of. Not totally sure if there's a redirect check anywhere.

## Pass criteria

The output must:
1. Correctly identify `fetch_customer_doc` as model/user-influenced (URL comes from a pasted support ticket, so effectively untrusted) and score its SSRF gating as `PARTIAL` (a denylist exists but no private-range/metadata-IP blocking and no redirect re-validation — explicitly note the "not totally sure if there's a redirect check" as a gap to close, not ignore).
2. Correctly identify `retry_webhook` as NOT a candidate for this audit (its target URL is a fixed, developer-constructed internal endpoint, not a model/user-chosen URL) — or explicitly ask the user to confirm `webhook_id` can't be used to construct an arbitrary target, rather than silently drafting a full SSRF policy for a non-fetch-surface tool.
3. Score `fetch_customer_doc`'s domain-safety gating as `NONE` (a denylist of "known-bad hosts" is not a relevance check nor a reputation-API-backed abuse check) and draft both halves: a named reputation API recommendation, and a relevance rule tied to "matches our product's documentation."
4. Ask for clarification on the redirect-check uncertainty rather than guessing, OR explicitly flag it as an open question needing verification before finalizing the `PARTIAL` vs `NONE` SSRF score.
5. Still produce a full policy table, SSRF config draft, domain-safety policy draft, audit-log fields, residual risks, and test checklist for `fetch_customer_doc`.

## Fail criteria

- Drafts a full SSRF/domain-safety policy for `retry_webhook` as if it were an equally open fetch surface, without flagging that its URL isn't model/user-chosen.
- Scores `fetch_customer_doc` as `COVERED` because a `BLOCKED_HOSTS` list exists.
- Fails to flag the unresolved redirect-check uncertainty at all.
- Produces only a generic "add input validation" response without the specific SSRF config elements (private ranges, metadata IP, redirect re-validation) and the specific domain-safety split (reputation API + relevance rule).
