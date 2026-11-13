# Compat Watch: A CI-Integrated Semantic Drift Detector for MCP Tool Behavior Changes

- **Status**: EXPLORING (promoted 2026-11-13 cycle 56: evidence density — ≥2 independent threads)
- **Date**: 2026-11-13
- **Topic**: Tool use & MCP ecosystem
- **Source**: research/2026-11-13-tool-use-mcp-ecosystem-2.md · P3
- **Maturity verdict**: PARTIAL — young CI schema-diff tools already attempt this exact gap: `mcp-contracts`/`mcpdiff` (snapshot/diff/validate with a GitHub Action; 8 stars, last push 2026-11-10), `mcp-compat` (PyPI, BREAKING/WARN/SAFE classifier, `--ci` flag), `Bellwether` (dotsetlabs, schema-drift CI check), and `Naim-arg/mcp-compatibility-checker` (loadable/not-loadable checker against MCP Inspector). All narrow, brand-new, single-digit-star, no evidence of adoption.
- **Format**: BOTH — the continuous baseline/scan/CI-gate pipeline is persistent infrastructure; a one-off pre-upgrade diff on two pasted snapshots is a separable one-shot task.
- **Data Sources**: CONNECTED — reads the target MCP server's live tool definitions directly via the standard MCP `list_tools`/`call_tool` protocol methods (mature, spec-defined, already implemented in every MCP SDK) to build baselines and run behavioral replay. The Skill Angle accepts pasted JSON snapshots when no live connection is available.

## The Gap
MCP server maintainers can change a tool in ways that break calling agents without the JSON schema itself changing — altered side effects, pagination semantics, error handling, a narrowed enum, changed units, or a reworded description that shifts which tool an agent picks. [codex.danielvaughan.com](https://codex.danielvaughan.com/2026/05/28/mcp-server-versioning-backwards-compatibility-managing-breaking-changes/), [Gravitee's corpus posts](https://gravitee.io/corpus/gen-2286/833a/mcp-server-versioning-and-compatibility-management.html), and a [Hashnode post](https://hashnode.com/blog/mcp-stateless-migration) on the disputed 2026-07-28 MCP spec revision all describe fixes as "teams should do X" (pin versions, diff schemas in CI, publish a compatibility matrix), not a named adopted tool. Four independent young tools now attempt schema-diffing alone; none replay behavior or flag description drift.

## The Project
A tool that snapshots an MCP server's full tool surface — JSON schema, natural-language description, and a small developer-supplied corpus of example calls/expected-shape responses — as a versioned baseline. On each scheduled scan it diffs the live server against that baseline across three change classes existing tools don't combine: (1) structural schema diffs (the layer mcpdiff/mcp-compat/Bellwether/mcp-compatibility-checker already cover), (2) description-text drift via embedding distance, flagging reworded descriptions likely to shift downstream tool-selection behavior, and (3) behavioral drift inferred by replaying the recorded example calls against the live server and diffing actual responses — catching pagination, unit, and error-handling changes invisible to schema or text alone. Outputs a BREAKING/WARN/SAFE classification per change, runs as a GitHub Action, and publishes a compatibility matrix across server versions.

Components: baseline snapshotter · schema-diff engine · description-embedding-drift detector · behavioral-replay runner · BREAKING/WARN/SAFE classifier · GitHub Action / compatibility-matrix publisher.

## Tangible Impact
**Population**: teams consuming third-party or their own frequently-updated MCP servers in production agents — downstream consumers of any of the official MCP Registry's 20,000-30,000+ listed servers, and concretely the maintainers of the four existing young point-tools (mcpdiff, mcp-compat, Bellwether, mcp-compatibility-checker), each independently building a fragment of this same fix within weeks of each other.
**Mechanism**: today a server update that changes behavior without changing its JSON schema ships silently; downstream agents keep calling the tool the same way and get subtly wrong results (wrong units, a now-rejected previously-valid enum value, different pagination) with no signal until a user notices a wrong answer. A gate that also catches description-drift and behavior-drift turns that into a pre-upgrade warning naming the specific diff.
**Measure**: (1) percentage of reproduced silent-breaking-change scenarios (narrowed enum, changed units, altered pagination, reworded description) caught by the three-layer diff vs. schema-diff alone; (2) false-positive rate on benign description rewordings that don't change tool-selection behavior; (3) number of MCP servers a pilot cohort successfully pins and monitors over a 30-day trial.

## Why Now
The MCP spec itself is mid-flux (the disputed 2026-07-28 stateless-migration revision, with sources disagreeing whether it's final) and the registry has scaled to tens of thousands of servers with no shared versioning discipline — exactly the condition under which four independent teams built schema-diff fragments within one month, none yet combining all three drift classes.

## Skill Angle
Paste two JSON snapshots of an MCP server's tool list (today's `list_tools` output next to a saved copy from before a version bump) plus a short description of how the integration currently calls the tool, and get back a classified diff (BREAKING/WARN/SAFE) naming the specific risk — narrowed enum, reworded description, changed units — as a one-time pre-upgrade check without adopting the full CI pipeline.

## MVP Sketch
2-4 weeks, 1-2 people. Build a CLI that snapshots a target server's tools + schemas + descriptions + 10-20 developer-supplied example calls; on re-run, diffs schemas (reuse an existing JSON-schema-diff library), computes description-embedding distance, and replays example calls against the live server diffing response shape/values; classifies each change and emits a GitHub Action report. Experiment: take 3 real, actively-maintained MCP servers, intentionally introduce the exact non-schema breaking changes named in the evidence, and measure catch rate vs. schema-diff alone.

## Risks & Open Questions
- The four existing young point-tools could each independently add behavioral-replay diffing and converge first — this project's differentiation rests on being first to combine all three layers well.
- Behavioral replay needs live, side-effect-safe example calls against the target server; tools with real side effects (e.g., sending an email) need a strict "read-only/idempotent calls only" scoping rule or the detector itself causes the damage it's trying to catch.
- Description-embedding-drift flagging is inherently fuzzy — tuning the threshold between a harmless copyedit and a behavior-shifting rewording risks either noisy false positives or missing the exact subtle-rewording failure mode the evidence names.
- The MCP spec's own mid-flux state means the baseline-snapshot format may need to track spec version, adding scope beyond the MVP.
