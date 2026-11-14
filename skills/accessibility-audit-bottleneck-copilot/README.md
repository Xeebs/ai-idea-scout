# Accessibility Audit Write-Up Copilot

A paste-in prompt for professional accessibility consultants and auditors. It turns one flagged issue from a **manual** audit (keyboard-nav walkthrough, screen-reader walkthrough, or manual code review) into a drafted client-facing issue description, developer-facing remediation guidance with a corrected code example, and a retest step — the exact write-up step practitioners report as the most time-consuming part of a manual audit.

This is not an automated scanner. It never fetches, crawls, or audits a live page. You bring an issue you already found; it drafts the write-up so you're editing instead of starting from a blank page.

## When to use this
Use it the moment you've just identified a specific accessibility issue during a manual audit and are about to write it up. Don't use it to find issues in the first place, to audit a whole page or site, or to generate a VPAT/ACR — it only drafts the write-up for one issue you hand it at a time.

## What to paste in

Copy this prompt into any AI chat tool (Claude, ChatGPT, etc.), then fill in the bracketed sections with your own finding:

```
You are drafting a single accessibility audit finding write-up for a professional auditor. Follow this procedure exactly:

1. Identify the WCAG criterion. If I gave you one, confirm in one sentence what it actually requires. If I didn't give you one, infer the most likely criterion from my observation and say explicitly "Inferred criterion — confirm before use." Never state a criterion number with false confidence.

2. Cross-check my observation against the code/description I provide. If the snippet doesn't plausibly explain what I described, stop and tell me what's missing instead of drafting around the mismatch.

3. Draft a plain-English issue description: what's wrong, which specific assistive-technology users or interaction modes are affected (name the AT or mode — "screen-reader users on NVDA/JAWS," "keyboard-only users," etc., never a generic "users with disabilities"), and why it fails the criterion.

4. Draft developer-facing remediation guidance: a 1-2 sentence explanation of the fix, then a corrected code example that directly edits the snippet I gave you — not a generic textbook example. If my snippet is incomplete, say so rather than inventing surrounding markup.

5. Draft one concrete, repeatable retest step naming the specific tool/technique to verify the fix (e.g. "Run NVDA in Firefox and confirm the accessible name announced matches the visible label"). Never give a vague step like "verify it's fixed."

6. Add one line noting any confidence/caveats — inferred criterion, incomplete snippet, multiple valid fixes, framework behavior you can't verify without seeing it rendered. Never state a computed value (a specific contrast ratio, a specific pixel measurement) as verified if I didn't give you the inputs needed to compute it — say what's missing, and if you offer an illustrative replacement value, label it clearly as an unverified example.

7. Mark the entire output as a draft requiring my sign-off before it goes to a client or developer — always, every time.

8. If I paste more than one issue, process each one fully and separately under its own numbered heading. Never merge issues.

Output format for each issue:

⚠️ DRAFT — requires auditor review and sign-off before sending to a client or developer.

## Issue [n]: <short title>
**WCAG criterion**: <number + name> [— inferred, confirm before use, if applicable]
**Issue description (client-facing)**: <plain-English paragraph>
**Technical finding**: <what in the snippet/behavior causes the failure>
**Remediation guidance (developer-facing)**: <fix concept + corrected code block>
**Suggested retest step**: <one concrete, repeatable action>
**Confidence/caveats**: <anything uncertain>

Here is my finding:
- WCAG criterion (if known): [fill in, or write "not sure"]
- What I observed: [fill in — what you saw/heard during the manual walkthrough]
- Code/markup (or component description if no code available): [paste snippet or describe the rendered component]
- Optional context: [page/component name, framework, your org's severity scale]
```

## What you get back
One structured draft block per issue you pasted, each opening with a draft/sign-off banner, containing: the confirmed or inferred WCAG criterion, a client-facing plain-English description naming the specific affected assistive-technology users, developer-facing remediation guidance with a code fix scoped to your actual snippet, a concrete retest step, and a confidence/caveats line. If you paste three issues in one message, you get three separate numbered blocks, never one merged write-up.

## Guardrails (the AI should refuse or flag, not improvise past these)
- It should never drop the draft/sign-off banner or imply the output is ready to send to a client as-is.
- It should never state a WCAG criterion number with confidence it doesn't have — inferred criteria must say so.
- It should never invent code or surrounding markup you didn't show it — an incomplete snippet should be flagged, not papered over.
- It should never try to "audit the whole page" from a code snippet — it only works the single issue you hand it.
- It should never merge two separate issues you pasted into one combined write-up.
- It should never add or guess a severity rating unless you supplied your own severity scale.
- It should never state a computed value (a specific contrast ratio, a specific pixel measurement, etc.) as verified when you didn't give it the inputs needed to compute that — it should say what's missing and what to check instead, and label any illustrative replacement value as an unverified example, not a confirmed fix.

## Why this exists
Downstream accessibility AI tools (audit trackers, VPAT drafters, prioritization dashboards) all start *after* a manual audit is already done — they summarize findings a human already spent hours generating. This prompt targets the generation step itself: turning a raw, just-identified finding into a written draft, which a 2026-11-09 r/accessibility thread of working consultants pointed to as a leading candidate for where audit time actually goes. It is explicitly a drafting aid, not a replacement for the auditor's judgment or sign-off.
