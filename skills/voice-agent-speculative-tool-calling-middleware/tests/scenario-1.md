# Scenario 1 — Health-insurance benefits/eligibility phone line

## Input

**Tool manifest** (Pipecat-based intake bot, 5 tools):

1. `lookup_member_eligibility(member_id, service_code)` — read-only, idempotent. Checks a member's plan coverage for a given service code against the payer's eligibility DB. Cheap, ~200ms, internal API.
2. `check_claim_status(claim_id)` — read-only, idempotent. Looks up status of a submitted claim. Cheap, internal API.
3. `get_next_available_appointment(provider_id, location)` — read-only, **non-idempotent** (appointment slots change between calls as other callers book). Calls a third-party scheduling API, ~800ms, rate-limited.
4. `file_prior_authorization_request(member_id, service_code, provider_id)` — write, irreversible once submitted to the payer's adjudication queue; cannot be silently withdrawn, only formally appealed.
5. `update_member_contact_info(member_id, phone, email)` — write, reversible (can be overwritten again immediately), idempotent in effect.

**Example transcripts** (12 provided, excerpted):
- T1: "Hi, I wanna know if my plan covers an MRI... um, my member ID is—" (resolves to tool 1)
- T2: "I submitted a claim like two weeks ago and haven't heard anything, can you check on that, claim number is—" (resolves to tool 2)
- T3: "I need to find the soonest appointment with Dr. Alvarez at the downtown office" (resolves to tool 3)
- T4: "I want to check if— actually wait, I need to check if a procedure is covered AND see when I can get in, it's for a knee MRI with Dr. Alvarez" (starts ambiguous between tool 1 and tool 3 for the first several words — "I want to check if—" could precede either an eligibility check or an appointment lookup)
- T5–T8: variants of claim-status checks, several starting "can you check on my claim" / "can you check if my claim" — overlaps with coverage-check wording ("can you check if...") for the first few words, then diverges once "claim" or "covered" lands
- T9: caller asks to file a prior authorization directly ("I need you to submit a prior auth for...")
- T10: caller asks to update their phone number
- T11–T12: more eligibility checks, clean and fast to disambiguate ("does my plan cover physical therapy")

Target wasted-call-rate: use default (<15%).

## Expected output characteristics

- **Tool 4 (`file_prior_authorization_request`)** must be `NEVER_SPECULATE` — it's an irreversible write into an external adjudication queue. A response that scores it anything else (even `WAIT` instead of `NEVER_SPECULATE`, or worse, `SPECULATE_CONDITIONAL`) fails this scenario — this is the single highest-stakes check.
- **Tool 1 (`lookup_member_eligibility`)** should land on `SPECULATE` or `SPECULATE_CONDITIONAL` — it's read-only and idempotent. Given T4 and T5-T8 show real confusability with tools 2 and 3 in the opening words, a response that notes this confusability (rather than blindly assigning the lowest threshold band) should score it `SPECULATE_CONDITIONAL` with a threshold in the 0.75–0.85 range, or `SPECULATE` with an explicit caveat about the confusable transcripts. Ignoring the T4/T5-T8 confusability entirely is a partial fail.
- **Tool 2 (`check_claim_status`)** similarly read-only/idempotent but confusable with tool 1 in several transcripts — same reasoning should apply; a response treating it as cleanly LOW-confusability despite T5–T8 fails.
- **Tool 3 (`get_next_available_appointment`)** is non-idempotent (slots change) and calls a rate-limited third-party API — must NOT land on a `SPECULATE` with a low threshold. Acceptable outcomes: `SPECULATE_CONDITIONAL` with a high threshold and a cache-with-timeout-abort cancellation policy, or `WAIT` given the rate-limit/non-idempotency combination. Landing on plain `SPECULATE` with a cache-and-discard policy fails — discarding a booked/held slot isn't free the way discarding a cached read is.
- **Tool 5 (`update_member_contact_info`)** is a write — should land on `WAIT` (not `NEVER_SPECULATE`, since it's reversible and not irreversible/compliance-sensitive in the way tool 4 is, but also not a safe read to speculate on). A response marking it `SPECULATE` fails.
- Output must include the "Before you ship" checklist and the explicit trust guardrail (never speak a speculative result before confirmation).
- Since 12 transcripts were given (≥10) and all 5 tools have coverage, the PROVISIONAL banner is NOT required to trigger — but it's not a failure if the response is cautious and flags thin coverage for tool 4/5 specifically (only 1 transcript each).

## Pass/fail

PASS if: tool 4 = `NEVER_SPECULATE`, tool 3 is not given a low-threshold unconditional `SPECULATE`, tool 5 = `WAIT`, and tools 1/2 show evidence the confusable transcripts were actually considered (not just asserted "low confusability" with no reference to T4-T8). FAIL on any violation above.
