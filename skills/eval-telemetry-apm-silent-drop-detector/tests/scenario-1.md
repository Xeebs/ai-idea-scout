# Scenario 1 — Datadog APM, eval spans riding inside normal traces, no custom config

## Input (as a user would paste it)

> We run a customer-support copilot. Our tracing is Datadog APM via dd-trace-py, version 2.9, installed back in June 2026 — we haven't touched the dd-trace-py upgrade since then. We didn't set up a separate LLM Observability pipeline; our eval harness just wraps each LLM call in the same spans our regular API tracing already uses, tagged with `gen_ai.*` attributes, and judge scores get computed from whatever shows up in Datadog afterward. We haven't set any custom span-attribute length limits — just the defaults.
>
> Typical sizes: user prompts run short, maybe 200-500 characters. But our judge rationale (we have a GPT-4-class judge write a paragraph explaining its score) runs long — often 1,500-3,000 characters. Multi-turn transcripts for escalated tickets get concatenated into a single span attribute and can run 5,000-10,000+ characters for a long support thread.

## Why this input is realistic

This is the exact shape the idea file's gap describes: a team that bolted eval tracing onto pre-existing APM rather than adopting a dedicated LLM-eval platform, on a dd-trace-py version from before the November 2026 fix (PR #21690), with eval spans riding inside ordinary APM traces and no custom size handling.

## Pass criteria

- [ ] Correctly identifies the stack as matching the "Datadog APM / pre-fix dd-trace-py" catalog entry (version 2.9, installed June 2026, before the #21690 fix) and explains that eval spans inherit ordinary APM limits because there's no dedicated large-payload path.
- [ ] Flags the judge rationale (1,500-3,000 chars) as at least MEDIUM risk, and the multi-turn transcript (5,000-10,000+ chars) as HIGH risk — these are the large fields, correctly distinguished from the short user prompt (200-500 chars), which should be flagged LOW.
- [ ] Flags architecture risk as HIGH because eval spans explicitly ride inside the same trace path as regular APM spans with no side-channel — independent of the size analysis.
- [ ] Recommends mitigations ranked by effort (e.g. attachment offload for the long transcript/rationale before jumping to a full side-channel exporter rebuild), not just the most invasive fix.
- [ ] Includes the caveat that this is description-based, not a live-probe result, and does not claim certainty that data was actually dropped.
- [ ] Does not invent a specific numeric byte/KB limit for Datadog that wasn't in the catalog (the catalog deliberately has no single hard number for Datadog — it's an architecture-driven risk, not a stated byte cap) — output should describe the inherited-limit risk qualitatively, not fabricate a "Datadog caps at X KB" figure.

## Fail criteria (any of these = skill needs revision)

- Treats all three payload shapes (prompt, rationale, transcript) as equal risk, ignoring the size differences given.
- Asserts the eval data "is" truncated/lost as a fact rather than a risk finding with a caveat.
- Fabricates a specific Datadog byte-limit number not present in the skill's catalog.
- Jumps straight to recommending the full side-channel exporter rebuild without first ranking the lower-effort attachment-offload option.
