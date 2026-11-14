# Verified Live: Independent Post-Deploy Artifact Verification for Agentic Release Pipelines

- **Status**: PROPOSED
- **Date**: 2026-11-14
- **Topic**: AI safety & guardrails in production
- **Source**: research/2026-11-14-ai-safety-and-guardrails-in-production.md · P5
- **Maturity verdict**: PARTIAL — Metoro's "AI Deployment Verification," Harness's MCP-based Dynatrace-linked post-deploy flow, and Azure AgentOps' "VERIFIED" gate are real adjacent building blocks, but none specifically targets "an agentic pipeline self-reporting release success without independently verifying the live artifact" as a named, evaluated product — every concrete example found (`amoai-tech/mdeai#655`) is one company's bespoke, unshared patch.
- **Format**: BOTH
- **Data Sources**: CONNECTED — queries the CI/CD pipeline's own deploy-status API (GitHub Actions, GitLab CI, or similar, all mature) to get the claimed deploy outcome, and independently hits the live production endpoint/CDN directly via HTTP plus, where available, a build-hash or content-fingerprint check against the expected artifact — no paste-in step; both sources are standard, already-exposed APIs/endpoints.

## The Gap
An AI-agent-driven release pipeline marks a deploy green based on the deploy step completing, not on an independent check that the live artifact reflects the intended change. `amoai-tech/mdeai#655` (2026-10-31, 22 comments) is a team's own discovery that their pipeline reported false-positive success, fixed with "report success only after the live website is verified" — explicitly because an agent had been "shipping" things that never verifiably went live correctly. No generic, evaluated guardrail for agentic CI/CD fills this gap; only one-off company fixes and general-purpose observability tools repurposed toward the problem.

## The Project
A middleware verification step that sits after an agentic deploy pipeline's own "success" signal and performs an independent out-of-band check before anything is marked truly verified: fetches the live production endpoint directly, compares a content/build-hash fingerprint against the expected artifact from the deploy manifest, and (optionally) queries an APM for post-deploy error-rate anomalies. Only after this independent check passes does it flip a separate "VERIFIED" status — generalizing the Azure AgentOps pattern and the one bespoke `mdeai` fix into a drop-in gate usable by any agent-driven pipeline, not one company's in-house stack.

## Tangible Impact
**Population**: engineering teams adopting agent-driven/autonomous release automation (coding agents that commit, build, and deploy with minimal human review) — a fast-growing but still identifiable segment, evidenced directly by the `mdeai` team's own discovery that their agentic pipeline needed this fix and by Harness's and Azure's parallel investment in adjacent verification tooling for the same emerging workflow.
**Mechanism**: converts "green means the deploy step ran" into "green means the live artifact was independently confirmed," preventing silent broken production pushes from being reported as successful — the exact false-positive the `mdeai` team found in their own system — before a user notices.
**Measure**: number of deploys where the independent check disagrees with the pipeline's own self-report (the core metric proving the gap is real); mean time between a failed/partial deploy and detection (target: seconds at the verification gate vs. whenever a user files a bug); reduction in "silently shipped nothing" incidents post-adoption.

## Why Now
The `mdeai#655` PR (2026-10-31) is a live, recent, named example of exactly this failure occurring in a real agentic pipeline, and the parallel emergence of Metoro's and Azure AgentOps' adjacent verification features shows the market is converging on "verification as a separate step" right now, without yet converging on a shared, evaluated tool for it.

## Skill Angle
A companion skill reviews a pasted CI/CD pipeline configuration (YAML or equivalent) and flags the specific anti-pattern this gap describes — reporting success at the deploy-command-completed step rather than an independent post-deploy check — with a suggested insertion point for a verification gate; a one-shot pipeline-design review, distinct from the project's always-running verifier.

## MVP Sketch
A standalone CLI step pluggable into one CI system (GitHub Actions) that, given a target URL and an expected content-hash or build-ID, fetches the live endpoint and compares. Validate against a scripted scenario: a deploy "succeeds" at the pipeline level while the CDN still serves the old cached artifact — does the tool correctly flag this as unverified? Buildable by 1-2 people in 2-3 weeks starting with HTTP-based verification before adding APM integration.

## Risks & Open Questions
- CDN/edge-caching delays can create false "mismatch" flags that are actually just propagation lag, not a real failure — needs a tunable grace period, not an instant hard-fail.
- Not every deployable artifact has an easy-to-check live fingerprint (e.g. backend-only services with no public endpoint) — the project's first version is strongest for web-facing deploys specifically.
- Strongest case this is already solved: if Harness or Azure AgentOps generalizes their existing adjacent feature into exactly this named, evaluated product before this ships, differentiation narrows to being framework/vendor-agnostic rather than tied to one platform.
