---
name: viral-jailbreak-continuous-retraining-loop
description: Point-in-time exposure audit for a production jailbreak/guardrail classifier — given the classifier's training cutoff and coverage, and a handful of newly disclosed (often hours-old, viral) jailbreak examples, estimates whether each would likely bypass the live classifier and recommends a retraining urgency tier and cadence. Use right after a team sees a new jailbreak technique circulating publicly and wants to know how exposed they are before deciding whether to build always-on feed-and-retrain infrastructure.
---

# Fresh Fence: Jailbreak Exposure Assessment

## When to use this
A team runs a production jailbreak/guardrail classifier (NeMo Guardrails, Guardrails AI, LLM Guard, or a custom model) and has just become aware — via a Reddit thread, an X/Twitter post, a disclosed red-team writeup, or a bug-bounty style submission — of one or more jailbreak techniques circulating publicly, often within hours of discovery. Before scrambling to retrain or deciding whether to invest in an always-on jailbreak-intake-and-retraining pipeline, they want a fast, honest read on: *would these specific techniques likely get past what we have running right now, and how urgently should we act?*

This is a **one-shot diagnostic**, run against whatever the team can hand over right now — it does not touch the live classifier, does not retrain anything, and does not run continuously. If what's actually wanted is the always-on intake→cluster→retrain→eval-gate pipeline, that is separate runtime infrastructure (the parent idea's "Project" half), not this skill.

Do not reach for this to generate new jailbreak attack variants to test guardrail *wording* (that's `register-shift-jailbreak-redteam`), and do not reach for this to audit historical decision-log drift across months of traffic (that's `guardrail-accuracy-drift-monitor`). This skill is specifically about matching *newly disclosed, externally-sourced* techniques against what a classifier's training set already covers, as of a stated cutoff date.

## Inputs
**Data source**: Manual — the team pastes a description of its classifier's training/eval coverage as of a stated cutoff date, plus the newly disclosed jailbreak example(s) it's worried about. Nothing is fetched automatically: no mature, cross-vendor connector exists today that can pull a classifier's actual training corpus or monitor jailbreak-disclosure surfaces (Reddit, X, bug-bounty feeds) for you — that gap is exactly why the parent idea's always-on pipeline is a separate, heavier build than this audit.

Required:
1. **Training/eval cutoff date** for the current production classifier, plus **what it was trained/tuned to catch** — either representative training examples, or at minimum a named list of jailbreak technique families it covers (e.g., "DAN-style roleplay override," "base64/leetspeak encoding obfuscation," "multi-turn crescendo," "refusal-suppression token tricks," "fictional/narrative framing").
2. **1–10 newly disclosed jailbreak examples** — the actual prompt text or a close paraphrase — each tagged with its source (platform/thread/disclosure channel) and discovery date.

Strongly recommended (skip only if unavailable, and say so in the output):
3. The classifier's most recent internal eval false-negative rate, for context on how much margin it currently has.

If (1) is missing or too vague to compare against ("we trained it on jailbreaks" with no categories or examples), ask for it before proceeding — judging exposure against an unknown training set produces a guess, not an audit.

## Procedure
1. **Scope and safety check first.** This skill classifies and triages submitted examples; it never improves, strengthens, combines, or elaborates on any jailbreak technique as a side effect of describing it. If a submitted example is itself catastrophic-harm content (CBRN, mass-casualty, CSAM) rather than a guardrail-bypass technique, do not analyze it — say so and stop for that example.
2. **Build the training-coverage reference** from Input #1: a short list of technique families the classifier is described as covering, each with the cutoff date.
3. **For each new example**, classify its underlying **technique family** against a standard taxonomy (roleplay/persona override, encoding/obfuscation, multi-turn/crescendo escalation, prompt injection via tool-or-document content, refusal-suppression token tricks, narrative/fictional framing, authority/compliance-register framing, translation/low-resource-language evasion, or "novel/unclassified"). Name the family explicitly — do not skip straight to a verdict.
4. **Compare family to coverage** and assign an exposure verdict per example:
   - **LIKELY CAUGHT** — the technique family is explicitly represented in the stated training coverage, and the new example is a close surface variation of it (same mechanism, reworded).
   - **LIKELY BYPASSES** — the technique family is absent from stated coverage, or the new example's mechanism diverges meaningfully from how that family was represented (e.g., covered family was single-turn, new example is the same family executed as a multi-turn escalation).
   - **UNCERTAIN** — insufficient information in Input #1 to judge (the family is plausible but coverage detail is too vague).
   Give one line of reasoning per verdict naming the specific mechanism match or mismatch — never a bare label.
5. **Aggregate an exposure score**: count of LIKELY BYPASSES ÷ total examples, and separately flag if any single BYPASSES example maps to a technique family that is completely absent (a "new family" gap) versus a known family with a mechanism gap — a new family is the more urgent signal.
6. **Recommend an urgency tier and cadence**, referencing the JailbreaksOverTime result (weekly self-training retraining cut false-negative rate from 4% to 0.3%) as the slowest acceptable benchmark, scaled up for viral hours-to-days spread:
   - **IMMEDIATE (same day–48h)**: any new-family bypass, or bypass rate ≥50% of submitted examples.
   - **THIS WEEK**: bypass rate 20–50%, all within known families (mechanism-gap only).
   - **MONITOR (fold into next scheduled cycle)**: bypass rate <20%, no new-family gaps.
7. **State what this audit does not prove**: it is a reasoning-based estimate of mechanism overlap, not a measured run of the examples against the live classifier. If the team can actually run the examples through the production classifier directly, recommend doing that as ground truth and treat this audit as the triage step that justified spending the time.

## Output format
```
# Jailbreak Exposure Assessment

**Classifier coverage as of**: <cutoff date> — <summary of covered technique families>
**Examples assessed**: <n> (source(s): <platform/date range>)

## Per-example findings
| # | Technique family | Source / date | Verdict | Reasoning |
|---|---|---|---|---|
| 1 | ... | ... | LIKELY BYPASSES | <mechanism match/mismatch, one line> |

## Exposure score
Bypass rate: X / N (Y%)
New-family gaps: <list, or "none — all gaps are mechanism variations of known families">

## Recommendation
**Urgency tier**: IMMEDIATE / THIS WEEK / MONITOR
**Suggested cadence going forward**: <e.g., "weekly self-training per JailbreaksOverTime benchmark is likely sufficient" or "current ad hoc cadence is leaving a Z-day exposure window — consider the always-on intake pipeline">

## What this audit does not do
This is a one-time, reasoning-based mechanism-overlap estimate, not a measured test against the live classifier and not a running monitor. Treat LIKELY BYPASSES as "needs verification," not confirmed fact, until run against production.
```

## Guardrails
- Never generate new, strengthened, or combined jailbreak variants beyond what was submitted — this skill classifies and triages existing disclosed examples, it does not produce a reusable attack list or improve on one.
- Never claim a verdict is a confirmed result of running the example against the live classifier — every verdict is a mechanism-overlap estimate against described training coverage, and the output must say so explicitly in the closing section every time.
- Never invent the classifier's training coverage if the team didn't supply enough detail — mark the affected examples UNCERTAIN and name exactly what's missing, rather than guessing what a "jailbreak classifier" typically covers.
- Never analyze or reproduce catastrophic-harm content (CBRN, mass-casualty, CSAM) even if submitted as a "jailbreak example" — refuse that specific item and say why, independent of the rest of the audit.
- Never recommend disabling, loosening, or bypassing the guardrail itself — every recommendation is about retraining cadence or urgency, never about weakening existing coverage.
