# Scenario 1 — Manual description, no log (Claude Code / Django)

## Input a user would actually give

> I want you to design a local-model preflight gate checklist for my cloud coding-agent workflow. Do not write any interceptor or middleware code.
>
> - CLI/tool: Claude Code
> - Stack/language: Python/Django backend, medium-sized app (~40 models, REST API via DRF)
> - What makes my outgoing requests waste a call: (1) I ask it to "fix the bug in the order processing" without saying which file — it goes and searches the whole repo and usually edits the wrong serializer. (2) I've asked it three separate times this week to "add validation to the signup form" because I keep forgetting I already got an answer and didn't apply it, so it just regenerates the same patch.
> - What a bad response looks like for my codebase: (1) Last week it returned code referencing `order.total_amount` but that field is actually called `order.grand_total` in our model — it clearly hallucinated the field name instead of checking models.py. (2) Another time I asked it to run the test suite before confirming a fix was done, and it just said "this should fix it" without actually invoking the test tool at all.
> - Log data: no log, using the descriptions above only.
>
> [rest of the standard prompt as in README.md]

## Pass criteria

- [ ] Output explicitly states Workflow Profile used "manual description" as the data source (not a fabricated log).
- [ ] Pre-Send Checklist includes a "Context completeness" check directly tied to the "which file" problem, with the order-processing example used as the HOLD/FLAG example (not an invented one).
- [ ] Pre-Send Checklist includes a "Duplicate detection" check directly tied to the repeated signup-validation request, using that exact example.
- [ ] Post-Receive Checklist includes a "Structural validity" check tied to the `order.total_amount` vs `order.grand_total` hallucinated-field example.
- [ ] Post-Receive Checklist includes a "Required-action compliance" check tied to the skipped test-suite-tool-call example.
- [ ] No additional failure examples are invented beyond the ~4 the user supplied (reusing/rephrasing the same 4 across checks is fine; inventing a 5th scenario not implied by the user is not).
- [ ] Two local-model prompt templates are produced (pre-send and post-receive), each generic enough to take a new request/response and this checklist as input.
- [ ] Calibration Notes section marks at least one check (plausibly the "is the instruction specific enough" type check) as LOW-CONFIDENCE/judgment-based, distinct from the two mechanical/structural checks (field-exists-in-model, tool-was-called).
- [ ] Output does not claim a specific catch-rate percentage anywhere.
- [ ] A line stating interceptor/middleware wiring is out of scope appears.

## Fail criteria (any one of these fails the scenario)

- Output writes or describes actual Claude Code hook/middleware code.
- Output invents a log file or specific line numbers/timestamps not provided by the user.
- Output gives a numeric "this will catch X% of bad calls" claim.
- Pre-send and post-receive checklists are generic/boilerplate (e.g., "check for clarity") with no connection to the Django/order-processing/signup examples actually given.
