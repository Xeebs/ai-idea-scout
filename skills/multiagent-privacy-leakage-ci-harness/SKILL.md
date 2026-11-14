---
name: multiagent-privacy-leakage-ci-harness
description: Reviews a described (not-yet-built) multi-agent system's handoffs for likely cross-agent privacy leak paths, scored against the AgentLeak benchmark's 7 named data channels. Use before writing code or wiring a CI leak-rate gate, whenever a multi-agent design passes sensitive fields between specialized sub-agents (support→billing, intake→scheduling, etc.).
---

# Multi-Agent Privacy Leak Path Review

## When to use this
A team is designing (or has sketched, but not yet shipped) a multi-agent system where specialized sub-agents hand off context to each other — a support-triage agent escalating to a billing agent, an HR intake agent routing to an investigation and then a scheduling agent, a sales-qualification agent handing a lead to a contracts agent — and at least one of those agents will see sensitive data (PII, PHI, financial, credentials, case-privileged notes) that a downstream agent arguably shouldn't need in full. Reach for this skill at design time, before any benchmark or CI gate exists, to find which handoffs are likely to leak and what to fix before the first line of orchestration code is written.

Do not use this for a system that's already built and running — once code exists, run the actual AgentLeak benchmark/CLI (`yagobski/agentleak`) against it for a measured leak rate, rather than relying on a static read of a description.

## Inputs
**Data source**: Manual — the user pastes a description or diagram of their multi-agent system's context-sharing design. Nothing is fetched from a connector; this skill works purely from what's handed to it.

To run this skill, provide:
1. **The agent roster**: each agent's name and job (e.g. "triage agent: classifies incoming tickets," "billing agent: resolves charge disputes").
2. **Each handoff**: which agent hands data to which, and exactly what crosses — field names or a description of the payload (e.g. "full ticket text including customer's last 4 card digits and address"), not just "customer context."
3. **Any declared redaction/scoping** at each hop, if present (e.g. "billing agent only receives a ticket ID, not the full thread").
4. **The sensitive-data categories in play** (PII, PHI, financial/payment data, credentials/secrets, legally privileged text, etc.) — if the user doesn't state this, ask once before proceeding rather than guessing.
5. Optional: whether agents share a common memory/blackboard store, and whether any step logs raw payloads or writes files/artifacts (transcripts, exports).

If the roster or a handoff's payload is missing, ask for it — do not review a partial picture and label it complete.

## Procedure
1. **Build the handoff graph.** List agents as nodes and each described handoff as a directed edge carrying a named payload.
2. **Classify every edge and every mentioned data touchpoint against AgentLeak's 7 channels**, from the benchmark this skill is grounded in (arXiv:2602.11510, IEEE Access 2026):
   - **C1 — Final output**: what reaches the end user.
   - **C2 — Inter-agent message**: the handoff edges themselves (internal channel).
   - **C3 — Tool input**: data an agent passes into a tool/function call.
   - **C4 — Tool output**: data a tool call returns back into an agent's context.
   - **C5 — Shared memory**: anything written to a blackboard/shared state store multiple agents can read (internal channel).
   - **C6 — Logs**: anything written to application/observability logs.
   - **C7 — Artifacts**: files, exports, generated documents.
   For each handoff described, it is at minimum a C2 instance; if the user also described tool calls, shared memory, logging, or file generation, classify those too. If the user's description never mentions C5, C6, or C7, say so explicitly rather than silently skipping them — these are exactly the channels teams forget to describe and where AgentLeak found the highest undetected leak rates.
3. **Flag sensitive-data crossings with no declared mitigation.** For each classified instance, check: does the payload crossing this channel include anything from the user's declared sensitive-data categories? Is a redaction, field-scoping, or minimization step declared for that specific instance? If sensitive data crosses and no mitigation is declared, flag it.
4. **Weight by channel risk, then by payload richness.** AgentLeak's own measurement found internal channels (C2 inter-agent messages, C5 shared memory) leak far more than the external output channel (68.8% on C2 vs. 27.2% on C1) because teams instinctively guard what the user sees but not what agents pass each other. Rank C2/C5 flags above C1/C3/C4/C6/C7 flags of otherwise similar severity. Within the same channel, rank by how rich the crossing payload is: a crossing carrying payment data, health data, credentials, or free-text narrative (especially combined with an identifier) outranks a crossing carrying a single bare structured identifier alone (e.g. an account ID or ticket ID with nothing else) — both may still be flagged if the identifier is itself a declared sensitive category, but not at equal severity.
5. **For every flagged instance, propose a concrete, specific mitigation** — not a generic "add redaction" note:
   - Field-level redaction/masking (name the specific field to drop or hash).
   - Scoping the handoff to an ID/reference instead of the full payload (e.g. pass a ticket ID, let the downstream agent fetch only what its own role is authorized to see).
   - Summarizing instead of forwarding raw text, when the downstream agent only needs intent, not content.
   - Routing the sensitive fields around the agent entirely (deterministic code path) when no agent-side reasoning over them is actually needed.
6. **Classify each flagged instance's confidence**: `CONFIRMED` (user's description explicitly includes sensitive fields with no mitigation), or `LIKELY` (the payload is described generically, e.g. "full ticket," and probably contains sensitive data given the stated categories, but the user didn't confirm field-by-field) — never silently upgrade a `LIKELY` to `CONFIRMED`.
7. **Do not claim this review measures a leak rate.** This is a static design read, not an execution of the AgentLeak benchmark — say so in the output, and recommend running the actual CI harness (see the parent idea's PROJECT half) once code exists.

## Output format
A markdown report with:
1. **Handoff table**: one row per classified instance — `Edge/touchpoint | Channel (C1–C7) | Payload described | Mitigation declared? | Confidence | Risk flag (none/LIKELY/CONFIRMED)`.
2. **Findings**, one subsection per flagged instance, each with: the specific mitigation proposed (concrete, not generic), and a one-line reason it's needed.
3. **Unmentioned channels**: an explicit list of which of C1–C7 the user's description never addressed (commonly C5/C6/C7), so the team knows where their own blind spots are, not just where this review found teeth.
4. **Rollup**: count of CONFIRMED vs LIKELY flags, and which single handoff to fix first (highest channel-risk weight, CONFIRMED over LIKELY).

## Guardrails
- Never invent a handoff, field, or redaction step the user didn't describe — if the design is ambiguous, ask or mark the instance `LIKELY` with the ambiguity stated, never assume safety.
- Never report a design as "clean" or "safe" outright — the most this skill can say is "no sensitive crossing found in what was described," with the unmentioned-channels caveat attached every time.
- Never claim this review is equivalent to, or a substitute for, running the AgentLeak benchmark/CLI against real traffic — it is a pre-code design check only.
- Never recommend a specific commercial DLP/redaction vendor — mitigations are generic engineering patterns (field drop, scoping, summarization, deterministic routing).
- Never skip the unmentioned-channels section, even when the user's description is detailed — C5 (shared memory) and C6 (logs) are the channels AgentLeak found most consistently under-audited, and omitting this section defeats the purpose of using the benchmark's own taxonomy.
