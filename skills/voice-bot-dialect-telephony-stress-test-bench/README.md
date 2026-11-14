# Dialect x Telephony-Condition Failure Triage

A portable prompt that turns a pile of real voice-bot/IVR failure tickets into a prioritized list of which dialect x line-condition combinations to stress-test first — before a team commits to building or running a full regression bench.

This is for a voice-bot or IVR team that already has support tickets, call-QA notes, or escalation logs mentioning accent/dialect trouble and/or bad line quality, and wants a fast, honest read on where to focus testing effort. Works in any chat tool; paste text, no audio or API access needed.

## How to use it

Paste the block below into any AI chat tool, then give it a batch of failure entries — one ticket/note/transcript excerpt per entry. Works with as few as 5 entries; more reliable above ~15.

---

### The prompt

> You are triaging voice-bot/IVR failure reports to build a prioritized dialect x telephony-condition test matrix — which combinations a team should stress-test first, before committing to a full regression bench.
>
> For each failure entry I give you, extract two signals, **each only if explicitly stated or directly quoted in that entry's own text**:
> - **Dialect/accent/region tag** — only from an explicit statement (e.g. "caller spoke Tamil-accented English", "regional Hindi dialect", "Telugu-English code-switching"). Never infer dialect, accent, or ethnicity from a caller's name, phone number, or location alone — that is fabricated signal, not evidence.
> - **Telephony-condition tag** — only from an explicit audio/line-quality description (e.g. "static on the line", "call kept dropping", "sounded garbled", "mobile network kept cutting out", "customer repeated themselves 4 times due to noise"). A bare "bot didn't understand me" with no quality description does NOT count.
>
> Classify every entry into exactly one bucket:
> - **Full signal** — both tags present → goes into the matrix.
> - **Partial signal** — only one tag present → separate list by axis, never guessed into a cell.
> - **Untaggable** — neither present, or unrelated to dialect/line quality → excluded, just counted.
>
> Build a matrix: rows = distinct dialect tags found, columns = distinct condition tags found, cell = count of full-signal entries in that cell. Flag a cell (⚠) if any of its entries use escalation language (repeat complaint, "demanded a human", safety/compliance mention, churn threat).
>
> Rank cells by count descending, then by flagged-before-unflagged on ties. If total full-signal entries are below 15, say explicitly that the ranking is directional only — small counts can flip order with a few more tickets.
>
> Output exactly this structure:
> ```
> ## Priority Test Matrix (full-signal entries only)
> | Dialect \ Condition | <cond A> | <cond B> | ... |
> |---|---|---|---|
> | <dialect 1> | <count>[⚠] | <count> | ... |
>
> ## Top combinations to test first
> 1. <Dialect> x <Condition> — <count> entries[, flagged] — "<quoted/paraphrased evidence>"
> (up to 5)
>
> ## Partial-signal entries (one axis only)
> - Dialect known, condition unknown: <n> (e.g. <list>)
> - Condition known, dialect unknown: <n> (e.g. <list>)
>
> ## Untaggable: <n> entries excluded
>
> ## Confidence note
> <sample size and whether ranking should be treated as directional>
> ```
>
> Never infer a dialect/accent/ethnicity from a name, phone number, or location alone. Never invent a condition tag from a vague complaint with no audio-quality description. Never force a partial-signal entry into a matrix cell. Never present a small-N ranking as statistically confident. Never claim this output replaces actually running a stress-test bench — it only says where to point one first.
>
> Here are my failure entries:
> [paste one ticket/note/transcript excerpt per entry]

## Why this exists

Teams deploying voice bots into dialect-diverse, telephony-degraded markets (South Asia, the Middle East, Africa especially) accumulate real failure signal in tickets and QA notes long before anyone builds a systematic accent x line-condition regression suite — and when they finally do want to build one (see the companion open-source stress-test bench this skill is paired with), the question "which combination do we even test first" is usually answered by gut feel. This prompt turns the pile of tickets already sitting in a support queue into an evidence-ranked answer, with hard guardrails against the two easiest ways to get it wrong: inventing a caller's dialect from their name, and inventing a line-condition from a vague complaint.

Full project context, evidence, and the full stress-test bench this triage step feeds into: see [`ideas/voice-bot-dialect-telephony-stress-test-bench.md`](../../ideas/voice-bot-dialect-telephony-stress-test-bench.md) in the [ai-idea-scout](https://github.com/Xeebs/ai-idea-scout) repo.
