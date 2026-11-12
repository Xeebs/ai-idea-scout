# Agent-Scoped Credential Audit — Prompt Template

Paste this whole thing into any AI chat tool (Claude, ChatGPT, etc.) along with your integration details, and it will produce a minimal-privilege scope spec for an AI agent that currently holds (or is about to be given) a broad-scope credential.

## What this is

A one-shot design and audit exercise. It does **not** connect to any live system, does not issue or revoke any real credential, and does not perform the OAuth/API work itself. It reasons from a description you provide and hands back a draft policy — the same analysis a security engineer would do by hand before deciding how to scope an agent's API access, or before configuring a scoped-credential broker in front of that API.

Use it when:
- You're about to wire an AI agent into a production API, database, or SaaS tool and don't want to just hand it the existing full-privilege service-account key or admin token.
- You already have an agent running on a broad standing credential and want to know exactly what it actually uses versus what it was granted, before an incident forces the question.

Do not use it to debug a live auth failure, or to actually enforce anything — it's the paper exercise, not the broker.

## What you need to provide

**Data source: Manual.** You paste in a description — this tool does not read your API, your vault, or your IAM console directly. Specifically give it:

1. **The task(s) the agent performs** — plain language or pseudocode. Example: "Reads support tickets assigned to its session, drafts a reply, posts it as a comment, and if confidence is low, sets a status flag to escalate to a human."
2. **The actual API calls it makes today** — a list of endpoints/SDK methods/queries, or a short code excerpt. If you only have the task description, say so — the mapping will be weaker but still usable.
3. **The credential it currently holds and its scope** — e.g. "a service account with full read/write on the `tickets` and `customers` tables" or "a GitHub PAT with `repo`, `workflow`, `admin:org`." Never paste the actual secret value — only describe what it's allowed to do. (If you paste a real token by accident, it will be redacted and flagged, not echoed back.)
4. **Task cadence/duration** — how long one run takes and how often it fires (a single request, a 2-minute multi-step job, a background poller). This drives the expiry recommendation below.
5. Optional: **recent call logs** — these sharpen which granted permissions are actually used versus dormant.

If you don't give items 1–3, the assistant should ask for them rather than guess. If you don't give item 4, it should estimate conservatively (shortest defensible expiry) and say so, rather than block.

## What it does with your input

1. **Breaks the task into discrete actions.** Each distinct read/write/call gets its own line — "reads tickets" and "posts replies" are not merged into one blob, because they likely need different permissions.
2. **Maps each action to the narrowest scope the backend actually supports** — a specific endpoint and the tightest resource pattern available (one record ID, one named repo, a session-scoped filter), not "the whole table." If it's not sure whether the backend supports that granularity, it says "unverified — check the provider's docs" instead of guessing.
3. **Diffs that minimal set against your current credential's granted scope.** Anything granted but not used by any declared action goes on a flagged list, by exact name (e.g. `admin:org`, not "too broad"). If you mention the credential is shared with other scripts or integrations, it will note that tightening a shared credential breaks everything else using it — and recommend issuing this agent a dedicated scoped credential instead.
4. **Recommends an expiry (TTL)** tied to your stated task cadence — seconds-to-minutes for a single request, bounded to the job's own duration plus a small buffer for multi-step work. It will not suggest "no expiry" or a stock default like 24 hours or 90 days unless you've described a genuinely recurring background job and explained why a short-lived token per run won't work.
5. **Flags anything the backend can't scope natively** — e.g. a legacy API that only grants table-level access, or a classic (non-fine-grained) PAT — and marks it as needing proxy-level enforcement instead of pretending the backend handles it.
6. **Drafts a short YAML policy stub** mapping your task to the derived scope and TTL — a starting point for a human (or an actual credential-broker tool) to implement, explicitly marked as a draft to verify, not something already enforced.

## Output you should get back

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
```yaml
task_intent: <short id>
scope:
  - resource: <pattern>
    access: <read|write>
ttl_seconds: <n>
```
(Draft only — verify against the live backend's actual permission model before enforcing.)
```

## Rules it should follow (tell it these if it drifts)

- Never ask for, or repeat back, a real secret/token/key — only ask what it's allowed to do.
- Never claim a backend supports fine-grained scoping for a call it hasn't confirmed — say "unverified" instead.
- Never recommend an unbounded or stock-default TTL without your explicit justification for a recurring job.
- Never present the output as already enforced — it's a draft for a human (or a real broker) to implement and verify.
- Never collapse two different actions into one scope row — that's exactly how over-privilege hides.

## What this is not

This is not a running credential broker — it doesn't issue, store, rotate, or revoke tokens. If you need that, you're looking at building or adopting an actual broker service (short-lived, task-scoped token issuance with a revocation/audit log); this skill produces the scope spec you'd hand to one.
