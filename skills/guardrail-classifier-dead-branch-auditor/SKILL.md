---
name: guardrail-classifier-dead-branch-auditor
description: Audits a hand-written guardrail/intent classifier function for documented output categories that are structurally unreachable (a dead-branch/dead-category bug class that passes normal line coverage). Use when a developer is writing, reviewing, or debugging a rule-based classify_*()-style function in a guardrail or safety stack.
---

# Dead Branch Check: A Reachability Auditor for Guardrail Classifier Code

## When to use this
Reach for this skill the moment someone pastes a classifier function — `classify_intent()`, `classify_request()`, `route_message()`, a NeMo Guardrails custom rail, a Guardrails AI validator, or similar rule/if-elif-based logic in a guardrail or safety stack — and asks you to review it, debug an unexpected production reply, or sanity-check it before merging a PR. The specific trigger is: the function has a documented or typed set of output categories (a docstring list, an `Enum`, a `Literal[...]` type, or an inline comment), and the question is whether every one of those categories can actually be produced by some input, or whether one silently never fires. This is distinct from asking "does this code have bugs in general" — only use this skill when there's an explicit claimed output space to check against actual reachable outputs.

## Inputs
**Data source**: Manual — the user pastes (a) the classifier function's full source code, and (b) its documented category list, wherever that's stated: a docstring, an `Enum`/`Literal` type annotation, a comment, or a config/rule table. If the categories aren't stated anywhere in what's pasted, ask the user to state the intended full list explicitly before proceeding — never infer it from guessing at return-value strings in the code.

## Procedure
1. **Extract the declared category list.** Read the docstring, type annotation, enum, or comment the user pasted. If no explicit list exists, stop and ask for one — do not proceed on an inferred list.
2. **Build the branch trace.** Walk the function top to bottom in the exact order it executes (if/elif/else chains, `match`/`case`, dict/table lookups, early returns, loop-based rule tables). For each branch record, in order: the condition that must be true to enter it, and the category/value it returns or assigns.
3. **Classify each branch's data dependency.** Branches whose condition depends only on the literal input (string contents, length, regex match, membership in a static list/dict) are *staticly traceable*. Branches whose condition depends on a model score, embedding similarity, external API call, or other runtime-computed value are *not* staticly traceable — flag these as UNVERIFIABLE rather than guessing.
4. **For each declared category, determine reachability:**
   - Find every branch that returns this category.
   - If no branch returns it at all → **UNREACHABLE (no matching branch)**. This is the exact bug class the skill targets: a documented output nothing in the code ever emits.
   - If a branch returns it, check whether every earlier branch's condition could ever be false for some input that also satisfies this branch's condition. If an earlier condition is broad enough to catch every input that would otherwise reach this branch (e.g., a catch-all `else` placed too early, or an overlapping keyword check), mark **UNREACHABLE (shadowed by earlier branch)** and name the shadowing branch.
   - Otherwise mark **REACHABLE** and construct one concrete example input that satisfies this branch's condition and fails every earlier branch's condition. Show your reasoning for why it skips each earlier branch, not just the final match.
   - If reachability depends on an UNVERIFIABLE branch from step 3, mark **UNVERIFIABLE** and say what would make it checkable (a fuzz/property test against the live model, not static trace).
5. **Check for undeclared outputs.** Note any branch that returns a value not in the declared category list — this is a related but separate smell (output drift) worth flagging even though it's not the primary bug class.
6. **Propose the minimal fix** for every UNREACHABLE category: usually one of (a) add a missing branch/condition, (b) narrow an earlier catch-all so it stops shadowing, (c) reorder branches so the specific case is checked before the general one, or (d) fix a copy-paste/typo'd return value. Keep fixes to the smallest diff that restores reachability — do not propose a rewrite.
7. **State scope caveats.** If any branch was UNVERIFIABLE, say so plainly and recommend a dynamic check (property-based fuzzing, e.g. Hypothesis in Python or fast-check in JS, against the live function) rather than asserting a verdict you can't support from static reading alone.

## Output format
A single markdown report with these sections, in this order:

```
# Dead Branch Audit: <function name>

## Declared categories
- <category>: <where declared — docstring/enum/type/comment>
...

## Branch trace
| # | Condition | Returns | Data dependency |
|---|-----------|---------|------------------|
| 1 | ... | ... | static / unverifiable |
...

## Reachability verdict
| Category | Verdict | Evidence |
|----------|---------|----------|
| <category> | REACHABLE | Example input: "<input>" — matches branch #N, skips #1..#N-1 because <reason> |
| <category> | UNREACHABLE (no matching branch) | No branch in the trace returns this value |
| <category> | UNREACHABLE (shadowed) | Branch #N would return it, but branch #M (earlier) catches every input that satisfies #N's condition |
| <category> | UNVERIFIABLE | Depends on <model/external call>; recommend dynamic fuzz testing |

## Undeclared outputs (if any)
- Branch #N returns "<value>", which is not in the declared category list.

## Suggested fixes
1. <minimal, specific fix per UNREACHABLE category>

## Scope caveats
<what this audit could not verify and why — only present if relevant>
```

If every declared category is REACHABLE and there are no undeclared outputs, say so explicitly in one line at the top of the Reachability verdict section rather than omitting the section — a clean result is itself the useful output.

## Guardrails
- Never mark a category REACHABLE or UNREACHABLE without showing the structural reason (the specific branch and, for REACHABLE, a concrete example input). "I couldn't think of an input" is not evidence of unreachability — only a structural shadowing argument or the absence of any returning branch counts.
- Never infer the declared category list from the code's own return statements if the user provided an explicit docstring/enum/comment list — the whole point is catching divergence between the two. Only fall back to inferring from code if truly nothing else is available, and say so.
- Treat any branch gated on a model score, embedding distance, external API response, or other runtime value as UNVERIFIABLE by static trace. Never assert reachability or unreachability for these — recommend dynamic fuzz testing instead.
- Never rewrite or "fix" the user's code directly — only propose the fix in the report; this is a one-shot audit, not an autonomous editor.
- Never pad the branch trace or verdict table with branches that don't exist in the pasted code, and never skip a branch that does exist, even if it looks irrelevant — a shadowing bug often hides in a branch that looks unimportant.
- This skill is a one-shot manual review. It does not run automatically on every future commit — if the user wants that, point out that's a CI-integrated version of this same check (a separate, always-on tool), not something this skill does for them.
