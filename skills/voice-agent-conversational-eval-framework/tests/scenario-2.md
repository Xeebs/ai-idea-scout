# Scenario 2 — B2B outbound sales dialer bot, no systematic eval, no transcripts given

## Input

A small sales-tech team describes its setup:

1. **What we currently measure**: "Honestly, nothing systematic. We spot-check a handful of recordings manually each week when someone on the team has time, no fixed rubric, no written criteria. We've never measured ASR accuracy, never scored responses formally, no TTS review."
2. **How we measure it**: "Ad hoc listening by whoever's free. No script, no scoring, no logging of what's found."
3. **Our call types**: "Outbound cold-call intro (pitching a demo), follow-up call to a warm lead who requested more info, objection-handling calls where the prospect raises a specific concern (price, timing, competitor)."
4. **Example transcripts**: none provided.
5. **Known pain points**: "Sales team suspects the bot sometimes agrees to send pricing info it can't actually send, but nobody's confirmed this."

## Pass criteria

- [ ] Coverage Scorecard marks all four layers (ASR, LLM/dialogue, TTS, conversation-level) as `Missing`, with each "Why" line citing the "nothing systematic / ad hoc" description rather than inventing a partial-credit rationale.
- [ ] Still produces a full checklist walk-through (not skipped just because the setup is minimal) — every checklist item scored `Missing` with a reason tied to "no systematic measurement exists."
- [ ] Failure-mode taxonomy is produced separately for each of the three named call types (cold-call intro, warm-lead follow-up, objection-handling), each tailored to that call type's actual pattern — e.g., objection-handling taxonomy should include something like "false commitment under price pressure" or "promises an action the bot can't fulfill," directly addressing the stated pain point about promising pricing info.
- [ ] Worked Examples section states plainly that no transcripts were supplied and recommends providing some — does not fabricate a fake transcript excerpt to fill the section.
- [ ] Top Gaps explicitly surfaces the "agent may make commitments it can't fulfill" pain point as a goal-resolution / tool-capability-mismatch gap, even though no transcript evidence was given — grounded only in what the user said ("suspects," "nobody's confirmed").
- [ ] Recommended Next Steps gives a genuinely actionable first step for a team starting from zero (e.g., start logging a fixed weekly sample with a written rubric) rather than jumping straight to "buy/build a full conversational framework."
- [ ] Does not claim any layer is `Partial` or `Covered` when the user explicitly said nothing systematic exists.

## Fail conditions

- Marks any layer above `Missing` despite "nothing systematic" being stated for all of them.
- Produces one shared taxonomy table for all three call types instead of three tailored ones.
- Invents a transcript excerpt or specific recorded incident that was never provided.
- Skips the pricing-commitment pain point, or states it as a confirmed fact rather than an unconfirmed suspicion.
- Recommends only "adopt our full framework" as the single next step with no smaller, zero-to-one action first.
