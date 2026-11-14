---
name: agent-execution-sink-provenance-gate
description: Audits a described agent tool catalog for goal-hijack exposure — pairs of "reads untrusted external content" tools and "execution sink" tools with no trust boundary between them — and recommends a sink manifest and provenance-tag placement. Use before granting an agent broad tool access, or when reviewing an existing agent's tool list for prompt-injection-to-tool-call risk.
---

# Execution-Sink Provenance Audit

## When to use this
Use this when someone is about to grant an agent new tools, or wants a pre-deployment/periodic review of an agent's existing tool catalog, and the agent combines (a) any tool that reads content the agent didn't get as a direct user instruction — a fetched web page, an email body, a RAG/retrieval result, an issue-tracker comment, a file attachment — with (b) any tool whose call has a real-world, hard-to-reverse effect — code execution, shell exec, `eval`-backed tools, file write/delete, database write, sending email/messages, making payments, infra changes. That combination is exactly the "goal hijack" class behind CVE-2026-26030 (prompt injection reaching an `eval()` call in semantic-kernel) and OWASP's Agentic Top 10 goal-hijack entry: injected content doesn't need to escape a sandbox if it can talk the agent's own reasoning into calling a tool it's already allowed to call. Trigger phrases: "can you review our agent's tools for injection risk", "what should we gate before we turn on code-interpreter/shell access for this agent", "does our support bot's attachment-reading plus file-write setup have a hijack risk".

This is a one-time design/review aid done by hand. It is NOT the runtime enforcement layer — it does not intercept live tool calls or track provenance through a running agent's context. It produces the design decisions (which tools need gating, where the trust boundary goes) that a runtime interceptor would need to enforce. Say this explicitly in the output.

## Inputs
**Data source**: Manual — the user pastes a description of the agent's tool catalog. The parent project this skill is scoped from uses a CONNECTED data source for its runtime version (it hooks the agent framework's own tool-dispatch pipeline and content-ingestion adapters live), but that runtime interceptor is a separate, not-yet-built system. This skill only ever works from what's pasted in.

What to hand over, per tool in the catalog:
- Tool name and one-line purpose.
- What parameters it accepts and whether those parameters are typically filled from model reasoning (not hardcoded).
- Where its *output* comes from: is it direct user input, or does it fetch/return content from outside the user's own instruction (a URL, an inbox, a vector store, an issue tracker, an uploaded file, another agent's output)?
- What its *action* does when called: read-only / mutates internal app state / mutates external state (filesystem, shell, DB, network send, payment, infra) / executes arbitrary code.
- (If known) Whether a human-approval step already sits in front of any of these tools today.

If the user only gives a vague product description instead of a tool-by-tool list, ask for the tool list before producing the audit — do not guess at tool names or behaviors.

## Procedure
1. **Classify every tool** into one or more of: `INGESTION` (returns content the agent didn't get as a direct user instruction), `SINK` (its call has a real-world or hard-to-reverse effect: code exec, shell exec, `eval`, file write/delete, DB write/delete, external send, payment, infra change), `BOTH`, or `NEITHER` (e.g., a read-only internal lookup with no external content). When a tool's status is ambiguous from the description given, mark it `UNCLEAR` and ask rather than guess.
2. **Build the reachability pairs.** For every `INGESTION` tool, check every `SINK` tool: is there a plausible path, within this agent's own reasoning loop (not across agents/handoffs — that's a different gap), for content returned by the ingestion tool to end up, directly or after the model paraphrases/transforms it, inside the parameters of a call to the sink tool? Only flag pairs where no mandatory human-approval or sandboxed-dry-run step already sits between them per the user's description.
3. **Risk-tier every flagged pair:**
   - **CRITICAL**: sink has code-exec/shell/`eval`/infra-change power, AND the ingestion tool returns fully open-ended external content (arbitrary web pages, raw email bodies, arbitrary file attachments).
   - **HIGH**: sink writes or deletes persistent data, or sends external communications/payments, AND the ingestion source is semi-structured external content (issue-tracker fields, parsed documents, retrieval snippets).
   - **MEDIUM**: sink mutates state but the action is sandboxed, scoped, or trivially reversible (e.g., writes to a throwaway scratch directory).
   - **LOW**: sink is read-only, or the ingestion source is narrowly trusted (e.g., a fixed internal config the user controls, not arbitrary external content).
4. **For each CRITICAL/HIGH pair**, recommend a specific gate action: `BLOCK` (never allow this call when parameters trace to this ingestion tool's output), `REQUIRE_APPROVAL` (human sign-off before the call fires), or `SANDBOX_DRY_RUN` (execute in an isolated/reversible context first, surface the result for approval before any real-world effect). Pick based on how reversible the sink's action is and how open-ended the ingestion source is — don't default every pair to the same action.
5. **Write the sink manifest**: the list of tools the deploying team should mark as execution sinks, with each one's recommended default gate action from step 4 (or `NONE` if no flagged pair implicates it).
6. **Write the provenance boundary placement**: for each `INGESTION`/`BOTH` tool, state where a trust tag should be attached (at that tool's output, before its result enters the agent's working context) and which downstream sink calls that tag should block/gate per step 4 — this is the design spec a runtime interceptor would implement, not an implementation itself.
7. **Call out what this audit does not cover**: it does not catch an injected instruction that gets paraphrased by the model into text with no literal trace of the original untrusted content (provenance tags on text are inherently leaky through an LLM's own reasoning), and it does not replace runtime enforcement, logging, or red-team testing against the catalog once built.

## Output format
A markdown report with exactly these sections, in order:
1. **Tool Inventory** — table: `Tool | Classification (INGESTION/SINK/BOTH/NEITHER/UNCLEAR) | Why`.
2. **Flagged Reachable Pairs** — table: `Ingestion Tool -> Sink Tool | Risk Tier | Reasoning`. If zero pairs are flagged, say so explicitly and explain why (e.g., no sinks present, or all sinks already gated).
3. **Recommended Sink Manifest** — table: `Tool | Default Gate Action | Rationale`.
4. **Recommended Provenance Boundary Placement** — bullet list, one per INGESTION/BOTH tool: where the trust tag attaches and which sink calls it should constrain.
5. **Scope Note** — the paraphrase-laundering caveat and the "this is a design aid, not a runtime control" caveat from step 7, verbatim in substance.

## Guardrails
- Never mark a tool `SINK` or `INGESTION` by name alone (e.g., assuming anything called "search_tool" is safe) — classify from the actual behavior described; if behavior isn't described, ask.
- Never recommend `BLOCK` on every flagged pair by default — blanket-blocking execution sinks makes the audit useless to act on; match the gate action to the actual risk tier and reversibility.
- Never claim this audit measured or tested anything — it is a static read of a description, not a red-team run against a live system. Don't report a "block rate" or similar number; that only comes from actually building and testing the gate.
- Never treat this as covering cross-agent handoffs or RAG/memory sanitization — those are different gaps (a different trust boundary: between agents, or before content enters a prompt at all) and flagging them here as if this audit covers them would be misleading.
- If the user's tool list is incomplete or any tool's ingestion/sink status is genuinely unclear from what they gave you, say so in the Tool Inventory table as `UNCLEAR` and ask a follow-up — do not silently assume `NEITHER` to avoid asking.
