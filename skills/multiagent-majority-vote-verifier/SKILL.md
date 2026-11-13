---
name: multiagent-majority-vote-verifier
description: Audits one already-completed multi-agent LLM ensemble vote by comparing the reasoning quality of the majority against the strongest minority dissent, not just the vote count, and recommends accept/overturn/escalate. Use when a team has N agents' answers + rationales from a majority-vote ensemble (code review, moderation, eval-judge panel) and wants a second opinion before trusting the majority.
---

# Majority Vote Second Opinion

## When to use this
The trigger moment: someone has already run a multi-agent LLM ensemble that reached a decision by majority vote — N agents independently produced an answer plus reasoning for a single judgment call (a code-review verdict, a content-moderation escalation call, an eval-judge panel score, a multi-agent classification decision) — and before they accept the majority answer as final, they want to know whether the majority's reasoning actually *supports* that answer or whether the agents just happened to agree. This is also the right tool for a post-mortem: a majority vote was accepted, it turned out wrong, and the team wants to check whether the reasoning traces already contained the tell.

This is a one-shot audit of a single completed vote — it does not run the ensemble, does not monitor a live pipeline, and does not replace a programmatic verification layer wired into production. It is the judgment a human would make by hand, done rigorously, for one contested decision at a time.

## Inputs
**Data source**: Manual — the user pastes, for each of the N agents in the ensemble: (1) that agent's final answer/label, and (2) that agent's full reasoning or rationale text (not just the label — this skill cannot do anything useful with labels alone). The user should also paste the question or task the ensemble was deciding. Ground truth is optional and only relevant for a retrospective audit of a decision that already played out.

If any agent's reasoning is missing, truncated to a single phrase, or clearly boilerplate (e.g., "This looks correct"), say so explicitly rather than guessing at reasoning that was never given.

## Procedure
1. **Parse the vote.** List all N (answer, reasoning) pairs. Group agents by identical or equivalent final answer. Identify the majority group (largest group) and every minority group. Report the exact margin (e.g., "3-of-5" vs "3-of-5-with-a-near-tie-at-2" — a bare plurality with no true majority is not the same as a clean majority, say which one this is).
2. **Assess the majority's reasoning**, independent of its vote count. For the majority group, read each agent's rationale and check:
   - Does each agent's stated reasoning, read on its own, actually lead to the stated answer — or does it merely restate the answer ("the answer is X because X is correct")?
   - Is the reasoning specific to this task's evidence, or generic/templated? A one-clause rationale with no concrete reference to the task's actual content (e.g., "doesn't look like it," "looks fine") carries effectively zero weight — note explicitly that such a vote contributed no substantive reasoning, so the real reasoning-based support for the majority may be narrower than its raw headcount suggests.
   - Does the reasoning assert a fact as given when it was never verified against the actual evidence in the task (e.g., assuming who or what something is, assuming a cited source says what it's claimed to say)? An unverified assumption stated confidently is a real reasoning flaw — note it even though it reads as "specific." On a wide, clean-margin vote this alone may not be decisive; on a narrow margin it should push toward escalation rather than confident acceptance.
   - **Correlated-error check**: do multiple majority agents cite the exact same fact, assumption, or premise as their chain of reasoning? If so, flag this explicitly — agreement built on one shared premise is not independent corroboration, it's one opinion counted multiple times. This is the single most important check this skill performs, because a raw vote count cannot see it.
3. **Assess every minority group's reasoning** on the same two criteria (does it support the answer, is it specific) plus a third: does it identify something concrete the majority's reasoning missed or got wrong (an edge case, a counterexample, a logical gap)? Reasoning that is merely "I disagree" with no concrete objection does not count as strong dissent, regardless of how confidently it's worded.
4. **Compare majority vs. strongest minority.** Rank minority groups by reasoning strength if there's more than one. Determine whether the single strongest minority rationale out-argues the majority's rationale — not whether it merely contradicts it.
5. **Decide a verdict**, using this policy:
   - **ACCEPT MAJORITY** — majority reasoning is specific, non-circular, and not built on a single shared flawed premise; no minority rationale identifies a concrete, substantiated flaw.
   - **OVERTURN TO MINORITY** — a minority rationale identifies a concrete, specific flaw or edge case in the majority's premise or logic that the majority reasoning does not address, and the minority's own reasoning is itself specific and sound (not just contrarian).
   - **ESCALATE TO HUMAN** — any of: reasoning on both sides is too thin to judge; the correlated-error check flags the majority as resting on one shared premise and no minority exists to counter it; the vote margin is a near-tie (on a small panel, treat any non-unanimous split as near-tie by default) *and* the majority's real reasoning-based support is weaker than its headcount — e.g., one or more "majority" votes contributed no substantive reasoning, or the decisive majority reasoning rests on an unverified assumption; or the decision is explicitly high-stakes and the case is genuinely close.
   When uncertain between two of these, escalate — this skill should never force false confidence onto a close call.
6. **Write the justification** as a tight paragraph that quotes or closely paraphrases the specific reasoning (majority and, if relevant, minority) that drove the verdict — never a generic statement like "the majority's reasoning was weak" without citing which part.

## Output format
Produce exactly this structure:

```
VOTE SUMMARY: <margin, e.g. "3-of-5 majority on 'approve'; minority of 2 on 'reject'">

MAJORITY REASONING ASSESSMENT: <2-4 sentences: specific/generic, circular or not, correlated-error flag yes/no and why>

MINORITY REASONING ASSESSMENT: <per minority group, same treatment; "none" if unanimous>

VERDICT: ACCEPT MAJORITY | OVERTURN TO MINORITY | ESCALATE TO HUMAN

CONFIDENCE IN THIS VERDICT: High | Medium | Low

JUSTIFICATION: <one paragraph, quoting the specific reasoning that drove the call>

RECOMMENDED NEXT ACTION: <e.g., "accept and ship," "route to minority's conclusion and flag the majority's shared premise for review," "send to a human reviewer with this summary attached">
```

## Guardrails
- Never fabricate or infer reasoning the user didn't paste. If an agent's rationale is missing or one sentence, say explicitly that there isn't enough to assess that agent and factor that into the confidence rating, don't silently pad it.
- Never equate vote count with reasoning strength. A 4-1 vote with a thin, circular majority rationale and one sharp, specific minority objection can still warrant OVERTURN TO MINORITY or ESCALATE — say so even though it will look like second-guessing a clear majority. Likewise, a "majority" vote where one or more of its members gave no substantive reasoning has less real support than its headcount implies — discount those votes explicitly rather than counting them at full weight.
- Always run the correlated-error check explicitly in every assessment, even when the majority reasoning looks fine on its face — this is the exact failure mode this skill exists to catch, and it is invisible to a vote count.
- Never deliver ACCEPT MAJORITY or OVERTURN TO MINORITY when the reasoning on the decisive side is too thin to support the call — escalate instead of forcing a confident-sounding answer.
- Do not present this as a live or automated verification layer. It is a one-time manual audit of a single pasted vote; say so if the user seems to expect it to monitor an ongoing pipeline.
- Do not use ground truth (if provided) to shortcut the reasoning assessment — assess the reasoning on its own merits first, and only use ground truth, if given, to label the final output as correct/incorrect in retrospect, not to pick the verdict.
