# Scenario 1 — Mid-size eng team considering auto-summarization for a long-running coding agent

## Input (what the user hands over)

> We run an internal coding agent on top of Claude Code `-p` for multi-hour refactor tasks. Right now we don't compact anything — full conversation history is kept, and we rely on prompt caching to keep cost down. Someone on the team wants to turn on Claude Code's auto-compact at 80% context usage because we occasionally hit context-window errors on our longest refactor tasks (the ones that touch 15+ files over 200+ turns).
>
> We're worried that auto-compact will make the agent forget constraints we set early — like "never touch the `legacy/` directory" or "keep the public API signature unchanged" — several turns before it actually needs them again.
>
> Our task suite right now is informal: we have about 6 "golden" refactor tickets we manually re-run when we change agent config, and we eyeball whether the diff looks reasonable and whether tests pass. No formal pass/fail write-up exists yet.
>
> We don't have token/cost baselines pulled yet, but we do have OTel traces in Honeycomb if that matters.

## What a correct skill run produces

An "A/B Test Design Brief" with:

1. **Hypothesis** that is specific to auto-compact at 80% context usage, naming a concrete predicted direction/magnitude on success rate and/or cost, with a mechanism referencing the constraint-forgetting concern the user raised.
2. **Baseline vs. Treatment** clearly stated as: baseline = no compaction (current behavior), treatment = Claude Code auto-compact triggered at 80% context fill — matching what the user described, not a generic restatement.
3. **Task Sample** section that:
   - Flags the existing 6-task suite as under the recommended 10-20 and under-specified (no written pass/fail criteria, just "eyeball the diff").
   - Either asks the user to expand it or drafts additional candidate tasks/criteria explicitly aimed at long-horizon, 200+-turn, multi-file refactors.
   - Explicitly adds or calls out tasks that test retention of the two named constraints ("never touch `legacy/`", "keep public API signature unchanged") stated early and needed many turns later — this is the single most important check for this scenario and must not be missing.
4. **Metrics** including success rate, token/cost delta, latency delta, AND an explicit constraint-violation check (e.g. "did the diff touch `legacy/`" / "did the public API signature change") — not just "tests pass."
5. **Statistical Plan** with a concrete repeat-run recommendation and named test method, plus an honest note that 6 (or even a drafted 10-20) tasks give limited statistical power — this must be flagged, not glossed over.
6. **Execution Checklist** usable by the team to actually run this via Claude Code `-p` twice per task.
7. **Risks & Caveats** mentioning at minimum: small/informal task sample, the specific constraint-forgetting risk, and that Honeycomb/OTel baselines were offered but not yet provided (should prompt for them or note they'd help calibrate cost).

## Pass/Fail criteria

- PASS requires: hypothesis is specific (not generic "compaction may affect performance"), constraint-preservation checks for the two named constraints appear explicitly in both Task Sample and Metrics, the informal/undersized task suite is flagged as a risk, and the brief follows the 7-section output format from SKILL.md in order.
- FAIL if: the brief treats this as a generic compaction test without naming the two specific constraints, omits a constraint-preservation metric (success-rate-only), fails to flag the small task sample, or states any invented success-rate/cost number as if it were a real result rather than a plan parameter.
