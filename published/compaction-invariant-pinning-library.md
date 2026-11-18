# Pin It: An Invariant-Retention Library for Context Compaction

Long-running coding and research agents have a quiet, expensive bug: every time their context gets compacted, the summary pass has no memory of what it already protected last time. So an agent can burn an hour re-attempting a fix it already tried and failed on three compactions ago — not because the model got worse, but because the thing meant to keep it running efficiently is the thing erasing its memory of its own mistakes.

## The Gap

A tianpan.co post, "Compaction Traps: Why Long-Running Agents Forget What They Already Tried" (April 2026), names the failure precisely: the compaction summary drops what the agent already tried, so it repeats failed approaches. That alone would be one blogger's complaint, except the same 30-day research window turned up the same underlying idea surfacing independently, under different names, from different corners of the ecosystem: a "constraint pinning" write-up for Codex CLI/Claude Code that comes with its own violation-rate numbers, a per-type retention policy pattern documented at agentpatterns.ai, an academic "Structured Context Eviction" paper, and a referenced `pi-smart-compact` package with its own architecture notes on invariant retention. Four independent namings of the same technique in one month is real, validated demand — but notably, none of them has shipped as a single, adopted, reusable library. Everyone keeps re-discovering the problem and re-inventing a bespoke fix.

## The Project

The fix is a middleware library that sits in front of any agent framework's compaction pipeline. Right before a summarization pass runs, it pulls out a small, bounded "invariant set" — approaches already tried and their outcomes, hard task constraints, and key decisions — and writes it to a protected slot that survives every future compaction untouched. Everything else still goes through normal lossy summarization as before; only the things that would be actively harmful to forget get carved out.

The centerpiece is a pluggable invariant classifier (rule-based logic plus a cheap-model judgment call) that decides, item by item, what belongs in that protected slot versus what's safe to compress away. That classifier is paired with a hard token budget on the pinned slot itself, with internal eviction — because a "fix" for context rot that quietly grows into its own unbounded blob of pinned history is no fix at all. The planned components: compaction-hook adapters for Claude Code's PreCompact hook, LangGraph's checkpointer API, and a generic wrapper for any OpenAI/Anthropic-compatible agent loop; the invariant classifier itself (a tried-approaches extractor plus a constraint extractor); the pinned-slot store with its fixed budget; and a violation-rate eval harness that measures, concretely, how often a compacted session re-attempts something it already tried.

## Tangible Impact

**Population**: Teams and solo developers running long-horizon autonomous coding or research agents that execute for hours to days and hit automatic context compaction multiple times per session — the cohort reporting "agent repeats failed approaches after compaction" across the tianpan.co post, the constraint-pinning write-up, and the Structured Context Eviction paper's benchmark subjects.
**Mechanism**: Today each compaction pass produces a fresh lossy summary with no memory of what's already been protected, so an agent can re-attempt a fix it tried and failed three compactions ago, burning time and tokens. Pinning the tried/constraint set outside summarization means every future compaction inherits that protected context for free, turning "agent forgot it already tried X" from a recurring tax into a one-time classification cost.
**Measure**: (1) Repeated-failed-approach rate per session before vs. after, on a benchmark of long-running coding tasks with forced compaction. (2) Task completion rate and wall-clock time on multi-hour agent runs. (3) Pinned-slot overhead as a percentage of total context budget, to confirm the fix doesn't just relocate the bloat.

## Try It

A companion skill, `skills/compaction-invariant-pinning-library/`, is already written. It is the one-shot design half of this idea, not the live middleware: hand it a description of your agent's workflow (and ideally a transcript excerpt around a compaction boundary) and it drafts the invariant-classification scheme for your specific setup — what should get pinned as "already tried," what's a hard constraint, what's safe to summarize, and a recommended token budget for the pinned slot. As its `SKILL.md` puts it:

> Designs a per-workflow "invariant pinning" scheme for a long-running agent's context compaction — what must survive every summarization pass (already-tried approaches, hard constraints, key decisions) vs. what's safe to lose. Use before wiring in a compaction hook, or after noticing an agent re-attempts something it already tried and failed.

To use it: either paste the contents of `skills/compaction-invariant-pinning-library/README.md` into any AI chat tool along with your workflow description and transcript excerpt, or drop the whole `skills/compaction-invariant-pinning-library/` folder into `~/.claude/skills/` if you're running Claude Code.

Worth being clear-eyed about the risk here: this exact technique surfaced under four independent names in a single month, which means whichever framework vendor — Anthropic, LangChain, or someone else — ships it natively first simply absorbs the idea. The classifier itself is also an LLM judgment call that can mis-fire: a stale "already tried" pin could block a retry that would now succeed under changed conditions, which is why the skill's procedure explicitly tags time-sensitive failures for review rather than treating them as permanent blocks.

Surfaced from `research/2026-11-13-context-engineering-memory.md`, pattern `P3`.
