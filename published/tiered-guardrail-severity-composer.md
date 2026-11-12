# Tier Gate: A Severity-Tiered Fail-Open/Fail-Closed Guardrail Composer

Most teams running LLM guardrails today have quietly backed themselves into the same bad trade: either every failing check blocks the whole response, or nothing does. A tone classifier flags a slightly stiff sentence and the user gets a generic "I can't help with that" — or a compliance check trips on something genuinely dangerous and the system logs it and moves on anyway, because the "block on any failure" switch got flipped off after one too many false alarms. The industry has converged on an obvious fix — let severity decide which checks fail open and which fail closed — but nobody has turned that idea into something you can install, configure, and trust.

## The Gap

Vendor engineering teams are all describing the same pattern independently in 2026: GMI Cloud writes up an 86M-parameter fast gate sitting ahead of an 8B hazard classifier, Openlayer publishes a how-to on layered enforcement with audit trails, and a live team inside `opendatahub-io/opendatahub-tests` (PR #2670) is refactoring its own NeMo Guardrails call patterns to better model exactly this kind of tiered behavior. The shape of the solution — safety and compliance categories fail closed, tone and formatting fail open — keeps showing up because it's the obvious answer to "which check gets to block the response?"

But every one of these is a single vendor's blog post or one team's internal refactor. There's no shared benchmark proving a given fail-open/fail-closed policy actually works, and no reusable library for composing conflicting verdicts across multiple checks. The underlying guardrail toolkits — NVIDIA's NeMo Guardrails (7.5k GitHub stars), Guardrails AI (7.6k stars), LLM Guard (3.2k stars) — are mature and actively maintained, and even a gateway like TrueFoundry ships a basic "enforce but ignore on error" per-validator mode. None of them expose severity-tiered composition as a named, reusable feature. What exists instead is cascading-latency advice and per-hook failure-mode guidance scattered across vendor blogs (Splunk, Coralogix) — guidance, not infrastructure.

## The Project

Tier Gate is a declarative policy composer that sits on top of the guardrail toolkits teams already run rather than replacing them. Instead of hand-rolling the logic that decides "this check failed, does the whole response die or not," teams write a YAML policy per category — `safety: fail-closed`, `compliance: fail-closed`, `tone: fail-open`, `formatting: fail-open` — and the composer orchestrates the classifier calls, resolves conflicting verdicts according to the declared tier ordering, and logs every composition decision for audit.

The centerpiece isn't the YAML format — it's the benchmark. A set of mixed-severity scenarios, each combining an adversarial high-severity flag with a benign low-severity one in the same response, run through a candidate policy to measure two numbers that actually matter: the false-block rate on low-severity cases, and the missed-hazard rate on high-severity ones. That's the thing nobody currently has — a way to prove your tiering logic is correct before it ships, instead of finding out it's wrong from an incident postmortem or a wave of user complaints.

## Tangible Impact

**Population**: engineering teams at mid-size AI product companies (customer support bots, internal copilots, agent platforms) running layered guardrail stacks — a proxy for scale is the combined ~18k GitHub stars across NeMo Guardrails, Guardrails AI, and LLM Guard, implying thousands of teams already composing multiple checks by hand.
**Mechanism**: today teams hand-roll ad hoc code deciding which failing check blocks a whole response vs. logs-and-continues; mistakes in this logic either over-block (user frustration, support cost) or under-block (safety incident). A declarative composer with a validated benchmark replaces bespoke glue code with testable policy and lets teams catch composition bugs before shipping, not after an incident review.
**Measure**: false-block rate on low-severity benchmark cases at equal-or-better missed-hazard rate on high-severity cases, compared against each team's current naive "block on any failure" logic; time to implement/change a severity policy (before vs. after adoption); count of production incidents traced to guardrail composition bugs post-adoption.

## Try It

No companion Claude Code skill exists for this idea yet — the project is tagged `Format: BOTH` in the idea file, and a design/review skill (one that reviews a team's existing guardrail categories and drafts a recommended severity-tier policy) is planned but hasn't been built this cycle. Check back in `skills/tiered-guardrail-severity-composer/` for that companion piece; for now, the MVP sketch in the idea file — a Python library over NeMo Guardrails/Guardrails AI/LLM Guard outputs, a YAML severity-tier config, and a 50–100 case mixed-severity benchmark — is the place to start building this by hand.

## The Honest Risk

The biggest threat to this project's reason for existing is that a guardrail vendor ships severity-tier composition as a native feature in a point release — NeMo or Guardrails AI absorbing this the way platforms tend to absorb glue-code categories once enough teams build the same workaround. It's also possible the composition math turns out to be simple threshold logic not worth productizing as a standalone library, and that without real multi-team production traffic, "better" composition stays a benchmark claim that doesn't generalize to someone else's traffic mix. Teams already juggling a guardrail stack may also just resist one more policy DSL on top.

---

Surfaced from `research/2026-11-12-ai-safety-and-guardrails-in-production.md`, pattern `P1`.
