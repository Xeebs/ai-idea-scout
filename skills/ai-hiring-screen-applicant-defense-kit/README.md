# Screen Defense: Applicant-Side AI Hiring-Screen Risk Flagger & Accommodation Drafter

Paste the block below into any AI chat tool (ChatGPT, Claude, Gemini, etc.) along with your job posting and resume text. It works as a one-shot prompt — no installation, no account, no API.

## What this is for

Many job applications now run through at least one automated step before a human ever sees them: an ATS keyword filter, a one-way video interview, a game-based or personality assessment, a chatbot pre-screen. If you have a disability, an accommodation need, or a conviction history, and the application asks about it, you're making a disclosure decision into a process you can't see inside of. This tool does two narrow things:

1. **Flags specific, quotable risk signals** in your resume/application against the posting — not generic "improve your resume" advice (plenty of tools already do that), but signals specifically tied to automated-screening risk: ATS keyword mismatches, unexplained employment gaps, and how conviction-history or disability-disclosure questions are framed and timed in the posting.
2. **Drafts an ADA accommodation-request email** — if you have a disability and the process includes an automated step, US law (per EEOC/DOJ guidance) gives you the right to request a human-reviewed alternative to that specific automated step. Almost no applicant knows this right exists or how to invoke it in writing. This drafts that specific request.

It does not and cannot see or diagnose any specific employer's actual screening model — there is no API that exposes that. Everything here works from the text you paste, nothing else.

## What to paste

Copy the prompt block below, then paste after it:
1. The full job posting text, including any application-portal questions (disability self-ID, conviction-history checkboxes) — paste the actual text, not a summary.
2. Your resume/application draft text, in full.
3. (Optional, only needed if you want the accommodation-request draft) One or two sentences, in your own words, describing your disability/accommodation need or conviction history, and whether the process includes an automated step (name it if you know what it is: online test, one-way video interview, chatbot screen, assessment game).

If you skip #3, you'll still get the risk-flag pass — just not the accommodation draft.

## The prompt

```
You are reviewing my job application for automated-hiring-screen risk and, if applicable, drafting an ADA accommodation-request email. Follow this procedure exactly:

1. If I did not give you a disability/accommodation/conviction-history description below, do the risk-flag pass only and tell me plainly that you skipped the accommodation draft because I didn't give you that context. Never invent a disclosure I didn't give you.

2. Risk-flag pass — read my posting and resume/application together. Flag ONLY signals you can tie to an exact quoted phrase from what I pasted:
   - ATS keyword mismatch: hard requirements or repeated terms in the posting missing from my resume. Quote the missing term and where it appears in the posting.
   - Employment-gap flag: any gap of 6+ months in my resume's dates with no stated explanation. Name the exact gap (from/to).
   - Conviction-history checkbox: if the posting/application has one, quote its exact wording and note whether it appears to come before or after a conditional-offer stage, if that's determinable from the text.
   - Disability/accommodation checkbox: if present, quote its exact wording and note whether the posting names or implies an automated screening step (test, video interview, game-based or personality assessment, chatbot screen) — the ADA right to request a human-reviewed alternative only attaches to an automated step, so flag this only if one is named or clearly implied.
   Do not flag anything that isn't tied to an exact quote. If nothing qualifies, say "No risk signals found in the text given" instead of inventing one.

3. Edit suggestions — for ATS keyword or employment-gap flags ONLY (never for disability or conviction-history flags, since those are disclosure decisions, not resume edits), suggest one concrete wording change or addition, quoting the exact posting language it responds to.

4. Accommodation-request draft — only if I gave you a disability/accommodation description AND named or implied an automated screening step: draft a short, factual email that (a) states I'm applying for the named role, (b) names the specific automated step, (c) requests a reasonable accommodation under the ADA — a human-reviewed alternative to that step, framed as a request, not a medical disclosure or a demand, (d) never discloses more medical/personal detail than I gave you, and (e) ends with a one-line reminder to send it in writing and keep a copy as a record.

5. Always close with a "Limits" section, every time: (a) this is a heuristic read of visible text only, it cannot see or diagnose any employer's actual screening model, and no flag is proof any specific rejection was caused by that signal; (b) if no accommodation draft was produced, say why; (c) recommend having a disability-rights or employment-law advocate review any accommodation request before sending it.

Never claim a flagged signal caused any actual rejection. Never infer a disability or conviction history from my resume content alone (a gap is never evidence of either) — only act on what I explicitly tell you in this conversation. Never suggest hiding or omitting a required disclosure question — only suggest edits to neutral resume/keyword content. Never state legal outcomes as certain ("you will win") — frame rights and mechanisms only, and always include the advocate-review line.

Here is the job posting:
[PASTE FULL POSTING TEXT, INCLUDING APPLICATION-PORTAL QUESTIONS]

Here is my resume/application draft:
[PASTE FULL RESUME/APPLICATION TEXT]

(Optional) My disability/accommodation need or conviction history, and whether an automated step is part of this process:
[DESCRIBE IN YOUR OWN WORDS, OR DELETE THIS LINE IF NOT APPLICABLE]
```

## What you'll get back

- A numbered list of risk flags, each tied to an exact quote from what you pasted, with a suggested edit where relevant (ATS/employment-gap flags only).
- If you provided disclosure context and an automated step, a drafted accommodation-request email ready to send (after you or an advocate reviews it).
- A closing "Limits" section every time, reminding you this is heuristic guidance, not a diagnosis of why anything happened, and recommending advocate review before sending anything.

## What this will not do

- It will not tell you why you were actually rejected — no tool can see inside an employer's real screening system.
- It will not help you hide or omit a conviction-history or disability question the posting requires you to answer.
- It will not give you legal certainty — it names the right and mechanism (requesting a human-reviewed alternative under the ADA), not a guaranteed outcome. Have an actual advocate or employment lawyer review anything before you send it, especially if you've already been denied once.
