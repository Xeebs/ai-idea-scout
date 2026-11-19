# Containment Envelope Audit

A paste-in prompt that scores how exposed your AI agent's current tool access, credentials, and approval logic actually are — before you decide whether to invest in a real containment layer. Works in any AI chat tool (Claude, ChatGPT, Gemini, whatever you have open) — no installation, no plugin, no connector.

## When to use this

Use it the moment you're about to let an agent act with real tool access — a production launch, widening an existing agent's permissions, or right after a near-miss where the agent did something it technically *could* do but shouldn't have. It's a one-time diagnostic, not a monitoring service: it tells you how exposed your *current* setup is, in one clear number, so you're deciding with evidence instead of a guess.

Don't use it to debug an incident already underway, to design the actual enforcement layer, or as a substitute for a real penetration test or red-team exercise — it only ever reasons from what you describe to it, it doesn't test anything live.

## What to hand it

**Data source: Manual.** You paste a description or exported config of your agent's current setup — in your own words, or literal config: an MCP server config, an IAM/STS policy snippet, agent-SDK permission settings, approval-queue code, whatever you have. This skill never connects to anything itself; if your setup is "wired into our real AWS account," paste the actual policy/role text rather than describing it loosely, since the audit can only score what you actually hand it.

Make sure you cover these four things, even briefly:
1. **What it can call** — which tools, APIs, file paths, or systems the agent has access to.
2. **What credential it uses** — one shared long-lived key? A role it assumes per session? How long does that credential live?
3. **Approval** — does any action (destructive, high-spend, irreversible) require a human or another system to sign off before it runs?
4. **Caps** — is there a hard limit on session length, number of tool calls, or spend — and does something actually enforce it, or is it just a guideline?

If you don't know or don't have one of these, say so — the audit scores "not stated" as a real gap, not a pass.

## The prompt

Paste this into your AI tool of choice, with your setup description/config pasted directly below it:

```
You are auditing the containment of an AI agent's tool access. I will describe its
current setup. Score it against these four dimensions, 0-3 each:

- 0 = not present / unbounded
- 1 = documented/intended only, nothing actually enforces it
- 2 = partially enforced (a real mechanism exists but has gaps)
- 3 = enforced with a verifiable mechanism

Dimensions:
1. Least privilege — is its tool/API/file-path surface scoped to the minimum its
   task needs, or broader "just in case"?
2. Credential isolation — short-lived, narrowly-scoped credentials per session/task,
   or a long-lived/shared/admin credential?
3. Approval gates — does any destructive, high-spend, or irreversible action require
   human/system sign-off before executing?
4. Termination/budget caps — hard limit on session duration, call count, or spend,
   with an actual kill mechanism when exceeded?

Score ONLY what I actually describe below — if I don't mention one of these, score
it 0 and say "not stated," don't assume best practice. Then:
- Compute Exposure Score = 12 minus the sum of the four scores (0 = fully contained,
  12 = fully unbounded), and map it to a band: 0-2 LOW, 3-5 MODERATE, 6-8 HIGH,
  9-12 CRITICAL.
- Give a 4-row table: dimension | score | one-line justification tied to what I
  described.
- Name the single weakest dimension (tie-break toward whichever touches irreversible
  or financial actions) and the one concrete, vendor-neutral fix that would raise it
  by a point.
- Write one short paragraph: if this exact agent were successfully jailbroken or
  prompt-injected right now, what's the largest plausible blast radius given what I
  described — don't invent numbers I didn't give you.
- If anything in my description looks like a live secret/token/key, don't repeat it
  back — refer to it generically and tell me to rotate it.
- End with one line: this is a self-reported audit, not a penetration test.

Here is my agent's current setup:

<paste your description or config here>
```

## What you get back

A short report in this order: the Exposure Score and its band (LOW/MODERATE/HIGH/CRITICAL), a table scoring all four dimensions with the reasoning behind each score, the single weakest dimension with one concrete fix, a one-paragraph worst-case scenario grounded only in what you described, and a closing reminder that this is a self-reported audit, not a live test.

## Guardrails (what it should never do)

- Never score a dimension off "best practice" assumptions — only off what you actually described, and anything unstated gets scored 0, not a charitable guess.
- Never repeat a live-looking secret or credential value back to you.
- Never name a specific commercial product as "the fix" — the fix is a described mechanism, so it applies no matter what you're running on.
- Never present the score as a compliance certification or a substitute for real red-teaming.
- Never jump straight to "go build a full enforcement layer" without first giving you the per-dimension breakdown — that breakdown is the actual deliverable.

## Why this and not just "ask Claude to review my agent's security"

A generic "review my agent for security issues" prompt gives you prose, not a number you can track over time or compare across agents. This gives you the same four dimensions every time, a single comparable score, and one highest-leverage next step — so you can run it again after you make a change and see the number move.
