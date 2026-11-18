# Carryover: A Portable Context Handoff Protocol for Cross-Tool Agent Work

Ask Hacker News how people keep their AI coding tools in sync on the same project, and you get the loudest non-answer in recent memory: 98 points, 60 comments, and not one canonical fix. That's the shape of a real gap — not a question nobody's asked, but a question everyone's asked and nobody's settled.

## The Gap

The thread was simple: "How do you manage your AI agents' context across clients and projects?" It drew the single highest engagement of the entire research run it came from, and it closed with no agreed-upon answer. The pain underneath it is familiar to anyone who bounces between Claude Code, Cursor, and ChatGPT on the same codebase in the same week — every tool switch means re-establishing architecture, re-explaining recent decisions, and re-litigating approaches that were already tried and rejected somewhere else, because each tool only reads its own memory format.

It's not that nobody's trying. The gap analysis turned up a genuinely crowded field of early attempts: more than ten "portable-agent-memory" repos on GitHub, plus a cluster of named point solutions — Carryover itself (an alpha-stage Rust crate), Continuity, BuildBetter CLI, Byterover, EverMemOS, Relay, Unabyss, ContextStream. That's a lot of people independently deciding this is worth building. What none of them have is independent adoption or benchmark validation — no tool in that list has become the thing people point to when someone asks the HN question. Crowded and unsolved can both be true at once, and here they are.

## The Project

The core idea is a single, versioned "context bundle" — one file holding project architecture, recent decisions (with rationale), open threads, and file-level state — paired with thin adapters that render it natively into whatever tool you're opening next: Claude Code's CLAUDE.md/memory, Cursor's rules, a generic system-prompt block for ChatGPT or anything else. The adapters are the actual point of the project, not the file format. A bundle schema is easy; making the same bundle show up correctly whether the next session opens in Cursor or Claude Code is the part the ten-plus existing repos haven't cracked yet.

A CLI (`carryover sync`) keeps the bundle current by diffing it against recent commits and session summaries instead of demanding manual re-entry every time something changes, plus a staleness check that flags when the bundle hasn't been touched in N commits — so it doesn't quietly become the stale memory file every existing point solution eventually degrades into.

## Tangible Impact

**Population**: Developers — solo and small-team — who routinely work across 2+ AI coding tools on the same project within a week, the explicit audience of the 60-comment HN thread; a conservative proxy is the overlap of Cursor's and Claude Code's user bases, both independently reported in the hundreds-of-thousands in 2026 vendor disclosures.
**Mechanism**: Today, switching tools means re-typing or re-discovering project context, or working from a stale memory file only one tool reads; a synced, multi-tool bundle means the next tool a developer opens already knows what the last one decided, cutting the "re-orientation tax" every switch currently pays.
**Measure**: (1) Time from opening a new tool on an existing project to first useful agent action drops measurably in a pilot (self-reported before/after logs). (2) Rate of agents proposing something already decided/rejected in another tool's session drops. (3) Bundle staleness (commits since last sync) stays below a target threshold without manual nagging.

## Try It

A companion Claude Code skill, [`skills/portable-context-handoff-protocol/`](../skills/portable-context-handoff-protocol/), is already written: *"Drafts a tool-agnostic 'context bundle' (architecture, decisions, open threads, pitfalls) and renders it into CLAUDE.md, Cursor rules, and a generic system-prompt block, so a developer switching between AI coding tools on the same project doesn't re-explain context from scratch. Use when a user is about to switch tools, is onboarding a new tool to an existing project, or complains about re-explaining the same project context repeatedly."*

To use it: drop the `skills/portable-context-handoff-protocol/` folder into `~/.claude/skills/` if you're running Claude Code, and hand it your project's one-liner, the tools you switch between, and anything you've already got (an existing CLAUDE.md, `.cursorrules`, or just a rundown of recent decisions). No Claude Code install? Paste the skill's `README.md` into any AI chat tool as a prompt template — it's written to stand on its own. Unlike the full sync-CLI project, the skill is a one-shot drafting task: it doesn't watch your repo or auto-detect drift, it produces a snapshot bundle (and tells you honestly what's missing) the moment you hand it context, with no ecosystem buy-in required.

## The Honest Risks

The clearest reason this might not need building at all: any of the eight-plus existing point solutions, or the tool vendors themselves — Anthropic, Cursor — could ship native cross-tool sync and absorb the whole idea overnight. There's also a real chance the HN thread's lack of a canonical answer means the problem resists a generic solution because it's too workflow-specific, not that nobody's found the right shape yet. Separately, a static bundle can drift from actual codebase state faster than developers remember to update it, so the staleness-detection piece is unproven in practice. And different tools' context mechanisms have different size and format limits, meaning a single bundle may render well in one tool and get awkwardly truncated in another.

Surfaced from `research/2026-11-11-context-engineering-and-memory.md`, pattern `P2`.
