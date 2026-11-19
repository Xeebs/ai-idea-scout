# Correction Loop: A Live-Feedback Retraining Toolkit for Low-Resource-Language Interpretation Services

Tarjimly connects refugees with volunteer interpreters, and every time one of those volunteers fixes a mistranslation, the correction becomes machine-translation feedback. Quill.org does the same thing in a different domain: volunteers correcting data that trains LLMs for 55 low-resourced languages. Two organizations, same loop, same realization — and neither one open-sourced it. If you run a smaller version of either service for your own under-covered language, the correction your volunteer just made either gets logged in a spreadsheet nobody retrains on, or it gets thrown away the moment the conversation ends.

## The Gap

The pattern is simple and, per the evidence, already proven twice: capture a model's output, let a human correct it in the normal course of doing their job, and feed that correction back into the model instead of discarding it. Tarjimly and Quill.org both run this loop today as bespoke internal pipelines — real, working, at scale. But neither released the tooling. The closest thing to an open implementation is CMULAB (`neulab/cmulab` on GitHub), a genuine human-in-the-loop correction framework validated on the Seneca language — but it's a 15-star academic project, last pushed in September 2025, built for a research lab's workflow rather than a nonprofit's. So the gap isn't "does this pattern work" — it demonstrably does, twice over — it's "can an org smaller than Tarjimly or Quill.org stand up the same loop without rebuilding it from the ground up." Right now, the answer is no.

## The Project

The idea is a reusable capture-correction-retrain toolkit that plugs into the messaging channel a nonprofit already uses — not a new app volunteers have to learn. It intercepts the (original model output, volunteer correction) pair the moment a human fixes a translation, interpretation, or tutoring response, logs it into a growing validated dataset, and runs a scheduled fine-tune of an open-weight model against the accumulated corrections. The point is that the labor already happening — volunteers correcting output as part of their normal work — stops being a one-time fix thrown away after each conversation and starts compounding into a dataset the org actually owns. On the data side, this reaches directly into the WhatsApp Business API or Twilio Conversations API — both mature, already-deployed channels — to capture message pairs live rather than asking volunteers to manually export and paste transcripts; a manual CSV-upload path is the fallback for orgs not yet on a supported channel.

## Tangible Impact

**Population**: Small nonprofits and community organizations running live interpretation, translation, or tutoring services for speakers of under-covered languages — organizations the scale of Tarjimly and Quill.org already prove the demand, but the much larger population of smaller orgs serving a single refugee community or under-covered language who cannot build bespoke ML infrastructure the way those two did.
**Mechanism**: Today, a smaller org's volunteers correct machine output in real time, but those corrections are logged at best and discarded at worst — there is no retraining pipeline turning them into model improvement. A plug-in capture-and-retrain toolkit lets that org's existing channel feed a growing dataset automatically and periodically improve its own model, without hiring an ML team.
**Measure**: (1) validated correction pairs captured per month with no added volunteer workload beyond what they already do; (2) measured output-quality improvement (native-speaker-rated accuracy or BLEU/COMET) after N retraining cycles vs. the static starting model; (3) number of distinct small orgs/languages onboarded within a year, as a direct test of whether it displaces bespoke internal builds like Tarjimly's and Quill.org's.

## Try It

A companion Claude Code skill exists at `skills/live-correction-loop-retraining-toolkit/`: "Turns a description of a nonprofit's live interpretation/translation/tutoring workflow and a sample of its volunteer correction pairs into a concrete capture-schema, retraining-cadence, and consent plan for standing up a correction-loop retraining pipeline. Use when an org already has volunteers correcting model output in real time but has no plan for turning those corrections into model improvement."

It's a one-time design/planning pass, not a running system — it produces the schema, integration recommendation, retraining plan, and consent checklist a team would hand to an engineer to build. Two ways to use it:

- **Any AI chat tool**: paste the contents of `skills/live-correction-loop-retraining-toolkit/README.md` into the chat, then describe your current workflow and paste a sample of recent correction pairs.
- **Claude Code**: drop the `skills/live-correction-loop-retraining-toolkit/` folder into `~/.claude/skills/`, and Claude will reach for it automatically when a team asks how to turn its volunteers' corrections into a better model.

It refuses to treat consent as a formality — using real conversation data from refugees, students, or other vulnerable populations to retrain a model is a serious ethical constraint, not a box to check after the fact, and the skill marks consent items `NOT DONE` by default rather than assuming them. It's also worth saying plainly before anyone builds on this: it's possible Tarjimly's or Quill.org's internal tooling is already further along and closer to generalizable than this search surfaced, and CMULAB's academic framework may be closer to production-ready than its 15-star GitHub profile suggests — both are worth checking directly before assuming a rebuild is necessary.

---

Surfaced from `research/2026-11-19-applied-ai-for-underserved-domains.md`, pattern `P3`.
