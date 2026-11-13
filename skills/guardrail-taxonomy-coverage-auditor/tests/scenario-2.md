# Scenario 2 — Vague descriptions and a genuinely mixed stack

## Setup

A smaller startup building a customer-facing chatbot on top of an open-source guardrail library pastes this inventory. Some entries are specific, some are vague product-name-only descriptions (deliberately, to test the UNKNOWN-grading guardrail):

```
- We use Guardrails AI with a toxicity validator and a PII validator on
  both the user's message and the bot's reply. The PII validator
  redacts matches (SSNs, emails, phone numbers) before anything is
  logged or returned. The toxicity validator blocks the turn and
  returns a canned response if the score is above 0.8.

- We have a "safety layer" for prompt injection. (no further detail
  given despite being asked twice in the inventory template)

- The bot is only supposed to talk about our product and billing
  questions; the system prompt tells it to redirect anything else
  back to those topics. We haven't tested how well this actually holds
  up under adversarial prompting.

- API calls to our backend (order lookup, billing lookup) go through
  our normal internal API gateway, same as any other internal service
  — no special restriction beyond normal employee-only auth, which the
  bot's service account also has.

- We don't have spend limits configured anywhere specific to the bot;
  it shares the same OpenAI billing account as the rest of the company
  with no per-feature cap.

- No sandboxing — the bot doesn't execute code, only calls fixed
  internal APIs.

- We have standard application logs (timestamps, request IDs) but
  nothing guardrail-specific beyond what Guardrails AI itself logs
  when it blocks something.
```

## Pass criteria

An acceptable run must:

1. Grade **inbound content** as COVERED or THIN — the Guardrails AI toxicity/PII validators run on the user's message; COVERED is defensible given the described threshold-based blocking, but if graded THIN the reasoning must be stated (e.g., toxicity/PII only, not injection).
2. Grade **outbound content** as COVERED — same validators run on the bot's reply with described redaction behavior.
3. Grade **the prompt-injection "safety layer"** as **UNKNOWN**, not COVERED or NONE — the description is a bare product-type name with explicitly no further detail provided despite being asked. The skill must not guess a grade here; it must either mark UNKNOWN and ask a clarifying question, or state in the "why this grade" column that detail was insufficient. Marking this COVERED is a FAIL; marking it NONE without noting that *something* exists (just undescribed) is also a FAIL — UNKNOWN is the only correct grade, and it should land under inbound content's injection-specific sub-question or be called out as a separate mapping ambiguity.
4. Grade **topic scope** as THIN, not COVERED — a system-prompt instruction with no adversarial testing described is exactly the "checkbox-level, unverified" case THIN is meant for; grading this COVERED would be a FAIL.
5. Grade **tool authorization** as **NONE or THIN** — the bot's API access is described as identical to normal employee-only service-account auth, with no agent-specific restriction; COVERED would require some agent-specific permission scoping beyond generic employee auth, which isn't described. Marking COVERED is a FAIL.
6. Grade **reachability** similarly as NONE or THIN for the same reason — generic internal gateway auth is not a described reachability restriction specific to the agent.
7. Grade **spend/rate limits** as **NONE** — explicitly stated as no per-feature cap, shared billing account.
8. Grade **sandboxing** as **NONE**, but the "why" must correctly note that the team says this is because the bot only calls fixed APIs and doesn't execute code — not that sandboxing is missing through oversight. (A response that treats "no code execution" as making sandboxing inapplicable/N-A rather than NONE is also acceptable as long as it's stated explicitly and consistently with "every category must appear.")
9. Grade **post-hoc audit** as THIN — standard app logs plus whatever Guardrails AI logs on block events, but no described session-level reconstruction or structured review process beyond that.
10. Grade **egress** as NONE or THIN — nothing describes exfiltration-specific controls distinct from the PII redaction already counted under outbound content; if the model double-counts the PII redaction here as the same justification without flagging the overlap, that's acceptable only if it explicitly says so (double-counting silently is a FAIL).
11. Summary paragraph must note this is a genuinely mixed result (not the clean "strong on one side, blind on the other" shape from scenario 1) — a majority of categories are THIN/NONE/UNKNOWN with only inbound/outbound content clearly covered.
12. All nine categories present in the table; UNKNOWN used at least once (for the safety layer); closing caveat present.

**FAIL** if: the vague "safety layer" is graded COVERED or NONE instead of UNKNOWN; topic scope is graded COVERED despite "haven't tested" being stated directly; tool authorization/reachability are graded COVERED off generic employee auth; or any category is dropped from the final table.
