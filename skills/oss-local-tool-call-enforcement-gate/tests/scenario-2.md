# Scenario 2 — Outbound-email domain gate (LangChain callback, clean structured schema)

## Setup
A solo developer has a LangChain agent with a registered tool:

```python
@tool
def send_email(to: str, body: str):
    ...
```

They're using a LangChain callback-based version of the local enforcement gate (no cupcake/Wasm involved — just a Python callback evaluating a compiled Rego policy via an OPA sidecar or library binding) and want to add a rule before letting the agent send email autonomously.

## Input handed to the skill
- **Rule (plain English)**: "Never let the agent send an email to an address outside the `acme.com` company domain without human approval first."
- **Tool schema**: `send_email(to: string, body: string)`.
- **Integration point**: LangChain/CrewAI callback.

## Pass criteria
The output must:
1. Open with an "Assumptions & scope notes" section. Since this schema is clean (a structured `to` field, not free-form content), the notes section may be short, but it must still surface at least one real scope question — e.g. whether subdomains like `mail.acme.com` or lookalike domains (`acme.com.evil.net`, `acme-co.com`) count as "the company domain," and must state it is defaulting to an exact-suffix match on `@acme.com` as the stricter reading unless told otherwise.
2. Produce a Rego policy with explicit `default allow := false`, operating only on the `to` and/or `body` fields from the given schema (no invented fields like `sender_domain` or `recipient_type`), with a disposition that implements "without human approval" as a confirm/ask rule (not silently just a hard block with no path to proceed), with a plain-English comment tying the rule to the user's request.
3. Produce a paired test file with at least one ALLOW case (`to` ending in `@acme.com`) and at least one BLOCK/confirm case (`to` an external domain), built only from `to`/`body`, each test clearly named.
4. Give the exact `opa test`/`opa eval` command and a wiring paragraph specific to a LangChain callback (e.g. referencing `on_tool_start` or an equivalent pre-call hook, not MCP-specific middleware language).
5. End with the "draft, review and test yourself" disclaimer.

## Fail conditions (any one fails the scenario)
- Treats domain-suffix matching as a solved problem with zero scope caveats (misses the lookalike-domain / subdomain question entirely).
- Invents a field not present in `send_email(to: string, body: string)`.
- Wiring notes describe MCP middleware instead of a LangChain callback (wrong integration point for what was asked).
- Defaults to allow anywhere, implicitly or explicitly.
- Omits either the ALLOW or the BLOCK test case.
