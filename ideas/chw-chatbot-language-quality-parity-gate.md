# Parity Gate: A Language-Quality-Parity Safety Layer for Community-Health-Worker Chatbots

- **Status**: PROPOSED
- **Date**: 2026-11-13
- **Topic**: Applied AI for underserved domains
- **Source**: research/2026-11-13-applied-ai-for-underserved-domains.md · P3
- **Maturity verdict**: PARTIAL — the Rwanda CHW study (5,609 real clinical questions, 101 CHWs, chwcentral.org/research.birmingham.ac.uk), a Malawi Chichewa chatbot evaluation, and the Sakhi/SimPPL WhatsApp maternal-health chatbot all measure and flag local-language quality degradation; SMARThealth Pregnancy and Beshte are in-progress co-design fixes. No project found runs a real-time parity check between a chatbot's local-language answer and its own English answer to the same clinical question and acts on the gap — every existing effort is either a one-time research measurement or a slow, bespoke co-design process.
- **Format**: BOTH

## The Gap
The Rwanda CHW study found LLMs answering real clinical questions outperformed clinicians and were far cheaper per response — but "performance degraded slightly when LLMs communicated in Kinyarwanda" versus English, on the exact same questions. The George Institute's SMARThealth Pregnancy chatbot and IDRC's Beshte project in Kenya are both still in co-design stages trying to add local-language support, meaning the degradation these researchers measured is not yet addressed in any shipped, general-purpose way. No deployed CHW chatbot checks, at answer time, whether its local-language response is meaningfully worse than the answer it would have given in English to the same question.

## The Project
A middleware safety layer that sits between a CHW chatbot's LLM backend and its messaging channel (WhatsApp/Telegram/SMS). For every incoming question, it silently generates both the local-language answer the CHW will see and a parallel English answer, then scores semantic and clinical-content agreement between the two (key facts present/absent, dosage or referral-threshold numbers matching, hedging/uncertainty language matching). When the local-language answer scores below a calibrated agreement threshold, the system doesn't just serve it — it either falls back to a verified back-translation of the English answer, or flags the response for human clinical supervisor review before the CHW acts on it, with the specific discrepancy highlighted. Over time it logs where and how degradation clusters (by topic, by phrasing, by language) so program staff can target fixes instead of guessing.

## Tangible Impact
**Population**: Frontline community health workers who rely on LLM-chatbot clinical guidance in a local/regional language rather than English or French — WHO/secondary estimates put the global CHW workforce above 1.3 million, heavily concentrated in exactly the low- and middle-income countries where the local-language chatbots in the digest (Kinyarwanda, Chichewa, Hindi/Marathi) operate, and where a wrong dosage or missed referral threshold has direct patient-safety consequences.
**Mechanism**: Today a degraded local-language answer reaches the CHW with no signal that it's worse than the same model's English answer would have been — the CHW has no way to know to double-check. A parity check turns an invisible quality gap into a visible, actionable flag, routing only the risky minority of answers to a safer fallback or human review instead of trusting every local-language response equally.
**Measure**: (1) rate of flagged-vs-unflagged answers that a clinical reviewer independently judges unsafe or incomplete (precision/recall of the flag against a human-labeled gold set, replicating the Rwanda study's 5,609-question evaluation design); (2) reduction in the measured quality gap between local-language and English answers on matched question pairs, before vs. after fallback routing; (3) CHW-reported trust/confidence in chatbot answers in the local language, pre/post deployment.

## Why Now
The Rwanda study and the Malawi/Sakhi evaluations are all 2026-dated, independent confirmations that this specific degradation is real, measured, and still unaddressed in production — the research has done the hard part of proving the gap exists and is large enough to matter; no one has yet built the operational layer that acts on that finding in a live deployment.

## Skill Angle
A Claude Code skill version: given a pasted batch of CHW chatbot Q&A transcript pairs (the local-language question/answer plus the same question re-asked in English), the skill scores each pair for content/safety agreement and returns a ranked list of the riskiest discrepancies with a plain explanation of what's missing or wrong in the local-language answer. This is the one-shot audit a program's clinical supervisor runs periodically on exported logs — the project is the always-on middleware that intercepts every live message and fails safe automatically. The skill validates the scoring logic cheaply before anyone wires it into a live WhatsApp/Telegram deployment.

## MVP Sketch
Scope to one language pair already studied (Kinyarwanda/English, reusing a de-identified slice of the Rwanda study's question set as a validation benchmark) and one chatbot channel (WhatsApp, via a platform like Glific or Turn.io that CHW programs in this space already use and that exposes webhook/API access to intercept messages). Stack: dual-generation call to the existing LLM backend, a lightweight agreement scorer (embedding similarity plus a structured key-fact extraction/compare step), and a fallback/flagging policy. The validating experiment: run the pipeline against the Rwanda study's held-out question set and measure whether the parity flag actually correlates with the paper's own documented quality-degradation findings.

## Risks & Open Questions
- Running two generations per question roughly doubles inference cost and adds latency — needs to be cheap enough (e.g., a smaller/faster model for the English shadow-answer) not to break the "far cheaper per response" economics the Rwanda study credited LLMs with in the first place.
- A fallback that routes too many answers to human review defeats the purpose of automating CHW support at all; the threshold calibration is the whole product and needs real clinical input, not a default guess.
- Risk this is already being solved quietly inside SMARThealth Pregnancy or Beshte's ongoing co-design work — worth directly contacting those projects before building, since both are explicitly working on this exact problem.
- Back-translation-as-fallback can itself introduce new errors; it needs its own accuracy check, not an assumed-safe default.
