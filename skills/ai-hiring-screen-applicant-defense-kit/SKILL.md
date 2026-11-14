---
name: ai-hiring-screen-applicant-defense-kit
description: Flags resume/application signals likely to interact badly with automated hiring screens (disability disclosure, conviction-history disclosure, employment-gap, ATS keyword mismatch), and drafts an ADA accommodation-request email asking for human review of an automated step. Use when a job seeker is about to submit an application that includes a disability accommodation need or a conviction-history question, or has already been screened out and wants to understand why and what they can still do.
---

# Screen Defense: Applicant-Side AI Hiring-Screen Risk Flagger & Accommodation Drafter

## When to use this
A job applicant is about to submit (or has just been rejected from) an application process that includes any automated step — an online application portal, an ATS, a one-way video interview, a game-based or personality assessment — AND either (a) the posting or application asks about disability/accommodation needs or conviction history, or (b) the applicant has a disability or conviction history they're deciding whether/how to disclose. This is not a general resume-polishing or keyword-optimization tool (those exist and are saturated); it exists specifically for the narrower moment where disclosure risk and the ADA's human-review right intersect with an automated screening step.

## Inputs
**Data source**: Manual — the applicant pastes the job posting text (including any application-portal questions, e.g. disability self-ID or conviction-history checkboxes) and their own resume/application draft, plus, optionally, a one-line description of a disability, accommodation need, or conviction history they're deciding whether/how to disclose. No API exposes employer-side ATS or AI-screening logic to applicants, so this skill works only from visible, applicant-side text — it cannot see or diagnose any specific employer's actual model.

Required for any run:
1. The job posting text, pasted in full (not summarized) — including any screening questions shown in the application portal.
2. The applicant's resume/application draft text, pasted in full.

Optional, only needed for the accommodation-drafting half:
3. A one-line description of the disability/accommodation need or conviction history, in the applicant's own words, and whether an automated step (online test, one-way video interview, chatbot screen, game-based assessment) is part of this specific process.

If input 3 is absent, skip the accommodation-request draft and say so explicitly — never invent a disclosure the applicant didn't give.

## Procedure
1. **Confirm scope.** If only a resume and posting are given with no disclosure/accommodation context, do the risk-flag pass only (step 2) and state plainly that no accommodation draft was produced because no disclosure context was given.
2. **Risk-flag pass.** Read the posting and resume/application together and flag only signals with a direct, named mechanism — never a vague "this might hurt you":
   - **ATS keyword mismatch**: hard requirements or repeated terms in the posting that don't appear anywhere in the resume (named skills, certifications, years-of-experience phrasing, job-title language). Quote the missing term and where in the posting it appears.
   - **Employment-gap flag**: a gap in the resume's date ranges of 6+ months with no explanation visible in the text — name the specific gap (from/to dates).
   - **Conviction-history checkbox**: if the posting/portal includes a conviction-history question, note the question's exact wording and whether it appears before or after what looks like a conditional offer stage (ban-the-box timing matters) — flag if timing is unclear from the posting alone.
   - **Disability/accommodation checkbox**: if present, note the exact wording and whether the posting describes the screening method it applies to (test, video, assessment) — the ADA right to request an alternative attaches specifically to automated screening steps, so this only matters if an automated step is actually named or implied.
   - Do not flag anything you cannot tie to a specific quoted phrase in the posting or resume. No flag may be based on inference about the employer's intent.
3. **Edit suggestions.** For each ATS/keyword or employment-gap flag only (never for disability or conviction-history flags — those are disclosure decisions, not resume edits), suggest one concrete rewording or addition the applicant could make, quoting the exact posting language it responds to.
4. **Accommodation-request draft** (only if input 3 was given and names or implies an automated screening step): draft a short, factual email that:
   - States the applicant is applying (or has applied) for the named role at the named employer/posting.
   - Names the specific automated step described (by the applicant or the posting).
   - Requests a reasonable accommodation under the ADA: a human-reviewed alternative to that specific automated step, framed as a request, not a diagnosis or demand.
   - Does not disclose more medical/personal detail than the applicant gave — never pad the disclosure to sound more "legitimate."
   - Includes a one-line note to send it in writing (email, not just a verbal request) and keep a copy, since that is the applicant's evidentiary record if the request is later ignored.
5. **Close with the limits**, every time, regardless of what was produced in steps 2-4 (see Guardrails) — this is not optional boilerplate, it is the thing that keeps a heuristic flag from being read as a diagnosis.

## Output format
```
## Risk Flags
1. [ATS_KEYWORD | EMPLOYMENT_GAP | CONVICTION_HISTORY | DISABILITY_DISCLOSURE] — <quoted posting/resume text> — <one-line why this is a known risk pattern>
   Suggested edit (ATS_KEYWORD/EMPLOYMENT_GAP only): <concrete rewording>
(repeat per flag; if none found, say "No risk signals found in the text given" — don't invent one)

## Accommodation Request Draft
(omit this section entirely if no disclosure/accommodation context was given — don't draft a placeholder)
Subject: <role> Application — Accommodation Request
<drafted email body>

## Limits
- This is a heuristic read of visible text only — it cannot see or diagnose the employer's actual screening model, and a flag here is not proof that any specific rejection was caused by this signal.
- [If no disclosure context given] No accommodation draft was produced because no disability/accommodation or conviction-history context was given — add one if this applies to you.
- Have a disability-rights or employment-law advocate review any accommodation request before sending it, especially if a prior request was ignored.
```

## Guardrails
- Never claim or imply a specific rejection was caused by any flagged signal — frame every flag as "a known risk pattern," never a diagnosis of what happened.
- Never draft an accommodation request without an explicit disclosure/need from the applicant in the current conversation — don't infer a disability or conviction history from resume content (e.g. a gap alone is never treated as evidence of either).
- Never pad a disclosure with more medical or personal detail than the applicant actually provided, even if it would make the draft "sound more convincing."
- Never suggest editing around (hiding, omitting required disclosure for) a conviction-history or disability question where the posting or applicable law requires an answer — only suggest edits to neutral resume/keyword content, never to disclosure questions themselves.
- Never produce legal advice framed as certain ("you will win," "this violates the law") — frame rights and mechanisms ("you can request," "the ADA guidance says employers must consider") and always close with the advocate-review line.
- If the posting text or resume isn't actually pasted (only described secondhand), ask for the literal text before flagging anything — flags must trace to quoted text, not to a paraphrase.
