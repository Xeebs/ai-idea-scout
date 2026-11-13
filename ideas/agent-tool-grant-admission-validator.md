# Grant Gate: Admission-Time Validation for Agent Tool/MCP Permission Declarations

- **Status**: PROPOSED
- **Date**: 2026-11-12
- **Topic**: AI safety & guardrails in production
- **Source**: research/2026-11-12-ai-safety-and-guardrails-in-production-pass2.md · P6
- **Maturity verdict**: PARTIAL — general admission-control technology for this exact failure shape is mature (Kubernetes `ValidatingAdmissionPolicy`, OPA/Gatekeeper reject malformed resources at admission using CEL/Rego testable in CI), and at least two vendor products apply similar validate-before-save logic to agent/AI policy broadly (Lumenova's AI Policy Engine, Gravitee's policy-drift checks). No product specifically validates an agent's declared tool/MCP-server grants against actual platform-held permissions at admission time — that narrow slice is unimplemented even though the surrounding admission-control pattern is not new.
- **Format**: BOTH
- **Data Sources**: MANUAL — user pastes/uploads the agent's declared tool/MCP manifest and a platform grant-records export; no single named connector is mature across the varying platforms (agentgateway, OAP, Bifrost) this would target. (Backfilled 2026-11-13 cycle 36 — this idea predates the mandatory Data Sources field; inferred from the Skill Angle section by the skill-synthesizer.)

## The Gap
`awslabs/open-agentic-platform` issue #144 names this as a known, open "admission gap": "nothing prevents an agent declaring `mcpServers` it holds no `mcpAccess` grant for. Today that surfaces as a 403 at call time rather than a rejected Application." The same thread cites a prior real bug where `agentgateway` "keeps one [policy] at random and silently drops the other while both report Accepted" when two rules of equal specificity collide — and states the design principle directly: "a guardrail that fails silently is worse than no guardrail, because it produces the appearance of coverage."

## The Project
An admission-time validator, modeled on `ValidatingAdmissionPolicy`/OPA patterns but purpose-built for agent tool/MCP declarations: when an agent application is deployed or updated, the validator cross-checks every declared `mcpServers`/tool entry against the platform's actual grant records and rejects the deployment outright if any declared capability has no corresponding grant, or if a policy-collision would silently drop coverage. It ships as a CI-testable policy set (so the mismatch is caught in a pull request, not in production) plus a runtime admission hook for platforms that deploy outside CI.

## Tangible Impact
**Population**: platform engineering teams operating agent gateways with declarative tool/MCP permission systems — the `awslabs/open-agentic-platform` team and any team on a comparable gateway (`agentgateway`, Bifrost, or similar) where tool access is expressed as a declared grant rather than hardcoded per-agent.
**Mechanism**: today a misdeclared or collided grant looks identical to a correctly configured one until an agent actually tries to use the tool and gets a runtime 403 — or worse, a silently-dropped policy that neither errors nor warns. Admission-time rejection catches the mismatch before deploy, the same way a bad Kubernetes manifest is rejected before it reaches a cluster, converting a silent-failure class into a loud, CI-visible one.
**Measure**: number of grant mismatches caught at admission/CI time versus previously discovered only via a runtime 403 (goal: shift discovery left); reduction in production incidents traced to a silently-dropped or uncaught policy collision; time from a bad grant declaration being committed to it being rejected (target: CI run, not a user-facing error).

## Why Now
The admission-control pattern itself is proven at scale in Kubernetes/OPA, and the specific gap — applying it to agent tool/MCP grants rather than generic resource manifests — is a live, named backlog item in the OAP thread this month, meaning the underlying grant/declaration schema already exists to validate against.

## Skill Angle
Trigger: a team hands over an agent's declared tool/MCP manifest plus their platform's actual grant records (or API access to query them). The skill runs a one-shot cross-check and reports every mismatch or collision it finds, as a pre-deploy audit before committing to the always-on CI gate. The project is the CI-integrated policy engine and runtime admission hook that enforces the same check on every deploy automatically.

## MVP Sketch
A CEL/Rego-style policy that takes an agent's declared tool/MCP manifest and the platform's grant records as two inputs and fails if any declared capability lacks a matching grant, or if two policies of equal specificity would collide. Package it as a CI action plus a minimal runtime admission webhook. Single experiment: reproduce the `agentgateway` policy-collision bug and the OAP `mcpAccess` mismatch scenario as test fixtures and show the validator rejects both before deploy instead of surfacing as a runtime 403.

## Risks & Open Questions
- Needs real API access to a platform's grant records to validate against — a generic version without platform-specific adapters won't catch anything on its own.
- Could be read as redundant with the broader guardrail-taxonomy auditor (tool authorization is one of its nine categories) — the differentiator here is admission-time rejection with CI enforcement, not coverage discovery; the two are complementary, not the same build.
- Teams may resist adding another admission gate to an already-complex deploy pipeline unless the mismatch rate is demonstrably non-trivial.
- A platform vendor could close this specific gap in a point release once it's named this explicitly in public.
