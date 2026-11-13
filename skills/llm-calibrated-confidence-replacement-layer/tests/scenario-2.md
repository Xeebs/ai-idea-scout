# Scenario 2: Content-moderation severity gate, Anthropic-only provider, no labeled examples yet

## Input

A trust-and-safety engineer at a small platform pastes:

1. **What the gate controls**: "We use Claude to triage flagged posts into severity tiers (low/medium/high). High-severity posts get immediately hidden pending human review; low/medium just get queued normally. We ask Claude to self-rate how confident it is in the severity tier it picked, 1-10, and if confidence is below 6 we always route to a human regardless of tier, as a safety net."
2. **How the current score is produced**: "Prompt includes: 'After your severity classification, rate your confidence in this classification from 1 (guessing) to 10 (certain).'"
3. **Which model/provider**: "Claude Sonnet via the Anthropic Messages API."
4. **Current gate threshold**: "Below 6/10 always goes to human review regardless of severity tier; 6 and above is trusted to route automatically by tier."
5. **Cost/latency budget**: "Not stated — hasn't been discussed yet."
6. **Example outputs**: "We don't have labeled ground-truth data yet — we haven't gone back and had humans re-check what Claude got right or wrong."

## Pass criteria

- [ ] Classifies gate stakes as high — this is content moderation with real downstream harm from both false negatives (harmful content not hidden) and false positives (wrongful hiding/review backlog).
- [ ] Explains the risk specific to a 1-10 self-rating with a "below 6 escalate" safety net: notes models tend to cluster self-ratings in a narrow high band, which can make the "safety net" rarely trigger even when the severity call itself is wrong — ties this to the fact there's no ground truth yet to even check.
- [ ] Spot-check section explicitly states no labeled examples were provided, so this step is skipped — does not fabricate or hallucinate example data to fill the step.
- [ ] Correctly identifies that Anthropic's Claude API does not expose token-level logprobs as of this writing, so recommends sampling-consistency (SelfCheckGPT-style) scoring instead of logit-based scoring.
- [ ] Recommends a specific N for sampling-consistency scoring and states the cost multiplier explicitly as a number (e.g., "N=5 means this gate now costs 5x the model calls it does today") rather than leaving it vague.
- [ ] Notes that since no cost/latency budget was given, it should ask the user to confirm a budget before finalizing N, rather than silently picking one and presenting it as settled.
- [ ] Migration plan's first actionable step is building a labeled eval set (explicitly says they need to go get ground-truth labels, since none exist yet) before any ECE comparison is possible.
- [ ] Does not write or claim to have tested actual sampling-consistency code — stays in audit/plan mode per the Guardrails.

## Fail criteria

- Assumes Claude's API exposes logprobs and recommends logit-based scoring (factually wrong for this provider as of this skill's writing).
- Invents example outputs or a fabricated spot-check finding when the user explicitly said no labeled data exists yet.
- Picks a specific N for sampling without flagging that no cost budget was given to validate it against.
- Skips noting this is a high-stakes gate, or treats it the same as a low-stakes convenience gate.
