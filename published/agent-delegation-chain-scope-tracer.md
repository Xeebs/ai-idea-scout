# Scope Trace: Authorization & Failure Propagation Across Agent Delegation Chains

Every multi-agent system eventually delegates: a parent agent spawns a subagent, hands it a slice of trust, and waits for an answer back. The quiet assumption underneath that handoff is that the child inherited the right amount of trust and that if something went wrong, the parent would know. Neither assumption is being checked by anything shipping today — and a maintainer asking for exactly this fix, in their own open-source tool, is sitting unresolved right now.

## The Gap

On 2026-11-09, a GitHub issue filed against `NicoGenti/opencode-session-observability` (issue #4) said it plainly: "In OpenCode 2 multi-agent architectures, tasks are frequently delegated via subagent tool calls producing child sessions... Currently, `ObservabilityService.loadDataset` processes each session in isolation, meaning subagent failures are invisible" to the parent. That's not a hypothetical — it's the maintainer's own tool, describing its own blind spot, in a feature request that's still open.

It isn't an isolated complaint either. Three days earlier, `Luminous-Dynamics/luminous-platform` (issue #288, 11 comments) tasked a team with reproducing an academic benchmark — MasDrift, backing the paper "Benchmarking Authorization Preservation Across Multi-Agent Architectures" (arXiv 2608.07556) — specifically to study this same failure mode. One is a tool maintainer fielding a live request against their own observability dataset loader; the other is a team independently benchmarking the same problem academically. Neither has shipped a fix.

The honest state of the art, after a real multi-channel search (GitHub, web, papers): a benchmark artifact exists (`ZhuoningXu/MasDrift`), a second paper (arXiv 2606.09692) proposes an agent-aware observability gateway design, and there's scattered vendor/practitioner guidance (Cedar-based layered-policy writeups, nhimg.org) on re-checking scope per hop. But nobody has shipped a tool that does authorization-preservation *and* failure-propagation together. Everything found is a benchmark, a paper proposal, or advice — not a working fix a team could install today. That's a PARTIAL verdict, not OPEN, and it's worth being direct about the one outstanding risk: the opencode-session-observability maintainer could simply build this themselves inside their own repo, since the issue is filed against code they already own. If they do, this project competes with — or should defer to — that fix rather than duplicate it.

## The Project

The core idea is to stop treating "did the child stay in scope" and "did the child fail silently" as two separate problems, because in practice they're the same blind spot wearing two hats. A delegation-chain tracing middleware sits inside the framework's own delegation path — starting with OpenCode, the framework actually named in the evidence — and does two things at once: it attaches an immutable authorization-scope token to every delegation hop, so a parent can always answer "what privileges did this child actually have, and did it try to exceed them," instead of trusting that scope inheritance just worked; and it propagates a child's failure or scope-violation signal up to the parent's observability view in real time, closing the exact `ObservabilityService.loadDataset`-isolation gap the maintainer named.

The pieces: a scope-token wrapper around the framework's delegation call, a cross-session failure-propagation bus, a dashboard view rendering the delegation tree with scope and failure status annotated at every node, and — this is the part that keeps the whole thing honest — a MasDrift-benchmark runner. The project doesn't get to claim it works because it says so; it has to beat MasDrift's own documented drift scenarios, pass/fail, the same benchmark the Luminous-Dynamics team is independently reproducing.

## Tangible Impact

**Population**: Teams building production multi-agent systems on frameworks with subagent delegation (OpenCode, Claude Code subagents, LangGraph) who currently have no visibility into whether a delegated subagent silently exceeded its scope or failed without the parent noticing — the exact gap the opencode-session-observability maintainer is fielding a feature request for in the last 30 days, representative of any team running delegation-heavy agent fleets in production rather than single-agent prototypes.
**Mechanism**: Without this, a privilege-drifted or silently-failed subagent's bad output gets treated by the parent as a normal, trusted result — the parent has no signal to distinguish "child did its job within scope" from "child quietly did something it shouldn't have or failed partway" — so errors and scope violations propagate invisibly into whatever the parent does next; this project turns that invisible failure mode into a visible, alertable event at the exact hop it occurred.
**Measure**: (1) MasDrift benchmark pass rate (scope-preservation and drift-detection scenarios) before vs. after adopting the middleware; (2) mean time to detect a subagent scope violation or silent failure, from "never" (today's isolated-session baseline) to a bounded number of seconds; (3) in a pilot deployment, the fraction of delegation-chain incidents that the tool flags before they cause a downstream parent-level error, vs. the fraction only discovered after the fact via manual log inspection.

## Try It

A companion Claude Code skill is already built: [`skills/agent-delegation-chain-scope-tracer/`](../skills/agent-delegation-chain-scope-tracer/).

> Audits a multi-agent system's delegation/subagent-spawning code to find every call site where a child session implicitly inherits authorization scope instead of being explicitly narrowed, and every call site where a child's failure or scope violation has no path back to the parent.

This is the one-shot code-review half of the idea, not the always-on tracing middleware described above — it reads delegation code you paste in and tells you where scope is implicitly trusted or failures are swallowed, with a remediation for each finding. It won't catch runtime drift; for that you still need the project itself.

To use it: paste the contents of `skills/agent-delegation-chain-scope-tracer/README.md` into any AI chat tool along with your delegation/subagent-spawning source code, or drop the whole `skills/agent-delegation-chain-scope-tracer/` folder into `~/.claude/skills/` if you're running Claude Code.

---

Surfaced from `research/2026-11-12-multi-agent-architectures-ii.md`, pattern `P5`.
