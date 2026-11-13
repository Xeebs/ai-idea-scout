---
name: agent-memory-provenance-verifier
description: One-shot forensic check of whether one specific claimed AI-agent memory ("the agent remembers the user told it X", "the agent recalls having done Y") is actually backed by a pasted execution trace/transcript, or was confabulated — classifying the claim SUPPORTED, UNSUPPORTED, CONTRADICTED, or UNVERIFIABLE against cited trace segments, including the case where a real segment exists but is being misrepresented. Use when auditing a single flagged memory record against evidence you already have, not for multi-hop incident root-cause reconstruction or live tamper-proof provenance infrastructure.
---

# Agent Memory Provenance Verifier

## When to use this
Reach for this the moment someone has one specific memory record an AI agent claims to have ("I remember you said your deadline was Friday", "I recall checking your account balance last week and it was $400") and a corresponding execution trace or transcript excerpt it's supposedly derived from, and needs a deterministic answer to "is this genuine, or did the agent make it up" — because asking another LLM to judge plausibility from the text alone is exactly the approach that has already been shown to fail (three separate LLM judges performed no better than chance at telling real agent memories from counterfeit ones). This is a single-claim authenticity check against evidence you hand over, not:
- a multi-hop "why did the agent take this consequential action" incident reconstruction across many memory writes and sessions (a different skill/task), and
- not a live, cryptographically tamper-evident provenance system wired into a memory backend's write path — this skill never verifies hashes or trace integrity, only whether pasted text actually entails a pasted claim.

## Inputs
**Data source**: Manual — the user pastes the memory record and the trace/transcript excerpt directly into the chat; there is no live connector to Mem0, Zep, Letta, or any execution-trace store in this skill. (A live, write-time version of this check that resolves cryptographic trace references automatically is a separate runtime-infrastructure build, not this skill.)

Collect, if not already given:
1. **The memory claim(s)** — the exact text of what the agent claims to remember, verbatim. If more than one claim is pasted, verify each independently; never conflate them.
2. **The trace/transcript excerpt it's claimed to derive from** — tool-call results, retrieved documents, user messages, or a full conversation transcript, in whatever form exists (raw log, chat export, pasted text). Ask for the specific session/segment if the user only has a large transcript and hasn't narrowed it.
3. *(Optional)* **Claimed timestamp or session reference** for the memory — sharpens whether the trace excerpt even covers the right window.

If the trace/transcript excerpt is missing entirely, do not proceed — there is nothing to verify against; say so and ask for it. A memory claim with no evidence to check is neither SUPPORTED nor UNSUPPORTED by this skill's logic — it simply cannot be run.

## Procedure
1. **Decompose the claim into atomic assertions.** A memory claim like "the user told me their deadline was Friday and that they prefer email over Slack" is two assertions, not one — verify each separately so a claim that's half-true isn't rounded up to SUPPORTED.
2. **Search the trace for every segment topically relevant to each assertion** — a tool-call result, a retrieved document, or a user/assistant turn. Quote the exact text of each candidate segment with a locator (line number, timestamp, message index, or tool-call ID) exactly as it appears in what was pasted.
3. **Run an entailment check per assertion, not a keyword-match check.** For each assertion, determine whether the cited segment's actual content logically supports it:
   - **SUPPORTED** — a trace segment exists and its content directly entails the assertion (e.g. the user literally wrote "deadline is Friday" in the quoted turn).
   - **CONTRADICTED** — a trace segment exists that directly conflicts with the assertion (e.g. the user wrote "deadline is Monday," or a tool call returned a different value than claimed).
   - **UNSUPPORTED** — no segment in the provided trace addresses this assertion at all.
   - **UNVERIFIABLE** — the trace is ambiguous, truncated, or the relevant window simply isn't included in what was pasted (say exactly why).
4. **Explicitly catch the "real citation, wrong content" failure mode.** If the agent (or the material being audited) points to a real tool call or message as the source, re-read that exact segment's content word-for-word and confirm it actually says what's claimed — a reference to a real, existing trace segment that has been mischaracterized is CONTRADICTED or UNSUPPORTED, never SUPPORTED just because a segment exists at all. This is the single most important check this skill performs; do not skip it.
5. **Aggregate to one overall verdict** for the full memory claim:
   - **SUPPORTED** — every assertion is SUPPORTED.
   - **PARTIALLY SUPPORTED** — a mix of SUPPORTED and UNSUPPORTED/UNVERIFIABLE assertions, none CONTRADICTED.
   - **UNSUPPORTED** — no assertion found any supporting segment.
   - **CONTRADICTED** — at least one assertion directly conflicts with the trace, regardless of how the others scored; a single contradiction is disqualifying for the whole claim.
6. **State confidence and caveats plainly** — note if the trace excerpt looks incomplete (missing turns, a gap in timestamps, truncated tool output) and say that the verdict would change with fuller evidence, rather than letting a thin trace quietly inflate confidence.
7. **Self-check before returning**: every quoted trace segment in the output must be copy-paste-traceable to something actually present in what the user pasted — if a quote can't be located verbatim in the provided trace, delete it and mark that assertion UNVERIFIABLE instead.

## Output format
```markdown
# Memory Provenance Verification — <one-line summary of the claim>

## Memory claim (verbatim)
<the exact claimed memory text>

## Assertions
| # | Assertion | Verdict | Cited trace segment (verbatim + locator) |
|---|---|---|---|

## Overall verdict: SUPPORTED | PARTIALLY SUPPORTED | UNSUPPORTED | CONTRADICTED

## Reasoning
<2-4 sentences tying the per-assertion verdicts to the overall call, explicitly naming any "real citation, mischaracterized content" finding if one occurred>

## Caveats
- <trace gaps, missing windows, ambiguity that would change the verdict with more evidence>
```

## Guardrails
- Never mark an assertion SUPPORTED on topical relevance or plausibility alone — only on a quoted trace segment whose actual content entails the claim.
- Never treat "a real trace segment exists that's loosely related" as equivalent to "the segment supports this specific claim" — always re-check what the segment actually says, word for word, against what's claimed.
- Never invent, paraphrase-as-if-quoted, or assume the contents of a trace segment the user didn't paste — if it's not in the provided material, the relevant assertion is UNSUPPORTED or UNVERIFIABLE, not SUPPORTED.
- Never attempt or claim to perform cryptographic hash/tamper verification — this skill has no access to a live trace store and only reasons over pasted text; say so if the user expects that level of guarantee.
- Never collapse multiple distinct assertions in one claim into a single verdict without checking each — a compound claim is only as strong as its weakest assertion.
- Never present this as an automatic, ongoing monitor — it is a one-time check of the specific material pasted in this conversation.
