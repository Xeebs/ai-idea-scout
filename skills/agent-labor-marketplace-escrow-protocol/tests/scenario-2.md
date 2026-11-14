# Scenario 2: Content-review agent, no price set, deliverable is a judgment call

## Input (what the user pastes)

> My agent reviews draft blog posts for a client and gives a "ready to publish" verdict plus a rewritten version if it's not ready. It checks things like tone consistency with the brand voice, whether the argument actually holds together, and whether it'll land with the target audience — basically an editorial judgment call, not something with a hard checklist. I haven't charged for this before, it's been a favor for a friend's startup so far. Takes me (the agent) about 10 minutes per post. I don't have a clean example to share, just trust me it works. Honestly I've had two cases where the friend disagreed with my "ready to publish" call and we just argued about it over Slack.

## Expected output characteristics

- **Deliverable type** classified as "judgment call" — this is the explicit test that the skill doesn't force this into a fake schema.
- **Price** marked `[NEEDS SELLER CONFIRMATION]` since the seller gave no number and no cost-basis figures beyond a time estimate that alone isn't enough to derive a dollar price — acceptable for the drafter to attempt a cost-basis estimate from the 10-minute figure IF it states an assumption (e.g. an hourly rate) but it must still flag the number as needing confirmation since no rate was given.
- **Deliverable spec** covers both outputs mentioned: the ready/not-ready verdict and the rewritten version when not ready — should not invent a schema/JSON shape that the seller never described, since this is prose/document output, not structured data.
- **Acceptance criteria**: the core "is it ready to publish" and "does the tone match brand voice" criteria MUST be flagged `[NOT MACHINE-CHECKABLE — requires human/AI-judge review]` since the seller explicitly described this as a judgment call with a history of disagreement — this is the critical test. A small number of criteria (deliverable arrived within stated turnaround, a rewritten version was actually included when verdict is "not ready") can legitimately be machine-checkable.
- **Escalation** note should reference the past disagreement pattern implicitly by routing disputed/judgment items to human review before fund release — must not claim an automated check can settle a "ready to publish" disagreement.
- **Open items** should flag: missing example deliverable, unconfirmed price, and should note the past-dispute history as a reason the acceptance criteria need the human-review escalation path (this is exactly the kind of gap the Procedure step 7/Open Items section exists to surface).
- Given the lack of a concrete example, the skill may reasonably ask one clarifying question instead of drafting blind — either behavior (asking, or drafting with explicit flagged assumptions) is acceptable, but silently fabricating a confident, fully-specified listing as if this were an easy structured case is not.

## Pass criteria
- [ ] Deliverable type correctly identified as judgment-call, not forced into a fake JSON schema.
- [ ] Price is marked unconfirmed (or the skill asks a clarifying question about rate) rather than inventing a confident dollar figure.
- [ ] At least the core "ready to publish" / tone-match criteria are explicitly tagged `[NOT MACHINE-CHECKABLE]`.
- [ ] Escalation section explicitly avoids implying an automated check resolves the exact kind of disagreement the seller already had.
- [ ] Open items section surfaces the missing example and the unconfirmed price; doesn't claim "None — ready as drafted" for a case this underspecified.

## Fail conditions
- Every acceptance criterion presented as machine-checkable despite the seller explicitly describing this as a judgment call with a real dispute history — this would mean the listing looks enforceable but isn't, which is the exact failure mode SKILL.md's guardrails exist to prevent.
- A confident specific price is produced with no flag, with no rate given by the seller.
- "Open Items" claims the listing is fully ready despite missing an example and a confirmed price.
