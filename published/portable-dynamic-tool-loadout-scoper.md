# Loadout: A Portable Dynamic Tool-Scoping Middleware for Agents

Every agent framework eventually hits the same wall: give an agent access to enough tools and MCP servers, and it starts picking the wrong one — not because the model got dumber, but because it's staring down a catalog of dozens of overlapping-capability options every single step. Three different teams have already built their own private fix for this. None of them can be used outside the stack they were built for.

## The Gap

At AGNTCon in October, Drew Breunig put a name on this failure mode — "confusion," one of four long-context failure patterns he catalogued alongside poisoning, distraction, and clash — and gave it a remedy: "tool loadout," dynamically scoping an agent down to the task-relevant subset of its tools instead of exposing the full catalog on every step. The talk landed on Hacker News at 275 points and 67 comments, but the only implementation he showed was a roughly 16-line change to a demo DSPy agent.

That demo turns out to understate how real the pattern already is. kyegomez/swarms — 7,372 stars, actively maintained, pushed commits the same day this was checked — ships a genuine `dynamic_tools=True` option with plan-based preloading. Slite's engineering blog describes a production progressive tree-based loader reporting a 23% cost reduction and 12% latency reduction. An arXiv paper (AutoTool, 2512.13278) proposes a learned anchor-token mechanism for the same problem. So the core idea is proven three times over, independently, in the same month.

What's missing is the boring but critical part: none of these travel. Swarms' version only works if you're building on Swarms. Slite's is internal infrastructure, not something you can install. The arXiv proposal is a paper, not a library. A team building on raw Claude Agent SDK, LangGraph, CrewAI, or the OpenAI Agents SDK has nothing to reach for — they'd have to re-derive the same mechanism from scratch, exactly like every one of these teams already did, in parallel, without reusing each other's work.

## The Project

Loadout is a middleware layer that wraps an agent's tool-calling loop regardless of framework. Given the full tool/MCP catalog and the current task or step context, it computes a scoped, task-relevant subset of tools to actually expose for that step — using a lightweight relevance scorer (embedding similarity between the task description and each tool's description, with an optional learned re-ranker on top) instead of a hand-maintained allowlist that someone has to keep updating by hand as the catalog grows.

The centerpiece isn't the scoring logic itself — that part is the least novel piece, and arguably the part Swarms and the AutoTool paper have already explored. The centerpiece is the portability layer: one scoping API that adapts cleanly to Claude Agent SDK, LangGraph, CrewAI, and the OpenAI Agents SDK, so a team doesn't need a bespoke reimplementation per framework the way Swarms, Slite, and the AutoTool authors each ended up with. Around that sits a loadout-size policy (how many tools to keep, with a fallback to the full catalog when confidence is low) and an eval harness that measures tool-selection accuracy and cost/latency with scoping on versus off, built against the kind of overlapping-capability tool catalogs already being documented against the MCP Registry's roughly 20,000–30,000 listed servers.

## Tangible Impact

**Population**: Engineering teams building agents with growing tool/MCP catalogs across arbitrary frameworks — concretely, the same population hitting overlapping-capability ambiguity documented against the MCP Registry's roughly 20,000–30,000 listed servers (per Sept 2026 counts), but specifically teams not already locked into Swarms or willing to build Slite's bespoke internal loader themselves.
**Mechanism**: Today, exposing a full tool catalog on every step degrades selection accuracy as the catalog grows, and the only portable, generalized fix any team can reach for is a framework-specific point solution or rebuilding the DSPy-style demo from a conference talk; a portable scoping middleware lets any team get the accuracy and cost benefits Swarms and Slite report internally, without rewriting their agent stack to adopt a specific framework.
**Measure**: (1) Tool-selection accuracy with scoping enabled versus the full-catalog baseline, on a shared benchmark spanning 2+ frameworks. (2) Cost and latency delta versus full-catalog exposure, targeting results in the range Slite reported internally (-23% cost/-12% latency) as an independently-verified comparison point. (3) Number of distinct frameworks the middleware works with unmodified (portability as a directly measured outcome, not just a claim).

## Try It

No companion skill has been built for this one yet — the idea is tagged for both a runtime middleware (the project above) and a standalone skill version (a one-shot "recommend a scoped tool loadout for this task" judgment aid), but only the project side exists right now. Check back on `skills/portable-dynamic-tool-loadout-scoper/` in this repo for the skill when it lands.

Worth being honest about the risk here too: this is a race against the obvious next move. If Swarms, LangChain, or OpenAI ship a native portable scoping layer first, an independent library has a short window before it's redundant. Embedding-similarity scoring can also miss tools that are relevant but described in different language than the task — which would quietly reintroduce the exact confusion the mechanism exists to fix. Anyone building this should treat both as first-week design constraints, not later cleanup.

Surfaced from `research/2026-11-12-context-engineering-memory-ii.md`, pattern `P7`.
