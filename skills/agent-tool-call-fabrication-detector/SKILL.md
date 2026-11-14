---
name: agent-tool-call-fabrication-detector
description: Reviews a pasted agent execution trace or transcript for signs that a tool call was fabricated (the model generated a plausible result without the tool actually running) or that context corruption from an earlier turn silently propagated forward. Use when a production agent's claimed action (refund issued, email sent, tests passed, PR merged) is in doubt and you need a fast triage before you go check the real system of record.
---

# Did It Actually Happen: Tool-Call Fabrication Triage

## When to use this
Someone on a team running a production or semi-autonomous agent has a specific tool-call claim they don't fully trust — a support agent says it issued a refund, a coding agent says it ran the test suite and everything passed, an ops agent says it sent a notification — and they want a fast second opinion on "did this plausibly actually happen, or does it smell fabricated?" before spending time digging into the real logs themselves.

Use this when:
- A customer or teammate reports an outcome that contradicts what the agent claimed (e.g., "I never got the refund").
- A trace looks "too clean" or suspiciously fast for an operation that should take real time.
- You're doing a periodic spot-check of an agent's high-stakes tool calls and want a structured first pass instead of free-reading the whole trace.

Do not reach for this skill to diagnose a crash, an explicit tool error, or a known exception — those already surfaced as failures. This is specifically for calls that *look* successful but might not be.

## Inputs
**Data source**: Manual — you paste the relevant excerpt of the agent's execution trace or transcript directly into the chat. This skill has no live connection to your tracing platform (OTel, Langfuse, etc.) or to any tool's real confirmation API; it reasons only over the text you provide. (The idea this skill comes from also describes a always-on, CONNECTED middleware version that queries real system-of-record APIs automatically — that's a separate piece of infrastructure to build, not this skill. This skill is the one-off manual-paste diagnostic half of that idea.)

To run this skill, provide:
1. The tool call(s) in question: tool name, the parameters the agent passed, and the raw response as it appears in the trace (not just the agent's paraphrase of it, if both are available).
2. The agent's natural-language claim built on that result (the sentence(s) that assert the action succeeded).
3. Timestamps for the call and response, if the trace has them (optional but improves accuracy).
4. Optional context that sharpens the check: what the tool's normal/expected response schema looks like, how long the real operation typically takes, and — for a context-corruption check — any ground-truth facts established earlier in the session (e.g., "the customer's order total is $43") that a later turn might contradict.

If you only have the agent's final summary with no distinguishable tool-call/response structure, say so when you provide it — the skill will tell you there isn't enough structure to run a per-call check rather than guessing.

## Procedure
1. **Parse the trace into discrete events.** For each tool call, extract: `tool_name`, `params`, `raw_response` (if shown separately from the agent's claim), `timestamp`/`duration` (if present), and the specific sentence(s) in the agent's output that assert this call's outcome.
2. **Run six checks per tool call**, recording which ones trigger:
   - **Schema conformance** — does `raw_response` look like real structured tool output (expected fields, types, a success marker) or does it read like free-text narration pretending to be a response? Flag if it's missing fields a real response of this type would have, or reads like prose rather than data.
   - **Timing plausibility** — if timestamps/durations exist, is the gap between call and response implausibly fast for that operation (e.g., a "full test suite passed" claim with no elapsed time, an email "sent" in under 50ms with no provider roundtrip)? Flag if so; if no timing data exists, mark this check "not checkable" rather than flagging or clearing it.
   - **Missing identifiers** — does a consequential action (refund, payment, email, commit, merge) lack any concrete ID, confirmation number, hash, or message ID that a real system of record would normally return? Flag if the claim implies completion but no identifier appears anywhere in the response or claim.
   - **Hedge/confidence mismatch** — does definitive language ("Done!", "Refund issued.") sit next to hedging markers ("should have", "I believe", "this likely completed", "presumably") in the same claim, or is the claim oddly generic with zero operation-specific detail? Flag either pattern.
   - **Parameter-result consistency** — does the claimed outcome actually match the input parameters (e.g., claims to have refunded $340 when the call parameters said $43; claims to have emailed a recipient different from the one in `params`)? Flag any mismatch regardless of whether it looks like fabrication or a genuine tool bug — it's worth surfacing either way.
   - **Templated repetition** — across multiple distinct calls to the same tool, does the "response" text look suspiciously identical or boilerplate (same phrasing, same structure, no call-specific values) in a way that suggests pattern completion rather than relayed real output? Flag if 2+ calls look interchangeable.
3. **Score and classify each tool call** by count of triggered flags (treat "not checkable" as neither triggered nor cleared):
   - 0–1 triggered → `LIKELY GENUINE`
   - 2–3 triggered → `SUSPICIOUS` — recommend manual verification against the real system of record
   - 4+ triggered → `LIKELY FABRICATED` — strongly recommend verifying before anyone acts on this claim
4. **Run the context-integrity check separately**, only if ground-truth facts from earlier in the session were provided: scan later turns for any assertion that contradicts one of those facts without citing a reason for the change (e.g., a corrected input, an explicit update). If found, note the turn number where the divergence first appears and quote both the original fact and the contradicting statement.
5. **If the pasted text has no identifiable tool-call/response structure**, state that plainly and stop — do not invent calls or force a verdict onto a plain narrative transcript.
6. Compile results into the output format below.

## Output format
A markdown triage report with:
1. **Summary line**: `N calls reviewed — X likely genuine, Y suspicious, Z likely fabricated.`
2. **Per-call table**: `Call # | Tool | Claimed outcome (short) | Flags triggered (list) | Verdict | Suggested verification step` — the verification step names the actual real-world source to check (e.g., "check the email provider's send log for this message ID," "check the payment processor's transaction log for this refund"), since this skill cannot check it itself.
3. **Context-integrity section** (only if applicable): turn number, the original ground-truth fact, the contradicting statement, and a one-line note on what that could mean if uncorrected.
4. **What to do next**: one or two concrete sentences naming the single highest-priority call to verify first and against what real source.

## Guardrails
- Never state a tool call definitely *was* fabricated — this is a heuristic triage over text, not proof. Always phrase verdicts as "likely genuine / suspicious / likely fabricated" and always list which specific checks triggered.
- Never fabricate evidence to complete a check — if timestamps, schemas, or raw responses aren't in the provided text, mark that check "not checkable" and say why, rather than guessing a verdict.
- Never claim to have checked, or offer to check, any real system of record yourself — you have no live connection to one. Every suggested verification step is something the human or their team does next, not something this skill performs.
- Never recommend reversing a transaction, re-sending a notification, or taking any other corrective action directly based on this skill's output alone — the output is a prompt to verify against ground truth, not a verdict to act on.
- Never pad the report with findings for tool calls that aren't actually present in the provided text, and never run the context-integrity check if no ground-truth facts were supplied — say "not applicable" instead.
- Keep this distinct from the project's always-on middleware version: a single flagged call here is a point-in-time manual review of one paste, not continuous monitoring, and it carries no guarantee it has seen every call in the session unless the full trace was provided.
