# Skill Admission Ablation Audit

A paste-in prompt that reviews a candidate AI agent "skill" (a SKILL.md file, a system-prompt block, a reusable instruction set, a tool-reference document — anything meant to be loaded into every future agent invocation) and tells you whether it's actually worth the context budget it costs, before you add it to a shared catalog or publish it to a marketplace.

## When to use this

Use this the moment you're about to:
- Add a new skill to a team's shared `skills/` directory, internal CLAUDE.md, or tool catalog that every future agent run will load.
- Publish a skill to a marketplace (Agensi, claudemarketplaces.com, claude-plugins.dev, skills.sh, or similar) and want a sanity check before you ship it.
- Prune an existing catalog that's grown large, where you suspect some entries are dead weight — pasted reference tables, or instructions duplicating something the model already does on its own.

This is a fast, one-shot heuristic review you can run by pasting into any AI chat tool. It is not a live benchmark — it's the gate you run *before* deciding whether a skill is even worth the time of setting up a real with/without test.

## What you need to provide

This skill works entirely from what you paste in — it does not run code, fetch anything, or connect to any system. You need three things:

1. **The candidate skill's full content** — the entire SKILL.md body, system-prompt block, or tool-reference text. Paste it in full, not a summary.
2. **2-3 representative task scenarios** — real tasks this skill is meant to help with.
3. **A note on how the base model performs on those same scenarios WITHOUT the skill** — what it got right, what it got wrong or had to be corrected on, and roughly how long it took (turns, obvious backtracking, etc.). This is the baseline you're comparing against. If you don't have this, run the scenarios once without the skill first and note what happens — without a baseline, any verdict is a guess, not an audit.

## The prompt

Paste the following into any AI chat tool, filling in the three inputs above:

```
Act as a skill admission auditor. I'm about to add a candidate skill to a shared catalog
(or publish it), and I want you to tell me whether it's worth the context cost before I do.

CANDIDATE SKILL (full content):
<paste the full SKILL.md / system-prompt block / instruction set here>

REPRESENTATIVE SCENARIOS (2-3 real tasks this skill is meant to help with):
<paste scenarios here>

BASE MODEL BEHAVIOR ON THESE SCENARIOS WITHOUT THE SKILL:
<describe what happened when you ran these same scenarios with no skill present —
what it got right, what it got wrong, how long it took>

Run the following five checks against the candidate skill, scoring each PASS (clears
the concern) or FLAG (shows the failure signature):

1. CAPABILITY DUPLICATION — Compare the skill's instructions against my reported
   no-skill baseline. If the base model already produced the same outcome without
   being told, FLAG this — the skill is teaching the model something it already knows.

2. REFERENCE-DUMP DENSITY — Estimate what fraction of the skill's content is a
   verbatim table/list (API signatures, parameters, enum values, URLs) versus actual
   instructions or judgment calls. FLAG if more than half the content is a dump AND
   my scenarios don't show the model needing that exact data to avoid hallucinating it.

3. COMPACT OPERATIONAL HABIT — Look for a workflow step, ordering constraint, or
   verification check the model would not reliably do unprompted. PASS only if my
   baseline scenario actually shows the model skipping or getting this wrong without
   the skill present — not just because the skill's own text claims to encode a habit.

4. ROUTER VIABILITY — Would a one-line pointer ("if task matches X, load this skill's
   full content") work as well as loading the full body on every invocation? FLAG if
   the skill is rarely relevant but large enough to cost meaningful context regardless.

5. NET EFFICIENCY TRADEOFF — Weigh the measured/reported benefit (did it change the
   OUTCOME, not just the process) against the token/context cost of including it in
   every future invocation of whatever catalog it joins.

Then give me:
- An overall verdict: KEEP, DELETE, or RESTRUCTURE-TO-ROUTER
- A one-line rationale per check, citing the specific scenario or content excerpt
  that drove the call — not a generic restatement of the rule
- A confidence note stating clearly that this is a heuristic review of the scenarios
  I supplied, not an executed test, and naming the follow-up (an actual with/without
  trial run, same scenarios, same model, run twice) if the stakes are high — e.g. a
  shared catalog many people depend on, not just my own personal skill folder

Rules you must follow:
- Never claim you ran a live test. Every verdict here is a read of what I pasted.
- Never issue DELETE on reference-dump density alone if my scenarios show the model
  hallucinating or getting exact values wrong without the skill — that's KEEP or
  RESTRUCTURE, not DELETE.
- Never score "compact operational habit" PASS just because the skill's own text
  claims to encode a habit — only count it if my baseline scenario shows the failure
  actually happening without the skill.
- Never let skill length alone drive the verdict — short skills can be pure
  duplication, long skills can be dense and earn their keep.
- If I didn't give you a no-skill baseline, ask for it before giving a confident
  verdict, or clearly mark your answer LOW CONFIDENCE if I want to proceed anyway.
```

## What you get back

A short table scoring the five checks PASS/FLAG, an overall KEEP / DELETE / RESTRUCTURE-TO-ROUTER verdict, one rationale line per check tied to your actual scenarios (not generic boilerplate), a 2-3 sentence recommendation (including a suggested router-entry rewrite if the verdict is RESTRUCTURE), and a confidence note telling you plainly that this was a heuristic review, not a live test, plus whether your situation warrants running an actual with/without trial before you act on the verdict.

## Why this isn't just a vague "review my skill" prompt

Generic "review this and tell me if it's good" prompts don't produce a decision you can act on — they produce adjectives. This prompt forces five specific, falsifiable checks (each tied to a concrete baseline-vs-candidate comparison you provide), refuses to issue a DELETE or a PASS without evidence from your own scenarios, and is explicit that it's a heuristic gate, not a substitute for actually running the same task twice with and without the skill. If you're making a decision that affects a shared catalog many people's agents will load from, treat this as the fast pre-check — then go build (or have someone build) the real with/without trial before you commit.

## Limits — know when to use something heavier instead

This is a paste-and-judge review, not code that executes anything. It cannot catch noisy, run-to-run-variable effects that only show up across many repeated trials, and its "reference-dump" and "router viability" calls are estimates from reading the content, not measurements. If you're deciding whether to gate an entire shared skill catalog in CI (not just review one candidate before you personally add it), you need an actual ablation test harness that runs scenarios twice — with the skill installed and without — across repeated trials, which this prompt does not do.
