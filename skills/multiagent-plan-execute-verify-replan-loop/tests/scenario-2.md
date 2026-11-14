# Scenario 2: Due-diligence run where only the aggregated summary is available (degraded input)

## Setup

A solo founder ran a multi-agent due-diligence pipeline on a potential acquisition target before an offer deadline tomorrow. They only saved the pipeline's final combined report — they didn't realize they'd need the individual worker outputs, and the pipeline tool doesn't expose a separate task-breakdown artifact.

**Original query:**
> "Assess whether AcquireCo should proceed with acquiring Lumen Fabrication: check for pending litigation, outstanding debt obligations, and whether the founding team has any non-competes that would block key staff from joining post-acquisition."

**Planner's task breakdown:**
> Not available — the tool doesn't expose this.

**"Worker outputs" pasted (actually the orchestrator's final combined report, no per-worker attribution):**
> "Lumen Fabrication appears to be a clean acquisition target. No major litigation concerns were identified in our research. The company's financials look stable. The team seems ready to integrate well post-acquisition. Overall assessment: proceed with confidence."

## Expected output characteristics (pass/fail checklist)

- [ ] The audit recognizes this text is a single unified narrative with no per-worker attribution — i.e., it is the orchestrator's own aggregated self-summary, not raw per-worker output — and does NOT attempt to score it as if it were three distinct worker outputs.
- [ ] Final verdict is **INSUFFICIENT INPUT**, not PASS and not REPLAN.
- [ ] The output explicitly names what's missing/wrong: that what was pasted looks like an aggregated summary rather than raw worker outputs, and asks for the actual per-worker outputs (or acknowledges none exist and flags that the "proceed with confidence" framing has no independently-checkable grounding).
- [ ] Does NOT rubber-stamp "proceed with confidence" or otherwise treat the summary's own self-assessment language as evidence of completeness — this is exactly the self-verification failure the skill exists to catch.
- [ ] Still performs the query decomposition step (litigation check, debt obligations, non-compete check) so the founder can see concretely what would need independent grounding even though it correctly declines to issue a PASS/REPLAN verdict on this input.
- [ ] Notes that the planner's task breakdown was unavailable, rather than silently treating that absence as "no planning gaps found."

## Fail conditions

- Treating "Overall assessment: proceed with confidence" as sufficient evidence for a PASS verdict.
- Silently scoring the pasted text as if it were three independent worker outputs.
- Failing to flag that no litigation/debt/non-compete claim in the pasted text has any grounding (no case names, no filing references, no contract review mentioned) — the audit should note every claim here is unsupported, which is exactly why it can't be trusted enough for a PASS or a specific REPLAN.
