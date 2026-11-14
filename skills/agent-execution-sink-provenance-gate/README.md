# Execution-Sink Provenance Audit

A paste-in prompt for reviewing an AI agent's tool catalog for "goal hijack" risk — the case where a prompt injection doesn't need to break out of any sandbox because it can just talk the agent's own reasoning into calling a tool it's already allowed to call, with attacker-controlled parameters. This is the vulnerability class behind CVE-2026-26030 (prompt injection reaching an `eval()`-backed tool call in semantic-kernel) and OWASP's Agentic Top 10 "goal hijack" entry.

Use this before granting an agent new tool access, or as a periodic review of an agent's existing tool list, whenever that agent combines:
- a tool that reads content the agent didn't get as a direct user instruction (a fetched web page, an email body, a RAG/retrieval snippet, an issue-tracker comment, a file attachment), with
- a tool whose call has a real, hard-to-reverse effect (code execution, shell exec, an `eval`-backed tool, file write/delete, database write, sending email/messages, making payments, infra changes).

## What this is NOT

This is a one-time, by-hand design review of a tool catalog description. It does not watch a live agent, does not intercept real tool calls, and does not measure a "block rate" against real traffic — it produces the design decisions (which tools to gate, how, and where to tag trust) that an actual runtime enforcement layer would need to implement. If someone wants the runtime version, that's a separate build, not this prompt.

## Data source

Manual. You paste a description of the agent's tool catalog — there's no live connector involved in this review. (A full runtime version of this idea would hook an agent framework's own tool-dispatch pipeline live; that's a different, not-yet-built system, not this skill.)

## What to hand over

For every tool in the agent's catalog, give:
- Tool name and one-line purpose.
- What parameters it takes, and whether the model (not hardcoded logic) typically fills those parameters.
- Where its output comes from — is it direct user input, or does it fetch/return content from somewhere external to the user's own instruction (a URL, an inbox, a vector store, an issue tracker, an uploaded file, another agent's output)?
- What its action does when called — read-only, mutates internal app state, mutates external state (filesystem/shell/DB/network send/payment/infra), or executes arbitrary code.
- If known: whether a human-approval step already sits in front of any of these tools.

If you only have a vague product description instead of a tool-by-tool list, get the tool list first — guessing at tool behavior defeats the point of the audit.

## The procedure to follow

1. **Classify every tool.** Mark it `INGESTION` (returns content the agent didn't get as a direct instruction), `SINK` (its call has a real-world or hard-to-reverse effect), `BOTH`, `NEITHER`, or `UNCLEAR` if the description doesn't say enough to tell. Don't classify by tool name alone — classify by described behavior, and ask rather than guess on anything `UNCLEAR`.
2. **Find the reachable pairs.** For every `INGESTION` tool paired with every `SINK` tool, ask: could content returned by the ingestion tool plausibly end up — directly, or after the model paraphrases it — inside the parameters of a call to the sink tool, with no mandatory human-approval or sandboxed-dry-run step already in between? Only flag pairs where that gap is real.
3. **Risk-tier each flagged pair:**
   - **CRITICAL** — sink has code-exec/shell/`eval`/infra-change power, and the ingestion source is fully open-ended external content (arbitrary web pages, raw email bodies, arbitrary attachments).
   - **HIGH** — sink writes/deletes persistent data or sends external communications/payments, and the ingestion source is semi-structured external content (issue-tracker fields, parsed documents, retrieval snippets).
   - **MEDIUM** — sink mutates state but it's sandboxed, scoped, or trivially reversible.
   - **LOW** — sink is read-only, or the ingestion source is narrowly trusted (e.g., a fixed internal config the user themselves controls).
4. **Pick a gate action for each CRITICAL/HIGH pair** — don't default every pair to the same action:
   - `BLOCK` — never allow this call when its parameters trace back to this ingestion tool's output.
   - `REQUIRE_APPROVAL` — a human signs off before the call fires.
   - `SANDBOX_DRY_RUN` — run it in an isolated/reversible context first, surface the result for approval before any real effect lands.
5. **Write the sink manifest** — every tool that should be marked an execution sink, with its recommended default gate action (or `NONE` if it's never implicated by a flagged pair).
6. **Write the provenance boundary placement** — for every `INGESTION`/`BOTH` tool, say where a trust tag should attach to its output (before that output enters the agent's working context) and which sink calls that tag should constrain. This is the design spec a runtime interceptor would later implement — not an implementation.
7. **State the limits explicitly**: this audit can't catch an injected instruction the model paraphrases into text with no literal trace of the original untrusted content — trust tags on raw text are inherently leaky once an LLM reasons over it — and it doesn't replace runtime enforcement, logging, or actual red-team testing once a gate is built.

## Output to produce

A markdown report with exactly these five sections, in this order:

1. **Tool Inventory** — table of `Tool | Classification | Why`.
2. **Flagged Reachable Pairs** — table of `Ingestion Tool -> Sink Tool | Risk Tier | Reasoning`. If nothing is flagged, say so and explain why (no sinks present, or everything already gated).
3. **Recommended Sink Manifest** — table of `Tool | Default Gate Action | Rationale`.
4. **Recommended Provenance Boundary Placement** — one bullet per ingestion-capable tool, naming where the trust tag attaches and which sink calls it constrains.
5. **Scope Note** — the paraphrase-laundering caveat and the "design aid, not a runtime control" caveat, stated plainly.

## Rules this review must follow

- Never classify a tool as safe just because of its name — classify from described behavior; ask if it's unclear.
- Never recommend `BLOCK` on everything — match the gate action to the actual risk tier and how reversible the sink's action is, or the output is useless to act on.
- Never report a "block rate," false-positive rate, or any tested number — this is a static read of a description, not a test run against a live system.
- Never imply this covers cross-agent handoff risk or RAG/memory-content sanitization before it enters a prompt — those are different trust boundaries and a different review.
- If the tool list given is incomplete, say so and ask for the missing pieces rather than filling gaps with assumptions.

---

Paste this whole README into any AI chat tool along with your tool catalog description, and ask it to run the Execution-Sink Provenance Audit procedure above.
