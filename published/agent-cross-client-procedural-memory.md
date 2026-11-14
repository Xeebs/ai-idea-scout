# Playbook: A Portable Procedural-Memory Layer for Coding Agents That Jump Between Clients

Every freelance developer and consultancy engineer who runs an AI coding agent across multiple client codebases has lived the same small indignity: the agent has, in some real sense, already solved this exact class of problem — the CI setup for a given stack, the ORM migration dance, the recurring debugging pattern — on a different engagement last month. It doesn't matter. The session is gone, the context is gone, and the agent re-derives the whole approach from scratch, as if it had never seen the problem before. Nobody has shipped a standard way to let it remember the *recipe* rather than the client.

## The Gap

Hacker News's "Ask HN: How do you manage your AI agents' context across clients and projects?" pulled 100 points and 62 comments — a live, unanswered "has anyone built this" thread, not a hypothetical. That's a direct signal that people doing this for a living have no accepted answer. A single Reddit poster describes building "a procedural memory system for AI agents — solve a task once, reuse it next time," which proves the itch is real but is one unreferenced indie build, not a standard anyone else has adopted.

The twist is that this gap persists *despite* mature memory infrastructure already existing. mem0 (68.9k GitHub stars) and Letta/MemGPT (25.4k stars) are both widely adopted, production-grade memory layers — and the HN thread is happening anyway. The reason is that mem0 and Letta solve episodic and semantic memory — what happened, what facts are true — not procedural memory: *how* a class of problem gets solved, generalized and stripped of the specifics of any one client. The handful of repos that do name "procedural memory" explicitly (vbcherepanov/total-agent-memory, Memorix, agentic-cortex, PMB) are small, unvalidated, blog-post-adjacent projects with no verified adoption. The abstraction layer that would turn "I've solved this before" into "apply the known-good recipe" simply doesn't exist as something you can install.

## The Project

This is a personal, cross-project procedural-memory store — a layer that captures the recipe an agent used to solve a recurring class of task (stack signature, steps taken, decisions made, dead ends hit), strips it of anything client-identifying, and makes it available on any future engagement regardless of which codebase it's in. The abstraction-and-matching step is the actual product here, not the storage format: on a new task, a pre-task matcher checks the store for a procedure that fits the current stack/task signature and surfaces it as a starting recipe instead of letting the agent re-derive the approach cold.

It's deliberately designed as a *global* layer that complements, rather than competes with, client-isolation boundaries — facts about Client A's codebase stay walled off from Client B exactly as they should, while the generalized procedure for "set up CI for a Next.js + Postgres app" is precisely the kind of thing that *should* cross that wall. Four pieces make it work: an end-of-session capture step that proposes a sanitized "procedure card" for human confirmation; a local store keyed by task-type/stack signature; a pre-task matcher that surfaces the top candidate before the agent starts; and a sanitization check that flags anything identifier-like before a card is ever saved.

## Tangible Impact

**Population**: Freelance developers, dev consultancies, and agency engineers who repeatedly solve the same class of task across many separate, isolated client codebases, and currently re-derive or re-explain the approach to their agent fresh at every engagement because sessions and context reset between clients — the explicit audience of the unanswered HN Ask thread.
**Mechanism**: Today, switching to a new client engagement means the agent starts from zero on a task it has effectively already solved elsewhere. A sanitized, matched procedure store converts "I've definitely done this before but have to re-explain it" into "apply the known-good recipe and adapt the specifics," cutting redundant exploration on recognized task types.
**Measure**: time-to-first-fix on a recognized recurring task-type before versus after adoption, self-reported across a pilot freelancer's engagements; percentage of new tasks correctly matched to an existing stored procedure, plus the false-positive misapplication rate on mismatches; number of distinct procedures reused two or more times within a 90-day pilot, as evidence the store compounds value instead of being write-only.

## Why Now

The live, unanswered 100-point HN thread is the clearest "no standard exists" signal in the current window — and it's happening despite mem0 and Letta already being widely adopted, which is exactly what isolates the gap: it's the procedural-abstraction layer specifically, not memory storage in general, and the community is actively asking rather than quietly solving it in private.

## Try It

A companion Claude Code skill, [`skills/agent-cross-client-procedural-memory/`](../skills/agent-cross-client-procedural-memory/) — "Procedure Card: Cross-Client Reusable-Solution Extractor & Matcher" — is already written: *"Turns a just-solved task (or a pasted description of one) into a sanitized, reusable 'procedure card' — stack signature, steps, rejected approaches, gotchas, and what to adapt per engagement — and matches a new task against a folder of previously saved cards."*

It's useful standalone, well before any matching infrastructure gets built: hand it a just-finished task (or 2-3 pasted examples of similar past solved tasks) and it drafts the sanitized card directly — stack signature, steps, gotchas, what to adapt. When run inside Claude Code it reads the session's own transcript to do this rather than making you paste it; outside Claude Code, you paste the material instead. To use it: paste the `README.md` into any AI chat tool, or drop the `skills/agent-cross-client-procedural-memory/` folder into `~/.claude/skills/` if you're on Claude Code.

## Risks & Open Questions

Sanitization could miss a subtle client-identifying detail, which is a real leakage risk — this is better composed with a dedicated client-isolation enforcement layer than trusted to this project's own filter alone. Stack-signature matching could be too coarse, misapplying the wrong recipe, or too narrow, missing a true match phrased differently — that needs real tuning against a labeled set, not keyword overlap alone. There's a live risk that mem0 or Letta simply adds a "procedural" memory type and absorbs this into their existing, far larger install base before an independent layer gets traction. And freelancers may reasonably not trust an agent silently applying an old recipe without review, which means a mandatory human-confirm step is likely non-negotiable — reintroducing some of the friction the project exists to remove.

Surfaced from `research/2026-11-13-agentic-ai-autonomous-agents.md`, pattern `P4`.
