# Bridge Watch: A Protocol-Level Reliability and Observability Layer for ACP-to-MCP Tool-Call Bridges

- **Status**: PROPOSED
- **Date**: 2026-11-20
- **Topic**: Tool use & MCP ecosystem
- **Source**: research/2026-11-20-tool-use-mcp-ecosystem.md · P5
- **Maturity verdict**: OPEN — GitHub search for "ACP MCP bridge" turns up only point-to-point translation bridges (`oijkn/copilot-acp-mcp-bridge`, `krkr521/dsh-acp-mcp-bridge`, `yjloong/kimi-mcp-bridge`) that ARE the components that fail, not reliability/observability layers on top of them. A March 2026 arXiv field study proposes protocol-level primitives (timeout budgeting, structured failure semantics) and the official `agentclientprotocol.com` RFD addresses MCP-over-ACP error semantics, plus scattered blog posts on symptoms (hung calls, duplicate side effects on retry, inconsistent error typing across SDK versions) — but no implementation of a general cross-runtime bridge-reliability layer exists anywhere.
- **Format**: BOTH
- **Data Sources**: CONNECTED — wraps the bridge's own existing stdio/process interface (the ACP stdio bridge pattern already in production use by T3 Code, `copilot-acp-mcp-bridge`, and similar tools) on one side, and the standard MCP tool-call protocol on the other; both interfaces already exist and are mature integration points for any ACP-speaking runtime — no manual data entry needed beyond pointing the layer at the bridge binary/config it wraps.

## The Gap

A `pingdotgg/t3code` GitHub PR ("[FEATURE] Add Mistral Vibe support," 2026-11-06, 4 reactions/32 comments) states plainly: "the generic ACP Registry driver leaves gaps for Vibe users in T3 Code. Steering interrupts and restarts the active turn, Mistral plan usage is unavailable, and T3 MCP tool calls can fail through the ACP stdio bridge." This is one engineering team's own admission of a gap in their own product, and it is echoed structurally everywhere else a non-MCP-native agent runtime bridges in: every other bridge implementation found (`copilot-acp-mcp-bridge`, `dsh-acp-mcp-bridge`, `kimi-mcp-bridge`) is itself a narrow translation layer with the same failure shape, not a fix for it.

## The Project

A reliability-and-observability sidecar that any ACP-to-MCP translation bridge wraps itself in, rather than a replacement for any specific bridge. It adds: per-call timeout budgeting with explicit propagation (so a bridge-side hang surfaces as a typed timeout instead of an indefinite stall); idempotency-safe retry keyed on a stable call ID, so a retried call after a bridge crash can't silently duplicate a side effect; and a common failure taxonomy (timeout / malformed-translation / upstream-reject / duplicate-effect) that every wrapped bridge's raw, SDK-version-dependent error shape gets normalized into. Every tool call crossing the bridge boundary is traced, so a developer can see exactly where in the translation a call died — model side, bridge logic, or MCP server — instead of a flat "tool call failed."

## Tangible Impact

**Population**: Developers and maintainers of coding-agent runtimes that bridge a non-MCP-native model or provider (Mistral Vibe, Kimi, GitHub Copilot) into an MCP-speaking host via an ACP-style translation layer — concretely the T3 Code team behind the evidenced PR, and the authors/users of the three narrow point-to-point bridges found in this research pass. Downstream, the end users of those bridged coding agents who currently hit an undiagnosable "tool call failed" with no way to tell whether the model, the MCP server, or the bridge's own translation logic was at fault.
**Mechanism**: Today a tool call that dies inside a translation bridge surfaces as a generic failure — a hung call, a silently duplicated side effect on retry, an error type that varies by SDK version — with no standard way to localize the fault. A reliability layer imposes structured failure semantics and call-ID-keyed deduplication at the bridge boundary itself, converting an undiagnosable "it just failed" into a classified, traceable event a maintainer can act on and a caller can safely retry without risking a duplicate write.
**Measure**: % of a fixture suite of induced bridge failures (injected timeout, malformed upstream response, simulated process crash mid-call) correctly classified into the common taxonomy, versus the baseline of an undifferentiated error today; duplicate-side-effect rate on retried idempotency-marked calls before vs. after (target: zero); median time for a maintainer to localize a reported "tool call failed" bug to bridge-vs-server-vs-model using the trace versus ad hoc log reading.

## Why Now

Multiple independent runtimes are actively adding non-MCP-native provider support via ACP-style bridges right now (T3 Code's own PR is dated 2026-11-06), the `agentclientprotocol.com` RFD on MCP-over-ACP error semantics is a live, recent standards effort rather than a settled one, and the handful of point-to-point bridges that exist today give a concrete, inspectable surface to build the reliability layer against instead of a hypothetical one.

## Skill Angle

A standalone "diagnose this bridge failure" skill: hand Claude a bridge's raw error log or a captured failing tool-call transcript (request, the bridge's intermediate translation if available, and the raw error returned), and it classifies the failure against the common taxonomy, names the most likely fault location (model-side, bridge translation, or MCP server), and suggests the specific fix (add a timeout budget here, dedupe this retry path, normalize this error type). Usable standalone by a maintainer debugging one incident without deploying the always-on sidecar; differs from the project by being a one-shot forensic read rather than a continuously-running wrapper.

## MVP Sketch

3-4 weeks, 1-2 people: wrap one real open-source bridge (`copilot-acp-mcp-bridge` or `dsh-acp-mcp-bridge`) with the timeout-budgeting, call-ID dedup, and failure-classification layer as a drop-in process wrapper (no changes to the bridge's own code required). Experiment: inject a representative set of failures (kill the bridge process mid-call, return a malformed MCP response, simulate a double-send retry) and show the wrapped bridge reports a classified, traceable failure with zero duplicate side effects, versus the unwrapped bridge's undifferentiated error and observed duplicate writes.

## Risks & Open Questions

- The official `agentclientprotocol.com` RFD could formalize error semantics directly into the ACP spec itself, making a third-party reliability layer redundant once implementations catch up.
- Wrapping a bridge as an external process sidecar may not have visibility into failures that occur inside the bridge's own internal state machine (e.g. a corrupted in-memory session) without cooperation from the bridge's maintainers.
- Idempotency-safe dedup requires the underlying MCP server's tool calls to be meaningfully classifiable as idempotent or not — a server with undocumented side effects could still slip through.
- Evidence here is thin (one PR admission plus three narrow point bridges and a standards RFD) — if ACP-to-MCP bridging turns out to be a shrinking pattern (vendors adding native MCP support instead of bridging), the addressable population could be smaller than it looks today.
