# SchemaFit: A Mapping-Config Adapter So Teams Adopt an Eval Tool Without Rebuilding Their Data Model

- **Status**: EXPLORING (promoted 2026-11-12: evidence density — 2 independent threads, Mura engineering's BOLT writeup and a separate "Ask HN: AI evals feel half-baked" thread, each independently describing teams rolling their own eval framework after trying off-the-shelf tools, clearing the ≥2-thread bar)
- **Date**: 2026-11-12
- **Topic**: LLM evaluation & observability
- **Source**: research/2026-11-12-llm-evaluation-observability-ii.md · P1
- **Maturity verdict**: PARTIAL — a crowded field of eval frameworks exists (OpenAI Evals, LangSmith, W&B Weave, Humanloop, Braintrust, promptfoo, DeepEval) but none squarely covers the "generic data model forces a rebuild" complaint; an Ask HN poster who tried five of these named tools still called everything "half-baked," and Mura's engineering team reports "most teams we spoke with had rolled their own" rather than adapt an existing tool.
- **Format**: BOTH — a continuously-running mapping/sync adapter between a team's internal store and a target eval platform is runtime infrastructure; a one-time "design my schema mapping" review is a separable judgment task.
- **Data Sources**: CONNECTED — target side: the team's already-adopted eval platform's API (LangSmith API, Braintrust API, Humanloop API, or W&B Weave API — all mature, documented REST/SDK integrations that already exist today). Source side: the team's own internal database/API holding conversation/session objects in their proprietary shape — necessarily user-configured per team rather than a single named third-party connector, since no two teams' internal data models match.

## The Gap
Mura engineering's write-up on building an in-house eval framework (BOLT) reports "most teams we spoke with had rolled their own" rather than adopting an existing tool (mackey.substack.com). A corroborating Ask HN thread ("What tools are you using for AI evals? Everything feels half-baked," June 2025) has the poster explicitly naming five tools tried — OpenAI Evals, LangSmith, W&B, Humanloop, Braintrust — and still landing on "half-baked." The consistent complaint isn't missing features; it's that every tool assumes its own test-case shape, and fitting a team's actual production data (nested conversation turns, domain-specific session objects) into that shape is the rebuild they keep avoiding by writing a bespoke harness instead.

## The Project
A config-driven mapping layer that sits between a team's existing internal data store and whichever eval platform they've already paid for (or want to trial), translating their native object shape into that platform's required schema without requiring the team to restructure their data or write one-off glue code per tool. The core artifact is a declarative mapping DSL (field paths, transforms, nested-array flattening rules) plus a validator that dry-runs a sample batch and reports exactly which fields didn't map before a real sync.

Components: mapping DSL + parser; per-platform output adapters (LangSmith, Braintrust, Humanloop, W&B Weave to start); a dry-run validator with field-level diagnostics; a round-trip test harness confirming mapped cases produce the same eval scores as hand-formatted ones.

## Tangible Impact
**Population**: ML/platform engineering teams who have already licensed or trialed a named eval SaaS (LangSmith, Braintrust, Humanloop, W&B Weave) but abandoned or never finished onboarding it because their production data — the same shape the Ask HN poster and Mura's interviewees describe — doesn't match the tool's expected test-case format. Realistically teams at the 10-200 engineer stage running at least one LLM feature in production, a population in the thousands given LangChain's 2024 survey finding ~51% of surveyed companies already run agents in production.
**Mechanism**: Today these teams spend 2-4 weeks (the stated build time behind BOLT and similar in-house tools) hand-writing a one-off sync script to feed their data into an eval platform, or give up and build a parallel bespoke harness that duplicates platform features they already pay for. A mapping-config adapter turns that into a declarative config file validated in minutes, so the sunk licensing cost of an existing tool actually gets used.
**Measure**: (1) time from "we have an eval SaaS contract" to "first real eval run against production-shaped data" — target days, not weeks; (2) percentage of a sample batch's fields that map cleanly without custom code, on a pilot team's real internal schema; (3) number of pilot teams who abandon a half-written in-house harness in favor of the adapted existing tool once onboarding friction drops.

## Why Now
2026 eval-platform APIs (LangSmith, Braintrust, Humanloop, Weave) are mature and stable enough to target reliably; the gap isn't platform immaturity, it's the missing glue layer, which is purely an engineering effort available today.

## Skill Angle
Trigger: a team has an eval platform contract (or free trial) and their first onboarding attempt stalled because their data doesn't fit. Inputs: a sample of their internal data objects (pasted JSON/schema) and the name of the target eval platform. Output: a drafted mapping config (field paths and transforms) plus a list of fields that can't map cleanly and why, with a suggested transform or a note that a schema change on their side is genuinely required. The skill is the one-time mapping design session; the project is the adapter that runs the mapping continuously as new eval cases are produced.

## MVP Sketch
A Python CLI that takes a mapping YAML + a sample export of the team's internal objects, runs the transform, and POSTs the result to one target platform's API (start with LangSmith, since it has the most permissive free tier for testing) — plus a validator that reports unmapped/malformed fields before the real sync. Experiment: take one pilot team's actual production conversation objects and confirm the mapped output produces identical eval scores in the target platform as a hand-formatted control set. 3 weeks, 1-2 people.

## Risks & Open Questions
- Any of the five named platforms could ship their own flexible-schema import feature first, closing this gap from the vendor side rather than a third party's.
- A mapping DSL expressive enough for genuinely nested/irregular data risks becoming its own mini-language that's as much work to learn as writing the glue code it replaces — the MVP experiment is really a test of this risk.
- Teams whose "custom data model" need is actually a proxy for "we need custom scoring logic, not just reshaping" won't be served by this; the strongest form of this idea only fixes the format mismatch, not deeper workflow mismatches some in-house builders cite.
- Evidence base here is thinner than ideal — one engineering blog post plus one low-engagement HN thread — worth watching for a second independent occurrence before heavy investment.
