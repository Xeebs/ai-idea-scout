---
name: skill-admission-ablation-audit
description: Reviews a candidate agent skill (SKILL.md, system-prompt block, or tool-reference doc) against five bloat/lift failure signatures before it's added to a shared loadout or published, and returns a keep/delete/restructure verdict with per-factor rationale. Use when someone is about to add a new skill to a team's catalog, publish one to a marketplace, or prune an existing catalog that's grown token-expensive.
---

# Skill Admission Ablation Audit

## When to use this
Reach for this the moment someone is about to:
- Add a new skill/instruction-set to a shared Claude Code `skills/` directory, team CLAUDE.md, or internal tool catalog that every future agent invocation will load.
- Publish a skill to a marketplace (Agensi, claudemarketplaces.com, claude-plugins.dev, skills.sh) and wants a pre-publish sanity check.
- Audit an existing catalog that has grown large and suspect some entries are dead weight — pasted API tables, duplicated base-model capability, or skills nobody can prove ever helped.

This is a fast, one-shot heuristic review, not a live benchmark run. It is the quick gate you run before deciding whether a skill is even worth the time of building a full with/without ablation harness.

## Inputs
**Data source**: Manual — the user pastes (1) the candidate skill's full definition (its SKILL.md body, system-prompt block, or tool-reference content, in full — not a summary), (2) 2-3 representative task scenarios the skill is meant to help with, and (3) a note on how the base model currently performs on those same scenarios *without* the skill (what it got right, what it got wrong or had to be told, and roughly how long/how many turns it took). All three are required; this skill does not run code or fetch anything itself.

If scenario #3 (the no-skill baseline) is missing, stop and ask for it before producing a verdict — a lift judgment made with no baseline is a guess, not an audit, and must be labeled as such if the user insists on proceeding without one.

## Procedure
1. **Confirm inputs are complete.** If fewer than 2 scenarios or no baseline-behavior note is provided, ask for what's missing. If the user wants a verdict anyway, proceed but prefix the output with "LOW CONFIDENCE — insufficient scenario coverage."
2. **Run the candidate skill through five checks**, in this order, scoring each `PASS` (skill clears this concern) or `FLAG` (skill shows this failure signature):
   - **Capability duplication** — Strip away the skill's instructions and compare against the reported no-skill baseline. If the base model already produced the same outcome on the same scenarios without being told, this skill is teaching the model something it already knows. FLAG if ≥1 of the given scenarios shows identical success with no efficiency gain.
   - **Reference-dump density** — Estimate what fraction of the skill's content is a verbatim table/list (API signatures, parameter tables, enum values, URL lists) versus instructions/judgment/workflow. FLAG if the dump fraction is high (rough eyeball: more than half the content by line count) AND the scenarios don't show the model needing that exact verbatim data to avoid hallucinating it.
   - **Compact operational habit** — Look for content that encodes a workflow step, ordering constraint, verification check, or gotcha the model would not reliably do unprompted (e.g., "always check X before Y", "never do Z because it silently corrupts W"). PASS if present and the baseline scenarios show the model skipping or getting this wrong without the skill.
   - **Router viability** — Ask whether a one-line pointer ("if task matches X, load skill Y's full content") would perform as well as loading the full skill body on every invocation. FLAG if the skill is rarely relevant to most tasks but is large enough to cost meaningful context when loaded upfront regardless of relevance.
   - **Net efficiency tradeoff** — Weigh the measured or reported benefit (did it change the outcome, not just the process) against the token/context cost of including it in every future invocation of whatever catalog it joins.
3. **Produce the verdict.** Combine the five checks:
   - **DELETE** — Capability duplication FLAGs on most/all scenarios, or reference-dump FLAGs with no evidence of needed precision, and no compact operational habit found.
   - **KEEP** — Compact operational habit PASSes, capability duplication PASSes (model genuinely couldn't do this without the skill), and the efficiency tradeoff favors inclusion.
   - **RESTRUCTURE-TO-ROUTER** — The content is genuinely useful (no duplication FLAG) but is reference-heavy or rarely triggered — recommend converting to a short pointer entry that loads the full body only on match, rather than deleting it outright.
4. **Write one line of rationale per factor**, naming the specific scenario or content excerpt that drove the call — never a generic restatement of the rule.
5. **State the confidence boundary explicitly**: this review is based on the scenarios and baseline the user supplied, not an executed test. Recommend an actual with/without trial run (same scenarios, same model, twice) before a high-stakes catalog-wide decision, especially if the verdict is DELETE for a widely-used skill.

## Output format
```
## Skill Admission Audit: <skill name>

**Verdict: KEEP | DELETE | RESTRUCTURE-TO-ROUTER**
(LOW CONFIDENCE flag here if scenario coverage was thin)

| Check | Result | Rationale |
|---|---|---|
| Capability duplication | PASS/FLAG | <one line, cites the scenario> |
| Reference-dump density | PASS/FLAG | <one line, cites what fraction and why> |
| Compact operational habit | PASS/FLAG | <one line, cites the habit or its absence> |
| Router viability | PASS/FLAG | <one line> |
| Net efficiency tradeoff | favors keep/delete | <one line, token cost vs benefit> |

**Recommendation**: <2-3 sentences — what to actually do, including a suggested router-entry rewrite if RESTRUCTURE>
**Confidence note**: <state this was a heuristic review of supplied scenarios, not a live ablation run; name the follow-up test if the stakes warrant it>
```

## Guardrails
- Never fabricate or imply a live test was run. Every verdict in this skill is a heuristic read of what the user pasted — say so, every time, in the confidence note.
- Never issue a DELETE verdict on reference-dump density alone when the user's scenarios show the model hallucinating or getting exact values wrong without the skill — that's a case for KEEP or RESTRUCTURE, not DELETE, regardless of how table-heavy the content looks.
- Never score "compact operational habit" as PASS just because the skill *claims* to encode a habit in its own prose — only count it if the supplied no-skill baseline scenario actually shows the model failing that habit without the skill present.
- Never let skill length alone drive the verdict. Short skills can be pure duplication; long skills can be dense and earn their keep. The checks are about behavior change, not word count.
- Never proceed to a confident verdict with zero baseline-behavior information — ask for it first, or clearly label the output LOW CONFIDENCE if the user insists on skipping that step.
- This is not a substitute for the full ablation harness (running the same scenarios twice, with/without, against a real agent framework, repeated for noise). Say so whenever the stakes are a shared catalog many people depend on, not just one person's personal skill folder.
