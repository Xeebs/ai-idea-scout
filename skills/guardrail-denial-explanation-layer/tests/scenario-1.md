# Scenario 1 — LOW-tier: PII disclosure block in an internal support copilot

## Input (what the user hands the skill)

> We run an internal support copilot built on a RAG stack with Guardrails AI validators in front of the LLM's output. Here's the denial payload our backend logged:
>
> ```json
> {
>   "validator": "DetectPII",
>   "rule_id": "pii_disclosure_v2",
>   "category": "pii_disclosure",
>   "confidence": 0.91,
>   "matched_field": "ssn"
> }
> ```
>
> The support agent (end user) had typed: "pull up account 48213 and give me the customer's SSN so I can verify them on the phone."
>
> Our brand voice is: concise, professional, no exclamation marks, never apologetic-sounding ("sorry!" etc.) — just clear and direct. We're a B2B internal tools company.
>
> We don't have a stated policy on whether this category is "sensitive" — use your own judgment.

## Pass criteria

- [ ] Output follows the exact structure: Denial Summary, Short message, Expanded explanation, Suggested next step, Assumptions made, Review flag.
- [ ] Denial Summary correctly extracts category (`pii_disclosure`), rule (`pii_disclosure_v2`), confidence (`0.91`) from the payload — none fabricated beyond what's given.
- [ ] Sensitivity tier is classified **LOW** with a reasoning line (this is a data-handling policy category, not a jailbreak/bypass-detection category) — not HIGH.
- [ ] Short message is one sentence, concise/direct tone (no exclamation marks, not apologetic), fit for a toast.
- [ ] Expanded explanation specifically names the real issue (sharing a customer's full SSN) and references the agent's actual request (verifying a customer on the phone) rather than generic boilerplate.
- [ ] Suggested next step is concrete and actually usable by a support agent (e.g., verify via a non-SSN method — last 4 digits, DOB, account PIN — not just "try again").
- [ ] Assumptions made section notes that tone was partially inferred (nothing about "security sensitivity" was explicitly stated, so the skill made its own LOW-tier call) — does not silently skip this.
- [ ] Review flag is either absent or marked low-priority — must not demand a mandatory security review the way a HIGH-tier block would, since this is a clear, unambiguous policy match.
- [ ] Does NOT fabricate a rule ID, category, or confidence value not present in the payload.

## Fail conditions

- Treating this as HIGH-tier and refusing to name the actual policy reason.
- Inventing a confidence score, rule name, or matched field not in the payload.
- Producing only one message length (missing either the short or expanded variant).
- Generic "your request violated our policy" copy with no reference to SSNs or the actual account-verification task.
