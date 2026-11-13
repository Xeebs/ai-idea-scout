A disaster hits, a hotline fields the call, and the caller doesn't speak a language anyone on staff reads fluently. The machine translation that answers them is often wrong in exactly the ways that matter most in a crisis — and right now, nothing checks before it's sent.

## The Gap

The ADAPT Centre's own researchers (citing Way et al.) put it plainly: "there have been alarmingly few attempts to provide automatic translation services for use in crisis scenarios." That's not a stray complaint — a 2026 evaluation paper found that Llama3.2-1B and X-ALMA have "significant failure modes in low-resource scripts," concluding these tools "remain unreliable for dissemination in crisis communication." A Feb 2026 arXiv follow-up goes further, documenting urgency-level distortion: machine translation that doesn't just garble words but flattens or inflates how urgent a message sounds, exactly the signal a crisis responder needs most. A Nov 2026 workshop paper is still asking, in its own title, "Is Machine Translation Ready for the Next Crisis or Pandemic?" — and the honest answer the field is giving itself is no.

Meanwhile the closest real-world precedents — Tarjimly and Translators without Borders' Gamayun project — route calls to a human interpreter network, but neither is confirmed to be using AI in hotline operations at all. So the gap sits in plain sight between two facts that don't talk to each other: MT models are cheap and fast enough to run at hotline scale, and the people who study crisis MT failure modes closely are the same people saying, in four separate papers across 2024–2026, that nobody has shipped a way to tell a trustworthy MT output from an untrustworthy one before it reaches a caller.

## The Project

The idea isn't to build a better translator — it's to build the thing that decides whether to trust the translator you already have. A routing layer sits in front of a crisis or volunteer hotline's existing translation pipeline. Every incoming message or call gets machine-translated, and then that output gets scored against the known crisis-MT failure signatures: script degradation, the urgency-distortion pattern the Feb 2026 paper documented, and the MT model's own confidence calibration. High-confidence, low-risk output passes straight through. Anything that scores as high-risk gets escalated to a human volunteer interpreter through a Tarjimly/TWB-style on-call network — and every one of those escalation decisions gets logged, so the whole system can be audited after the fact instead of trusted blindly.

The centerpiece here is the risk-scored triage gate itself — not a new translation model, not a generic ticketing queue bolted onto an existing hotline. It's deliberately narrow: decide, call by call, whether this particular MT output is safe to hand to someone in crisis, or whether it needs a human in the loop right now.

## Tangible Impact

**Population**: speakers of low-resource languages in crisis situations — displaced and disaster-affected communities relying on hotlines. Translators without Borders estimates roughly 200 million people globally lack access to crisis information in a language/format they understand (TWB's own stated reach figures); volunteer networks like Tarjimly (~20,000 volunteer interpreters per TWB/Tarjimly public reporting) are the current fallback and are chronically oversubscribed.

**Mechanism**: fewer low-resource-language callers get a silently degraded or urgency-distorted MT answer at a crisis moment — the exact failure mode the Feb 2026 arXiv paper documents — because the highest-risk cases get escalated to a human instead of trusted to raw MT blindly, while scarce volunteer interpreter time is reserved for calls that genuinely need it instead of being drowned out by every call.

**Measure**: (1) escalation precision/recall against a held-out set of known MT failure cases (urgency distortion, script degradation); (2) median response latency for low-risk calls (should match raw-MT speed) vs. escalated calls (should match current human-only latency); (3) post-incident audit rate — how often a logged pass-through decision is later flagged by reviewers as a missed escalation.

## Try It

No companion skill has been built for this idea yet — the Format tag on this one is BOTH, so a skill is planned but hasn't shipped. When it does, it will be a one-time pre-deployment reliability audit: an org hands over a language pair and a batch of sample MT outputs, and the skill flags specific risky outputs against the known failure taxonomy before the org commits to deploying on a given language pair — distinct from the always-on routing middleware described above.

Worth sitting with before building either version: this could already be solved somewhere nobody's published. Tarjimly or TWB may have an unannounced internal MT-assist pilot running right now — the research behind this idea found none, but that's a search result, not a guarantee, and it's worth a direct outreach check before assuming this is greenfield. There's also a harder structural limit: triage reduces unnecessary escalations, but it doesn't create more human interpreter capacity, which is already the real bottleneck. And because false negatives — a genuinely high-risk message scored as safe — carry outsized harm in a crisis context, any real deployment will likely need conservative thresholds that trade some throughput for safety, not a free lunch.

Surfaced from `research/2026-11-12-applied-ai-for-underserved-domains.md`, pattern `P4`.
