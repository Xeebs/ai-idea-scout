# Scenario 1 — Single derived artifact, no authorship at all

## Setup
A computational-biology postdoc packaged a variant-calling pipeline output as an RO-Crate for deposit on WorkflowHub. One of the derived files — a filtered VCF — was produced by an autonomous coding agent that wrote and ran the filtering script end-to-end from a natural-language spec; the postdoc only reviewed and approved the result. The crate currently has no authorship claim at all on that file.

## Input handed to the skill

Pasted `ro-crate-metadata.json` excerpt:
```json
{
  "@context": "https://w3id.org/ro/crate/1.1/context",
  "@graph": [
    {
      "@id": "ro-crate-metadata.json",
      "@type": "CreativeWork",
      "conformsTo": {"@id": "https://w3id.org/ro/crate/1.1"},
      "about": {"@id": "./"}
    },
    {
      "@id": "./",
      "@type": "Dataset",
      "name": "Variant calling pipeline run 2026-11-10",
      "hasPart": [
        {"@id": "raw_reads.fastq.gz"},
        {"@id": "filtered_variants.vcf"}
      ]
    },
    {
      "@id": "raw_reads.fastq.gz",
      "@type": "File",
      "name": "raw_reads.fastq.gz",
      "creator": {"@id": "#jane-doe"}
    },
    {
      "@id": "filtered_variants.vcf",
      "@type": "File",
      "name": "filtered_variants.vcf",
      "encodingFormat": "text/vcf"
    },
    {
      "@id": "#jane-doe",
      "@type": "Person",
      "name": "Dr. Jane Doe",
      "identifier": "https://orcid.org/0000-0002-1111-2222"
    }
  ]
}
```

Artifact details given to the skill:
- Artifact `@id`: `filtered_variants.vcf`
- Model/tool: "AutoBio-Agent v3.2 (Nov 2026 snapshot)"
- Invocation ID: `run-20261110-0847`
- Date generated: 2026-11-10
- Supervising human: Dr. Jane Doe, ORCID `0000-0002-1111-2222` (already present as `#jane-doe` in the crate)
- Full-crate scan requested: yes

## Pass criteria
- [ ] Crate Scan Summary correctly classifies `filtered_variants.vcf` as `MISSING` (no creator/author at all) and `raw_reads.fastq.gz` as not in scope (it already has a human creator and wasn't named as agent-produced).
- [ ] Drafted `SoftwareAgent` entity uses `@type: ["SoftwareApplication", "prov:SoftwareAgent"]`, includes `name`, `softwareVersion`, `invocationId: "run-20261110-0847"`, `dateCreated: "2026-11-10"`, and `supervisedBy` pointing to `#jane-doe` (reusing the existing Person entity rather than drafting a duplicate).
- [ ] Patch section shows a before/after snippet adding `creator: {"@id": "#agent-..."}` (or similar) to `filtered_variants.vcf` only — not a full-file rewrite.
- [ ] Heuristic Review List runs since the scan was requested, and does not falsely re-flag `filtered_variants.vcf` (already handled) or `raw_reads.fastq.gz` (already has a real human creator, not generated-looking) — if nothing else qualifies, says so explicitly rather than inventing candidates.
- [ ] Standing Caveat section present, states this is not an adopted schema.org/RO-Crate type, cites the open GitHub issue.
- [ ] Does not ask the three-option MISATTRIBUTED question here (correctly, since this artifact was MISSING, not MISATTRIBUTED).

## Fail conditions
- Treats `filtered_variants.vcf` as already having valid authorship, or skips drafting the patch.
- Invents an invocation ID, version, or supervisor different from what was given.
- Drafts a duplicate `Person` entity for Jane Doe instead of reusing `#jane-doe`.
- Presents the `SoftwareAgent` type as an official/ratified schema.org term.
- Rewrites the entire crate file instead of a scoped patch.
