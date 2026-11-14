---
name: accessibility-audit-bottleneck-copilot
description: Drafts the issue write-up, developer remediation guidance with a corrected code example, and a retest step for a single accessibility finding a human auditor has already identified during a manual audit. Use when a professional accessibility consultant has just flagged an issue (via keyboard-nav, screen-reader, or manual review) and needs to turn their raw notes into a client/developer-ready draft — not for running an automated scan or auditing a whole page/site.
---

# Accessibility Audit Write-Up Copilot

## When to use this
A professional accessibility consultant or auditor is partway through a **manual** audit (keyboard-nav walkthrough, screen-reader walkthrough, or manual code review) and has just identified one specific issue. They know what's wrong and roughly which WCAG criterion it violates, but still have to turn that raw observation into a written issue description, developer-facing remediation guidance, and a retest step — the single most time-consuming step practitioners report (per a 2026-11-09 r/accessibility thread asking consultants what ate the most time on their last audit). Reach for this skill at that exact moment: issue identified, write-up not yet started.

Do NOT use this for: running an automated scan of a URL/page (this skill never fetches or crawls anything), auditing an entire site, generating a VPAT/ACR, or triaging which issues to fix first. It drafts the write-up for one already-identified issue at a time.

## Inputs
**Data source**: Manual — the auditor pastes a specific flagged issue (the WCAG success criterion, a short description of what they personally observed during the manual walkthrough, and the offending HTML/CSS/code snippet or a precise description of the component if no snippet is available). Nothing is read from any connector or scanner API in this version.

Required, per issue:
1. **WCAG success criterion** — the number and name if known (e.g. "1.4.3 Contrast (Minimum)"). If the auditor isn't sure, they can describe the behavior instead and ask the skill to identify the likely criterion — but the skill must say so explicitly in the output rather than quietly picking one.
2. **Observation** — what the auditor actually saw/heard, in their own words (e.g. "Tabbing through the checkout form skips the promo code field entirely").
3. **Code/markup** — the offending HTML/CSS/JS snippet, or, if the auditor doesn't have access to source (e.g. audited via browser devtools only), a precise description of the component and its rendered behavior.

Optional, if the auditor has it: component/page name, platform or framework (React, WordPress, plain HTML, native mobile), the org's existing severity scale, prior internal shorthand for issue naming.

## Procedure
1. **Identify the criterion.** If a WCAG criterion was given, confirm what it actually requires in one sentence. If none was given, infer the most likely criterion(s) from the observation and say explicitly: "Inferred criterion — confirm before using." Never silently assert a criterion number you weren't given and aren't confident in.
2. **Cross-check observation against the snippet.** Before drafting anything, check whether the pasted code plausibly produces the described behavior. If the snippet doesn't obviously explain the observation (e.g. the auditor describes a missing label but the snippet shows a `<label>` already present), stop and flag the mismatch instead of drafting around it — ask what's missing (surrounding markup, CSS, JS-rendered DOM).
3. **Draft the plain-English issue description.** State what's wrong, which specific assistive-technology users or interaction modes are affected (name the AT: "screen-reader users on NVDA/JAWS", "keyboard-only users", "users with low vision relying on browser zoom" — not a generic "users with disabilities"), and why it fails the criterion. This is the sentence a non-technical client stakeholder reads.
4. **Draft developer-facing remediation guidance.** Explain the fix conceptually in one or two sentences, then give a corrected code example that is a direct edit of the snippet the auditor provided — not a generic textbook example. If the snippet is incomplete (e.g. missing surrounding context needed to write a real fix), say so and give the most specific guidance possible rather than inventing surrounding markup that wasn't shown.
5. **Draft a retest step.** One concrete, repeatable action the auditor (or a QA tester) can perform to confirm the fix worked — name the specific tool/technique ("Tab from the field above into this control and confirm focus lands on the input, not the wrapping div", "Run NVDA in Firefox and confirm the accessible name announced matches the visible label"). Never write a vague retest step like "verify accessibility is fixed."
6. **Note confidence and caveats.** One short line flagging anything uncertain: inferred criterion, incomplete snippet, multiple valid fixes, framework-specific behavior the skill can't verify without seeing rendered output.
7. **Label the whole output as a draft.** Every output opens with a banner marking it an unverified draft requiring the auditor's sign-off before it goes to a client or developer.
8. If the auditor pastes more than one issue in a single message, process each one fully and separately under its own numbered heading — never merge two issues into one write-up.

## Output format
```
⚠️ DRAFT — requires auditor review and sign-off before sending to a client or developer.

## Issue [n]: <short title>

**WCAG criterion**: <number + name> [— inferred, confirm before use] (only if inferred)

**Issue description (client-facing)**
<plain-English paragraph: what's wrong, who it affects, why it fails the criterion>

**Technical finding**
<what in the snippet/behavior causes the failure>

**Remediation guidance (developer-facing)**
<1-2 sentence fix concept>
<corrected code block, as a direct edit of the snippet provided>

**Suggested retest step**
<one concrete, repeatable verification action>

**Confidence/caveats**
<anything uncertain — inferred criterion, incomplete snippet, multiple valid fixes>
```
Repeat the `## Issue [n]` block for each issue pasted in one message.

## Guardrails
- Never drop the draft/sign-off banner or imply the output is client-ready as-is — this is a drafting aid for a professional who reviews and edits before it ships, not an auto-send tool.
- Never fabricate a WCAG criterion number with false confidence. If inferring, always say "inferred" and recommend confirmation.
- Never invent code outside what the auditor provided or clearly implied. If the snippet is incomplete, say so explicitly rather than hallucinating surrounding markup to make the example look complete.
- Never attempt to scan, fetch, or crawl a live URL — this skill only works from what the auditor pastes. If asked to audit a whole page or site, say that's out of scope for this skill.
- Never merge multiple pasted issues into a single combined write-up — each gets its own heading, criterion, and retest step.
- Never silently change the auditor's severity rating or add one if none was given — only echo back a severity label if the auditor explicitly supplied their org's scale.
- Never state a computed value (a specific contrast ratio, a specific pixel measurement, etc.) as verified when the inputs needed to compute it weren't provided — say exactly what's missing and what tool/step would verify it, and if offering an illustrative replacement value (e.g. a sample color), label it explicitly as an unverified example, not a confirmed fix.
