# RO-Crate Agent-Authorship Drafter

A self-contained prompt template for drafting correctly-formed AI-agent authorship metadata into an existing [RO-Crate](https://www.researchobject.org/ro-crate/) (`ro-crate-metadata.json`). Paste the prompt below into any AI chat tool (Claude, ChatGPT, Gemini, etc.), fill in your details, and run it.

## Why this exists

RO-Crate is the JSON-LD packaging format used to bundle research datasets, code, and derived outputs with their metadata — it's the format behind WorkflowHub and several national research-data infrastructure projects. Its metadata vocabulary comes from schema.org, and schema.org's `creator`/`author` properties only accept a `Person` or an `Organization` — there is no type for "an autonomous AI agent produced this." As AI agents increasingly generate datasets, run analyses, or produce derived research artifacts inside pipelines that already use RO-Crate, researchers are forced to either misattribute agent-produced work to the supervising human, or drop authorship metadata entirely. Neither is acceptable for reproducibility audits, citation records, or later disputes about who's responsible for an error.

This skill does not wait for a ratified standard. It drafts a documented, interoperable extension — layering `prov:SoftwareAgent` (from the existing W3C PROV ontology) onto a `schema:SoftwareApplication` base — and produces the exact patch to insert into your crate today, while being explicit that this is a community extension, not yet an adopted schema.org or RO-Crate type.

## What you need before you start

1. **The full contents of your `ro-crate-metadata.json`** — paste the whole file, or at minimum the `@graph` entries for the artifacts in question, if the file is very large.
2. **For each artifact the AI agent produced**, have ready:
   - Its `@id` in the crate, or enough of a description (filename, position) to find it.
   - Which model/tool produced it — name and version or snapshot date.
   - An invocation or session identifier, if your tooling logs one (a run ID, job ID, or conversation/session ID).
   - The date the artifact was generated.
   - The supervising human's name, and ORCID if you have one.
3. **Decide whether you also want a full-crate scan** for *other* artifacts that look agent-produced but currently have no authorship claim at all.

If you're missing any detail in item 2, say so honestly when you run the prompt — don't make something up to fill the field. A fabricated-looking invocation ID or model version defeats the entire point of recording accurate provenance.

## The prompt

```
You are drafting agent-authorship metadata for a RO-Crate research artifact package.

Background: schema.org's `creator`/`author` properties only accept `Person` or
`Organization` — there is no ratified type for "an AI agent produced this." I need
you to draft a documented extension (layering `prov:SoftwareAgent` onto a
`schema:SoftwareApplication` base, since that's the most interoperable choice
available without inventing a vocabulary from scratch) and show me the exact
patch to apply to my existing crate file. Do NOT claim this is an adopted
schema.org or RO-Crate standard — it is a community extension pending an open
standards discussion (see the ResearchObject/ro-crate GitHub issue on this exact
gap), and your output must say so explicitly.

Here is my ro-crate-metadata.json (or the relevant @graph excerpt):
<PASTE JSON HERE>

Here is what the AI agent produced:
- Artifact @id (or filename/description): <...>
- Model/tool name and version or snapshot date: <...>
- Invocation/session/run ID (if logged): <...>
- Date generated: <...>
- Supervising human's name (and ORCID if known): <...>

[If you want the full-crate scan, add:]
Also scan the rest of the crate for other entities that look agent-produced
(by filename pattern, encodingFormat, or position in a pipeline) but have no
creator/author claim at all. Flag these as unconfirmed candidates only — do not
assert they are definitely agent-produced.

Now do the following, in order:

1. Parse the crate JSON. If it doesn't parse, tell me specifically what's
   wrong and stop — don't guess at structure.
2. Find the named artifact(s) by @id (or by matching the description I gave).
3. For each one, classify its current authorship state as OK (already has a
   creator/author appropriate to the agent-produced reality), MISSING (no
   creator/author at all), or MISATTRIBUTED (credited to a Person for work I
   told you the agent actually did).
4. Draft the SoftwareAgent entity: @id built deterministically from the model
   name + version + invocation ID, @type ["SoftwareApplication",
   "prov:SoftwareAgent"], name, softwareVersion, invocationId, dateCreated,
   and supervisedBy pointing to a Person entity (reuse one already in the
   crate if it matches my supervisor, or draft a minimal new Person stub).
5. For each MISSING or MISATTRIBUTED artifact, draft the exact patch — the
   creator/author property to add. If an artifact is MISATTRIBUTED, do NOT
   silently replace the existing human reference. Ask me to choose: (a)
   replace the human creator with the agent, (b) list both as co-creators, or
   (c) keep the human as creator and add the agent via a separate
   prov:wasGeneratedBy-style property.
6. If I asked for the full-crate scan, list the heuristic candidates you
   found, each tagged "unconfirmed — check by hand."
7. Give me the standing caveat about this not being a ratified standard yet,
   citing the open GitHub issue.

Format your answer as:
1. **Crate Scan Summary** — table: Artifact @id | Current creator/author |
   Status (OK/MISSING/MISATTRIBUTED).
2. **Drafted SoftwareAgent Entity** — the full JSON-LD block to append to
   @graph, plus any new minimal Person stub needed.
3. **Patch to Apply** — before/after JSON snippets for each MISSING/
   MISATTRIBUTED artifact, not a full-file rewrite.
4. **Heuristic Review List** (only if I asked for the scan) — unconfirmed
   candidates.
5. **Standing Caveat** — the non-ratified-extension note, with the GitHub
   issue cited.

If anything I gave you is missing or the JSON doesn't parse, stop and ask me
instead of filling the gap with a placeholder.
```

## What you get back

A five-section markdown report: a scan table showing each artifact's current authorship status, the drafted `SoftwareAgent` JSON-LD entity (and any new minimal `Person` stub it needs), a reviewable before/after patch for each artifact that needs fixing (never a full-file rewrite), an optional list of other unconfirmed agent-produced-looking artifacts if you asked for the scan, and a standing caveat that this extension isn't an adopted standard yet.

## What this is not

This is a one-shot drafting aid for a specific crate, not an automated pipeline, not a validator library you run in CI, and not the standards process itself. If you want a maintained validator that checks any crate against this extension automatically, or you want to help push the extension toward actual adoption, that's a separate, larger effort tracked against the open `ResearchObject/ro-crate` GitHub issue on AI-agent authorship — this skill only gets you the correctly-drafted metadata for the artifacts in front of you right now.

## Guardrails this prompt enforces

- Never overwrites an existing human authorship claim without asking which of three fixes you actually want.
- Never invents an invocation ID, model version, generation date, or supervisor identity — it asks instead.
- Never claims the extension is an adopted schema.org/RO-Crate standard.
- Never asserts the heuristic scan's results as fact — they're flagged for human review only.
- Never rewrites your whole crate file silently — you always see a reviewable patch.
