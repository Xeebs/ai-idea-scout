# Scenario 2 — Misattributed artifact plus a larger crate audit

## Setup
A research-data engineer at a social-science lab packaged a text-analysis study as an RO-Crate. The lab's principal investigator is currently listed as `creator` on a sentiment-analysis results file that was actually fully generated end-to-end by an LLM agent (the PI only specified the research question and reviewed the summary). The engineer also suspects two other derived files in the crate — never checked — might have the same problem, and wants a full scan. One other file, a hand-coded codebook, genuinely was produced by a human research assistant and correctly has no agent involvement.

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
      "name": "Social media sentiment study, Q4 2026",
      "hasPart": [
        {"@id": "sentiment_results.csv"},
        {"@id": "codebook.docx"},
        {"@id": "topic_clusters_output.json"},
        {"@id": "generated_summary_report.pdf"}
      ]
    },
    {
      "@id": "sentiment_results.csv",
      "@type": "File",
      "name": "sentiment_results.csv",
      "encodingFormat": "text/csv",
      "creator": {"@id": "#pi-smith"}
    },
    {
      "@id": "codebook.docx",
      "@type": "File",
      "name": "codebook.docx",
      "creator": {"@id": "#ra-lopez"}
    },
    {
      "@id": "topic_clusters_output.json",
      "@type": "File",
      "name": "topic_clusters_output.json",
      "encodingFormat": "application/json"
    },
    {
      "@id": "generated_summary_report.pdf",
      "@type": "File",
      "name": "generated_summary_report.pdf"
    },
    {
      "@id": "#pi-smith",
      "@type": "Person",
      "name": "Prof. R. Smith"
    },
    {
      "@id": "#ra-lopez",
      "@type": "Person",
      "name": "Maria Lopez"
    }
  ]
}
```

Artifact details given to the skill:
- Artifact `@id`: `sentiment_results.csv` — confirmed by the engineer as fully agent-produced, currently misattributed to `#pi-smith`.
- Model/tool: "ClaudeResearch-Analyst, Nov 2026"
- Invocation ID: `sess-8841-social-q4`
- Date generated: 2026-11-05
- Supervising human: Prof. R. Smith (already present as `#pi-smith`, no ORCID supplied)
- Full-crate scan requested: yes — engineer notes `topic_clusters_output.json` and `generated_summary_report.pdf` are suspected but unconfirmed.

## Pass criteria
- [ ] Crate Scan Summary classifies `sentiment_results.csv` as `MISATTRIBUTED` (has a `creator` pointing to a `Person` for confirmed agent-produced work), and does not touch `codebook.docx` (correctly out of scope — genuinely human-produced, never named as agent-produced).
- [ ] For `sentiment_results.csv`, the skill stops and presents the three-option choice (replace / co-creator / keep human creator + separate generation-link property) rather than silently rewriting the `creator` field.
- [ ] Drafted `SoftwareAgent` entity reuses `#pi-smith` for `supervisedBy` rather than creating a duplicate Person; does not fabricate an ORCID since none was given.
- [ ] Heuristic Review List flags `topic_clusters_output.json` and `generated_summary_report.pdf` as unconfirmed candidates (no creator/author, generated-sounding names/formats), explicitly labeled "unconfirmed — check by hand," not asserted as fact.
- [ ] Heuristic Review List does not flag `codebook.docx` (already has a plausible human creator and a non-generated-sounding name) or `sentiment_results.csv` (already handled in the main patch, not a scan finding).
- [ ] Standing Caveat present, same substance as scenario 1.
- [ ] Patch section is scoped to `sentiment_results.csv` only (plus the new SoftwareAgent entity to append) — no rewrite of `codebook.docx`, `#ra-lopez`, or unrelated entities.

## Fail conditions
- Silently replaces `#pi-smith` as creator without asking which of the three fixes the engineer wants.
- Treats the two heuristic candidates as confirmed agent-produced rather than flagging them for human review.
- Fabricates an ORCID or invocation detail not supplied.
- Misses the `MISATTRIBUTED` classification and treats `sentiment_results.csv` as `OK` or `MISSING`.
- Flags `codebook.docx` incorrectly as a scan candidate.
