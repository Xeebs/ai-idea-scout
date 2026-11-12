# Idea File Format

This template is shared by both tracks. INFRA-track ideas live in `ideas/<kebab-case-slug>.md` (public repo). MARKETPLACE-track ideas live in `marketplace-content/ideas/<kebab-case-slug>.md` (separate private repo — see `marketplace-content/README.md`) and carry one extra header field.

```markdown
# <Project Title>

- **Status**: PROPOSED | EXPLORING | PROTOTYPING | SHELVED
- **Date**: YYYY-MM-DD
- **Topic**: <rotation topic this came from>
- **Source**: research/<digest-file>.md · <pattern ID, e.g. P3> (MARKETPLACE track: `marketplace-content/research/<digest-file>.md`)
- **Maturity verdict**: OPEN | PARTIAL (copy the gap-analyst's verdict note)
- **Format**: PROJECT | SKILL | BOTH (see heuristic in `docs/METHODOLOGY.md`)
- **Marketplace Fit**: LOW | MEDIUM | HIGH (MARKETPLACE track only — omit this line entirely on INFRA-track ideas in `ideas/`. See the rubric in `docs/METHODOLOGY.md`. Only HIGH ideas with Format SKILL/BOTH and a written `marketplace-content/skills/<slug>/` get packaged for the marketplace review queue.)
- **Data Sources**: MANUAL | CONNECTED — mandatory on both tracks. See the classification and required detail format in `docs/METHODOLOGY.md`'s "Data Sources" section. This is the single most load-bearing field for a human reviewing the idea: it's the first thing that decides whether a skill is a thin paste-and-prompt wrapper or something that actually reaches into the buyer's real data.

## The Gap
2–4 sentences: what the community signal showed, why nothing adequate exists today. Cite the evidence from the digest — who was asking for this and where.

## The Project
What gets built, concretely. Core loop, key components, and how the novel pattern is the centerpiece (not a feature bolted onto a generic app). 1–2 short paragraphs plus an optional component list.

## Tangible Impact
**Population**: the specific group of people affected, with a size estimate and a source for that estimate where possible. On the MARKETPLACE track this is the specific buyer type (e.g. "freelance copywriters doing cold outreach"), not an affected-population size estimate.
**Mechanism**: how this project changes their day, week, or outcomes — the causal chain, not a vibe.
**Measure**: 2–3 metrics that would prove the impact is real (e.g., "median time to file an appeal drops from 3 weeks to 2 days", "clinic triage error rate on the eval set").

## Why Now
What in the last 30 days makes this newly feasible or newly urgent (model capability, API, cost curve, regulation, community momentum).

## Skill Angle
(Only if **Format** is SKILL or BOTH.) What a Claude Code skill version of this would actually do: the trigger moment, the inputs a user hands it, and the output. For BOTH, state clearly how the skill differs from the project (e.g., the skill is a design/review/adoption aid; the project is the runtime infrastructure). Omit this section entirely for PROJECT-only ideas.

## MVP Sketch
The smallest version that tests the core hypothesis: scope, rough stack, and the single experiment that validates or kills it. Target: buildable in 2–4 weeks by 1–2 people.

## Risks & Open Questions
3–5 bullets. Include the strongest reason this might already be solved or unworkable.

## Human Feedback
(Optional, appears only once a human leaves a note via `dashboard/`.) Append-only, timestamped bullets: `- YYYY-MM-DD HH:MM — "<note>" (via dashboard)`. Never written by an agent, never removed by an agent — see `CLAUDE.md`'s "Human feedback always wins" rule.
```

## Rules

- The **Tangible Impact** section is mandatory and must name a specific population. "Developers" or "businesses" alone is too broad — narrow until you could find these people in a room.
- Never overwrite an existing idea file. Supersede with a new file and cross-link in `ideas/INDEX.md`.
- Keep ideas under ~120 lines (the optional **Human Feedback** section doesn't count against this — it's a human-maintained log, not part of the pitch).
- Status changes outside the pipeline's own promotion logic (PROTOTYPING, SHELVED, or a human overriding PROPOSED/EXPLORING) are made by a human via `dashboard/`, by editing the `- **Status**:` line directly — never automatically reverted.
- **Data Sources** must be concrete, never a bare "MANUAL" or "CONNECTED" label with nothing after it — name exactly what the user pastes/uploads (MANUAL) or exactly which named data source/API/MCP connector it reaches into and whether that connector already exists and is mature (CONNECTED). The dashboard surfaces this field prominently so a human can judge it at a glance; a vague entry defeats the point.
