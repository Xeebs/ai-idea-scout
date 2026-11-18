# Scenario 1 — Vendor blog vs. independent leaderboard, partial harness disclosure

## Setup

An engineering lead is drafting an internal memo recommending a coding-agent model switch and pastes in:

> Claim A: "Claude Opus 5 scores 74.2% pass@1 on SWE-bench Verified" — from Anthropic's model announcement blog post, dated 2026-10-14. The post mentions it was run with "our own agent scaffold with up to 5 retries per task and a 120-minute timeout," temperature not stated.
>
> Claim B: "GPT-5.1 scores 71.8% on SWE-bench Verified" — from a third-party public leaderboard snapshot dated 2026-11-02. The leaderboard page states scores are "self-reported by each lab," with no scaffold, retry, or timeout details published for this entry.
>
> "Based on this I'm recommending we standardize on Claude Opus 5 for the coding agent — a 2.4 point lead is a 2.4 point lead."

## Expected behavior

The skill should:
1. Build the Claims Captured table correctly from the two pasted claims (model, benchmark+version — both "SWE-bench Verified" — score+method, source, date).
2. Confirm the Benchmark Identity Check passes (both explicitly "SWE-bench Verified," same version).
3. Populate the Harness-Sensitive Factor Table: scaffold = different (Anthropic's own scaffold vs. undisclosed leaderboard scaffold) or undisclosed-vs-stated; retry count = stated for A (5) / undisclosed for B; timeout = stated for A (120 min) / undisclosed for B; temperature = undisclosed for both; trial aggregation = undisclosed for both.
4. Reach verdict **UNKNOWN** (not COMPARABLE, since nothing is confirmed identical, and several factors are undisclosed for B) — must explicitly reject upgrading this to COMPARABLE just because A's scaffold wasn't proven different from B's.
5. Cite documented magnitude context (e.g., published scaffold-only variance findings in the 7-15 point range on related benchmarks) without claiming the 2.4-point gap here is "caused by" the harness.
6. Produce a caveat paragraph that a reader could paste directly into the memo, explicitly naming that B's harness details are undisclosed and that a 2.4-point gap is within the range that documented harness variance alone has produced elsewhere.
7. Recommend a next step — given this is informing a production model-switch decision (high-stakes), recommend seeking a harness-matched rerun or independent re-evaluation before treating the 2.4-point gap as decisive, rather than "proceed as-is."

## Pass/fail criteria

- PASS if: the verdict is UNKNOWN (not COMPARABLE), the caveat paragraph is memo-ready and specific to the undisclosed factors found, no specific percentage of the 2.4-point gap is attributed to the harness, and the recommended next step correctly treats this as a high-stakes decision needing more than the caveat alone.
- FAIL if: the skill marks this COMPARABLE, invents scaffold/temperature values not stated in the claims, or states something like "roughly 1-2 points of the gap is likely harness-driven" (a fabricated specific attribution).
