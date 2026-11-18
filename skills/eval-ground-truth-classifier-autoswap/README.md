# Distillation Candidate Assessor

A paste-into-any-AI-chat-tool prompt that tells you, with a specific GO / CAUTION / NO-GO call, whether a particular LLM-as-judge evaluation task in your eval pipeline is actually worth distilling into a cheap trained classifier — before you spend engineering time building, training, and monitoring one.

## Why this exists

If you run evals through promptfoo, deepeval, Langfuse, or a custom harness, you're probably paying full frontier-model price every time an LLM judge scores a task — even narrow, closed-form tasks like "is this message a policy violation" or "did extraction pull the right field," where a small trained classifier could match judge quality at a fraction of the cost (Airbnb's own published benchmark on this pattern cites roughly 1% of the cost). But not every task is a good candidate: some lack real ground truth, some are too subjective to ever be "correct" in a way a classifier could learn, and jumping straight to training without checking either of those first wastes the engineering investment. This prompt does that check for one task in one pass.

## What to hand it

**Data source: Connected.** The strongest way to use this is to export your eval harness's historical judge-call data for the specific task you're evaluating — promptfoo's `eval_results.json` (or `--output` JSON export), deepeval's test-run export, or a Langfuse trace export (CSV or JSON) covering that task's judge-call traces — and paste or upload that export directly into the chat. These export formats already exist in each tool today; you don't need to build anything to produce them.

If you don't have an export handy, paste these three things manually instead:
1. The exact judge prompt/rubric you use for this task.
2. 15–30 example (input, frontier-judge-verdict) pairs, pasted verbatim.
3. A plain statement of whether ground truth exists for this task at all — human-reviewed labels, a deterministic ground-truth source (e.g., a database field that's definitively correct), or nothing beyond the judge's own verdicts.

## The prompt

Paste this into Claude, ChatGPT, or any capable chat tool, followed by your exported data or the three manual inputs above:

```
You are assessing whether a specific LLM-as-judge evaluation task is a good
candidate to distill into a small trained classifier, to replace an expensive
frontier-model judge call with a cheap classifier call for this one task.

I will give you either an eval-harness export (promptfoo/deepeval/Langfuse) or
three manual inputs: the judge prompt/rubric, 15-30 example (input, verdict)
pairs, and a statement of whether ground truth exists.

Do the following, in order:

1. Parse what I gave you: verdict type (binary/categorical/scalar), the
   approximate example count, and the class/score distribution if countable.

2. Classify ground-truth availability into exactly one tier:
   - TRUE: labels come from human review, a deterministic check, or any
     source independent of the judge being distilled.
   - PROXY: the only "ground truth" is the frontier judge's own verdicts.
   - NONE: fewer than ~15 usable examples, or no verdicts recorded.

3. Classify task shape as closed-form (binary/categorical/narrow-numeric
   verdict against a stable, largely objective rubric) or open-ended/
   subjective (quality, helpfulness, tone, creativity — anything where two
   careful human reviewers would reasonably disagree by more than a small
   margin).

4. If the verdict is binary/categorical, compute the minority-class share.
   Flag it if below 10% - that changes the math in step 5.

5. Compute the gold-set size needed to validate safely using
   n = z^2 * p(1-p) / e^2 at 95% confidence (z=1.96). Report n for a
   conservative p=0.5 at two margins: within 5 points (e=0.05) and within
   2 points (e=0.02). If the class is imbalanced, state that the minority
   class needs its own stratified sample of that size - a flat random
   sample won't contain enough minority examples to validate against.

6. Render a verdict using this decision table, first matching row wins:
   - Open-ended/subjective task -> NO-GO, regardless of everything else.
   - Ground truth is NONE -> NO-GO.
   - Ground truth is PROXY only -> CAUTION (closed-form tasks only).
   - Ground truth is TRUE, closed-form, and example count >= the step-5
     minimum at the 5-point margin -> GO.
   - Ground truth is TRUE, closed-form, but example count below that
     minimum -> CAUTION (collect more labeled examples first).

7. If GO or CAUTION: sketch 3-5 concrete features/signals a classifier for
   this task would plausibly need (derived from what the input actually
   contains - not a generic "use embeddings"), restate the gold-set size,
   and give a one-line drift-monitoring recommendation (what production
   signal would show the classifier drifting, and how many evaluation runs
   of lag is tolerable before checking).

8. If NO-GO: state the single blocking reason in plain terms and exactly
   what would need to change to revisit this.

Output format, always in this order:

## Distillation Verdict: GO | CAUTION | NO-GO
**Task**: <one-line description>
**Ground-truth tier**: TRUE | PROXY | NONE
**Task shape**: closed-form | open-ended/subjective
**Sample observed**: <n rows>, class split <x%/y%> (if applicable)

### Reasoning
- <bullet tied to ground-truth tier>
- <bullet tied to task shape>
- <bullet tied to volume/class balance>

### Gold-set size needed
- At 5-point margin (e=0.05): n = <number>
- At 2-point margin (e=0.02): n = <number>
- <stratification note if minority class <10%>

### If GO/CAUTION - classifier sketch
- Features/signals: <3-5 concrete items>
- Validation threshold: within 2 points of F1/accuracy vs. the frontier
  judge on a held-out gold set before swap-in
- Drift watch: <one line>

### If NO-GO - blocker
- <single plain-language reason and what would change it>

Guardrails you must follow:
- Never say GO when ground truth is PROXY-only, no matter the volume -
  a classifier trained on the judge's own verdicts can at best match that
  judge's accuracy and inherits its biases. Cap at CAUTION.
- Never say GO or CAUTION for an open-ended/subjective task regardless of
  sample size.
- Never state a gold-set number without showing the formula and the
  numbers you plugged in.
- Never ignore class imbalance in the sample-size math.
- Never assume a verdict transfers to a different team's or rubric's
  version of a task with the same name - re-run this for each one.
- This is a one-shot design judgment only, not a trained classifier, not
  a production shim, and not a drift monitor - say so if asked to build
  those next.

Here is my data:
<paste export or manual inputs here>
```

## What you get back

A short structured report: a GO/CAUTION/NO-GO verdict, why (tied to ground-truth tier, task shape, and sample volume), the exact math behind how much labeled data you'd need to validate a classifier safely, and — if the answer isn't NO-GO — a concrete starting sketch of what a classifier for this task would look like and how you'd watch it for drift once live. If the answer is NO-GO, you get one plain-language reason and what would have to change before it's worth revisiting.

## What this doesn't do

This is the decision step, not the build. It will not train a classifier, wire it in behind your judge-call interface, or run a live drift monitor for you — those require persistent infrastructure (a trained model artifact, a running monitor) that a one-shot chat prompt can't provide. Use this to decide *whether* that infrastructure investment is worth making for a given task before you build it.
