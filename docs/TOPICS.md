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

A second, independent rotation for the MARKETPLACE track (see `marketplace-content/queue.md` — private repo), regenerated from this list the same way. This track runs every hour in parallel with INFRA, not alternating with it. Audience is Agensi.io's actual traffic — indie builders, freelancers, and small-business operators searching Google, not AI researchers browsing GitHub. Topics are chosen for broad, everyday recurring tasks with plausible willingness to pay, not technical novelty.

1. **Content & copywriting** — product descriptions, ad copy, landing page headlines, cold outreach
2. **Social media & marketing ops** — caption batches, content calendars, repurposing one piece across platforms
3. **Freelancing & client work** — proposals, scope-creep emails, invoices, contracts, scope docs
4. **Resume & job search** — tailoring resumes per posting, cover letters, interview prep, LinkedIn copy
5. **Personal productivity & note-taking** — meeting notes to action items, daily planning, habit tracking prompts
6. **Email & inbox triage** — drafting replies, summarizing threads, unsubscribing/cleanup workflows
7. **Small-business & solo-preneur ops** — SOPs, onboarding docs, policy drafts, simple financial summaries
8. **SEO & blogging** — outlines, meta descriptions, keyword-to-article briefs, content refreshes
9. **No-code/indie-hacker launch tooling** — landing page copy, pricing page drafts, launch checklists, Show HN/Product Hunt posts
10. **Creative writing & worldbuilding** — character bios, outline generators, critique/feedback passes
11. **Personal finance & budgeting helpers** — expense categorization prompts, budget templates, negotiation scripts
12. **Study & learning aids** — flashcard generation, exam-style question drafting, concept explainers

## Phrasing guidance for the marketplace-trend-scout

Query for *buyer pain and existing paid alternatives*, not community tech discussion: "best AI prompt for <topic>", "is there a GPT or skill that does <topic>", "I paid for <topic> template and it was bad", "<topic> AI tool reviews". The goal is demand + a visible quality gap in what's already for sale, not an unbuilt technique. If a topic repeatedly yields thin signal, note it in `pipeline/sessions/` and rephrase or replace it here.
