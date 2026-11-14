# Multi-Agent Privacy Leak Path Review — portable prompt template

Paste this whole template into any AI chat tool (Claude, ChatGPT, Copilot Chat, etc.) along with a description of your multi-agent system, and it will work as a standalone design review — no other files or context needed.

## What this does

If you're designing a multi-agent system where specialized sub-agents hand data to each other — a support-triage agent escalating to a billing agent, an HR intake agent routing to an investigation agent and then a scheduling agent, a sales-qualification agent handing a lead to a contracts agent — some of those hand-offs probably carry more sensitive data downstream than the receiving agent actually needs. This review finds those hand-offs *before you write any code*, using the same 7-channel taxonomy as the AgentLeak academic benchmark (arXiv:2602.11510, IEEE Access 2026), which measured a 68.8% leak rate on inter-agent messages versus 27.2% on final outputs — i.e., the channel between agents leaks far more than what the end user sees, because teams instinctively guard the latter and forget the former.

This is a **static design read**, not a benchmark run. It can't tell you your actual leak rate — only where your described design is most likely to leak and what to fix. Once code exists, pair this with an actual CI-integrated benchmark run (e.g. wrapping `yagobski/agentleak`) for a measured number.

## What to hand over

Paste or describe:

1. **Your agent roster** — each agent's name and job. Example: "triage agent: classifies incoming support tickets," "billing agent: resolves charge disputes."
2. **Every hand-off** — which agent passes data to which, and *exactly* what crosses: field names or a specific description of the payload (e.g. "full ticket text including the customer's last 4 card digits and shipping address"), not a vague "customer context."
3. **Any redaction or scoping already planned** at each hop, if you have one (e.g. "billing agent only receives a ticket ID, not the full thread").
4. **The sensitive-data categories involved** — PII, PHI, financial/payment data, credentials/secrets, legally privileged text, etc. If you don't know, say so and the reviewer should ask before proceeding rather than guess.
5. Optional but useful: whether your agents share a common memory/blackboard store, and whether any step logs raw payloads or writes files/exports.

If your description is missing the roster or a hand-off's actual payload, the reviewer should ask for it rather than reviewing half a picture.

## The review procedure

1. **Build the hand-off graph** — agents as nodes, each described hand-off as an edge carrying a named payload.
2. **Classify every edge and touchpoint against these 7 channels** (from the AgentLeak benchmark):
   - **C1 — Final output**: what reaches the end user.
   - **C2 — Inter-agent message**: the hand-off edges themselves. *(Internal channel — historically the highest-leak one.)*
   - **C3 — Tool input**: data an agent passes into a tool/function call.
   - **C4 — Tool output**: data a tool call returns back into an agent's context.
   - **C5 — Shared memory**: anything written to a blackboard/shared state multiple agents can read. *(Internal channel — the other historically high-leak one.)*
   - **C6 — Logs**: anything written to application/observability logs.
   - **C7 — Artifacts**: files, exports, generated documents.

   Every hand-off is at least a C2 instance. If you mentioned tool calls, shared memory, logging, or file generation, those get classified too. If you never mentioned C5, C6, or C7 at all, the review should say so explicitly — these are exactly the channels teams forget to describe, and where the benchmark found leaks hide.

3. **Flag sensitive crossings with no declared mitigation** — for each classified instance: does the payload include anything from your declared sensitive-data categories, and is a redaction/scoping/minimization step declared for *that specific instance*? No mitigation + sensitive data crossing = flagged.

4. **Weight C2 and C5 flags higher** than C1/C3/C4/C6/C7 flags of similar severity — these are the internal channels that leaked 68.8% of the time in the benchmark precisely because they're invisible to end users and therefore under-guarded. Within the same channel, a crossing carrying payment data, health data, credentials, or free-text narrative outranks one carrying a single bare identifier alone, even if both technically fall under a declared sensitive category.

5. **Propose a concrete fix for every flag**, not a generic "add redaction" note:
   - Field-level redaction/masking — name the exact field to drop or hash.
   - Scoping to a reference/ID instead of forwarding the full payload (let the downstream agent fetch only what its role is authorized to see).
   - Summarizing instead of forwarding raw text when the downstream agent only needs intent, not content.
   - Routing sensitive fields around the agent entirely via deterministic code, when no agent reasoning over them is actually needed.

6. **Mark each flag's confidence**: `CONFIRMED` (you explicitly described sensitive fields crossing with no mitigation) or `LIKELY` (the payload was described generically and probably contains sensitive data given your stated categories, but wasn't confirmed field-by-field). Never silently promote a `LIKELY` to `CONFIRMED`.

## Output you should get back

1. **Hand-off table**: one row per classified instance — Edge/touchpoint | Channel (C1–C7) | Payload described | Mitigation declared? | Confidence | Risk flag.
2. **Findings**: one subsection per flagged instance, with the specific proposed fix and a one-line reason it matters.
3. **Unmentioned channels**: an explicit list of which of C1–C7 your description never addressed — usually C5/C6/C7.
4. **Rollup**: count of CONFIRMED vs. LIKELY flags, and which single hand-off to fix first.

## What this will never do

- Invent a hand-off, field, or redaction step you didn't describe. Ambiguity gets flagged `LIKELY` or asked about, never assumed safe.
- Declare your design "safe" or "clean" outright — at most, "no sensitive crossing found in what was described," always with the unmentioned-channels caveat.
- Substitute for actually running the AgentLeak benchmark/CLI against built, running code — this is a pre-code check only.
- Recommend a specific commercial DLP or redaction vendor.
- Skip the unmentioned-channels section, even on a detailed design — that's the part most likely to surface a real blind spot.
