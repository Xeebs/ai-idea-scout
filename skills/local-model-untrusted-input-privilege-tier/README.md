# Local-Model Tool-Privilege Exposure Audit

A self-contained prompt template for auditing a local/small-model agent's tool access against the untrusted content it reads — before you build any enforcement. Paste the block below into any AI chat tool (Claude, ChatGPT, etc.) along with a description of your stack, or drop this whole folder into a Claude Code `skills/` directory.

## Why this exists

If you're running a local or small open-weight model (Llama, Qwen, Mistral, Phi — via Ollama, vLLM, LM Studio, or a raw loop) inside an agent that both reads content it didn't originate (fetched web pages, inbound email, uploaded files, RAG documents, other tools' output) and has tool access that does something beyond returning text (send email, write files, run shell commands, call paid APIs, touch production data), you have a structural exposure: a successful prompt injection in that content can potentially trigger any tool the model can call. Small/local models are generally more injection-prone than frontier hosted models, which raises the stakes further.

Content-level injection filters (classifiers, decoys) help but sometimes fail. This audit assumes they will sometimes fail and instead asks: if an injection succeeds, what's the worst it could reach — and how do you cap that *before* you write any filtering code? It produces a one-time report, not a running policy engine. (The running version — middleware that actually enforces the tiers at your tool-dispatch boundary — is a separate build; this is the design review that tells you what to build.)

## What to hand over

Paste or describe, in your own words:

1. **Every tool your agent can call**, with a one-line description of what each one does (e.g., "send_email — sends an email on the user's behalf", "fetch_url — reads a web page, read-only", "run_shell — executes a shell command").
2. **Every input channel that reaches the model's context** — direct operator/user instruction, fetched web pages, inbound email or chat messages, uploaded files, RAG retrieval, outputs of other tools or subagents.
3. **What currently gates each tool call**, if anything — nothing, a system-prompt instruction, per-call human approval, a hardcoded rule, or "I don't know." If you don't know, say so explicitly; don't guess in your own favor.

Optional: which model makes the tool-call decision, and whether anything already keeps untrusted content structurally separate from the operator/system prompt (e.g., delimited blocks) versus just concatenated together.

## The prompt

```
You are auditing my local-model agent stack's tool access against untrusted-input exposure. Here is my stack:

TOOLS:
<list every tool and what it does>

INPUT CHANNELS:
<list every source of content reaching the model: direct instruction, fetched web pages, email, uploads, RAG, other tool/subagent output>

CURRENT GATING:
<for each tool, what currently restricts when it can be called — or say "nothing" / "I don't know">

Do the following:
1. Classify every tool by side-effect severity: Read-only, Reversible-write, or Irreversible/external-effect.
2. Classify every input channel as Trusted (direct operator instruction, first-party config) or Untrusted (fetched content, email, uploads, RAG docs, or any tool/subagent output that itself ingested untrusted content).
3. For each tool, determine whether it's currently reachable from an Untrusted channel. Default to "reachable" unless I've described an actual existing gate that prevents it — if it's genuinely unclear, mark it "Ambiguous" and ask me rather than assuming it's safe.
4. Flag each tool HIGH (irreversible + reachable from untrusted), MEDIUM (reversible-write + reachable from untrusted), or LOW (read-only, or only reachable from trusted input).
5. Recommend a tier for each flagged tool: Trusted-only, Low-trust-readonly, or Escalation-required (if my own use case genuinely needs that tool triggered from untrusted content, don't just recommend blocking it — recommend an escalation/confirmation step).
6. Call out residual risks tiering alone doesn't fix: whether untrusted content is structurally segmented from the operator prompt or just logically tagged (a model can paraphrase its way around a label), and any workflow that needs a tool from untrusted content with no confirmation step today.
7. Do not write enforcement code — just the audit report.

Output format:
- A table: Tool | Side-effect tier | Reachable from untrusted input? | Current gating | Risk flag — every tool I listed must appear, including LOW-risk ones.
- A recommended tier policy (trusted / low_trust / escalation_required groupings).
- A residual-risks section.
- A one-paragraph summary with counts of HIGH/MEDIUM/LOW and an overall verdict.

Guardrails: never mark a tool safe without an actual stated gate behind it (fail-closed, not fail-open); never drop a tool from the output table; never claim tiering alone stops injection — it limits blast radius, it does not replace content-level detection; never recommend a hard block where my use case needs the tool reachable from untrusted content — recommend escalation instead.
```

## What you get back

A Markdown audit report with a complete tool-by-tool reachability table (every tool you listed, no silent omissions), a recommended trust-tier policy grouping tools into trusted / low-trust-readonly / escalation-required, a residual-risks section (provenance-leak risk, escalation-path gaps, and the explicit reminder that this is blast-radius limiting, not injection detection), and a one-paragraph summary with HIGH/MEDIUM/LOW counts.

## What this is not

This is a design review, not a deployed defense. It tells you which of your tools are currently exposed to untrusted-input-triggered calls and what tier each should sit in — it does not install, hook into, or enforce anything in your running stack, and it does not detect injection attempts in content. Building the actual enforcement (a middleware hook at your tool-dispatch boundary, e.g. a LangChain/LangGraph callback or an MCP server's tool-call boundary, backed by a declarative tier policy file) is a separate, ongoing engineering task that this audit's output is meant to scope.
