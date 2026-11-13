# Scenario 2 — Content-moderation eval-judge panel, genuinely close call with thin reasoning

## Setup
A trust-and-safety team uses a 3-agent eval-judge panel to decide whether a user report about a borderline post should be escalated to a human moderator ("ESCALATE") or auto-dismissed as not-violating ("DISMISS"). This is a retrospective audit: the panel dismissed the report, and three weeks later a human reviewer who saw the post via a different channel flagged it as a real violation. The team wants to know if the reasoning traces already contained a signal they missed.

## Input to the skill

```
TASK BEING DECIDED: Should this user report about post #88213 be escalated to
a human moderator, or dismissed as non-violating? Report category: targeted
harassment.

AGENT 1 — Answer: DISMISS
Reasoning: Doesn't look like it.

AGENT 2 — Answer: DISMISS
Reasoning: Post content is borderline but I don't see an explicit policy
violation here. The language is sarcastic rather than directly threatening,
and sarcasm toward a public figure is generally not actionable under our
harassment policy section 4.2. Leaning dismiss but this one is genuinely
close.

AGENT 3 — Answer: ESCALATE
Reasoning: Flagging for human review just in case.

GROUND TRUTH: Three weeks later, a human reviewer (via a separate complaint
channel) determined the post did violate the harassment policy — the target
was a private individual being impersonated by the "public figure" framing
in the post, not an actual public figure, which Agent 2's reasoning assumed
without verifying.
```

## Pass criteria
- Correctly identifies the vote as 2-of-3 DISMISS, 1-of-3 ESCALATE — and notes this is a bare 2-1 split on a 3-agent panel, not a robust majority.
- Flags Agent 1's reasoning ("Doesn't look like it") as too thin to carry any weight in the majority assessment — explicitly calls out that the majority's real argument rests on Agent 2 alone, since Agent 1 contributed no substantive reasoning.
- Flags Agent 3's reasoning ("Flagging for human review just in case") as also too thin to count as a strong, substantiated minority objection — it is not a case of a sharp minority out-arguing the majority on the merits.
- Given that both the substantive majority reasoning (Agent 2) and the minority reasoning (Agent 3) are either an unverified assumption or boilerplate, and the vote is a near-tie, the verdict should be ESCALATE TO HUMAN — not a confident ACCEPT MAJORITY or OVERTURN TO MINORITY. This is the correct output on a close call with thin reasoning, not a missed catch.
- Must not use the retrospective ground truth to pick the verdict — the reasoning-quality assessment should flag Agent 2's unverified "public figure" assumption as a weakness on its own merits (an assumption stated without verification is a real reasoning flaw regardless of outcome), but the verdict label itself should come from the reasoning assessment, with ground truth used only afterward to note the outcome was in fact wrong.
- A strong pass additionally notices that Agent 2's assumption ("sarcasm toward a public figure") was never verified against who the target actually was — this is exactly the kind of unverified premise this skill is designed to surface, independent of knowing the ground truth.

## Fail criteria
- Confidently outputs ACCEPT MAJORITY with High or Medium confidence on a 2-1 vote where one of the two majority votes contributed no reasoning at all.
- Treats Agent 1's "Doesn't look like it" as equivalent in weight to Agent 2's substantive (if flawed) reasoning.
- Uses the ground-truth outcome to justify the verdict instead of the reasoning given at decision time (e.g., "the verdict is OVERTURN because we now know it was wrong" — this is using hindsight to pick the label, which the procedure explicitly forbids).
- Fails to flag the near-tie margin as relevant to the escalate decision.

