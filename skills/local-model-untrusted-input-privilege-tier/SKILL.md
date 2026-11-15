---
name: local-model-untrusted-input-privilege-tier
description: Audits a local/small-model agent stack's tool grants against untrusted-input exposure — flags which tools an injected web page, email, or file upload could currently trigger, and recommends a trust-tier policy to cap the blast radius. Use when someone describes their local agent's tools and input sources and asks where it's exposed, before they build any enforcement.
---

# Local-Model Tool-Privilege Exposure Audit

## When to use this
Someone is running (or about to run) a local or small open-weight model (Llama, Qwen, Mistral, Phi, etc., via Ollama/vLLM/LM Studio/a raw transformers loop) inside an agent that both (a) reads content the model didn't originate — fetched web pages, inbound email, user-uploaded files, RAG documents, outputs from other tools or subagents — and (b) has tool access that does something beyond returning text (send email, write files, run shell commands, call paid APIs, post to a database, modify calendars/tickets). They describe this stack and ask something like "where is my agent exposed to prompt injection from the content it reads" or "should every one of these tools be callable no matter what fed the model its current context" — before writing any enforcement code. This is a one-time design review, not a running service: it produces a report, not a deployed policy engine.

Do not use this for pure content-level injection detection (classifiers that scan text for injection attempts) — that is a different, complementary layer. This skill only restricts which tools are reachable from which input provenance; it assumes some injections will get through and limits what they can reach.

## Inputs
**Data source**: Manual — the user describes/pastes their own stack: the tool list the agent can call, and which input channels feed each tool-call decision. This differs from the runtime enforcement version of this idea (the actual middleware that intercepts LangChain/LangGraph tool-dispatch or an MCP server's tool-call boundary in-process, which is Connected and persistent infrastructure); this skill is the one-time audit that happens *before* anyone builds that middleware, so it reasons only over what the user describes, not a live connector.

Required, in the user's own words or pasted from their code/config:
1. **Tool list** — every tool/function the agent can invoke, with a one-line description of what each one does.
2. **Input channels** — every source of content that reaches the model's context: direct operator/user instruction, fetched web pages, inbound email/chat messages, uploaded files, RAG retrieval over a corpus, outputs of other tools, outputs of other agents/subagents.
3. **Current reachability** — for each tool, what the user believes currently gates whether it can be called (nothing / a system prompt instruction / per-call human approval / something else). If they don't know, say so — the skill will default to the worst case rather than guess favorably.

Optional but useful: which model runs the tool-selection step, and whether any step already segments untrusted content away from the system/operator prompt (e.g., wrapping fetched content in a clearly delimited block vs. concatenating it directly).

## Procedure
1. **Classify every tool** on side-effect severity:
   - Read-only (no state change outside the conversation: search, summarize, fetch, read-file)
   - Reversible-write (state change that can be undone or has low blast radius: draft-save, add-calendar-tentative, label-email)
   - Irreversible/external-effect (send-email, post-publicly, transfer-funds, run-shell, delete-file, call a paid/rate-limited external API, modify production data)
   If a tool's severity is ambiguous from the description, ask one clarifying question rather than guessing it into a lower tier.
2. **Classify every input channel** as Trusted (direct operator/user instruction entered live, first-party config/code) or Untrusted (anything the agent reads that a third party authored or could influence: fetched web content, inbound email/messages, uploaded files, RAG docs from a corpus anyone can write to, tool/subagent output that itself ingested untrusted content upstream).
3. **Determine current reachability** per tool: which input channels, as described, can currently influence whether that tool gets called. If the user's architecture is a single-loop agent where the model decides every tool call from its full context window (the common case), treat every tool as reachable from every Untrusted channel present in the stack — this is the fail-closed default, not a convenience shortcut. Only mark a tool as "not reachable from untrusted input" if the user describes an actual existing gate (e.g., a hardcoded rule that `send_email` only fires on a literal operator slash-command, never on content from the fetch tool).
4. **Assign a risk flag** per tool using severity × reachability:
   - Irreversible/external-effect reachable from any Untrusted channel → **HIGH**
   - Reversible-write reachable from any Untrusted channel → **MEDIUM**
   - Read-only reachable from Untrusted, or any severity reachable only from Trusted channels → **LOW**
5. **Recommend a tier** per flagged tool: Trusted-only (full tool set, direct operator instruction required), Low-trust-readonly (only read-only tools callable when current context includes an Untrusted channel), or Escalation-required (the tool is genuinely needed from untrusted-triggered workflows — e.g., "read this email and file a support ticket" — so recommend a human-confirmation or explicit escalation step rather than a hard block). Never recommend a hard block for a HIGH-risk tool without checking whether the user's own stated use case actually needs that tool reachable from untrusted content — if so, it's an escalation case, not a block case.
6. **Call out residual risks** that tiering alone does not fix:
   - Provenance leak: if the user's description doesn't mention segmenting untrusted content from the system/operator prompt (e.g., a model could paraphrase fetched text into something that reads as an operator instruction), flag this explicitly — tagging a chunk's source logically is not the same as keeping it structurally separate in the prompt.
   - Escalation-path gap: any legitimate workflow that needs a tool triggered from untrusted content but has no confirmation step today.
   - Scope reminder: this audit does not detect injection content itself; a successful injection within the allowed tier can still happen, it just can't reach a higher tier.
7. **Write the report** in the Output format below. Every tool the user listed must appear in the table, including LOW-risk ones — an audit that silently drops tools it judged "fine" is not trustworthy.

## Output format
A single Markdown report:

```
# Tool-Privilege Exposure Audit — <stack name/date>

## Tool reachability table
| Tool | Side-effect tier | Reachable from untrusted input? | Current gating | Risk flag |
|---|---|---|---|---|
| <name> | Read-only / Reversible-write / Irreversible | Yes/No/Ambiguous | None/Partial/Full | HIGH/MEDIUM/LOW |
...one row per tool, no omissions...

## Recommended tier policy
trusted:
  allowed_tools: [<all tools>]
low_trust:
  allowed_tools: [<read-only tools only>]
escalation_required:
  tools: [<tools flagged Escalation-required>]
  condition: <what must happen before the tool fires from untrusted-triggered content>

## Residual risks (tiering does not fix these)
- <provenance-leak note, if applicable>
- <escalation-path gaps, if any>
- Content-level injection detection is a separate, complementary layer — this audit only limits blast radius, it does not detect injection attempts.

## Summary
<N> tools audited — <x> HIGH, <y> MEDIUM, <z> LOW. <one-sentence verdict, e.g. "3 irreversible tools are currently reachable from inbound email with no gating; tiering them would close the worst exposure.">
```

## Guardrails
- Never mark a tool's reachability as "No" (safe) based on an assumption — only mark it "No" when the user describes an actual existing gate; if genuinely unknown, mark "Ambiguous" and flag it rather than silently treating it as safe. Fail-closed, not fail-open.
- Never omit a tool the user listed from the output table, regardless of risk level.
- Never write or deploy actual enforcement code (middleware, hooks, policy engine) as part of this skill — that is the separate, persistent-infrastructure half of this idea. This skill produces a report only.
- Never claim the recommended tiering alone stops prompt injection — always state in the report that it limits blast radius assuming content-level detection sometimes fails, and does not replace it.
- Never guess which input channels reach which tools when the user hasn't described their architecture clearly enough to tell — ask one targeted clarifying question instead of producing a confident-looking but fabricated reachability table.
- Never recommend a hard block for a tool the user's stated use case genuinely needs reachable from untrusted content — recommend an escalation/confirmation step instead, and say so explicitly.
