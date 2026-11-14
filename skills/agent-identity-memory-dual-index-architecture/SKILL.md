---
name: agent-identity-memory-dual-index-architecture
description: Splits an AI agent's accumulated memory into a stable identity lane and an ordinary working-memory lane, then produces a pre/post persona-probe set and a go/no-go checklist for a model or embedding swap. Use before swapping the LLM or embedding model behind a persistent persona/companion/assistant agent, or when its memory has never been split and you want to do it proactively.
---

# Identity/Memory Migration Planner

## When to use this
Use this when someone is building or operating a persistent AI agent with a maintained persona — a companion app, a character/roleplay bot, a long-running personal assistant with a name and personality — and one of these is true: (1) they are about to swap the underlying LLM or the embedding model that powers its memory store and are worried the persona will visibly change for users (the Replika-style "my AI changed" complaint); or (2) their memory is currently one undifferentiated store and they want to proactively split persona-defining facts from ordinary working memory before that risk ever comes up. This is a one-shot planning/design task — it drafts a migration plan and a probe set on paper. It does not run against a live vector store, does not perform the re-embedding itself, and does not replace actually running the swap and watching real user reactions.

## Inputs
**Data source**: Connected — when run as a Claude Code skill with file access, it reads the agent's own existing identity/memory artifacts directly from the user's repo (e.g. an `IDENTITY.md`/`PERSONA.md`/system-prompt file, a vector-store config such as a FAISS/pgvector/Pinecone schema, or the embedding-client code) rather than asking the user to retype them; no new external API or connector is built or required, because this only re-reads what the agent's own stack already holds. When run as a portable prompt in a chat tool with no file access, the user pastes the same artifacts manually as a fallback — state in the output which mode was used.

Specifically needed, by either path:
1. **Current memory architecture** — one combined store, or already split; which vector store/embedding model it uses; roughly how large the corpus is.
2. **Persona-defining material** — the actual text: name, personality/voice description, backstory, relationship facts with specific users, stated values/boundaries. Not a summary — the real strings that would need to end up in an identity lane.
3. **A sample of 10-30 real memory entries or conversation turns**, if the store isn't split yet, so each one can be classified.
4. **The swap in question** (if imminent) — old model/embedding → new model/embedding — or "none yet, planning proactively" if there isn't one.

If any of 1-4 is missing, say so explicitly in the output and proceed on what was given rather than inventing the rest.

## Procedure
1. Restate the setup back in 2-3 sentences (architecture, corpus size, swap target or "proactive, no swap yet") so the user can correct it before the plan is built on a misunderstanding.
2. Classify every persona fact and every sample memory entry into one of three buckets, with the rule applied explicitly, not just the verdict:
   - **Identity lane** — facts that define who the agent is regardless of session or task: name, core personality/voice traits, backstory, stated values/boundaries, and *specific, named* relationship facts with a user (e.g. "the user's name is Priya and we have a running joke about her cat").
   - **Working lane** — everything session-, task-, or time-scoped: recent events, world-state facts, preferences that are known to change, anything timestamped or tied to a specific conversation.
   - **Ambiguous — flag, default to working lane** — facts that look identity-like but the user's own description implies the persona is meant to evolve through experience (per the idea's own risk note). Default these to the working lane and say explicitly why, rather than silently picking one side.
3. From the identity-lane facts only, generate 10-20 fixed **persona probe** prompts designed to be asked of the agent before and after the swap, covering at minimum: name/self-identification, one specific relationship fact, one stated value/boundary, one voice/tone sample ("how would you phrase X"), and one query where a generic/base-model answer would be visibly different from the persona's answer. Number them so they can be reused run after run.
4. Estimate re-validation cost: identity-lane item count vs. total corpus item count, stated as a ratio and in plain terms (e.g. "47 of ~3,200 entries — under 2% of the corpus needs re-embedding or re-validation, not the full store").
5. Write a go/no-go checklist with concrete, checkable criteria, not vague advice — e.g. "pre/post probe pairs produce semantically consistent answers on at least 9/10 probes, judged by [cosine similarity above a stated threshold if embeddings are available, or a blind human read-through if not]." Always route to "no-go without a human reviewing the actual pre/post transcripts" when any safety/boundary-related probe fails — never let an automated score alone clear a boundary-probe failure.
6. Draft a **fallback transition brief** — a short, honest, user-facing note to send if the probes show real drift, modeled on the "post-hoc transition brief" approach referenced in the source idea, for use when migration can't fully preserve the persona. Write it in the agent's own established voice whenever the persona's own rules allow a direct, literal explanation (e.g. "the way I respond is changing a bit while I switch to a new underlying model — let me know if something feels off," phrased the way this specific persona talks). If the persona has an explicit never-break-character or never-admit-being-an-AI rule, do not override that rule to deliver the brief — instead draft it as in-world flavor text that signals "something changed" without literal tech language (e.g. a tavern keeper saying they're "restocking the cellar" rather than announcing a model swap), and say explicitly that this is the chosen resolution of the tension between honesty and the character rule, rather than picking one side silently.
7. List 2-4 risks specific to this setup (e.g. no distinct identity lane exists yet so lane assignment is this plan's own best guess and should be reviewed by the user; the persona is explicitly evolving, which weakens the identity/working split's core assumption; corpus is too small for the probe set to be statistically meaningful).

## Output format
A single markdown report, in this order:
1. **Setup summary** — restated architecture, corpus size, swap target (or "proactive"), and which input mode was used (file-read vs. pasted).
2. **Identity Lane Manifest** — numbered list of the exact facts/text assigned here.
3. **Working Lane Manifest** — numbered list (can be summarized by category if the sample is large, but call out any individually notable items).
4. **Ambiguous / Flagged Items** — bullet list with the one-line reason each was flagged and why it defaulted to working lane.
5. **Persona Probe Set** — numbered list of 10-20 prompts, each tagged with which identity fact it tests.
6. **Re-validation Cost Estimate** — the ratio and plain-language statement.
7. **Go/No-Go Checklist** — numbered, checkable pass/fail criteria, ending with the mandatory human-review-on-boundary-failure rule.
8. **Transition Brief Template** — the drafted fallback note, ready to copy/paste/edit.
9. **Risks Specific to This Setup** — 2-4 bullets.

## Guardrails
- Never invent persona facts, memory entries, or corpus statistics the user didn't provide or that weren't actually present in the files read — classification and estimation only, no fabrication to fill gaps.
- Never present the probe set as a guarantee against drift — state explicitly that it is a bounded sample, not exhaustive coverage, and that it does not substitute for watching real user reactions after a swap ships.
- Never recommend shipping a swap as "go" based on probe results alone when a safety/boundary-related probe failed — that always routes to human review, regardless of how well other probes scored.
- Never build or claim to execute the actual dual-index runtime, re-embedding job, or migration script — this skill produces the plan a human or the separate runtime infrastructure then executes; say so if asked to "just do the migration."
- If the persona-defining material given is too thin to classify meaningfully (e.g. only a one-line description with no sample memories), say so and ask for more rather than padding the Identity Lane Manifest with guesses.
