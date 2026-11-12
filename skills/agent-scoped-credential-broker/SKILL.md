---
name: agent-scoped-credential-broker
description: Audits an AI agent's API/credential integration and derives a minimal-scope, time-boxed permission spec (plus a flagged list of unused standing privileges) from its declared task — a design/review exercise for teams about to wire an agent into production APIs with a full-privilege key. Use before granting an agent integration standing access, or when reviewing one that already runs on a broad service-account key.
---

# Agent-Scoped Credential Broker (Design & Audit Skill)

## When to use this

Reach for this when someone is about to connect an AI agent to a production API, database, or SaaS integration — or already has one running — using a standing, broad-scope credential (a shared service-account key, a classic PAT with `repo:*`-style scopes, an admin DB login) and wants to know what the agent *actually needs*, versus what it's been handed. This is a one-shot design/audit exercise, not a running service: it does not issue, store, rotate, or revoke any real credential. It produces the policy spec a human (or an actual credential-broker service, if one exists) would then go implement.

Do not reach for this to debug a live authentication failure, or to perform any live API call — it only reasons from a description the user provides.

## Inputs

**Data source**: Manual — the user pastes a description of the integration (no live API/credential connector is read). Specifically, ask for:

1. **The task(s) the agent performs**, in plain language or pseudocode — e.g. "reads support tickets assigned to its session, drafts a reply, posts it, and if confidence is low, flips a status flag to escalate to a human."
2. **The actual API calls / SDK methods / queries it makes today** — a list of endpoints, GraphQL operations, DB queries, or a short code excerpt. If the user only has the task description and not the call list, proceed on the task description alone and say explicitly that endpoint-level mapping is weaker without it.
3. **The credential it currently holds and its granted scope** — e.g. "service account with full read/write on `tickets` and `customers` tables," "GitHub PAT with `repo`, `workflow`, `admin:org`." Never ask for the actual secret/token value — only the *scope/role description*. If a secret-shaped string is pasted anyway (a long opaque token, `ghp_...`, `sk-...`), do not echo it back; note it was redacted.
4. **Task cadence / duration** — how long one task run takes and how often it fires (single request, a 2-minute multi-step job, a background poller). This drives the TTL recommendation; if absent, ask before guessing a number.
5. Optional: **recent call logs or traces** — sharpens which granted permissions are actually exercised versus dormant.

If inputs 1–3 are missing, do not proceed with a fabricated scope — ask for them. Input 4 missing is the only gap you may flag-and-estimate conservatively (shortest defensible TTL) rather than block on.

## Procedure

1. **Decompose the task into discrete actions.** List every distinct read/write/call implied by the task description — do not merge "reads tickets and posts replies" into one blob; they are two actions with potentially different scopes.
2. **Map each action to a minimal API surface.** For each action, state the specific endpoint/method and the narrowest resource identifier pattern the backend's permission model actually supports (a single record ID, a session-scoped filter, a named repo) — not "the whole table" or "the whole repo" unless that really is the backend's finest grain. If you don't know whether the backend supports resource-level scoping for a given call, say "unverified — check provider's permission docs" rather than asserting a granularity you haven't confirmed.
3. **Diff against the current credential's granted scope.** Every permission present in the current scope (input 3) that no action from step 1 actually exercises goes on the **flagged over-privilege list**. Be specific (the exact scope string or table/permission name), not "too broad." If the user states the current credential is shared with other scripts/integrations, add a note that tightening a shared credential breaks everything else using it — a dedicated, task-scoped credential for this agent avoids that, which is a concrete reason to prefer issuing a new scoped credential over editing the existing one.
4. **Derive a TTL.** Base it on the stated task cadence from input 4: a single-request task gets a TTL on the order of the request's own timeout (seconds to low minutes); a multi-step job gets a TTL bounded to its declared or observed max duration plus a small buffer (e.g. +25%). Never recommend "no expiry" or a stock default (24h, 90 days) unless the user explicitly describes a recurring background job and justifies why a short-lived token can't be reissued per run.
5. **Call out non-scopable gaps.** If a backend has no native fine-grained permission for an action (e.g. a legacy API with only table-level grants, a classic GitHub PAT that can't be repo-scoped the way a fine-grained PAT can), say so explicitly and mark it "requires proxy-level enforcement" — i.e., the narrowing has to happen in front of the API (a scoped-proxy token or broker), not inside the backend's own permission model. Don't silently assume a native scope exists.
6. **Draft the policy stub.** Express the minimal-scope spec as a short YAML block mapping the declared task intent to the derived scope and TTL — this is a draft artifact a human would hand to whatever enforces it (a credential broker, an IAM policy, a PAT generation step), not something this skill applies itself.
7. **Self-check before returning**: every row in the minimal-scope table traces to an action named in step 1; every entry on the flagged list appears in the user's stated current scope but in no minimal-scope row; the TTL has a one-line rationale tied to the stated cadence, not a round-number default; every non-scopable gap is marked, not quietly scoped as if the backend supported it.

## Output format

```markdown
# Scoped-Credential Audit — <integration name>

## Task breakdown
| Action | What it does | Why it's needed |
|---|---|---|

## Minimal scope spec
| Endpoint / resource pattern | Access (read/write) | Justification (which action) | Native scope confirmed? |
|---|---|---|---|

## TTL recommendation
<value> — rationale: <tied to stated cadence>

## Flagged — granted but unused
- <exact permission/scope string> — not exercised by any declared action

## Non-scopable gaps (require proxy-level enforcement)
- <action/endpoint> — <why the backend can't scope this natively> — mitigation: <proxy/broker approach>

## Draft policy stub
\`\`\`yaml
task_intent: <short id>
scope:
  - resource: <pattern>
    access: <read|write>
ttl_seconds: <n>
\`\`\`
(Draft only — verify against the live backend's actual permission model before enforcing.)
```

## Guardrails

- Never ask for or echo back a live secret, token, or key value — only scope/role descriptions. Redact and flag any secret-shaped string pasted anyway.
- Never assert that a backend supports fine-grained scoping for an endpoint you haven't confirmed — mark it "unverified" rather than guessing.
- Never recommend an unbounded or default-stock TTL (24h, 90 days, "no expiry") without an explicit, stated justification for a recurring job.
- Never present this output as an enforced policy — it is a draft design/audit artifact for a human (or a real broker service) to implement and verify; this skill does not issue, store, revoke, or proxy any credential itself.
- Never merge distinct actions into one scope row to save space — under-decomposing hides exactly the over-privilege this exercise exists to catch.
