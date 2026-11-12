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
