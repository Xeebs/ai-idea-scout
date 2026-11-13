# Majority Vote Second Opinion

A self-contained prompt template for auditing one already-completed multi-agent LLM ensemble vote. Paste this whole document (or just the "Prompt to use" section plus your data) into any AI chat tool — Claude, ChatGPT, Gemini, a local model — no Claude Code install or prior context required.

## What this is for

If you've built (or are reviewing) a multi-agent LLM ensemble that reaches decisions by majority vote — a code-review verdict, a content-moderation escalation call, an eval-judge panel scoring another model's output, any setup where N agents independently answer and the majority wins — this skill gives that vote a second opinion before you trust it. It doesn't re-run the ensemble. It reads the reasoning each agent gave (not just its final answer) and checks whether the majority's reasoning actually *supports* the majority's answer, or whether the agents just happened to land on the same conclusion for weak or circular reasons — in which case a well-argued minority might be right instead.

This is a one-shot audit of a single vote you paste in. It is not a live monitoring system and does not wire into your ensemble's code — it's the judgment call a careful human reviewer would make by hand, done rigorously, once, on demand.

## What you need to hand over

**Manual input required** — you paste this directly into the chat, nothing is fetched automatically:
1. The question or task the ensemble was deciding (one or two sentences).
2. For each of the N agents: its final answer/label, AND its full reasoning/rationale text. Labels alone are not enough — this skill cannot assess reasoning it was never given.
3. Optional: if you're doing a post-mortem on a decision that already played out, the ground truth / what actually turned out to be correct.

## Prompt to use

Paste this, followed immediately by your data in the format shown:

```
You are auditing one completed multi-agent LLM ensemble vote. I will give you
the task being decided and, for each agent, its final answer and its full
reasoning. Do NOT just count votes. Your job:

1. Group agents by answer. State the exact margin (e.g. "3-of-5" — and say
   explicitly if it's a bare plurality rather than a true majority, or a
   near-tie).
2. Assess the MAJORITY group's reasoning on its own merits: does each
   agent's rationale actually lead to its answer, or does it just restate
   the answer? Is it specific to the evidence in this task, or generic? A
   one-clause rationale with no concrete reference to the task's actual
   content ("doesn't look like it," "looks fine") carries effectively zero
   weight — note that the real reasoning-based support may be narrower than
   the raw headcount suggests. Also check whether any majority reasoning
   asserts a fact as given without verifying it against the task's actual
   evidence (e.g., assuming who or what something is) — flag unverified
   assumptions stated confidently as a real flaw, and weigh this more
   heavily when the vote margin is narrow.
   CRITICAL: check whether multiple majority agents are citing the exact
   same underlying fact, assumption, or premise as their reasoning. If so,
   flag it — that's one opinion counted multiple times, not independent
   corroboration, and a vote count alone can never see this.
3. Assess every MINORITY group's reasoning the same way, plus: does it
   identify a concrete, specific flaw or edge case the majority's reasoning
   missed? "I disagree" with no concrete objection does not count as strong
   dissent.
4. Compare the majority's reasoning against the single strongest minority
   rationale (not just whether they disagree, but which one actually
   argues better).
5. Give a verdict:
   - ACCEPT MAJORITY if its reasoning is specific, non-circular, and not
     resting on one shared flawed premise with no minority challenging it.
   - OVERTURN TO MINORITY if a minority rationale identifies a concrete
     flaw the majority missed, and the minority's own reasoning is itself
     specific and sound.
   - ESCALATE TO HUMAN if reasoning on the decisive side is too thin to
     judge, the vote is a near-tie (on a small panel, treat any
     non-unanimous split as near-tie by default) and the majority's real
     reasoning-based support is weaker than its headcount (a "majority"
     vote with no substantive reasoning, or resting on an unverified
     assumption), the majority rests on one shared premise with no
     minority to challenge it, or the call is genuinely close and
     high-stakes.
   If you're torn between two of these, escalate — don't force confidence
   onto a close call.
6. Justify the verdict in one paragraph, quoting or closely paraphrasing
   the specific reasoning (majority and minority) that drove it. Never say
   "the reasoning was weak" without citing which part.

Never invent reasoning I didn't give you. If an agent's rationale is one
word or missing, say so and factor it into your confidence rating instead
of padding it. Don't use any ground truth I give you to pick the verdict —
assess the reasoning on its own first, and only use ground truth afterward
to label the outcome correct/incorrect in retrospect.

Output in exactly this structure:

VOTE SUMMARY: ...
MAJORITY REASONING ASSESSMENT: ...
MINORITY REASONING ASSESSMENT: ...
VERDICT: ACCEPT MAJORITY | OVERTURN TO MINORITY | ESCALATE TO HUMAN
CONFIDENCE IN THIS VERDICT: High | Medium | Low
JUSTIFICATION: ...
RECOMMENDED NEXT ACTION: ...

---
TASK BEING DECIDED: <paste here>

AGENT 1 — Answer: <...>  Reasoning: <...>
AGENT 2 — Answer: <...>  Reasoning: <...>
AGENT 3 — Answer: <...>  Reasoning: <...>
[... one block per agent ...]

GROUND TRUTH (optional, retrospective only): <paste here or omit>
```

## What you'll get back

A structured report with: the exact vote margin; an assessment of whether the majority's reasoning actually holds up (including an explicit check for agents all leaning on the same shared assumption — the failure mode a raw vote count can't catch); an assessment of the strongest minority objection, if any; a clear verdict (accept the majority, overturn to the minority, or escalate to a human); a confidence level on that verdict; a one-paragraph justification quoting the actual reasoning; and a recommended next action.

## What this will not do

- It will not run your ensemble or call your agents for you — you must already have their answers and reasoning in hand.
- It will not replace an automated verification layer wired into a live pipeline — this is a manual, one-decision-at-a-time audit.
- It will not manufacture a confident verdict when the reasoning you provide is too thin — it will tell you to escalate instead, and that's the correct output in that case, not a failure.
- It will not treat a bigger vote count as inherently better reasoning — that distinction is the entire point of this skill.
