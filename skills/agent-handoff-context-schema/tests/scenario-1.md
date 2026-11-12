# Scenario 1 — Research-to-Report Pipeline on LangGraph

## Input a user would actually give

> We're building an internal "market brief" generator on LangGraph. It's three agents in sequence:
> 1. **Researcher agent** — takes a topic, runs web search and a couple of internal document lookups, and summarizes the 6-8 most relevant sources, noting which claims are well-supported vs. shaky.
> 2. **Writer agent** — takes the researcher's summary and drafts a 1-page brief in our house style.
> 3. **Fact-Checker agent** — reads the draft and the original sources and flags any claim in the draft that isn't actually backed by a source.
>
> Today, all three agents just read and append to the same LangGraph message list — it's the full chat history, no structure. We're on LangGraph, no other framework.
>
> The failure we keep hitting: the Writer agent sometimes restates a claim the Researcher had already flagged as shaky/low-confidence as if it were solid, because that nuance gets buried in a long summary message and the Writer just skims for "facts," not confidence levels. We'd like a handoff envelope that fixes this.

## Pass criteria

- [ ] Output maps the pipeline as 3 agents and identifies 2 handoff points (Researcher→Writer, Writer→Fact-Checker), not collapsed into one.
- [ ] The Researcher→Writer envelope schema includes the six fixed fields (decisions_made, rejected_alternatives, artifacts, errors_encountered, open_questions, budget_consumed) plus meta, and is structured — not prose.
- [ ] `decisions_made` or a closely related field for this handoff explicitly carries confidence/shakiness per claim, since that's the named failure (e.g. decisions_made includes something like "treated source X as high-confidence" / rejected_alternatives or a flagged field marks low-confidence claims as not-yet-verified) — it should not bury confidence inside free text where it can get skimmed past again.
- [ ] Worked example uses this pipeline's actual domain terms (researcher, writer, fact-checker, market brief, sources, claims) — not generic "Agent A / Agent B" placeholders.
- [ ] Output states where the envelope slots into LangGraph specifically (a dedicated state key, not inside the message list) since the user named LangGraph.
- [ ] Validation checklist has at least one item that directly targets the named failure — e.g. a post-receive check asking whether the Writer's draft treats every low-confidence claim from the envelope as low-confidence.
- [ ] No invented specifics (no fabricated source names, numbers, or filenames) beyond what the user gave; any unfilled field is marked `<< not specified >>` rather than guessed.
- [ ] Does not output a validator library, adapter code, or installation instructions — stays a one-shot drafted schema + checklist.

## Fail conditions

- Treats all agents' handoffs as one generic envelope with no attention to the stated failure.
- Produces a single prose paragraph instead of the structured `## Pipeline / ## Envelope Schema / ## Worked Example / ## Where this slots in / ## Validation Checklist / ## Open Gaps` format.
- Invents source titles, confidence percentages, or budget numbers the user never gave without marking them as assumptions/unspecified.
