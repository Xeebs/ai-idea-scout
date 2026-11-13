# Escalation Ledger: An Auditable, Severity-Conditional Crisis-Escalation Policy Engine for Voice AI Agents

- **Status**: EXPLORING (promoted 2026-11-13 cycle 39: evidence density — 2 independent vendors building severity-conditional crisis-escalation logic, ferni-ai/voiceai and CallSphere)
- **Date**: 2026-11-13
- **Topic**: AI safety & guardrails in production
- **Source**: research/2026-11-13-ai-safety-guardrails-in-production.md · P5
- **Maturity verdict**: PARTIAL — GitHub search for "crisis escalation voice AI agent" / "suicide risk detection conversational agent" / "988 911 escalation chatbot" returned zero repos. WebSearch found only narrow, vendor-specific or proprietary implementations (CallSphere's proprietary "988 Warm-Handoff Safety Matrix," a community Claude-skill crisis_response_protocol doc, an NYU policy-proposal framework, and VERA-MH — an open-source *evaluation* rubric, not an escalation policy engine) — no maintained, composable, reusable escalation-policy library exists, but this isn't a clean blank slate either.
- **Format**: BOTH
- **Data Sources**: MANUAL for the Skill Angle (a team pastes its current crisis-escalation logic — a script, a flag-config snippet, or a policy description); CONNECTED for the Project — a voice AI platform's own risk-detection output (imminence/language/topic classifiers) and response-generation hook, reached via whichever framework the team runs (e.g., Vapi, Retell, Bland, or a custom stack) — no single mature cross-vendor connector exists, so the project ships adapters per platform.

## The Gap
GitHub PR `ferni-ai/voiceai#3748`, "feat(crisis): conditional 911 line after 988 in the severe script," ships one narrow, internal, feature-flagged rule (`CRISIS_SELF_HARM_911_LINE`) appending an extra escalation line to a severe self-harm/suicide script, gated on imminence, language, and topic detection. This is a single production vendor's internal rollout of one escalation rule — there is no general pattern or library for composable, auditable crisis-escalation policy logic (severity threshold → disclosure script → feature flag → gradual rollout) in conversational agents, despite this being a safety-critical decision point.

## The Project
A policy engine sitting between a voice AI agent's risk-detection layer and its response generator: teams declare escalation rules as data (severity threshold, language, topic, script variant, rollout percentage) instead of hardcoding them in application logic, and every escalation decision is logged with the inputs that triggered it (classified severity, language, topic, which rule fired, which script variant was spoken) for post-incident audit and clinical review. Ships with a default rule set modeled on the public 988/911 warm-handoff pattern, which teams override per jurisdiction or language instead of writing a new feature-flagged PR for every new escalation condition.

## Tangible Impact
**Population**: callers in active mental-health crisis reaching an AI-voice-staffed line. The 988 Suicide & Crisis Lifeline alone received an estimated 7.4 million contacts in FY2025 per a GAO report (23% up from FY2024, roughly 600k-700k contacts/month per KFF's tracking) — a growing volume that crisis organizations and commercial wellness/EAP vendors (like the one evidenced in this digest) are increasingly handling with voice-AI triage and response layers rather than purely human staff.
**Mechanism**: today each vendor hand-codes each escalation rule as application logic behind a feature flag (as in the evidenced PR), meaning a new at-risk condition (a new language, a new jurisdiction's crisis-line number, a new imminence threshold) requires an engineering PR and redeploy before it reaches callers, with no standard audit trail proving which rule fired for a given call if an outcome is later reviewed. A declarative, logged policy engine lets a clinical safety team change escalation rules without an engineering cycle and gives incident reviewers a complete record of what the agent decided and why.
**Measure**: time from "clinical team identifies a new escalation condition is needed" to "it's live for callers" (target: hours via config change, not a PR-and-deploy cycle); percentage of escalations with a complete, reviewable audit trail (target: 100%, vs. ad hoc logging today); false-negative rate on a labeled set of simulated crisis-severity scenarios (did the correct escalation fire).

## Why Now
Voice AI agents are now handling a meaningful share of crisis-adjacent call volume, evidenced directly by this digest's production PR from a real voice-AI vendor, and the underlying classifiers (imminence/language/topic detection) are mature enough off-the-shelf that the missing piece is specifically the policy/audit layer around them, not new ML.

## Skill Angle
A "Crisis Script Audit" skill — given a team's current crisis-escalation logic (pasted as a script, a flag-config snippet, or a policy description) and a checklist derived from public safety frameworks (the 988/911 warm-handoff pattern, NYU's policy-proposal framework, VERA-MH's evaluation criteria), the skill flags missing conditions (no non-English-language path, no explicit imminence threshold, no audit logging) as a one-time pre-launch or pre-incident-review check, before a team commits to adopting the full runtime engine.

## MVP Sketch
2-4 weeks, 1-2 people. Define the rule schema (severity tier, language, topic, script variant, rollout %), build a reference implementation wrapping one open-source voice-agent framework's response hook, implement the audit log, and validate against a labeled set of ~20-30 synthetic crisis-call transcripts (imminent/non-imminent, multiple languages), checking the right rule fires and is fully logged. Single experiment: compare escalation-rule change lead time (config edit vs. simulated PR-and-deploy) on the reference implementation.

## Risks & Open Questions
- This is the highest-stakes idea in this digest — a bug in the policy engine could mean a real at-risk caller doesn't get escalated; needs clinical/safety-expert review built into the MVP plan itself, not bolted on after.
- The one production example found (`ferni-ai/voiceai`) is proprietary; without access to real crisis-call data, the labeled test set has to be synthetic, limiting how confidently the MVP's false-negative rate generalizes.
- CallSphere's proprietary "988 Warm-Handoff Safety Matrix" suggests at least one vendor has already built something similar in-house — this project only has value if it's meaningfully more composable/auditable/open than that.
- Regulatory and liability exposure (this touches suicide-prevention response logic) may require legal review before any real deployment, independent of the technical build.
