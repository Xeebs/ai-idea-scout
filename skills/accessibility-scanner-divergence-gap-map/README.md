# Accessibility Scanner Divergence Gap-Map

Paste this whole document into any AI chat tool (ChatGPT, Claude, Gemini, Copilot Chat, etc.) along with your scan output, and it will turn a "scanner says we passed" result into a short, prioritized list of exactly what still needs a human look before you treat that scan as proof of accessibility.

## Why this exists

Automated accessibility scanners (axe-core, Lighthouse, WAVE, Siteimprove, Pa11y) are genuinely good tools, but they can only mechanically check a subset of WCAG success criteria. Industry estimates for how much of WCAG they can fully automate generally land somewhere in the 25-40% range (vendor estimates vary; this is not a precise, universally agreed number). The rest — logical focus order, whether alt text is actually meaningful, whether an error message is genuinely clear — requires a human judgment call the scanner cannot make. The problem is that a scanner's report usually doesn't tell you *which* of its green checkmarks fall into that blind spot. This prompt closes that gap using a bundled reference table, so a non-expert can get a short, concrete "verify these specific things" list instead of either (a) blindly trusting a 95% score, or (b) having to manually re-check every single criterion from scratch.

## What you need before you start

1. **Your raw scan output**, pasted in full — not just the summary score. JSON, CSV, or even a plain copy-pasted list of rows like `rule: color-contrast, status: pass, elements: 12` all work.
2. **Which tool produced it** — axe-core, Lighthouse's accessibility audit, WAVE, Siteimprove, Pa11y, or something else. Rule names differ between tools, and that affects how items get matched to a WCAG criterion.
3. **The page's URL or a short label**, just so the output has a readable header — this prompt cannot fetch or re-scan the page itself, so don't expect it to look at the live site.

If you haven't run a scan yet, run one first (for example `npx @axe-core/cli <your-url>` from a terminal with Node installed, or open Chrome DevTools → Lighthouse → Accessibility) and come back with that output.

## The instructions to give the AI

Paste the following, filling in your own scan output where indicated:

---

You are triaging an automated accessibility scan. Do not run or simulate a scan yourself — only work from the data I paste below. Follow these steps exactly:

1. Sort every item in my pasted scan output into three buckets: FAILED (confirmed violations), PASSED (scanner says compliant), and INCOMPLETE/NEEDS REVIEW (the scanner's own "can't tell automatically" category — axe-core calls these "incomplete"; other tools have an equivalent label).

2. For each PASSED item, map its rule to a WCAG 2.2 success criterion using this reference table of common axe-core rule IDs (if I used a different tool, match by criterion number/description instead of rule ID):
   image-alt→1.1.1, video-caption→1.2.2, aria-required-children/table-duplicate-name→1.3.1, color-contrast→1.4.3, meta-viewport→1.4.4, focus-order-semantics→2.4.3, link-name→2.4.4, heading-order→2.4.6, html-has-lang/html-lang-valid→3.1.2, label→3.3.2, aria-valid-attr-value/aria-roles→4.1.2.
   If a rule isn't in this table, mark it "unmapped — confidence unknown."

3. For each mapped criterion, look up its confidence tier in this gap-map (qualitative tiers based on well-documented community/vendor consensus about what automated accessibility testing can and can't reliably check — not a precise validated percentage):

   - RELIABLE: 1.4.3 Contrast (Minimum) — pure color math, automation's strongest case. 3.1.2 Language of Parts — lang attribute presence/validity. 2.5.3 Label in Name — accessible-name-vs-visible-label mismatch.
   - PARTIAL (mechanical part checked, substance still needs a human): 1.1.1 Non-text Content (alt text present ≠ alt text meaningful), 1.3.1 Info and Relationships, 1.4.4 Resize Text, 1.4.11 Non-text Contrast, 2.4.4 Link Purpose in Context, 2.4.6 Headings and Labels, 2.4.7 Focus Visible, 3.3.1 Error Identification, 3.3.2 Labels or Instructions, 4.1.2 Name/Role/Value.
   - MANUAL-ONLY (automation genuinely cannot test this): 1.2.2 Captions, 1.3.2 Meaningful Sequence, 2.1.1 Keyboard, 2.2.1 Timing Adjustable, 2.4.3 Focus Order, 3.2.4 Consistent Identification.

4. Build a checklist in this priority order:
   - Tier 1: every PASSED item mapped to a MANUAL-ONLY criterion (highest-risk false confidence).
   - Tier 2: every PASSED item mapped to a PARTIAL criterion.
   - Tier 3: every unmapped PASSED item.
   - Carried over as-is: every INCOMPLETE/NEEDS REVIEW item the scanner already flagged — never drop these.
   - Leave out entirely: RELIABLE-tier passes, and everything in FAILED (failed items already have an action: fix the violation).

5. For each checklist item, write one line: the WCAG criterion number and name, a concrete manual check that takes 2-5 minutes and doesn't require accessibility expertise (e.g. "Tab through the page using only the keyboard; check that focus moves in the same order as the visual layout"), and a one-sentence reason automation can't close that specific gap.

6. At the top, write one summary line: "Scanner reported X checks passed, Y failed, Z flagged incomplete. Of the X passes, M need a human look before you call this compliant."

7. End with this exact caveat, always included: "This gap-map is a snapshot of public, well-documented community/vendor consensus on automated-vs-manual accessibility testing coverage — it is not a re-validated empirical database. It narrows where to look; it does not certify WCAG or ADA/Section 508 compliance."

Never claim the page is "accessible" or "compliant" as a conclusion. Never invent a confidence tier for a criterion not in the table above. Never claim to have seen or re-scanned the live page — base every instruction only on the pasted scan data, kept generic and actionable. If what I paste doesn't look like real scanner output (no rule names, no pass/fail structure), tell me and ask for the actual export instead of guessing.

My scanner: [axe-core / Lighthouse / WAVE / Siteimprove / Pa11y / other]
My page: [URL or label]
My scan output:
[paste raw output here]

---

## What you get back

A short markdown checklist with checkboxes, grouped into: Tier 1 (scanner passed but can't actually test this), Tier 2 (scanner passed but only checked the mechanical part), carried-over items the scanner already flagged, and any unmapped rules — each with a concrete manual check and a one-line reason. A summary count at the top, and the compliance caveat at the bottom on every run.

## Limits, on purpose

This does not run a scan for you, does not fetch or inspect the live page, and does not certify compliance with WCAG, ADA, or Section 508 — it only re-prioritizes a scan you already ran so you know which of its green checkmarks are actually worth double-checking by hand before you ship or make a compliance claim. The confidence tiers are a reasonable community-knowledge snapshot, not a scientifically re-validated database — if you need that level of rigor for a legal compliance decision, pair this with an actual manual audit.
