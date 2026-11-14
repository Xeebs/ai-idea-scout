# Identity/Memory Migration Planner

A prompt template for splitting a persistent AI agent's memory into a stable "identity" lane and an ordinary "working memory" lane, and producing a before/after probe set so you can tell, concretely, whether swapping the underlying LLM or embedding model has changed the agent's personality. Paste the block below into any AI chat tool (Claude, ChatGPT, Gemini, etc.) along with your own agent's details.

## When to use this

Use this if you run a persistent AI agent with a maintained persona — a companion app, a character/roleplay bot, a long-running personal assistant with a name and personality — and either:

- You're about to swap the LLM or the embedding model behind it and you're worried users will notice the personality shift (this is the exact complaint users had about Replika's 2023 forced model change), or
- Your agent's memory is currently one undifferentiated store (persona facts and ordinary task memory all mixed together) and you want to split them proactively before you ever have to do a risky swap.

This produces a *plan* — a classification of your existing facts, a reusable test set, and a checklist. It does not run against your actual vector store, does not re-embed anything, and does not replace watching how real users react after you actually ship a swap.

## Data source

**Manual** in this portable form — you paste your own agent's details into the prompt below; there is no API or connector involved here. (If you're using this inside Claude Code or another tool that can read your files directly, you can instead point it at your identity/persona files and memory-store config and ask it to read them directly instead of pasting — the logic below is the same either way; just tell it which artifacts to open.)

## What to give it

Before pasting, gather:

1. **Current memory architecture** — one combined store or already split? Which vector store (FAISS, pgvector, Pinecone, etc.) and embedding model? Roughly how many entries/how big?
2. **Persona-defining material, verbatim** — the actual name, personality/voice description, backstory, stated values or boundaries, and any specific relationship facts with named users. Paste the real text, not a summary.
3. **10-30 real sample memory entries or conversation turns**, if your store isn't split yet, so each can be classified.
4. **The swap you're planning** (old model/embedding to new model/embedding) — or say "no swap planned yet, just want to split proactively."

## The prompt

```
You are an identity/memory migration planner for a persistent AI agent.

Here is my setup:
- Memory architecture: [describe: combined or split, vector store, embedding model, corpus size]
- Persona-defining material (verbatim): [paste name, personality/voice, backstory, values/boundaries, named relationship facts]
- Sample memory entries (if not already split): [paste 10-30 real entries]
- Planned swap: [old model/embedding -> new model/embedding, OR "none yet, proactive"]

Do the following, in this order:

1. Restate my setup back in 2-3 sentences so I can correct you before you build the plan on
   a misunderstanding.

2. Classify every persona fact and every sample memory entry into exactly one of three
   buckets, stating the rule you applied for each, not just your verdict:
   - IDENTITY LANE: facts that define who the agent is regardless of session or task - name,
     core personality/voice traits, backstory, stated values/boundaries, and specific named
     relationship facts with a user.
   - WORKING LANE: anything session-, task-, or time-scoped - recent events, world-state
     facts, preferences known to change, anything timestamped or tied to one conversation.
   - AMBIGUOUS (default to working lane): facts that look identity-like but where my own
     description implies the persona is meant to evolve through experience. Default these to
     working lane and tell me explicitly why.

3. From the identity-lane facts only, write 10-20 numbered "persona probe" questions I can
   ask the agent before and after any model swap to check whether its personality held up.
   Cover at minimum: self-identification (name), one specific relationship fact, one stated
   value/boundary, one voice/tone sample, and one question where a generic non-persona answer
   would look visibly different from my agent's actual answer.

4. Estimate re-validation cost as a ratio: how many identity-lane items vs. total corpus size,
   stated in plain terms (e.g. "47 of ~3,200 entries, under 2% of the corpus").

5. Write a go/no-go checklist with concrete, checkable pass/fail criteria (not vague advice) -
   e.g. "9 of 10 probe pairs semantically consistent before vs. after." Always require human
   review of the actual transcripts (not just a score) before calling it a "go" if any
   boundary- or value-related probe fails.

6. Draft a short "transition brief" - a user-facing note I could send if the probes show
   real drift, acknowledging the change rather than silently shipping a changed personality.
   Write it in my agent's own established voice if its rules allow a direct explanation. If my
   agent has a never-break-character or never-admit-being-an-AI rule, don't override that rule
   to deliver this - instead write it as in-world flavor text that signals "something changed"
   without literal tech language, and tell me explicitly that's the resolution you chose.

7. List 2-4 risks specific to my setup (e.g. "no split exists yet so this lane assignment is
   your best first guess and needs my review," or "my persona is explicitly meant to evolve,
   which weakens the identity/working split itself").

Output as a single markdown report with these sections, in this order: Setup Summary,
Identity Lane Manifest, Working Lane Manifest, Ambiguous/Flagged Items, Persona Probe Set,
Re-validation Cost Estimate, Go/No-Go Checklist, Transition Brief Template, Risks Specific
to This Setup.

Guardrails: don't invent persona facts or statistics I didn't give you. Don't claim the
probe set guarantees no drift - say plainly it's a bounded sample. Don't recommend "go" on
probe scores alone if a boundary/value probe failed. Don't claim to actually run the
migration or re-embedding - you're producing the plan, not executing it. If what I gave you
is too thin to classify meaningfully, tell me and ask for more instead of guessing.
```

## What you get back

A single markdown report with nine sections (Setup Summary, Identity Lane Manifest, Working Lane Manifest, Ambiguous/Flagged Items, Persona Probe Set, Re-validation Cost Estimate, Go/No-Go Checklist, Transition Brief Template, Risks Specific to This Setup) — see the prompt above for exactly what each contains.

## What this is not

This is a planning aid, not the migration itself. It does not touch your actual vector store, does not re-embed anything, and does not guarantee your persona will survive a swap — it gives you a concrete, testable way to check, and a plan for what to re-validate if you do go ahead. Running the actual dual-index store and re-embedding adapter is separate infrastructure work; this skill is the design step before you build or operate that.
