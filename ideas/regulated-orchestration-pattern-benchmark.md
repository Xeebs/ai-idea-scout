# RegBench: An Open, Cross-Domain Orchestration-Pattern Benchmark for Regulated Document Processing

- **Status**: PROPOSED
- **Date**: 2026-11-12
- **Topic**: Multi-agent architectures
- **Source**: research/2026-11-12-multi-agent-architectures.md · P6
- **Maturity verdict**: PARTIAL — An arXiv preprint (Kulkarni, 2603.22651) runs 500 configurations across 5 models and 4 orchestration patterns on financial-document extraction, introducing an amortized cost-per-field metric. OrchBench (arXiv 2607.25656) is a general but domain-agnostic orchestration-plan simulator. Real, fairly rigorous benchmarking work exists but is narrow to one domain (finance) and remains an academic preprint, not an adopted cross-domain standard.
- **Format**: BOTH

## The Gap
A GitHub issue (KatsuyaITO/indx-autoresearch-financeaiready, 2026-10-31) explicitly requests case studies on "Benchmarking Multi-Agent LLM Architectures for Financial Document Processing: Orchestration Patterns, Cost-Accuracy Tradeoffs and Production Scaling Strategies" generalized for making data "AI-ready" — itself an unmet ask, not a completed benchmark. An AWS guide (Nov 3, 2026) covers a multi-agent system for regulated engineering workflows, but is a single-vendor how-to for one domain, not a general cross-domain comparison. The one rigorous methodology that exists (Kulkarni) is locked to financial documents and lives only as an academic preprint.

## The Project
Generalize the Kulkarni methodology (amortized cost-per-field metric, 4 orchestration patterns across multiple models) into an open, maintained benchmark harness with pluggable domain modules — starting with financial documents (replicating/extending Kulkarni), then adding healthcare prior-authorization forms, legal contract review, and insurance claims processing, each with its own ground-truth-labeled extraction task but the same comparable cost-accuracy metric. The pluggable domain-module design — not a one-off financial study — is the centerpiece, directly answering the GitHub issue's ask for case studies that hold across "regulated" workflows generally rather than financial documents specifically.

Components: the core orchestration-pattern test harness (sequential/parallel/hierarchical/reflexive) with the amortized cost-per-field metric; a domain-module interface (dataset + ground truth + domain-specific error-cost weighting); the first two domain modules (finance, one additional regulated domain); a published, comparable results table.

## Tangible Impact
**Population**: Engineering and compliance teams at regulated-industry companies — insurance claims processors, healthcare prior-authorization teams, legal-document review shops, and the financial-services team already represented by the GitHub issue's requester — choosing an orchestration architecture for document-processing pipelines that must meet accuracy and auditability bars.
**Mechanism**: Today a regulated-industry team picking an orchestration pattern has no comparable data outside their own domain, so they either repeat an expensive 500-config-style study from scratch or guess. A maintained, pluggable cross-domain benchmark means a new regulated domain can slot into the existing comparable methodology instead of commissioning its own academic-scale study, cutting the time and cost to make an evidence-based architecture decision.
**Measure**: (1) Time/cost for a new domain team to get a comparable cost-accuracy verdict via the pluggable harness vs. commissioning a from-scratch study (target: days vs. months). (2) Amortized cost-per-field comparability across at least 3 domains on the published benchmark. (3) Number of regulated-domain teams citing or adopting the harness's results in their own architecture decisions.

## Why Now
The Kulkarni preprint just established a rigorous, reusable cost-accuracy methodology for one domain within recent months, and a live GitHub issue in this exact window is explicitly asking for the cross-domain generalization — the methodology and the demand surfaced in the same window, with nobody yet connecting the two.

## Skill Angle
Given a domain's document type and a small labeled sample, recommend which orchestration pattern is likely best based on existing benchmark data and domain-module results — a one-shot advisory task for a team that wants a quick, evidence-informed starting point before committing to running the full harness on their own corpus.

## MVP Sketch
Reimplement Kulkarni's financial-document benchmark as the first pluggable domain module (open-sourcing the comparison framework, not just the finance result), then add one additional domain using a public or synthetic labeled dataset with the same orchestration patterns and cost-per-field metric, to prove the pluggable design transfers. Experiment: if the amortized cost-per-field metric doesn't transfer meaningfully to the second domain, the "one metric fits all regulated domains" hypothesis breaks and domain-specific metrics are needed instead — a useful early finding. 3-4 weeks, 1-2 people.

## Risks & Open Questions
- A well-resourced vendor (AWS, Qodo, or a consulting firm) could publish their own cross-domain study first and set the de facto standard.
- Finding or constructing comparably labeled ground-truth datasets across multiple regulated domains is expensive and may require domain-expert involvement per module.
- "Regulated domain" compliance requirements (auditability, specific accuracy bars) vary enough across finance/healthcare/legal that a single comparable metric may oversimplify real decision criteria.
- The academic preprint's own authors could generalize their work across domains before this project gets built.
