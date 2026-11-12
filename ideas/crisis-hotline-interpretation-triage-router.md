# Interpretation Triage Router: Human-in-the-Loop AI Translation for Crisis and Volunteer Hotlines

- **Status**: EXPLORING (promoted 2026-11-12: evidence density — ≥3 independent research threads corroborate the same unsolved crisis-MT-reliability gap: a 2024 ADAPT Centre paper (Way et al.), a June 2026 ISCRAM paper (Ticona & Anastasopoulos), a Feb 2026 arXiv follow-up, and a Nov 2026 workshop paper explicitly titled "Is Machine Translation Ready for the Next Crisis or Pandemic?")
- **Date**: 2026-11-12
- **Topic**: Applied AI for underserved domains
- **Source**: research/2026-11-12-applied-ai-for-underserved-domains.md · P4
- **Maturity verdict**: OPEN — WebSearch for a deployed product found none, only research: a June 2026 ISCRAM paper (Ticona & Anastasopoulos) documenting MT quality degradation for low-resource crisis languages, a Feb 2026 arXiv follow-up on urgency-perception distortion, and a Nov 2026 workshop paper titled "Is Machine Translation Ready for the Next Crisis or Pandemic?" (still an open question). Tarjimly — the closest human-in-the-loop precedent — is confirmed by the same search not to be using AI yet.
- **Format**: BOTH

## The Gap
The ADAPT Centre (citing Way et al.) notes "there have been alarmingly few attempts to provide automatic translation services for use in crisis scenarios," and a 2026 evaluation paper found Llama3.2-1B and X-ALMA have "significant failure modes in low-resource scripts," concluding these tools "remain unreliable for dissemination in crisis communication." Tarjimly and Translators without Borders' Gamayun project are the closest human-in-the-loop precedents, but neither is confirmed to use AI in hotline operations — leaving a clear gap between available MT capability and anything actually deployed on a crisis/volunteer hotline.

## The Project
A routing layer in front of a crisis or volunteer hotline's translation need. For each incoming message or call, it runs MT and scores the output against known crisis-MT failure signatures — script degradation, the urgency-level distortion documented in the Feb 2026 arXiv paper, and the MT model's own confidence calibration — then either passes the MT output through (high confidence, low risk) or escalates to a human volunteer interpreter via a Tarjimly/TWB-style on-call network (high risk). Every escalation decision is logged for post-hoc audit. The centerpiece is the risk-scored triage gate itself, not generic MT or a generic ticketing queue.

## Tangible Impact
**Population**: speakers of low-resource languages in crisis situations — displaced and disaster-affected communities relying on hotlines. Translators without Borders estimates roughly 200 million people globally lack access to crisis information in a language/format they understand (TWB's own stated reach figures); volunteer networks like Tarjimly (~20,000 volunteer interpreters per TWB/Tarjimly public reporting) are the current fallback and are chronically oversubscribed.
**Mechanism**: fewer low-resource-language callers get a silently degraded or urgency-distorted MT answer at a crisis moment — the exact failure mode the Feb 2026 arXiv paper documents — because the highest-risk cases get escalated to a human instead of trusted to raw MT blindly, while scarce volunteer interpreter time is reserved for calls that genuinely need it instead of being drowned out by every call.
**Measure**: (1) escalation precision/recall against a held-out set of known MT failure cases (urgency distortion, script degradation); (2) median response latency for low-risk calls (should match raw-MT speed) vs. escalated calls (should match current human-only latency); (3) post-incident audit rate — how often a logged pass-through decision is later flagged by reviewers as a missed escalation.

## Why Now
The 2026 ISCRAM paper and the Nov 2026 "Is MT Ready for the Next Crisis" workshop paper give concrete, recent failure taxonomies to build risk-scoring rules from, and open MT models (Llama3.2, X-ALMA) are cheap enough to self-host at hotline scale — but per the digest's confirmed multi-channel search, no deployed product exists yet.

## Skill Angle
Trigger: a crisis-response or volunteer-hotline org has a specific language pair and a batch of real or sample MT outputs they're unsure whether to trust. Inputs: the language pair, sample transcripts/outputs, and the crisis context (medical triage, logistics, emotional support). The skill applies the known failure taxonomy (script degradation, urgency distortion) to flag specific risky outputs and recommends a go/no-go threshold for that language pair — a one-time pre-deployment reliability audit, distinct from the project's always-on real-time routing middleware.

## MVP Sketch
Pick one well-documented low-resource language pair from the ISCRAM paper's eval set, build a simple risk classifier (rule-based on known failure signatures plus the MT model's own calibrated confidence), wire it to a stub escalation queue (even a Slack/WhatsApp alert to a test volunteer), and measure escalation precision against a hand-labeled test set of 50-100 messages. 2-4 weeks, 1-2 people plus access to one bilingual reviewer.

## Risks & Open Questions
- No deployed baseline exists, so the risk-scoring rules have to be built mostly from academic failure taxonomy rather than field data — needs real pilot validation before claiming it works.
- Human interpreter capacity is already the bottleneck; triage reduces unnecessary escalations but doesn't create more human capacity.
- False negatives (a high-risk case scored as low-risk) in a crisis context carry outsized harm, so thresholds likely need conservative tuning at some throughput cost.
- Strongest reason this might already be solved: Tarjimly or TWB could have an unpublished internal MT-assist pilot — the digest's search found none, but worth a direct outreach check before assuming greenfield.
