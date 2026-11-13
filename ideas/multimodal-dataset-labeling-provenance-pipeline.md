# Modal Chain: A Unified Cross-Modal Labeling and Provenance Pipeline for Multimodal Agent Training Data

- **Status**: PROPOSED
- **Date**: 2026-11-12
- **Topic**: Voice & multimodal agents
- **Source**: research/2026-11-12-voice-multimodal-agents-iii.md · P6
- **Maturity verdict**: PARTIAL (no single open-source tool covers labeling+provenance across text/image/audio/video end to end; pieces exist — CVAT (open source, vision-only, now with SAM3/YOLO11 auto-annotation), Label Studio (open source, 27k+ stars, general but no cross-modal provenance), Voxel51/FiftyOne 3.0 (claims 4 provenance layers across images/video/3D/audio, unclear which ship in the open-source tier vs. enterprise-only), a NiFi+Pixeltable stack (handles lineage/movement, not labeling) — but nothing unified and openly available end to end)
- **Format**: PROJECT
- **Data Sources**: CONNECTED — reads directly from the team's existing annotation tool APIs (Label Studio API, CVAT API, or FiftyOne dataset objects) and raw asset storage (an S3/GCS bucket or local filesystem the team already uses), rather than requiring manual re-upload of each asset. These per-modality tools are mature and widely deployed; the cross-modal schema and provenance ledger unifying them is what's missing.

## The Gap
An Encord-adjacent source states multimodal training data "is often annotated with separate tools and schemas for text, images, audio, and video, which leads to disconnects," and that "video curation can take 10-50x longer than text curation for equivalent dataset sizes" (single-vendor figure, unverified). The same research found that "retrofitting provenance tracking onto an existing dataset is far harder than building it in from the start," and that the core failure mode — "a file can pass every single-modality check and still fail once the modalities are combined" — remains unresolved by current per-modality tooling. Every fix found (Encord, Turing, Wirestock, Voxel51) is a single vendor's enterprise-gated product, not a shared open pipeline.

## The Project
A thin orchestration layer that unifies existing mature single-modality tools (CVAT for vision, Label Studio for text/audio transcripts, a custom segment labeler for audio/video) under one cross-modal schema — every labeled asset gets a record with modality, label, and provenance metadata (source, annotator, timestamp, tool version) — backed by a lightweight, content-hash-chained provenance ledger built in from the start rather than retrofitted. The centerpiece is the cross-modal consistency check: catching a file that passes every single-modality check but fails once modalities are combined, something no per-modality tool currently does.

Components: per-tool adapters (CVAT, Label Studio, custom audio/video), a unified cross-modal schema and provenance ledger, a cross-modal consistency checker, and a curation-time dashboard surfacing flagged inconsistencies before a dataset ships.

## Tangible Impact
**Population**: small and mid-sized multimodal-AI teams — outside the Encord/Turing/Voxel51-Enterprise price tier — fine-tuning voice, vision, or multimodal agents who currently stitch together CVAT, Label Studio, and ad hoc audio/video tools by hand, plus the downstream end users of agents trained on datasets with undetected cross-modal defects (e.g., an agent that misreads a spoken command against the wrong visual context because a mislabeled audio-video pair was never caught).
**Mechanism**: one schema plus a built-in provenance ledger removes the tool-switching and reconciliation overhead the Encord source describes, catches cross-modal defects at ingestion instead of after a model trained on them misbehaves, and produces an audit-ready provenance trail usable for compliance or copyright disputes without a separate retrofit effort.
**Measure**: time to curate/label a reference multimodal dataset against the current multi-tool-stitching baseline; cross-modal defect catch rate — pairs that pass single-modality checks but fail combined, caught before vs. after; percentage of a dataset with complete, queryable provenance records (vs. effectively none in ad hoc pipelines today).

## Why Now
2026 has seen a real increase in teams fine-tuning their own multimodal agents rather than only consuming frontier multimodal APIs, creating fresh demand for affordable cross-modal tooling. The single-modality tools this project would unify (CVAT with SAM3/YOLO11, Label Studio) are mature enough today to build a coordination layer on top of, rather than building annotation tooling from zero.

## MVP Sketch
Build an orchestration layer wrapping CVAT (vision) and Label Studio (text/audio transcripts), unified by one JSON-schema-defined cross-modal record stored in a lightweight provenance ledger (SQLite/Postgres with content-hash chaining). Validate against one reference multimodal dataset (e.g., 500 paired audio-video clips with text captions), measuring curation time and defect catch rate against a baseline team using the same underlying tools without the unification layer.

## Risks & Open Questions
- Enterprise players (Voxel51/FiftyOne 3.0) already claim overlapping provenance features; an open build needs to clearly differentiate on cost, openness, and the actual cross-modal schema or risks redundancy.
- Multimodal labeling needs vary enough by use case (speech agents vs. video agents vs. AR) that one "unified" schema may not generalize cleanly, forcing per-domain customization that erodes the core value proposition.
- The single-vendor 10-50x curation-time figure is unverified; the quantified improvement claim needs its own benchmark before being treated as fact.
- Provenance tracking adds overhead to every labeling step; if it meaningfully slows annotators down, teams may disable it, defeating the purpose it was built to serve.
