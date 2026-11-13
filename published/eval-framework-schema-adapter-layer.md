# SchemaFit: A Mapping-Config Adapter So Teams Adopt an Eval Tool Without Rebuilding Their Data Model

Every team that ships an LLM feature eventually hits the same wall: they buy an eval platform, point it at their real production data, and discover that "onboarding" actually means a multi-week rebuild of their internal data model to match the tool's expected shape. So they quietly give up and write a bespoke harness instead — paying for a tool they never finish turning on.

## The Gap

Mura engineering's write-up on building their in-house eval framework, BOLT, puts it bluntly: "most teams we spoke with had rolled their own" rather than adopting an existing tool. That's not a shortage of options — a corroborating Ask HN thread ("What tools are you using for AI evals? Everything feels half-baked") has a poster who had already tried five named platforms — OpenAI Evals, LangSmith, W&B, Humanloop, and Braintrust — and still landed on "half-baked." The complaint in both cases isn't missing features. It's that every platform assumes its own test-case shape, and bending a team's actual production data — nested conversation turns, domain-specific session objects — into that shape is exactly the rebuild teams keep avoiding by writing a parallel bespoke harness instead of finishing the integration they already paid for.

The gap-analyst's verdict on this is PARTIAL, not OPEN, and it's worth being honest about why: the eval-tooling space is crowded. LangSmith, Braintrust, Humanloop, W&B Weave, promptfoo, and DeepEval are all real, maintained products. None of them squarely covers this specific complaint — the HN poster's "half-baked" framing came *after* trying five of them — but the risk that one of those vendors ships a flexible-schema import feature first and closes this gap from the inside is real and named explicitly in the idea file's own risk list. This is a bet that the glue layer stays missing long enough to matter, not a claim that the territory is empty.

## The Project

The fix isn't another eval framework — it's the missing layer between a team's existing data and whichever eval platform they've already licensed. The core artifact is a declarative mapping DSL: field paths, transforms, nested-array flattening rules, that describe how a team's native object shape becomes the shape a given platform expects. Paired with it is a dry-run validator that runs a sample batch through the mapping and reports exactly which fields didn't map — before anyone touches the real sync.

The components: the mapping DSL and its parser; per-platform output adapters starting with LangSmith, Braintrust, Humanloop, and W&B Weave; the dry-run validator with field-level diagnostics; and a round-trip test harness that confirms a mapped case produces the same eval score in the target platform as a hand-formatted control. None of this requires the eval platforms themselves to change — their 2026 APIs are mature and stable enough to target reliably today. The gap isn't platform immaturity. It's that nobody has written the adapter.

## Tangible Impact

**Population**: ML/platform engineering teams who have already licensed or trialed a named eval SaaS (LangSmith, Braintrust, Humanloop, W&B Weave) but abandoned or never finished onboarding it because their production data — the same shape the Ask HN poster and Mura's interviewees describe — doesn't match the tool's expected test-case format. Realistically teams at the 10-200 engineer stage running at least one LLM feature in production, a population in the thousands given LangChain's 2024 survey finding ~51% of surveyed companies already run agents in production.
**Mechanism**: Today these teams spend 2-4 weeks (the stated build time behind BOLT and similar in-house tools) hand-writing a one-off sync script to feed their data into an eval platform, or give up and build a parallel bespoke harness that duplicates platform features they already pay for. A mapping-config adapter turns that into a declarative config file validated in minutes, so the sunk licensing cost of an existing tool actually gets used.
**Measure**: (1) time from "we have an eval SaaS contract" to "first real eval run against production-shaped data" — target days, not weeks; (2) percentage of a sample batch's fields that map cleanly without custom code, on a pilot team's real internal schema; (3) number of pilot teams who abandon a half-written in-house harness in favor of the adapted existing tool once onboarding friction drops.

## Try It

A companion skill already exists at [`skills/eval-framework-schema-adapter-layer/`](../skills/eval-framework-schema-adapter-layer/): "Drafts a field-by-field mapping config (plus a dry-run preview and an unmapped-fields report) that translates a team's internal conversation/session data shape into the schema a named eval platform (LangSmith, Braintrust, Humanloop, or W&B Weave) expects, so a stalled eval-tool onboarding has a concrete next step instead of a bespoke glue script."

This is the one-time *design* half of the idea — it drafts a mapping, it doesn't run one. To use it: paste the [README.md](../skills/eval-framework-schema-adapter-layer/README.md) prompt template directly into any AI chat tool along with your target platform name and a sample of your own data objects (redact PII first), or drop the `skills/eval-framework-schema-adapter-layer/` folder into `~/.claude/skills/` if you're running Claude Code. Either way, you get a draft mapping config and a list of exactly which fields won't map cleanly, before you spend a week finding that out the hard way.

---

Surfaced from `research/2026-11-12-llm-evaluation-observability-ii.md`, pattern `P1`.
