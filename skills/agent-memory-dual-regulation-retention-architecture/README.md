# Agent Memory Dual-Regulation Retention Architecture

A paste-in prompt for drafting a memory retention policy that resolves the collision between **GDPR Article 17** (the right to erasure) and **EU AI Act Article 12** (the duty for high-risk AI systems to keep decision records). Use this when your team runs a memory-enabled agent — built on something like Mem0, Letta, or Zep — that makes or materially informs high-risk-adjacent decisions (credit, hiring, benefits eligibility, etc.) for people in the EU, and you need a defensible answer to "what can we delete and what must we keep?"

## When to use this

Use it the moment you hit, or want to get ahead of, this collision:

- You received a GDPR erasure request and aren't sure whether honoring it will wipe out records your AI Act high-risk obligations require you to keep.
- You're about to launch (or are already running) a memory-enabled agent in the EU market and legal is asking for a retention policy you don't have.
- Your memory backend's delete API (e.g., Mem0's delete-by-user) will happily erase everything, but you don't actually know which of those memories double as a legally-required decision record.

If your agent isn't high-risk under the AI Act and has no EU exposure, you don't need this — a plain TTL on all memory is enough, and you should say so instead of forcing this framework on a simple case.

## What you need to hand over

**This is a Manual input task in this portable form**: because a plain chat tool can't read your codebase or call your memory backend's API directly, you paste in the real artifacts yourself. (If you're using this inside Claude Code with repo access instead of this README, the skill can read your integration code directly rather than you retyping it — see `SKILL.md` in this folder for that version.)

Paste in:

1. **The actual memory-write call sites** — the code or config where your agent calls something like `memory.add()`, `memory.insert()`, or an equivalent write, for each distinct place in your system. Not a summary — the real snippets, or close paraphrases with real field names.
2. **The schema or fields stored per write** — what each write actually contains (free text, structured fields, metadata like timestamps or model version).
3. **A few representative log or trace entries** — real (or realistically redacted) examples of what gets written in each category, so the classification isn't guesswork.
4. **Which of your agent's actions are high-risk under the EU AI Act** (e.g., Annex III categories: credit scoring, employment/recruitment screening, benefits eligibility, biometric ID, etc.). This is a factual/legal call only you or your counsel can make — if you don't know yet, say so and the output will flag it rather than assume.
5. Optionally, your existing retention defaults (TTL for ordinary data, any existing legal hold policy) — if you don't have one yet, say so.

A paragraph like "we store conversations and some decisions" is not enough — bring the real snippets, schema, and sample log entries.

## What happens

Once you've supplied the inputs above, the assistant will:

1. **List every distinct memory write site** found in what you pasted — what triggers it, what it contains, what feature it supports. It will not invent write sites you didn't provide evidence for.
2. **Confirm your high-risk categories** before classifying anything — if you haven't stated them, it will ask rather than guess.
3. **Classify each write site** into one of three buckets:
   - **Working memory** — ordinary conversational/session content with no link to a high-risk decision. Erasable on request, expires on a TTL.
   - **Decision record** — the structured reasoning behind a confirmed high-risk action. Must be retained under Art. 12 even after an erasure request, with identifying conversational content stripped where possible while the decision rationale, timestamp, and model version survive intact.
   - **Ambiguous / needs counsel review** — anything that doesn't cleanly fit either bucket. These are always surfaced explicitly, never silently forced into the "easy" answer in either direction.
4. **Draft a tiered retention policy** — a TTL per working-memory category (using your stated default, or marking it "TBD — needs your input" if you haven't given one — it will not invent a number like "30 days" out of thin air) and a survive/redact rule per decision-record category.
5. **Map each category to its legal basis** in plain language (GDPR Art. 17 for erasable categories, AI Act Art. 12 for retained ones) — framed as "this targets the Art. 12 requirement, confirm with counsel," never as a legal conclusion that you are compliant.
6. **Propose a deletion-audit-log schema** — the fields you should log on every erasure request to prove afterward exactly what was deleted, what was retained, and why.
7. **Write a handoff note** stating clearly that this is a design artifact for engineering and legal to review together — not a compliance certification — and naming what it explicitly does not cover (executing the deletion, or proving a physical/vector-store purge actually happened).

## Output format

You'll get back a single structured report, in this order:

1. **Classification Map** — a table: Write Site | Trigger | Example Content | Classification | Confidence (Confirmed / Needs counsel review).
2. **Retention Policy** — a table: Category | Retention Rule | On-Erasure-Request Behavior | Legal Basis.
3. **Open Legal Questions** — every ambiguous write site, with the specific reason it's ambiguous.
4. **Deletion Audit Log Schema** — a field list with the purpose of each field.
5. **Handoff Note** — one paragraph on what this report is (and isn't), and what the next step is.

## Guardrails — what this will never do

- Never classify something you didn't give evidence for. No inventing memory categories from a generic idea of "what agents usually store."
- Never tell you a classification or retention period is legally compliant. This drafts a structure for your counsel to review — it is not legal advice and not a compliance certification.
- Never silently resolve an ambiguous case by picking whichever bucket is more convenient. Ambiguity always goes into Open Legal Questions.
- Never invent a specific retention duration without a stated basis from you — unclear durations are marked TBD, not guessed.
- Never actually delete, redact, or migrate any of your data. This produces a policy document and an audit-log schema only.
- Never claim to prove that a deleted record was physically purged from your vector store or backend — that's a separate, downstream problem this explicitly does not solve.

## Paste-in prompt

If you want to run this directly in any AI chat tool, paste the following along with your artifacts:

> I need you to act as a memory-retention compliance architect for an agent that may be high-risk under the EU AI Act and has GDPR exposure. I will give you: (1) the real memory-write call sites/code or config in my system, (2) the schema/fields stored per write, (3) sample log/trace entries, and (4) which of my agent's actions are high-risk under the AI Act. Using only what I give you — do not invent write sites or categories — classify each write site as "working memory" (erasable, TTL-bound), "decision record" (must be retained per AI Act Art. 12, PII-stripped but rationale/timestamp/model-version intact), or "ambiguous — needs counsel review." Then draft a retention policy table, flag every ambiguous case explicitly instead of guessing, propose a deletion-audit-log schema, and close with a handoff note on what this does and doesn't cover (it does not execute deletions or prove physical purge). Never assert legal compliance — frame everything as a draft for counsel review.
