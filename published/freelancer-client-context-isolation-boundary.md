# Client Wall: An Enforced Context-Isolation Boundary for Freelancers and Agencies

If you freelance or run a small shop juggling several clients, you already know the fear: the AI coding assistant you use for everyone remembers everything, and nothing stops it from remembering the wrong client's thing at the wrong time. The current fix is a folder-naming convention and a prayer. That's not a boundary — it's a habit, and habits slip.

## The Gap

Three separate posts landed in the same 30-day window, all converging on the same unsolved problem: MindStudio's guide to agentic context folder structure, a DEV.to piece on avoiding "context bleed" across projects (dev.to/martinlepage26bit), and Unabyss's write-up aimed squarely at freelancers and agencies structuring AI context for client work. All three independently propose a global/client/project folder taxonomy — and all three stop at the taxonomy. None of them ships a mechanism that actually *enforces* the separation; what they're describing is organizational discipline dressed up as architecture. Remember to keep the folders straight, remember not to let a global memory file pick up a client-specific fact, remember which terminal tab belongs to which client. One slip, and a confidentiality boundary that may be contractually binding has already been crossed.

It's not as though nobody tried to build the actual tool. Felo-Inc/memclaw set out to do exactly this — isolated workspaces per project, a dashboard, free to use — and picked up 43 stars before going stale (last commit seven months back, well past the point where a tool like this should be considered maintained). Its spiritual successor, caura-ai/caura ("formerly MemClaw"), is very much alive — 557 stars, pushed the same day this gap was logged — but it pivoted upmarket into enterprise multi-tenant "governed shared memory for AI agent fleets." That's a real, actively-maintained piece of infrastructure, and it has nothing to do with a solo freelancer protecting Client A's codebase from Client B's session. The one team that built for this population walked away from it. What's left is blog advice.

## The Project

Client Wall is a hook that sits in front of a coding agent's context-loading step and makes the global/client/project boundary mechanical instead of hoped-for. A freelancer tags each project directory (or git remote) with a client ID once. From that point on, the hook — a Claude Code/Cursor hook or a standalone MCP server intercepting context assembly — simply will not let content tagged to Client A into a session rooted in Client B's directory. Global facts (your own coding style, your own tool preferences) are explicitly allowed to travel everywhere; anything tagged to a specific client is not. The insight here isn't the folder taxonomy — three blogs already wrote that down — it's the enforcement layer nobody built on top of it.

The pieces: a per-directory/per-repo client-tagging config; the actual interception hook that strips mismatched client-tagged content out of assembled context; a CLI to tag, list, and audit client boundaries across a freelancer's whole project tree; and a leak-detection test mode that simulates cross-client context assembly on demand and reports exactly what would have leaked, so you can verify the boundary holds before you trust it with a real engagement.

## Tangible Impact

**Population**: Freelance software developers and small agencies (2–20 people) who maintain concurrent engagements for multiple clients using the same AI coding tools across those engagements — a population large enough that three independent blogs targeted it with distinct guides in the same period, and one dedicated (now-abandoned) product was built specifically for it.

**Mechanism**: Today, preventing cross-client leakage depends entirely on the freelancer remembering to keep tool configs, memory files, and context separate per client — a single slip (opening the wrong project, a shared global memory file picking up a client-specific fact) becomes a confidentiality breach with real contractual consequences. A mechanically enforced boundary converts "I hope I kept these separate" into "the tool refuses to let them mix," removing the single point of human-memory failure.

**Measure**: (1) Rate of simulated cross-client leaks caught by the leak-detection test mode, versus a measured baseline rate of actual leaks in freelancers' current ad hoc setups (self-reported in a pilot). (2) Time freelancers spend manually re-establishing per-client context when switching clients within a day, before versus after adoption. (3) Adoption among the ~600 stars' worth of users MemClaw/Caura's pivot left without a maintained tool.

## Try It

A companion skill already exists: [`skills/freelancer-client-context-isolation-boundary/`](../skills/freelancer-client-context-isolation-boundary/).

> "Audits a freelancer's or small agency's multi-client AI coding tool setup for context-bleed risk and drafts a concrete client-isolation policy (boundary definition, tagging convention, pre-session checklist). Use when onboarding a new client, consolidating tools across clients, or after a near-miss where one client's context nearly surfaced in another's session."

This is the audit-and-policy half of the idea, not the enforcement hook itself — it won't block a leak, but it will tell you where your current setup is already exposed and hand you a concrete tagging convention and pre-session checklist to adopt immediately. Two ways to use it: paste the contents of `skills/freelancer-client-context-isolation-boundary/README.md` into any AI chat tool (ChatGPT, Claude.ai, etc.) and answer its questions about your client list, tools, and shared resources; or, if you use Claude Code, drop the whole `freelancer-client-context-isolation-boundary/` folder into `~/.claude/skills/` and it becomes available automatically. Either way, it will not ask for or store your clients' actual secrets or code — only names, paths, and structure.

## The Honest Risk

Worth saying plainly: this gap could close on its own. Caura could reverse its enterprise pivot, or a new entrant could rebuild for freelancers specifically, before an independent effort gets traction. And enforcement at the context-loading layer has a hard ceiling — it can't catch a freelancer manually copy-pasting Client A's code into a Client B session; it only governs automated context assembly, not human error that happens upstream of it. There's also a real adoption question: the actual legal stakes (an NDA breach) may be rare enough in practice that freelancers underinvest even once the tool exists, limiting uptake to the already-careful. None of that is a reason to skip the enforcement layer — it's a reason to be honest about what it does and doesn't guarantee.

---

Surfaced from `research/2026-11-12-context-engineering-memory-ii.md`, pattern `P5`.
