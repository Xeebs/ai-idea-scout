# Scenario 1: RAG research-assistant with a bare `requests.get` fetch tool

## Input a user would realistically provide

> Agent task scope: "A research assistant that answers questions about renewable-energy policy by fetching and summarizing publicly linked PDF reports and news articles the model finds via its own web search, then citing them."
>
> Fetch-type tool call sites:
>
> ```python
> def fetch_url(url: str) -> str:
>     """Fetch the contents of a URL the model has chosen (from search results) and return the raw text/PDF bytes."""
>     resp = requests.get(url, timeout=10, allow_redirects=True)
>     resp.raise_for_status()
>     return resp.content
> ```
>
> Existing guards already in place: none — we just added a timeout recently after a slow-loris incident, nothing else.

## Pass criteria

The output must:
1. Score `fetch_url`'s SSRF gating as `NONE` (no private-range check, no metadata-endpoint check, `allow_redirects=True` with zero re-validation).
2. Score its domain-safety gating as `NONE` (no reputation check, no relevance check).
3. Draft an SSRF config naming: RFC 1918 ranges, link-local, loopback, and explicitly the cloud metadata IP `169.254.169.254`, plus a requirement to re-validate the resolved IP on every redirect hop (correctly flagging that `allow_redirects=True` as currently written is exactly the gap that lets a public-looking URL redirect to an internal address).
4. Draft a domain-safety policy naming one real, specific reputation API (e.g. Google Safe Browsing API) for the abuse/malware half, and a relevance rule derived from the "renewable-energy policy" task scope (e.g., keyword/embedding check against page title/meta-description) with a stated uncertain-case default of quarantine, not silent-allow.
5. Produce the full policy table, audit-log field list, residual risks (≥3), and the four-item test checklist.
6. Not claim the draft is a tested guarantee anywhere.

## Fail criteria

- Treats the timeout addition as meaningful SSRF/domain-safety coverage.
- Covers only SSRF and omits the domain-safety half, or vice versa.
- Invents a fake-sounding reputation API name instead of a real documented one.
- Produces generic advice without referencing the specific `fetch_url` function or its `allow_redirects=True` detail.
