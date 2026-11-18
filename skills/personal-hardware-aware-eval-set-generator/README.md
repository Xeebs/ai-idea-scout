# Personal Eval-Set Design Reviewer

A paste-in prompt for any AI chat tool. Use it when you want to compare a few local or small LLMs on a recurring task you actually do, but you only have a loose pile of example inputs and "good" answers — not a structured eval set, a scoring method, or a rubric. This tool reviews and tightens your eval set *before* you build or run anything against it. It does not run any model, check your hardware, or store scores — it's a one-time design pass.

## When to use this

You have a specific recurring task you run through a local/small LLM — rewriting dictation transcripts, classifying support tickets, generating commit messages from diffs, whatever — and 3-20 real examples of what you feed the model and what a good result looks like. You're about to compare two or more models on this task and want to know: is this set big enough, is it scored the right way, and what's missing before you trust a ranking built from it.

## What to hand over

Paste or type:
1. A one- or two-sentence description of the task.
2. Your examples — each one as an input/prompt plus either (a) a reference "good" answer, or (b) a plain-language description of what makes an answer acceptable or not. 3-20 examples is the useful range; fewer than 3 and there isn't enough to review.
3. (Optional) The names of the models you're considering — for context in the report only. Do not expect the reviewer to run, download, or know anything about them; model recommendations are out of scope for this tool.
4. (Optional) Any hardware limits you're aware of — also for context only, never used to drive the review itself.

This tool only ever works from what you paste. It never reaches into any API, file system, or hardware — if you want that (actually running candidate models, detecting what's installed, tracking scores over model updates), that's a separate, heavier tool this review is deliberately not trying to be.

## What the reviewer does

Paste this prompt into your AI chat tool along with your task description and examples:

---

**Prompt template:**

> I want you to review my eval set for comparing LLMs on a specific task, before I run anything. Here is my task and examples:
>
> Task: [describe the task in 1-2 sentences]
>
> Examples:
> 1. Input: [...] / Good answer or acceptance criteria: [...]
> 2. Input: [...] / Good answer or acceptance criteria: [...]
> (...3-20 examples total)
>
> Candidate models I'm considering (optional, for context only): [...]
>
> Please do the following, and nothing more — don't run or simulate running any model, and don't recommend which model to pick:
>
> 1. For each example, classify it as **deterministic** (checkable by exact/structured match) or **open-ended** (graded on criteria, not one right string), and assign a scoring method: exact-match, rubric-match against my reference, or LLM-judge against a rubric you draft.
> 2. Assess whether I have enough examples: fewer than 5 total is "too few to trust a ranking" — say so plainly. 5-7 is a rough first pass. 8+ with at least 2 per category is sufficient, but call out my weakest category.
> 3. Identify specific missing edge cases in my set — e.g., all happy-path with no malformed input, no length variation, no boundary/ambiguous case, no case where the model should decline or flag something, reference answers all one style when my real range is wider. Only list gaps that are actually missing from what I gave you.
> 4. For every open-ended example, draft a 3-5 dimension scoring rubric specific to my task (not generic "quality"), each dimension with a 1/3/5 description, plus one ready-to-paste LLM-judge prompt template using {input}, {reference_or_rubric}, {model_output} placeholders. If every example I gave you is deterministic/exact-match, say so plainly instead of forcing a rubric onto exact-match data.
> 5. Flag any example where my "good answer" description is too vague to score against, with a concrete rewrite suggestion (a checklist of required elements, or a tighter reference).
> 6. End with one explicit line on the limitation of LLM-judge scoring: it is not ground truth, and I should spot-check a sample of judge scores against my own read before trusting a ranking built on them alone.
>
> Give me the result as a structured report: example classification table, sample-size verdict, missing edge cases, scoring rubric + judge prompt template, tightening candidates, and the limitation line. Note clearly at the end that this is a design review only — running models, detecting hardware, and tracking scores over time are separate steps you are not doing here.

---

## What you get back

A structured report with these sections, in order:

- **Example Classification** — a table: example number, one-line input summary, type (deterministic/open-ended), assigned scoring method.
- **Sample-Size Assessment** — your count, category breakdown, and a verdict (too few / usable-rough / sufficient) with a target count if you're short.
- **Missing Edge Cases** — a bulleted list of specific gaps actually found in your set (not a generic checklist).
- **Scoring Rubric** — a table of 3-5 dimensions with 1/3/5 descriptions, plus a ready-to-paste LLM-judge prompt template with placeholders for input, reference/rubric, and model output.
- **Tightening Candidates** — any example whose "good answer" is too vague, with a concrete fix.
- **Limitation** — one line on LLM-judge calibration risk and the recommendation to spot-check.
- **Not Covered By This Review** — a reminder that running models, hardware detection, and score history are separate, out of scope here.

## What this is not

This is not a benchmark runner. It will not download, run, or score your examples against any actual model, and it will not tell you which model to pick. It also will not look at your hardware or installed models — that's a different, Connected-data tool (something that reads your local Ollama model list or GPU/VRAM via system introspection), not this one. This skill's only job is making sure the eval set itself — the examples, the scoring method, and the rubric — is sound before you spend time running anything against it.

## Guardrails

- Never invents example content, reference answers, or task details you didn't provide — if something's ambiguous, it gets flagged as a tightening candidate instead of guessed at.
- Never silently treats a too-small sample as sufficient — the sample-size verdict is always stated, even if you don't ask.
- Never presents an LLM-judge score as ground truth — the calibration-limitation line is mandatory whenever judge scoring is recommended.
- Never recommends specific models to use or drop — that's model-selection advice, which this tool doesn't give.
- Never simulates running your examples through a model — if the response includes made-up model outputs or scores, that's the tool going out of scope; ask it to stick to the eval-set design only.
