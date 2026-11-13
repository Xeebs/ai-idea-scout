# Dead Branch Check: A Reachability Auditor for Guardrail Classifier Code

Paste this whole document into any AI chat tool (ChatGPT, Claude, Gemini, etc.) along with your classifier function, and it will audit it for a specific, easy-to-miss bug: a classifier that's *documented* to return a category it can never actually produce. This bug class passes normal line/branch test coverage, because the code still runs and still returns something — it just never returns the one value it claimed it could.

## When to use this

Use this whenever you're writing, reviewing, or debugging a rule-based classifier function inside a guardrail, safety filter, or intent router — something like `classify_intent()`, `classify_request()`, `route_message()`, a custom rail in NeMo Guardrails, or a validator in Guardrails AI. The signal that this skill applies: the function has a stated list of possible outputs (a docstring, an `Enum`, a `Literal[...]` type, or a comment), and you want to know whether every one of those outputs can actually happen, or whether one of them is silently dead.

This is the same bug class behind a real production incident: a classifier documented to return `off_topic` as one of its categories had its final `else` branch accidentally return a different default, so `off_topic` never fired — anyone who should have gotten an off-topic redirect instead got whatever the fallback category produced, for months, until someone noticed the reply shape looked wrong.

## What to hand over

**Data source: Manual.** Paste two things:
1. The full source code of the classifier function (not a summary — the exact code, including comments).
2. Wherever the function's documented category list lives: a docstring, an `Enum` definition, a `Literal[...]` type hint, or an explicit comment. If none of those exist in the code you're pasting, write out the intended list yourself in your message (e.g., "this should be able to return: greeting, order_status, complaint, off_topic") — don't skip this step, because the entire point of the audit is checking the code against *your* stated intent, not against what the code happens to do.

If you don't give an explicit category list, the assistant should ask you for one rather than guessing — if it doesn't, tell it to stop and ask.

## What the audit does, step by step

1. **Reads your declared category list** from wherever you stated it.
2. **Traces every branch of the function in execution order** — every `if`/`elif`/`else`, `match`/`case`, dict/table lookup, or early return — noting the condition for each and what it returns.
3. **Flags branches it can't fully analyze statically** — anything gated on a model score, embedding similarity, or an external API call gets marked UNVERIFIABLE rather than guessed at.
4. **For every declared category, checks reachability:**
   - No branch returns it at all → flagged **UNREACHABLE (no matching branch)** — the bug class this tool exists for.
   - A branch returns it, but an earlier, broader branch would always catch the same inputs first → flagged **UNREACHABLE (shadowed)**, naming the branch doing the shadowing.
   - Otherwise → flagged **REACHABLE**, with one concrete example input constructed to prove it — and an explanation of why that input skips every earlier branch before landing on the right one.
   - Depends on an unverifiable branch → flagged **UNVERIFIABLE**, with a suggestion to dynamic-test it instead (e.g., property-based fuzzing with Hypothesis or fast-check) rather than trusting a static guess.
5. **Notes any branch that returns something *not* on your declared list** — a related smell (output drift) worth knowing about even though it's not the main bug.
6. **Suggests the smallest possible fix** for each unreachable category — reordering two branches, narrowing an over-broad condition, adding one missing `elif`, or fixing a typo'd return value. It should not propose rewriting your function.

## What you get back

A report structured like this:

```
# Dead Branch Audit: <function name>

## Declared categories
- <category>: <where it's declared>

## Branch trace
| # | Condition | Returns | Data dependency |
|---|-----------|---------|------------------|
| 1 | ... | ... | static / unverifiable |

## Reachability verdict
| Category | Verdict | Evidence |
|----------|---------|----------|
| off_topic | UNREACHABLE (no matching branch) | No branch in the trace returns this value |
| complaint | REACHABLE | Example input: "this is terrible, refund me" — matches branch #3, skips #1-2 because neither greeting nor order keywords appear |

## Undeclared outputs (if any)
- Branch #4 returns "unknown", which isn't in the declared category list.

## Suggested fixes
1. Change the final `else` in branch #4 to return "off_topic" instead of falling through to "complaint".

## Scope caveats
(only if something was UNVERIFIABLE)
```

If everything checks out — every declared category is reachable and there's no output drift — the report says that explicitly at the top of the verdict table. A clean result is a useful result; don't expect it to manufacture a problem.

## Rules this audit follows (and you should hold it to)

- It never declares a category unreachable just because it "couldn't think of an input" — it has to show either that no branch returns the value, or that an earlier branch structurally shadows the one that would.
- It never substitutes the code's own return values for your stated category list — the entire point is catching when those two things have quietly diverged. If you didn't give it an explicit list, it should ask, not assume.
- It treats anything depending on a model score, embedding, or external call as unverifiable by static reading alone, and tells you to test it dynamically instead of asserting a verdict.
- It doesn't rewrite your code — only the report, with suggested fixes you apply yourself.
- It's a one-shot, point-in-time review. If you want this check running automatically on every future PR, that's a CI-integrated version of the same idea — this document only covers the manual, paste-it-in review.
