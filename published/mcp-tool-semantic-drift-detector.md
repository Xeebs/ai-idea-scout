# Compat Watch: A CI-Integrated Semantic Drift Detector for MCP Tool Behavior Changes

An MCP server can break every agent calling it without changing a single character of its JSON schema. A tool's enum narrows from five accepted values to three. A response switches from returning dollars to cents. A pagination cursor starts behaving differently on the last page. Or — the subtlest one — someone just rewords the tool's description to read better, and that rewording is enough to shift which tool an LLM picks the next time it has a choice. None of that shows up in a schema diff. All of it ships silently to every downstream agent until a user gets a wrong answer and nobody can say why.

## The Gap

The fix for this has been "written up," not "built." Posts on [codex.danielvaughan.com](https://codex.danielvaughan.com/2026/05/28/mcp-server-versioning-backwards-compatibility-managing-breaking-changes/) and in [Gravitee's versioning/deprecation corpus](https://gravitee.io/corpus/gen-2286/833a/mcp-server-versioning-and-compatibility-management.html) describe the fix as a set of practices teams *should* adopt — pin versions instead of tracking `latest`, diff schemas in CI, publish a compatibility matrix — not a tool anyone actually runs. A [Hashnode post](https://hashnode.com/blog/mcp-stateless-migration) on the disputed 2026-07-28 MCP spec revision captures how unsettled the ground still is: sources can't even agree whether that revision is final, let alone how servers should version around it.

Meanwhile four small, independent teams converged on fragments of the same fix within weeks of each other: `mcp-contracts`/`mcpdiff` (snapshot/diff/validate with a GitHub Action, 8 stars, last push 2026-11-10), `mcp-compat` (a PyPI BREAKING/WARN/SAFE classifier with a `--ci` flag), `Bellwether` (a schema-drift CI check from dotsetlabs), and `Naim-arg/mcp-compatibility-checker` (a loadable/not-loadable check against MCP Inspector). All four do real work. All four do only schema diffing. None of them reads a tool's description for drift, and none replays an actual call to see if the *behavior* changed underneath an unchanged schema.

## The Project

Compat Watch snapshots an MCP server's full tool surface — JSON schema, natural-language description, and a small developer-supplied corpus of example calls with their expected-shape responses — as a versioned baseline. On a scheduled scan, it diffs the live server against that baseline across three layers, only one of which the existing point-tools cover:

1. **Structural schema diffs** — the layer `mcpdiff`, `mcp-compat`, `Bellwether`, and `mcp-compatibility-checker` already handle.
2. **Description-text drift**, via embedding distance — flags a reworded tool description likely to shift which tool an agent picks next time, a failure mode none of the four existing tools touches at all.
3. **Behavioral drift**, via replay — reruns the recorded example calls against the live server and diffs the actual responses, catching pagination changes, unit changes, and altered error handling that are invisible to a schema or a description alone.

Each detected change gets a BREAKING/WARN/SAFE classification. The whole thing runs as a GitHub Action and publishes a compatibility matrix across server versions — the CI-gate teams keep saying they should build, assembled once instead of per-team.

**Components**: baseline snapshotter · schema-diff engine · description-embedding-drift detector · behavioral-replay runner · BREAKING/WARN/SAFE classifier · GitHub Action / compatibility-matrix publisher.

## Tangible Impact

**Population**: teams consuming third-party or their own frequently-updated MCP servers in production agents — downstream consumers of any of the official MCP Registry's 20,000–30,000+ listed servers, and concretely the maintainers of the four existing point-tools, each independently building a fragment of this same fix within weeks of each other.

**Mechanism**: today a server update that changes behavior without changing its JSON schema ships silently; downstream agents keep calling the tool the same way and get subtly wrong results — wrong units, a now-rejected previously-valid enum value, different pagination — with no signal until a user notices a wrong answer. A gate that also catches description-drift and behavior-drift turns that into a pre-upgrade warning naming the specific diff, before it reaches production.

**Measure**: (1) percentage of reproduced silent-breaking-change scenarios — narrowed enum, changed units, altered pagination, reworded description — caught by the three-layer diff versus schema-diff alone; (2) false-positive rate on benign description rewordings that don't actually change tool-selection behavior; (3) number of MCP servers a pilot cohort successfully pins and monitors over a 30-day trial.

## Why Now

The MCP spec itself is mid-flux — the disputed 2026-07-28 stateless-migration revision, with sources disagreeing on whether it's even final — and the registry has scaled to tens of thousands of servers with no shared versioning discipline. That's exactly the condition under which four independent teams built schema-diff fragments within one month of each other, none of them yet combining all three drift classes.

## Try It

A companion skill, [`mcp-tool-semantic-drift-detector`](../skills/mcp-tool-semantic-drift-detector/), covers the one-shot version of this: *"Compares a before/after pair of pasted MCP server `list_tools` snapshots plus a description of how your integration calls the affected tools, and returns a BREAKING/WARN/SAFE classification that catches non-schema breaks (reworded descriptions, narrowed enums, changed units, altered pagination) that a plain schema diff misses."*

To use it: paste two JSON `list_tools` snapshots — one from before a version bump, one from after — plus a short description of how your integration currently calls the affected tool, into any AI chat tool using the skill's `README.md` as the prompt template. For Claude Code, drop the `skills/mcp-tool-semantic-drift-detector/` folder into `~/.claude/skills/` and invoke it directly. It's explicitly the manual, no-live-connection fallback — the full project above is the always-on, connected version that reads a live server and replays calls on a schedule.

## Worth Knowing

The honest risk here is a race: any of the four existing point-tools could add behavioral-replay diffing of their own and converge first, since nothing about that layer is exotic — this project's edge is being first to combine all three layers well, not having invented something the others can't eventually build. Behavioral replay also only works safely against read-only or idempotent calls; pointed at a tool with real side effects (sending an email, charging a card), the detector itself becomes the thing causing the damage it's meant to catch, so that scoping rule isn't optional. And description-drift detection is inherently fuzzy — get the embedding-distance threshold wrong and you either drown the gate in false positives on harmless copyedits, or miss exactly the subtle-rewording failure mode this project exists to catch.

Surfaced from `research/2026-11-13-tool-use-mcp-ecosystem-2.md`, pattern `P3`.
