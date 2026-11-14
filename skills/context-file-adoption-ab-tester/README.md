# Context File Adoption Triage

A paste-and-run prompt for reviewing an existing AGENTS.md / CLAUDE.md-style project context file and flagging which sections are most likely hurting more than helping — before you spend the time (and inference budget) running an actual A/B comparison with the file present vs. removed.

Background: a 2026 academic study found that LLM-generated project context files can *reduce* agent task success while *increasing* inference cost by over 20% — the opposite of the near-universal assumption baked into every major coding agent that shipped support for one of these files. The one purpose-built tool that tried to measure this on a team's own repo is now archived and abandoned. This prompt doesn't run that measurement for you (that needs real agent-CLI execution against your real repo, twice) — it's the five-minute triage pass that tells you where to point that measurement first, or whether your file already looks clean enough to skip it.

## When to use this

You already have a context file in production use with a coding agent, and you want a fast read on which sections are worth scrutinizing — either because you've seen the agent ignore or contradict the file, or just because you want to check before trusting it on faith either way.

Don't use this to write a new context file from scratch, to fix one instruction you've already diagnosed as wrong, or as a substitute for actually running the paired comparison — it only tells you where to point that comparison.

## What to hand over

This is a manual-paste skill — nothing here reads your repo or runs anything automatically. Give it:

1. **The full context file, pasted verbatim.** Not a summary of what it says — the exact wording, because exact wording is what causes an agent to drift from or over-index on an instruction.
2. **The coding agent it's used with** (Claude Code, Codex CLI, Cursor, Aider, Copilot, Gemini CLI, Windsurf, Amazon Q, etc.).
3. **A one-line repo description** — language/stack and rough size (e.g. "mid-size Python monorepo, ~80k LOC, FastAPI + Celery").
4. **Optional but useful**: 1-3 real recent task prompts (an issue title, a PR description, a typical "ask the agent to do X") you actually care about the agent handling well.

## The prompt

Paste this into any AI chat tool, with your context file and details filled in:

```
You are reviewing a coding-agent context file (AGENTS.md / CLAUDE.md style) to
triage which sections are most likely reducing task success or inflating
inference cost, based on failure patterns a 2026 study associated with these
files: staleness, unnecessary verbosity, contradiction with the agent's own
defaults, and redundancy with what the agent could just read from the code.

Agent used: <AGENT NAME>
Repo: <ONE-LINE DESCRIPTION — stack, rough size>
Real tasks we care about (optional): <1-3 TASK PROMPTS, OR "none provided">

Context file (verbatim):
---
<PASTE THE FULL FILE HERE>
---

Do the following:

1. Split the file into discrete sections by heading/bullet group, numbered
   S1, S2, ... in document order. For each, note its approximate line count
   and a one-line paraphrase.

2. Classify each section against these categories (a section can get 0, 1,
   or several flags):
   - STALE: references a file/tool/dependency/workflow that may not match
     the repo as described. If you can't verify it, flag it as
     "unverified — confirm against repo," don't assert it's actually stale.
   - VERBOSE: generic best-practice advice the agent's own defaults already
     cover, or repeats another section.
   - CONTRADICTORY: conflicts with the named agent's documented default
     behavior, or with another section in the same file.
   - REDUNDANT-WITH-CODE: states something the agent could derive from the
     code itself in one or two reads (e.g. restating what the manifest file
     already declares).

3. Assign each flagged section a Predicted Risk of HIGH/MEDIUM/LOW based on
   how many categories it trips, how long/directive it is, and whether it's
   near the top of the file (agents tend to weight earlier instructions
   more heavily).

4. Any section covering secrets, deployment gates, access control, or
   compliance/legal rules gets marked "exempt — do not cut without human
   review" instead of a risk score, even if it also trips another flag.

5. Rank the non-exempt flagged sections into a "test this first" shortlist
   (max 5), each with one falsifiable hypothesis in the form: "removing/
   trimming S<n> should [increase/have no effect on] success and [decrease/
   have no effect on] cost if the <category> pattern is real here."

6. List sections with zero flags under "Passed triage" — don't omit them.

7. End with one "Bottom line" sentence: is a real paired A/B run (same
   task suite, file present vs. removed) worth running now given what you
   found, or does the file look clean enough to skip it for now?

Output as a single markdown report with: File overview, Section table
(Section | Content | Flags | Predicted Risk | Note), Test this first,
Passed triage, Bottom line.

Rules: never state a section definitely IS harmful or stale — only flag it
as predicted/likely and recommend the real test. Never guess staleness
without saying so is unverified. Never recommend cutting a safety/
compliance section. Never simulate or claim to have run the actual A/B
comparison — you're producing the shortlist for a human (or a separate
tool) to test, not the test result itself.
```

## What you get back

A markdown report with five parts: a short file overview, a table listing every section with its flags and predicted risk, a ranked top-5 "test this first" shortlist with a falsifiable hypothesis per section, a "passed triage" list of sections with no flags, and a one-sentence bottom line telling you whether the real A/B run is worth running now.

## What this does not do

It does not run the agent against your repo, does not clone anything, and does not produce a measured success-rate or cost number — those require an actual paired run (same task suite, context file present vs. removed/trimmed, executed twice against your real agent CLI). This prompt only tells you where to point that run, or whether your file is clean enough that you can reasonably skip it for now. Treat every flag here as a hypothesis, not a verdict.
