# House Rules: An Owner-Scoped, Role-Based Shared Memory Architecture for Household AI Agents

Four different teams have independently hit the same wall this month: once you give a household one shared, always-on AI assistant, you've also quietly handed it everyone's private chats, search histories, and reminders — in one undifferentiated pool. Nobody wanted that. Everybody built around it anyway, each team re-deriving the same owner-scoping fix from scratch instead of reaching for something that already existed, because nothing that already existed actually covers it.

## The Gap

The pattern shows up in four unrelated places at once. Cogitator's product page describes one shared household agent instance where "nothing from a private chat enters the shared knowledge base," with admin/moderator/user roles and departure-triggered data removal. A separate personal-context-engine write-up from practitioner zackproser describes "a database-enforced scope wall" built on a single Postgres table to keep legal, financial, and family context out of work-facing agents. A ZimaSpace design essay argues the same point in the abstract: household memory "should be modeled as scoped records with explicit owners and access rules, not one shared transcript." And a Show HN post for ActingWeb tackles the adjacent individual-not-household version of the same problem.

What none of these are is mature or widely adopted. Cogitator is macOS-beta-only with no independent reviews. Mem0, the most-used memory backend in this space, ships only a binary private/public visibility label per user ID — no roles, no departure-triggered purge. A September 2026 arXiv paper (AIM) describes visibility-labeled memory as a research idea, not a product. Domus Next's "Nori" is still in public preview. Four independent convergences on the same problem, and not one finished, dependable answer among them — the textbook shape of a gap that's obvious enough that everyone keeps rebuilding it, and hard enough that nobody has actually closed it.

## The Project

The fix isn't another memory store competing on recall quality — it's a policy layer that sits in front of whatever memory backend a household assistant already uses (Mem0, Letta, or Zep) and enforces scoping the backend itself doesn't. Every write carries an owner tag and a default visibility — shared or private. Every read gets filtered through the querying member's role: admin, adult, teen, guest. And when someone leaves the household, one command purges every record tagged to them, with verification that nothing was missed.

The centerpiece is that enforcement and removal workflow, not a new database. Concretely: a scope-tagging write wrapper that stamps owner ID and default visibility onto every memory write; a role-based read filter sitting between the backend and the agent; a departure/removal command that doesn't just delete-and-hope but confirms zero records remain attributable to the departed member; and a cross-member leak scanner meant for pre-launch red-teaming, so a product team can catch a private-chat leak before a real family finds it for them.

## Tangible Impact

**Population**: Households running a shared, always-on AI assistant — the majority of U.S. households (Census Bureau: ~80% of households have more than one person) that adopt a shared smart-speaker or app-based family assistant, specifically multi-person households where at least one member (a partner, a teenager) wants private content (a private chat, search history) to stay private while the same device still handles shared household tasks (a dinner reservation, a grocery list).
**Mechanism**: Today's products either blend every member's input into one profile — risking a partner's private chat or a teen's search history surfacing to the rest of the household — or force each person onto a fully separate assistant, losing the convenience of shared context the household wanted in the first place. An owner-scoped layer lets one shared agent serve the household while mechanically walling off private content and cleanly removing a departing member's data, instead of relying on hope that no one looks.
**Measure**: (1) cross-member leak incidents caught in pre-launch red-team testing, driven to zero before any pilot household goes live. (2) Time to fully remove a departed member's data — target one command, under a minute, versus manual untangling today. (3) Household retention/satisfaction in a pilot, compared against a single-shared-profile baseline product.

## Try It

There's a companion Claude Code skill for the design side of this: [`skills/household-scoped-shared-agent-memory/`](../skills/household-scoped-shared-agent-memory/). Its one-line description: "Drafts a household's memory-visibility scheme (what's shared vs. private by default, who can override, what triggers reclassification, and how to purge a departing member's data) for a shared AI assistant serving multiple people. Use when someone is designing, configuring, or auditing a household/family AI assistant's privacy model, before any memory backend gets wired up."

It's deliberately a design aid, not the enforcement code itself — it won't wire into Mem0, Letta, or Zep for you, and it won't settle a real family-law dispute. What it will do is turn a rough description of your household's members and content categories into a concrete role table, a visibility classification per category, override rules, reclassification triggers, and a departure-removal checklist you can hand to whoever builds the actual access-control layer.

To use it: paste the contents of `skills/household-scoped-shared-agent-memory/README.md` into any AI chat tool and describe your household and the content categories your assistant handles, or drop the whole `household-scoped-shared-agent-memory/` folder into `~/.claude/skills/` if you're using Claude Code.

## Worth Naming the Risk

The idea file is upfront about the biggest threat to this ever mattering: Cogitator, Mem0, or Domus Next could just ship this natively first — they already own the memory layer and the household-product relationship, which is a much shorter path to "solved" than a third-party policy layer bolted on from outside. There's also a dependency this project doesn't solve: knowing *who is currently speaking* to apply the right scope is itself an unsolved problem for voice-first shared devices, and this build assumes that's handled upstream. And "what counts as sensitive" is ultimately a judgment call — a missed private-content leak undermines the entire value proposition, which is exactly why the design skill above is built to flag ambiguous classifications rather than guess through them.

---

Surfaced from `research/2026-11-14-context-engineering-and-memory.md`, pattern `P4`.
