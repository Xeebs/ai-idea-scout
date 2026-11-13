# Playbook: A Portable Procedural-Memory Layer That Lets Coding Agents Reuse Solved Procedures Across Clients

- **Status**: EXPLORING (promoted 2026-11-13 cycle 52: evidence density — source HN Ask thread alone carries 100pts/62cmt, exceeding the ≥50-point bar)
- **Date**: 2026-11-13
- **Topic**: Agentic AI & autonomous agents
- **Source**: research/2026-11-13-agentic-ai-autonomous-agents.md · P4
- **Maturity verdict**: PARTIAL — mature general memory infrastructure exists (mem0, 68.9k stars; Letta/MemGPT, 25.4k stars) but as episodic/semantic memory, not procedural "solve once, reuse next time" memory specifically; narrow procedural-memory-named repos (vbcherepanov/total-agent-memory, Memorix, agentic-cortex, PMB) are small and unvalidated. A live 100-point/62-comment HN Ask thread asking the community how they solve this, despite mem0/Letta's existence, shows the specific gap remains unclosed in practice.
- **Format**: BOTH
- **Data Sources**: CONNECTED — reads the agent's own session transcript / tool-call history directly via existing session-log and hook primitives (e.g., Claude Code's session JSONL logs and hook API) rather than requiring the user to paste anything; the primitive already exists maturely, but no one has wired it into a procedural-memory abstraction layer yet.

## The Gap
Hacker News's "Ask HN: How do you manage your AI agents' context across clients and projects?" (100 points, 62 comments) is a direct, unanswered "has anyone built this" thread — people solving the same class of problem across many separate client engagements have no standard way to make an agent remember *how* it solved something, not just *what* a specific codebase contains. A single indie Reddit post ("I built a procedural memory system for AI agents — solve a task once, reuse it next time") shows someone trying, but it's one unreferenced implementation, not a standard.

## The Project
A personal, cross-project procedural-memory store that captures the *recipe* an agent used to solve a recurring class of task — stack signature, steps taken, decisions made, gotchas hit — strips it of client-specific identifiers, and makes it available to the agent on any future engagement, regardless of codebase. On a new task, a pre-task matching step checks the store for a procedure matching the current stack/task signature and surfaces it as a starting recipe instead of making the agent re-derive the approach from scratch. The abstraction-and-matching step is the centerpiece, not the storage format — this is explicitly a *global*, cross-client layer, deliberately complementary to (not competing with) a client-isolation boundary: facts about a specific client stay walled off, while the generalized procedure for "set up CI for a Next.js+Postgres app" is exactly what should cross that wall.

Components: an end-of-session capture step that proposes a sanitized, generalized "procedure card" (stack signature, steps, rejected approaches, gotchas) for human confirmation; a local store keyed by task-type/stack signature; a pre-task matcher that surfaces the top candidate procedure before the agent starts solving; a sanitization check that flags anything identifier-like before a card is saved.

## Tangible Impact
**Population**: Freelance developers, dev consultancies, and agency engineers who repeatedly solve the same class of task (CI setup for a given stack, a recurring debugging pattern, an ORM migration recipe) across many separate, isolated client codebases, and currently re-derive or re-explain the approach to the agent fresh every engagement because sessions and context reset between clients. This is the explicit audience of the unanswered HN Ask thread.
**Mechanism**: Today, switching to a new client engagement means the agent starts from zero on a task it has effectively already solved elsewhere — a sanitized, matched procedure store converts "I've definitely done this before but have to re-explain it" into "apply the known-good recipe and adapt the specifics," cutting redundant exploration on recognized task types.
**Measure**: (1) Time-to-first-fix on a recognized recurring task-type, before versus after adoption, self-reported across a pilot freelancer's engagements. (2) Percentage of new tasks correctly matched to an existing stored procedure, and the false-positive misapplication rate on mismatches. (3) Number of distinct procedures reused two or more times within a 90-day pilot, as evidence the store compounds value rather than being write-only.

## Why Now
The live, unanswered 100-point HN thread is the clearest "no standard exists" signal in the current window, and it's happening despite mature general memory infrastructure (mem0, Letta) already being widely adopted — showing the gap is specifically the procedural abstraction, not memory storage in general, and that the community is actively asking rather than quietly solving it.

## Skill Angle
Given a description of a current problem plus 2-3 pasted examples of similar past solved tasks (the agent's own trace, or the developer's recollection), draft a generalized, sanitized "procedure card": stack signature, steps, gotchas, and what to adapt per engagement. Useful standalone even before the matching infrastructure exists, as a one-shot way to turn "I've done this before" into a reusable artifact.

## MVP Sketch
A CLI/hook that, at session end, prompts "was this a reusable procedure?" and if confirmed, extracts a sanitized card into a local store; a pre-task hook doing stack-signature/keyword matching against the store and surfacing the top candidate before the agent starts. Experiment: 1-2 freelance developers use it across 5+ real client engagements over 3-4 weeks, tracking time-to-fix and match precision against their own baseline from the prior month. 2-3 weeks for 1-2 people.

## Risks & Open Questions
- Sanitization could miss subtle client-identifying details, creating a leakage risk that would benefit from composing directly with a dedicated client-isolation enforcement layer rather than relying on this project's own filter alone.
- Stack-signature matching could be too coarse (misapplying the wrong recipe) or too narrow (missing a true match phrased or structured differently) — this needs real tuning against a labeled set, not just keyword overlap.
- mem0 or Letta could add a "procedural" memory type and absorb this capability into their existing, far larger adoption base.
- Freelancers may not trust an agent silently applying an old recipe without review, requiring a mandatory human-confirm step that reintroduces some of the friction the project is meant to remove.
