# Topic Rotation

The orchestrator regenerates `pipeline/queue.md` from this list whenever the queue runs dry. One topic per cycle, in order. Add, remove, or re-order topics here — the queue picks up changes on the next regeneration. Ad-hoc topics can be added directly to the queue and outrank the rotation.

## Rotation

1. **Agentic AI & autonomous agents** — planning, self-correction, long-horizon task execution, agent reliability
2. **Multi-agent architectures** — orchestration patterns, agent-to-agent protocols, role specialization, swarms vs hierarchies
3. **RAG techniques** — graph RAG, agentic RAG, late-interaction retrieval, hybrid search, RAG evaluation
4. **Context engineering & memory** — long-term agent memory, context compression, prompt caching strategies, knowledge distillation into context
5. **Tool use & MCP ecosystem** — Model Context Protocol servers, computer use, tool reliability, sandboxed execution
6. **LLM evaluation & observability** — agent tracing, eval harnesses, LLM-as-judge reliability, production regression detection
7. **Small & local models** — edge deployment, on-device agents, distillation, privacy-preserving inference
8. **AI safety & guardrails in production** — jailbreak resistance, output validation, permissioning for agents, audit trails
9. **Voice & multimodal agents** — real-time voice loops, vision-grounded agents, multimodal RAG
10. **Applied AI for underserved domains** — healthcare access, education, accessibility, civic/government services, low-resource languages

## Phrasing guidance for the trend-scout

Query the skill for *discovery*, not news: "new <topic> techniques people are building", "what developers struggle with in <topic>", "<topic> patterns and ideas". If a topic repeatedly yields thin signal, note it in `pipeline/sessions/` and rephrase or replace it here.

## Marketplace Rotation

A second, independent rotation for the MARKETPLACE track (see `marketplace-content/queue.md` — private repo), regenerated from this list the same way. This track runs continuously in parallel with INFRA, not alternating with it.

**Audience, revised 2026-11-12**: not narrow professional verticals (freelancers, solo small-business owners, indie hackers) — those produced ideas too niche to sell, confirmed by two real review-queue rejections and direct user feedback. The actual target is **general, adept Claude/ChatGPT/Copilot power users** doing common, *recurring* tasks — a developer using Claude Code daily, a writer, a researcher, an analyst, a student. This was checked against real data, not assumed: a direct look at Agensi.io's own published "best skills" guide and marketplace listings found its most-installed skill by far is `code-reviewer` (447 installs, free), with the rest of its proven top sellers clustered in git/PR workflow, test generation, and security auditing — all daily-use developer skills, not one-off or vertical-specific tasks. Agensi's own stated reasoning: **skills that save recurring time outsell one-off-task skills by a wide margin.** That's the standard every topic below is now held to — not just "is there demand" but "is this something an adept user would reach for *repeatedly*."

1. **Code review, git & PR workflow aids** — diff review, commit message generation, PR descriptions, pre-merge checklists. Confirmed highest-demand category on Agensi itself; the bar here is differentiation against `code-reviewer` and the "Code Review Bundle" (15 skills), not whether the category sells.
2. **Testing, security & code-quality checks** — test generation, secret/leak scanning, refactoring aids — for everyday developers using Claude Code/Copilot, not for people building agent infrastructure (that's the INFRA track).
3. **Prompt engineering & reusable prompt patterns** — structured prompting techniques, chain-of-thought templates, prompt libraries adept users build and reuse across tools.
4. **Research & multi-document synthesis** — summarizing/synthesizing across multiple sources, "chat with my docs" style workflows, literature-review-shaped tasks.
5. **Writing & editing for general use** — essay/report editing, tone and style matching, structural feedback — broadened from marketing-only copywriting to any adept writer.
6. **Data, spreadsheet & SQL wrangling** — using AI to clean, transform, and analyze data in Excel/Sheets/CSV/SQL.
7. **Meeting notes & action-item extraction** — transcript-to-summary, decision/action-item pull-out — broad professional use, not tied to one industry.
8. **Personal knowledge management** — note organization, "second brain" workflows, linking/structuring a growing personal knowledge base with AI.
9. **Everyday computer & browser automation** — a power user automating one repetitive task (not an agent framework — a single skill with a clear trigger and output).
10. **Learning, explaining & studying** — concept breakdowns, study guides, exam-style practice — broadened from student-only framing to anyone learning something.
11. **Resume, job search & career docs** — tailoring resumes, cover letters, interview prep — kept from the old rotation; genuinely broad appeal across virtually every adept AI user at some point, unlike the other dropped verticals.
12. **Creative writing & worldbuilding** — character bios, outline generators, critique passes — kept; broad hobbyist appeal, not tied to a single profession.

Dropped from the old rotation for being too narrow/vertical-specific (per direct user feedback): Social media & marketing ops, Freelancing & client work, Small-business & solo-preneur ops, SEO & blogging, No-code/indie-hacker launch tooling, Personal finance & budgeting helpers, Email & inbox triage, Content & copywriting (folded into the broader Writing & editing above).

## Phrasing guidance for the marketplace-trend-scout

Query for *buyer pain and existing paid alternatives*, not community tech discussion: "best AI prompt for <topic>", "is there a GPT or skill that does <topic>", "I paid for <topic> template and it was bad", "<topic> AI tool reviews". **Also search X/Twitter explicitly** — trending AI-tool-usage discussion lives there more than anywhere else right now: `<topic> site:x.com`, `"<topic>" twitter AI prompt`, and general WebSearch for threads *about* X discussion (many individual posts aren't indexable, but viral ones get quoted/screenshotted elsewhere — treat those citations as evidence same as a Reddit/HN thread, same sourcing rules apply, never invent a thread you didn't actually find). The goal is demand + a visible quality gap in what's already for sale, *and* a bias toward tasks an adept user would do repeatedly, not once. If a topic repeatedly yields thin signal, note it in `pipeline/sessions/` and rephrase or replace it here.
