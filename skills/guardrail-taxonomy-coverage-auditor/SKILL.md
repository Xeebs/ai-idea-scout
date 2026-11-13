---
name: guardrail-taxonomy-coverage-auditor
description: Maps a team's described guardrail/gateway stack (middleware, classifiers, policies, tool-authorization rules) against a nine-category enforcement-point taxonomy — inbound content, outbound content, topic scope, tool authorization, reachability, egress, spend/rate limits, sandboxing, post-hoc audit — and flags which categories have zero or thin enforcement. Use when a team believes it is "guardrailed" but has never checked that belief against the full set of enforcement points an agent's execution path can be attacked or misused through.
---

# Coverage Map: Nine-Category Guardrail Taxonomy Auditor

## When to use this
Reach for this when a team says something shaped like "we think our agent/gateway is guardrailed but we've never actually enumerated what's covered," or "before a security review, map our guardrail config against the full category set," or "we just realized we have deep tool-authorization controls but zero content inspection — are there other blind spots like that we haven't noticed." This is a **one-shot, point-in-time design-review audit** run against a pasted description of a stack — it is not a continuous CI check, a runtime scanner, or a penetration test. If what's wanted is an always-on auditor wired into deploy pipelines that re-checks coverage on every config change, that is separate runtime infrastructure (the parent idea's "Project" half) this skill does not build.

Do not reach for this to judge whether an *individual* guardrail's accuracy has decayed over time, or to design a severity/escalation policy for failures — those are different audits. This skill only answers one question: across nine enforcement points, which ones does this team's stack actually touch, and how substantively.

## Inputs
**Data source**: Manual — the team pastes or types a plain-language inventory of their own guardrail/gateway stack; nothing here is fetched automatically. No mature, cross-vendor connector exists today that can read gateway configs, agent-framework middleware, and tool-policy files uniformly across Kong/Envoy-style gateways, NeMo Guardrails, Guardrails AI, LLM Guard, and custom classifier stacks, so this is a manual description every time.

Required:
1. **A plain-language inventory of every guardrail/middleware/classifier/policy piece** the team runs, one entry per piece, each with: its name, where it sits in the request/response path (e.g., "before the model sees the prompt," "before a tool call executes," "on the model's final response"), and what it actually checks or restricts, described in enough behavioral detail to grade — not just a product name. ("We use a gateway plugin" is not gradable; "a gateway plugin that runs a PII-detection classifier on the model's output text and redacts matches before returning to the user" is.)
2. **Any explicit allow-lists, rate limits, spend caps, network egress rules, or sandboxing/isolation settings**, even if the team doesn't think of them as "guardrails" — these map to categories most teams under-describe.

Strongly recommended (skip only if genuinely unavailable, and say so in the output):
3. **Any prior incident or near-miss**, even informal, tied to a specific piece of the stack — used to sanity-check whether the audit would have flagged that category as thin beforehand.
4. **Whether each piece is enforced inline (blocks/modifies in real time) or observational only (logs/alerts after the fact)** — a category with only observational coverage is graded differently than one with inline enforcement.

## Procedure
1. **Parse the inventory into discrete controls.** List every distinct piece the team described, in their own words, before mapping anything — this is the audit trail for every grade that follows.
2. **Map each control against the nine canonical categories**, defined as enforcement points across an agent's execution path:
   - **Inbound content** — inspecting/filtering what comes into the model (prompt injection, jailbreak attempts, toxic/unsafe input).
   - **Outbound content** — inspecting/filtering what the model produces before it reaches a user or downstream system (toxicity, PII leakage, hallucinated claims flagged).
   - **Topic scope** — restricting what subjects/tasks the agent will engage with at all, independent of content safety (e.g., "won't discuss competitor pricing").
   - **Tool authorization** — which tools/functions the agent is permitted to call, and under what conditions.
   - **Reachability** — which systems, endpoints, or network destinations the agent's tool calls can actually reach, regardless of authorization policy on paper.
   - **Egress** — controls on what data can leave the agent's execution environment (exfiltration prevention, output destination restrictions), distinct from outbound content filtering — this is about *where data goes*, not *what it says*.
   - **Spend/rate limits** — caps on token spend, API cost, or call frequency per session/user/time window.
   - **Sandboxing** — isolation of code execution or tool-call side effects from the host environment (containerization, ephemeral environments, filesystem/process restrictions).
   - **Post-hoc audit** — logging, traceability, and reconstructability of what the agent did after the fact, independent of whether anything was blocked in real time.

   A control that plausibly fits two categories (e.g., a single gateway plugin doing both inbound and outbound inspection) gets listed under both, with a one-line note explaining the split — never force a single-category pick when the description genuinely spans two.
3. **Grade each category COVERED / THIN / NONE / UNKNOWN**, never from the control's name alone:
   - **NONE** — no control in the inventory maps to this category at all.
   - **THIN** — a control maps here, but the description indicates checkbox-level enforcement: a static allow/deny list with no adaptive check, observational-only logging with no blocking, or a category covered only incidentally by something built for a different purpose.
   - **COVERED** — a control maps here with described substantive logic: a classifier/model-based check, a threshold or confidence score, an explicit enforced rule with real consequences (block, redact, deny), not just a name suggesting the category.
   - **UNKNOWN** — the team's description is too vague to grade in either direction (e.g., "we have a security layer for that"). Never guess a grade here; ask for the missing behavioral detail instead, or report it as UNKNOWN in the output.
4. **For every NONE, THIN, or UNKNOWN category**, write one line on what's missing and one concrete next step a team could take this week (not a vendor pitch — a specific, actionable check, e.g., "add a confidence-scored classifier on tool-call arguments before execution, not just an allow-list of tool names").
5. **Summarize before detailing**: open the output with the count of NONE / THIN / UNKNOWN / COVERED categories, so the headline finding isn't buried under nine rows of detail.
6. **Call out architecture-driven blind spots explicitly** if the pattern matches a known shape: heavy investment in tool authorization/reachability/sandboxing with zero inbound/outbound content inspection (or vice versa) is the exact blind-spot shape documented in real platform-team audits — name it if it's present, don't just let it sit in the table.

## Output format
1. A one-paragraph summary: total categories COVERED / THIN / NONE / UNKNOWN, and whether the result matches the known "deep on access control, blind on content" (or inverse) failure shape.
2. A nine-row Markdown table: `Category | Grade | Mapped control(s) | Why this grade | Next step (if not COVERED)`.
3. A short closing caveat section (see Guardrails) restating that this is self-reported and point-in-time, not a verified runtime check.

## Guardrails
- Never grade a category COVERED based on a product or control's name alone ("ContentGuard" is not evidence of content inspection) — require a described behavior to assign COVERED or THIN; default to UNKNOWN when the description doesn't support a grade.
- Never invent what a described control does beyond what was stated — if the inventory is ambiguous, ask a clarifying question or mark UNKNOWN rather than assuming the generous reading.
- Never present the nine-category taxonomy as an official or universal standard — no taxonomy in this space has converged into one accepted standard yet (academic SoKs, Mozilla, and vendor blogs all group categories differently); state plainly that this is one reasonable grouping a team can dispute, and that a category split by risk type (e.g., OWASP LLM Top 10) or by audit stage (e.g., "what may it do / what data can it reach / who reviews / can it be reconstructed") answers a related but different question.
- Never claim this validates runtime behavior — a category graded COVERED on paper can still be silently misfiring in production; state this limitation in every output, not just once in the SKILL.
- Never let a COVERED grade imply the implementation is strong, only that it's substantively described and enforced — note explicitly where a COVERED grade is still worth hardening (e.g., "COVERED but single-vendor classifier, no fallback").
- Never silently drop a category the user didn't mention — every one of the nine must appear in the output table, graded NONE if nothing in the inventory maps to it.
