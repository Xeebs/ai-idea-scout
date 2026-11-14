---
name: parent-iep-compliance-checker
description: Flags likely IDEA compliance gaps (missing baselines, unmeasurable goals, unspecified service minutes, missing LRE/transition justification) in a parent's actual IEP document and drafts a specific, send-ready written request per flag. Use when a parent has a child's IEP (current or just-proposed) in hand and wants to check it before signing or to ask the school for something specific instead of a vague complaint.
---

# IEP Compliance Flag & Letter Drafter

## When to use this
A parent has their child's actual IEP document — current, just-proposed at a meeting, or a draft the school sent ahead of a meeting — and wants to know whether it meets the legal bar before signing it or pushing back. Use this the moment a parent says something like "the school just sent me this IEP, can you check it" or "I don't know what to ask for, I just know something feels off about this goal." This is a single-document (optionally two-document, for year-over-year comparison) review task, not an ongoing case-management tool — it does not remember a child's IEP history across sessions.

## Inputs
**Data source**: Manual — the parent pastes the full text of their child's actual IEP document (not a summary or screenshot description — the literal text, transcribed from a PDF or scan if needed) and names their US state. No API exposes a specific student's IEP (it's FERPA-protected and school-controlled), so there is no connected version of this input — the document the parent already has in hand is the only available source. Optionally, the parent also pastes a prior year's IEP text for a regression comparison, and states the child's age/grade (needed to check whether transition-services requirements apply).

Required for any run:
1. The full IEP text, pasted verbatim.
2. The parent's US state.

Optional:
3. A prior year's IEP text, pasted verbatim, for a regression comparison.
4. The child's age as of the IEP's effective date (triggers the transition-services check at 16+).

If the state is withheld, run the federal-only pass and say explicitly that state-specific flags were skipped and why.

## Procedure
1. **Confirm inputs.** If no IEP text was actually pasted (only described secondhand — "it says he gets speech therapy"), ask for the literal text before flagging anything. Every flag must trace to quoted text from the document, never to a paraphrase.
2. **Privacy nudge, once, before analysis.** Tell the parent that pasting this into a general AI chat tool shares its contents with that tool's provider, and suggest redacting the child's full legal name, student ID, and date of birth if they're comfortable doing so — then proceed with whatever they actually pasted either way. Never refuse to proceed over this; it's a heads-up, not a gate.
3. **Structural extraction pass.** Read the pasted text and determine, for each of the following components, whether it is present, present but vague/incomplete, or absent from the text given:
   - Present levels of academic/functional performance (PLAAFP) with actual baseline data (numbers, dates, assessment names) — not just a narrative description.
   - Each annual goal: does it have a measurable baseline, a specific target criterion, and a stated method/frequency of progress measurement?
   - Each special education/related service: frequency (sessions per week/month), duration (minutes per session), location, and start date — all four, not just the service name.
   - A least-restrictive-environment (LRE) statement that justifies any time spent outside the general education setting, if the placement removes the child from general ed at all.
   - Accommodations/modifications for both classroom work and testing.
   - A procedural safeguards notice reference with a date, or a prior-written-notice date for this IEP's changes.
   - If the child is 16 or older as of this IEP's effective date (per input 4, or stated in the document): postsecondary goals and transition services.
   - The IEP meeting date, annual review date, and triennial reevaluation date.
   Never infer a component is present if it simply wasn't included in the pasted text — "not found in the text provided" is a valid and expected finding, not a failure of the parent's paste job.
4. **Federal IDEA pass.** For each component found absent or vague in step 3, write a flag citing the general federal IDEA provision it relates to (e.g., 34 CFR §300.320 for required IEP content, §300.114–116 for LRE, §300.503 for prior written notice, §300.320(b) for transition at 16). Only cite a federal provision you are confident is accurate and well-established; if unsure of the exact citation, describe the requirement in plain language instead of guessing a section number.
5. **State-layer pass.** Using the named state, add any state-specific IDEA-implementation requirement you can state with real confidence (e.g., a state's own progress-reporting frequency, a shorter procedural-safeguards timeline, or specific LRE continuum documentation that state requires). Tag every state-specific flag `[state rule — verify]` and, at the end of this pass, add one line recommending the parent confirm state-specific items with their state's Parent Training and Information (PTI) Center (federally funded in every state) or a local special-education advocate. Never invent a state statute or code section — if you can't name it with confidence, describe the requirement in plain language and flag it for verification rather than attaching a citation you aren't sure of.
6. **Regression check (only if a prior-year IEP was also pasted).** Compare service minutes/frequency, goal count, placement, and accommodations between the two documents. Flag any reduction in services, minutes, or accommodations that has no documented data-based rationale visible in the current IEP's text.
7. **Draft one request paragraph per flag.** Each paragraph: names the specific IEP item (e.g., "Goal #3," "speech-language services"), states what's missing or unclear, and makes one concrete, specific ask ("please provide the baseline data and assessment used to set this goal," "please specify the frequency, duration, and location of occupational therapy services"). Never draft an accusation or a threat — frame every paragraph as a request for clarification or documentation, addressed to the IEP team.
8. **Assemble a combined letter** stitching every drafted paragraph into one short, polite, specific letter the parent can send as-is or edit, addressed to "IEP Team" by default.
9. **Always close with a Limits section** (see Output format) — this runs every time, regardless of how many flags were found.

## Output format
```
## IEP Compliance Flags
| # | Component | Finding | Basis | Citation / note |
|---|-----------|---------|-------|------------------|
(one row per flag; Basis is FEDERAL or STATE — VERIFY; if zero flags, state "No gaps found in the components checked against the text provided" — never invent a flag to fill the table)

## Drafted Requests
1. [Component] — <drafted paragraph>
(one per flag)

## Combined Ready-to-Send Letter
Subject: Request for Clarification — [Child's name/initials] IEP dated [date]
<assembled letter body>

## Regression Notes
(only if a prior-year IEP was given; otherwise omit this section entirely — don't write "N/A")

## Limits
- This is a read of the text you pasted only — it cannot see anything not included in that text, and a missing item here may simply mean it wasn't pasted, not that the school omitted it from the real document.
- State-specific flags are marked [state rule — verify] because this skill has no live connection to your state's current regulations; confirm them with your state's Parent Training and Information (PTI) Center or a special-education advocate before relying on them.
- Nothing here is a legal determination that the school violated the law — it's a list of things worth asking about. Have an advocate or attorney review before any formal complaint.
```

## Guardrails
- Never state or imply that a flagged gap is a confirmed legal violation — always frame it as "a gap to ask about," never a diagnosis of wrongdoing.
- Never fabricate a specific state statute, code section, or regulation number. If you can't name the state-specific provision with real confidence, describe the requirement in plain language and mark it `[state rule — verify]` instead of attaching an invented citation.
- Never infer that a component is compliant just because it wasn't mentioned as missing — if it genuinely wasn't in the pasted text, say "not found in the text provided," not "appears compliant."
- Never skip the privacy/redaction nudge in step 2, and never refuse to proceed if the parent declines to redact.
- Never give clinical, diagnostic, or therapy-method advice (e.g., don't suggest a different therapy approach) — stay strictly in the procedural/documentation-compliance lane.
- Never run a full analysis if no IEP text was actually pasted — ask for the literal text first.
- If no state was given, state plainly that the state-specific pass (step 5) was skipped, rather than silently doing federal-only and calling it complete.
