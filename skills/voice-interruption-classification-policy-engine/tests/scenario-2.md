# Scenario 2 — Outbound sales/collections qualification line, minimal context provided

## Input (as a user would actually provide it)

> We have an outbound voice agent that calls past-due customers to offer payment plan options and qualify them for a plan. I don't really know the demographics of who picks up — probably a mix of everyone. The one thing I know for sure is we're required by our compliance team to read a specific opt-out/debt-collection disclosure line in full near the start of every call, word for word, with no interruptions allowed on that line except if the person flat out says "stop calling me" or something clearly hostile. Other than that we haven't thought much about interruption handling — the agent currently just barges through everything and never stops talking until it finishes, which means it talks right over people trying to interrupt to ask a question. I don't know what our risk tolerance is, nobody's defined that yet.

## Expected output shape

This scenario deliberately omits two of the five inputs (caller population is vague/"probably a mix of everyone", and risk tolerance is explicitly "nobody's defined that yet") to test the missing-input handling.

1. Use case summary must explicitly flag that caller population is effectively unknown and that risk tolerance was not provided — and state the assumption made for each (e.g., defaulting risk tolerance toward balanced/conservative since none was given, and noting population as unknown rather than inventing a skew).
2. Policy table must still be produced with six distinct, justified rows despite the missing inputs — it cannot refuse to answer or produce a single generic "configure your risk tolerance first" non-answer instead of a real table.
3. The disclosure line must appear in the non-interruptible overrides section, explicitly carved out so that an explicit hostile/stop-calling statement still escalates or stops even during that block — mirroring the compliance requirement stated by the user almost verbatim.
4. Given "currently barges through everything and never stops," the report should note this is itself a binary-toggle problem (just the opposite extreme from scenario 1) and that the new policy should differentiate rather than keep that uniform behavior.
5. Open risks must mention the undefined risk tolerance and unknown caller population as explicit gaps to resolve before shipping, not paper over them.

## Pass/fail criteria

- PASS requires: the output clearly states what was missing/assumed rather than silently inventing a specific caller demographic or a specific risk-tolerance stance not given by the user; the compliance disclosure override is captured correctly including the "stop calling me"/hostile exception; the six-row table is still fully populated and differentiated.
- FAIL if: the output invents a caller population skew (e.g., claims "mostly elderly" or gives a fabricated percentage) that was never stated; the compliance line is not carved out as non-interruptible, or the hostile-statement exception is dropped; the report stalls out asking the user to answer more questions instead of producing the deliverable with assumptions flagged; all six rows collapse to "stop-and-listen" (i.e., no actual differentiation from the status quo being complained about).
