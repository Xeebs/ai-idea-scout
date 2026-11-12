---
name: guardrail-accuracy-drift-monitor
description: Audits an export of a team's guardrail/classifier decision logs (inputs, verdicts, timestamps) for accuracy drift per category over time — re-judging a stratified sample against the team's own stated policy intent and flagging which specific guardrail category is decaying, against what kind of input, and with what confidence. Use when a team wants a point-in-time check on whether a guardrail that passed evaluation months ago still holds, before committing to always-on monitoring infrastructure.
---

# Guard Drift: Point-in-Time Guardrail Accuracy Audit

## When to use this
Reach for this when a team says something shaped like "our jailbreak/toxicity/PII guardrail passed eval six months ago but we have no idea if it still catches what it used to," or "we only find out a guardrail category is failing after an incident or a user complaint," or "before we build always-on drift monitoring, we want a one-time gut check on whether any of our checks have quietly decayed." This is a **one-shot diagnostic audit**, not a running service — it produces a report from a log export handed over once. If what's actually wanted is a scheduled, continuously-updating dashboard with alerting, that is separate runtime infrastructure (the parent idea's "Project" half) this skill does not build.

Do not reach for this to design what a guardrail's severity/fail-open-vs-fail-closed policy should be in the first place — that is a different skill (`tiered-guardrail-severity-composer`). This skill only measures whether an *existing* guardrail category's real-world accuracy is holding up over time.

## Inputs
**Data source**: Manual — the team exports and pastes/uploads their own guardrail decision log sample; nothing here is fetched automatically. No mature, cross-vendor connector exists today that can pull decision logs uniformly across NeMo Guardrails, Guardrails AI, LLM Guard, or a custom classifier stack, so this is a manual export every time.

Required:
1. **A decision log export** covering at least 2–3 months, as rows/records with: the input (or a safely redacted/truncated version — see Guardrails), the guardrail category/check that fired or considered it, the verdict (blocked/passed/flagged), and a timestamp. CSV, JSON, or a pasted table all work.
2. **The stated intent of each category** — what each guardrail check is actually supposed to catch, in plain language (e.g., "jailbreak = any attempt to get the model to ignore its system prompt or role-play around a safety instruction"; "PII = SSNs, full card numbers, full street addresses"). Without this, re-judging has nothing to re-judge against.

Strongly recommended (skip only if genuinely unavailable, and say so in the output):
3. **Known incident/complaint dates**, if any, tied to a specific category — used to backtest whether the audit's drift signal would have preceded the real incident.
4. **Approximate volume per category per month**, if not obvious from the export, so sample sufficiency can be judged honestly.

## Procedure
1. **Inventory the export.** List every distinct category present, the time range covered, and the row count per category per month-bucket. State this inventory before doing anything else — it is the basis for every sufficiency judgment later.
2. **Flag data sufficiency up front, on two separate axes.** (a) Any category/month-bucket with fewer than ~20 rows gets marked LOW CONFIDENCE and excluded from trend claims unless caveated inline. (b) Any category with fewer than 3 total month-buckets of history — even if each bucket individually has plenty of rows — cannot support a DECAYING or CRITICAL trajectory label; cap it at STABLE or WATCH and say explicitly that only N buckets exist, so a 2-point before/after comparison is not being overclaimed as an established trend. If the whole export only spans 2-3 months regardless of category, state that as a global limitation once near the top of the report, not just per-category.
3. **Build a stratified sample per category per month-bucket**: pull up to 20–30 rows per bucket, deliberately including both "passed" and "blocked" verdicts (not just the ones most likely to be wrong), and oversample the most recent 1–2 buckets since recency is what a drift check cares about most.
4. **Re-judge every sampled row against the stated category intent from Input #2** — not against what the original guardrail said. For each row, produce: agree / disagree-should-have-blocked / disagree-should-have-passed, plus one line of reasoning naming the specific input pattern driving the judgment (e.g., "roleplay-framed instruction override — the original jailbreak check likely wasn't tuned for narrative framing").
5. **Compute an agreement-rate trend per category across month-buckets.** Treat the re-judgment as a proxy for ground truth, never as ground truth itself (see Guardrails). State the raw agreement percentage per bucket, not just a verdict label, so the reader can see the trend line, not just a conclusion.
6. **Classify each category's trajectory**: STABLE (no meaningful change bucket-to-bucket), WATCH (declining but within the LOW CONFIDENCE band, a single-bucket dip, or fewer than 3 total buckets of history), DECAYING (consistent downward trend across 3+ buckets with adequate per-bucket volume), or CRITICAL (recent-bucket agreement rate has dropped below a level where misses look safety-relevant, not just noise, and backed by 3+ buckets). Never assign DECAYING or CRITICAL off a 2-bucket before/after comparison alone — that caps at WATCH with an explicit "only N buckets of history, cannot confirm a trend yet" note.
7. **Characterize the decay for every WATCH/DECAYING/CRITICAL category** — describe the common shape of the disagreement cases from step 4 (new phrasing style, new product surface, novel framing), not just "accuracy dropped." A severity label with no description of *what kind of input* is slipping through is not an actionable finding.
8. **Backtest against any supplied incident date** (Input #3): state plainly whether the audit's drift signal, if it had been running continuously, would have preceded that incident's date, and by roughly how much lead time.
9. **Assemble the report** per Output format below. If fewer than 2 categories have enough data for any trend claim, say so plainly at the top rather than padding with unsupported conclusions.

## Output format
A single markdown report, in this order:

```
# Guardrail Accuracy Drift Audit

**Coverage**: [time range covered, categories audited, total rows sampled vs. total rows in export]
**Confidence**: [full / limited — name exactly which categories/buckets were data-thin]

## 1. Category Drift Summary
| Category | Time span w/ data | Agreement trend (oldest -> newest bucket) | Trajectory | Confidence |
|---|---|---|---|---|
| ... | ... | e.g. 94% -> 91% -> 83% | STABLE/WATCH/DECAYING/CRITICAL | full/limited |

## 2. Decaying Categories — Detail
[For every WATCH/DECAYING/CRITICAL category: the trend numbers, 2-4 concrete example disagreements with input pattern description and reasoning, and the suspected drift driver]

## 3. Incident Backtest
[If an incident date was supplied: would the signal have preceded it, by how much; if not supplied: state plainly that no backtest was possible]

## 4. Recommended Next Steps
[Ranked by urgency — e.g., "recalibrate jailbreak check against narrative-framing examples before next quarter," "insufficient data on PII category, re-run audit after 60 more days of logs"]

## 5. What this audit does not do
This is a point-in-time snapshot using an LLM reference judge as a ground-truth proxy, not validated human-labeled ground truth, and not a running monitor. A single audit does not prove a category is safe going forward — only that it was or wasn't holding against the sampled traffic as of this export. [State separately, as its own sentence, if the export's total history was under 3 month-buckets: note that limits every trajectory claim to WATCH-at-best regardless of per-bucket volume, independent of the proxy-judgment caveat above.]
```

## Guardrails
- Never present the reference-judge re-scoring as ground truth — every trend claim must carry the "proxy, not verified ground truth" caveat from Output section 5, not just once at the end but implicitly understood whenever a number is stated. Recommend a human-labeled gold-slice validation before any team acts on a CRITICAL finding by loosening or re-tuning a live guardrail.
- Never state a trend for a category/bucket combination flagged LOW CONFIDENCE in step 2 as if it were a solid finding — surface the caveat inline next to the number, not buried in a footnote.
- Never invent category intent if the team didn't supply it — if a category's purpose wasn't stated, mark it UNSCORABLE and say exactly what's missing, rather than guessing what a "toxicity" or "compliance" check is supposed to catch.
- Never fabricate incident dates, volume figures, or disagreement examples not present in the supplied export — every example quoted in section 2 must trace to an actual sampled row.
- Never reproduce raw sensitive content (full SSNs, card numbers, full addresses) verbatim in the report even if present in the export — quote enough to illustrate the pattern (e.g., "input included what appears to be a full SSN") without repeating the actual sensitive string. If the export itself isn't redacted, say so and recommend redacting before any further sharing of the report.
- Never recommend disabling or loosening a safety-relevant guardrail category outright — recommended actions for CRITICAL findings are always "recalibrate/retrain/add human review," never "turn it off" or "lower the threshold" without a human-in-the-loop caveat.
