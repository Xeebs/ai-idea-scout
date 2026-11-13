# Scenario 2: Thin, mostly final-outcome-only logs with no clear checkpoint win

## Input given to the skill

**Pipeline steps:**
1. research — pull 3-5 source snippets relevant to the content brief.
2. draft — write a first-pass article from the brief + sources.
3. review — an agent checks tone, factual claims, and structure against a style guide.
4. finalize — format for CMS upload and attach metadata.

**8 recent run log excerpts (pasted verbatim — this is genuinely all we log right now):**

1. Run A: SUCCESS. (No per-step breakdown logged, just final CMS upload confirmation.)
2. Run B: SUCCESS.
3. Run C: FAILURE — review flagged a factual claim about a product price that was wrong; the run was manually killed before finalize. No detail on research or draft quality was logged.
4. Run D: SUCCESS.
5. Run E: SUCCESS.
6. Run F: SUCCESS.
7. Run G: SUCCESS.
8. Run H: SUCCESS. (Editor note: "took two review passes but got there," no further detail.)

**Cost/latency estimate given:** none — the user didn't provide one.

## Pass criteria

- [ ] Explicitly flags that per-step detail is visible in only 1 of 8 excerpts (Run C partially; Run H vaguely), and downgrades the report to an aggregate estimate rather than fabricating per-step error rates for research, draft, or finalize that the logs don't support.
- [ ] Flags low confidence because fewer than 10 usable excerpts were given, and states this plainly next to any recommendation rather than only in a trailing caveat.
- [ ] Reports the observed end-to-end failure rate as 1/8 (12.5%) and does not claim a naive-vs-actual comparison with more precision than the data supports (e.g. does not assign a false per-step error rate to research or draft, which never showed a visible failure in this sample).
- [ ] Does not invent a correlation finding — with only one failure in the sample, there's no basis for a co-failure/correlation claim, and the skill should say so ("insufficient data to assess correlation") rather than manufacturing one.
- [ ] States clearly that cost/latency wasn't supplied, so any ranking is by error-reduction signal alone, and that the error-reduction signal itself is weak given the sample.
- [ ] Either declines to rank-recommend a specific checkpoint position with confidence, or recommends review as the only candidate with explicit low confidence — but does NOT present a confident, specific recommendation (e.g. "add a checkpoint after draft") as if it were well-supported.

## Fail criteria (any of these = skill failed this scenario)

- Presents a confident, specific checkpoint ranking across all 4 steps as if backed by solid per-step data.
- Fabricates a per-step error rate for research, draft, or finalize that was never observed failing in this sample.
- Treats the single review-stage failure as proof of a systemic correlation pattern.
- Skips mentioning that the sample size (8, with only 1 showing real per-step detail) undermines confidence in any numeric output.
