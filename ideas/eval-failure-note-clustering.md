# Pattern Mine: Automatic Clustering of Annotated Eval Failures into Shared Categories

- **Status**: PROPOSED
- **Date**: 2026-11-13
- **Topic**: LLM evaluation & observability
- **Source**: research/2026-11-13-llm-evaluation-observability.md · P5
- **Maturity verdict**: PARTIAL — hamel.dev's "Evals FAQ" (Hamel Husain & Shreya Shankar) names this directly as an open gap ("error analysis and pattern discovery") that most eval tools don't cover beyond table-stakes logging/annotation; narrow attempts exist (faultmap, 1 star, last pushed April 2026; Snorkel AI's commercial `ErrorAnalysis` API; an Atla AI comparative write-up) but none is a widely-adopted, evaluated standalone tool.
- **Format**: BOTH — a continuously-updating clustering pipeline that re-clusters as new annotations land is runtime infrastructure; a one-shot "cluster what I've already annotated" pass is a separable analysis task.
- **Data Sources**: MANUAL — the user exports/pastes a CSV or JSON file of their already-annotated eval failures: one row per failed output with its free-text reviewer note (e.g. "wrong tone for investor") and the output text itself, from whatever annotation surface they already use (Braintrust comments, LangSmith feedback, a spreadsheet, a custom internal tool). No single annotation platform is dominant enough to build one mature connector against without excluding most of the population — the whole gap hamel.dev names is that teams' annotation stores are heterogeneous and homegrown, so a tool-agnostic file import is the realistic entry point, not a narrower vendor-specific integration.

## The Gap
hamel.dev's "Evals FAQ" explicitly calls out "error analysis and pattern discovery" as a gap most eval tools leave to the team: practitioners manually annotate failed outputs with free-text notes but get no help recognizing that ten differently-worded notes describe one underlying failure mode. The source frames this as something teams must build themselves and tells readers to "watch for vendors addressing these gaps" as a signal of tool quality — implying it is still commonly unsolved. The only implementations found (faultmap, Snorkel's commercial SDK feature, Atla's write-up) are either unmaintained, paywalled inside a much larger platform, or purely descriptive.

## The Project
A standalone tool that ingests a team's existing annotated-failure export, embeds each free-text note (not the raw output — the note is where the human's judgment already lives), clusters the embeddings, and asks an LLM to propose a short, human-readable label for each cluster (e.g. "persona-tone mismatch," "unit conversion error") along with representative examples. A human reviewer approves, merges, or splits clusters in a lightweight review UI/CLI; approved clusters become a persistent taxonomy that the tool matches new incoming annotations against on every re-run, so the category list grows deliberately instead of silently drifting into duplicate near-synonymous tags.

Components: note-embedding + clustering stage (HDBSCAN or similar over sentence-embeddings of the free-text notes); LLM cluster-labeling pass with representative-example citation; a persistent taxonomy store with new-vs-existing-cluster matching; a review CLI/UI for merge/split/approve decisions.

## Tangible Impact
**Population**: ML/eval engineers and product teams who already manually annotate failed LLM outputs with free-text notes — the same practitioner audience hamel.dev's FAQ is written for, realistically any team running a human-in-the-loop eval review process (a standard practice recommended across eval literature, not a fringe one) once their annotation volume exceeds what one person can mentally pattern-match (roughly 50+ annotated failures, per practitioner reports of when manual review analysis starts breaking down).
**Mechanism**: Today a team's hard-won annotation notes sit as isolated free text — nobody can answer "what are our top 3 failure modes this month" without a person re-reading every note by hand. Automatic clustering turns that pile of notes into a ranked, named taxonomy the team can prioritize fixes against, and the persistent taxonomy means the same underlying failure doesn't get re-discovered and re-named every review cycle.
**Measure**: (1) time to produce a "top failure categories this month" report, from hours of manual note re-reading to minutes; (2) cluster-label precision — percentage of proposed cluster labels a human reviewer approves without editing, targeting ≥70% on a pilot team's real annotation history; (3) reduction in duplicate/near-synonymous category tags across review cycles, measured by taxonomy size growth rate before and after adoption.

## Why Now
Embedding models cheap enough to cluster a few hundred short free-text notes at negligible cost, and LLMs capable of proposing a coherent cluster label from a handful of representative examples, are both now a non-issue cost- and quality-wise — the blocker was never capability, it's that nobody has packaged the loop (embed notes → cluster → label → persist → match new notes against existing taxonomy) as a reusable tool, which is exactly what hamel.dev's FAQ still names as a gap.

## Skill Angle
Trigger: a team has just finished an annotation pass on a batch of failed eval outputs and wants to know what the recurring failure modes are before writing a bug-fix ticket list. Inputs: the annotated-failure export (CSV/JSON of note + output pairs) and, if one exists, their prior taxonomy file from a previous run. Output: a ranked list of proposed failure categories with representative examples and a count per category, plus — if a prior taxonomy was supplied — a note on which categories are new versus recurring. The skill is the one-shot "what are my failure patterns" pass; the project is the persistent taxonomy store and review tooling that keeps that taxonomy coherent run over run.

## MVP Sketch
A Python CLI taking a CSV of (note, output) pairs, embedding notes with a standard sentence-embedding model, clustering with HDBSCAN, and calling an LLM once per cluster to propose a label and justification from the cluster's top-5 closest notes. Experiment: run against one pilot team's real 100+ item annotation history and check whether a human domain expert agrees the proposed clusters are coherent and the labels are usable without heavy editing. 2–3 weeks, 1 person.

## Risks & Open Questions
- Free-text notes vary wildly in granularity and style across reviewers on the same team, which may produce noisy clusters until note-writing conventions are nudged toward consistency — an adoption friction, not a technical blocker.
- A well-resourced eval vendor (Braintrust, Galileo) could ship this as a feature inside their existing annotation UI, which would undercut a standalone tool's reason to exist — the differentiator has to be working against whatever annotation export a team already has, not requiring migration to one platform.
- Cluster count and granularity (is "wrong tone" one cluster or three) is inherently subjective; the human merge/split review step is load-bearing and can't be fully automated away.
- Evidence here is one credible practitioner source (hamel.dev) plus a handful of unmaintained attempts — thinner signal than a trending community thread, worth watching for recurrence before heavy investment.
