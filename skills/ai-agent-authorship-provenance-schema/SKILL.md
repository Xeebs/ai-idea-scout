---
name: ai-agent-authorship-provenance-schema
description: Given an existing ro-crate-metadata.json and a description of what an AI agent produced (model, invocation, supervising human), drafts the correctly-formed SoftwareAgent authorship entity and the exact JSON-LD patch to insert it, and flags other entities in the same crate that look agent-produced but carry no authorship claim. Use when packaging or auditing RO-Crate research artifacts that include AI-agent-generated datasets, code, or analysis outputs.
---

# RO-Crate Agent-Authorship Drafter

## When to use this
Use this when someone has an RO-Crate (`ro-crate-metadata.json`) that packages research outputs — datasets, analysis code, derived results — and at least one of those outputs was produced (not just assisted) by an AI agent rather than, or in addition to, a human. Trigger phrases: "how do I record that an agent generated this dataset in my RO-Crate", "this derived file is credited to me but I didn't run the analysis, the agent did", "does our crate have other agent-produced files with no authorship on them at all". schema.org's `creator`/`author` properties only accept `Person` or `Organization` — there is no ratified type for "an autonomous agent did this" — so this skill fills that gap with a documented, community-traceable extension rather than silently misattributing to the supervising human or dropping authorship entirely.

This is a one-shot drafting/review aid, not the validator library or the RO-Crate spec PR themselves — those are the larger project this skill is scoped from. This skill produces the exact entity and patch a researcher pastes into their own crate file; it does not run as an automated pipeline step and does not submit anything upstream.

## Inputs
**Data source**: Connected — reads the researcher's own `ro-crate-metadata.json` file (RO-Crate is a mature, widely-adopted JSON-LD packaging format used by WorkflowHub and multiple national research-data infrastructures). The researcher pastes or uploads the file's actual JSON content directly rather than retyping or describing it; no external API call is made — RO-Crate is a local file format, not a live connector, so "connected" here means this skill reads the researcher's existing structured artifact in place rather than asking them to describe it in prose.

What to hand over:
1. The full contents of the existing `ro-crate-metadata.json` (paste the JSON, or the relevant `@graph` excerpt if the file is very large).
2. For each artifact the AI agent produced: its `@id` in the crate (or enough description to locate it, e.g. filename), which model/tool produced it (name and version/snapshot date), an invocation or session identifier if one exists (run ID, job ID, conversation/session ID — whatever the researcher's tooling logs), the date the artifact was generated, and the supervising human's name (and ORCID if known).
3. (Optional, for the audit pass) Whether the researcher wants the whole crate scanned for *other* entities that look agent-produced but carry no creator/author claim at all.

If any of the per-artifact details in (2) are missing, ask for them rather than inventing a placeholder invocation ID, model version, or supervisor name — a fabricated-looking provenance field is worse than an honestly incomplete one.

## Procedure
1. **Parse the crate.** Confirm the pasted JSON is valid JSON-LD with a `@graph` array. If it doesn't parse, say so specifically (what broke) and ask for a corrected paste rather than guessing at structure.
2. **Locate each named artifact** by `@id` (or by matching filename/description if no `@id` was given) inside `@graph`.
3. **Classify each artifact's current authorship state**:
   - `OK` — already has a `creator`/`author` pointing to an entity typed in a way consistent with the agent-produced reality (rare today; usually means nothing to do).
   - `MISSING` — no `creator`/`author` property at all.
   - `MISATTRIBUTED` — has a `creator`/`author` pointing to a `Person` (typically the supervising researcher) for work the researcher confirmed the agent actually produced.
4. **Draft the `SoftwareAgent` entity** for the producing model/tool, using the PROV-O-aligned extension (since no ratified schema.org type exists as of today, this layers `prov:SoftwareAgent` onto a `schema:SoftwareApplication` base via an explicit `@context` entry — the most interoperable choice available, not an invented vocabulary from scratch). Required fields: `@id` (deterministic, built from model name + version + invocation ID so repeated runs of the same model get distinct entities per invocation), `@type: ["SoftwareApplication", "prov:SoftwareAgent"]`, `name`, `softwareVersion` (model/tool version or snapshot date), `invocationId`, `dateCreated`, and `supervisedBy` (a reference to a `Person` entity — reuse an existing Person entity in the crate if the supervisor is already present, or draft a minimal new `Person` stub with name and ORCID if given).
5. **For each `MISSING` or `MISATTRIBUTED` artifact confirmed by the researcher as agent-produced**, draft the exact patch: the `creator` (or `author`) property to add pointing to the new `SoftwareAgent` `@id`. For `MISATTRIBUTED` entities specifically, do not silently drop the existing human reference — ask the researcher whether the correct fix is (a) replace the human creator with the agent, (b) list both as co-creators, or (c) keep the human as `creator` and add the agent via a separate `prov:wasGeneratedBy`-style property, since this is a provenance-accuracy judgment call, not a mechanical one.
6. **If the researcher opted into a full-crate scan**, walk the rest of `@graph` for entities with no `creator`/`author` property at all whose `@id`, filename pattern, or `encodingFormat` suggests a generated/derived artifact (e.g. names containing "output", "results", "derived", "generated", or formats typical of pipeline output like `.vcf`, `.csv` analysis results, generated code files) that the researcher hasn't already addressed in step 5. List these as **heuristic, unconfirmed** candidates for the researcher to check by hand — never assert these are definitely agent-produced.
7. **Assemble the output** (format below), including the standing caveat that `prov:SoftwareAgent`-via-schema.org is a community extension, not an adopted schema.org or RO-Crate-ratified type as of today, tracked by the open `ResearchObject/ro-crate` GitHub issue on this exact gap — anything consuming this crate downstream that doesn't know this extension will simply ignore the new properties, not break, but also won't display or index agent authorship correctly until the ecosystem adopts it.

## Output format
A markdown response with exactly these sections, in order:
1. **Crate Scan Summary** — table: `Artifact @id | Current creator/author | Status (OK/MISSING/MISATTRIBUTED)`, one row per artifact the researcher named.
2. **Drafted SoftwareAgent Entity** — the full JSON-LD block to append to `@graph`, plus any new minimal `Person` stub needed for the supervisor.
3. **Patch to Apply** — for each `MISSING`/`MISATTRIBUTED` artifact, the exact property/value to add or change on that artifact's existing entity, shown as a before/after JSON snippet (not a full-file rewrite) so the researcher can see precisely what moved.
4. **Heuristic Review List** (only if the full-crate scan was requested) — bullet list of other entities with no authorship claim that look generated, each tagged "unconfirmed — check by hand."
5. **Standing Caveat** — the non-ratified-extension note from step 7, verbatim in substance, with the GitHub issue cited.

## Guardrails
- Never silently overwrite an existing human `creator`/`author` claim — a `MISATTRIBUTED` entity always gets the three-option question from step 5, never an automatic replace.
- Never invent an invocation ID, model version, generation date, or supervisor identity to fill a gap in what the researcher provided — ask instead; a fabricated-looking provenance field defeats the entire point of this skill.
- Never present the `SoftwareAgent` extension as an adopted schema.org or RO-Crate standard — it is a community-level extension pending an open standards discussion, and every output must say so.
- Never treat the heuristic scan (step 6) results as confirmed fact — they are candidates for human review only, and must be labeled as such in the output.
- Never rewrite the entire `ro-crate-metadata.json` file wholesale when a partial, reviewable patch would do — the researcher needs to see exactly what changed to trust the edit.
- If the pasted crate JSON doesn't parse or the researcher can't supply the per-artifact details in Inputs item 2, stop and ask rather than guessing at crate structure or provenance details.
