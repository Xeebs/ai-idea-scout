---
name: accessibility-scanner-divergence-gap-map
description: Triages a pasted automated accessibility scan (axe-core, Lighthouse, WAVE, Siteimprove, Pa11y, etc.) against a bundled WCAG-criterion confidence map, and produces a ranked "what still needs a human" checklist — for when a scan comes back green and someone is about to treat that as proof of accessibility compliance.
---

# Accessibility Scanner Divergence Gap-Map

## When to use this
A user has just run (or received) an automated accessibility scan — axe-core, Lighthouse's accessibility audit, WAVE, Siteimprove, Pa11y, or similar — and is about to treat a "pass" / high score as evidence the page is accessible or WCAG-compliant. Trigger moments:
- "Our scanner says we're at 95% / all green, are we good to ship?"
- "Here's our axe-core output, what should I actually worry about?"
- Before a release, a compliance claim, or a response to an accessibility complaint, when the only accessibility signal available is an automated tool's report.

Do not use this to run a scan — it has no browser and cannot execute axe-core, Lighthouse, or anything else. It only re-prioritizes a scan result the user already has in hand.

## Inputs
**Data source**: Manual — the user pastes the raw scanner output (JSON, CSV, or a plain list of "rule / status / element count" rows) from whatever tool they already ran, plus the page's URL or name for labeling. This skill implements only the manual secondary path described in its parent idea; the idea's primary CONNECTED path (running axe-core + Chromium directly against a live URL) is a separate, not-yet-built project component — a chat-tool skill has no browser to drive, so it cannot do that part itself.

What to ask for if not already provided:
1. The raw scan output, pasted verbatim (not just a summary number).
2. Which tool produced it (axe-core, Lighthouse, WAVE, Siteimprove, Pa11y, or other) — rule naming differs by tool and this changes the mapping step.
3. The page's URL or a short label, for the output header only (not fetched or re-scanned).

If the user has no scan yet, tell them to run one first (e.g. `npx @axe-core/cli <url>` or Chrome DevTools Lighthouse) and come back with the output — do not guess at results.

## Procedure
1. **Parse the pasted output** into three buckets: `FAILED` (confirmed violations), `PASSED` (scanner says compliant), `INCOMPLETE/NEEDS REVIEW` (the scanner's own built-in "can't tell, ask a human" category — axe-core calls these "incomplete"; most other tools have an equivalent).
2. **Map each PASSED rule to its WCAG 2.2 success criterion**, using the Scanner Rule → WCAG table below. If a rule isn't in the table, label it `unmapped — confidence unknown, verify manually to be safe`; never silently drop it or guess a tier for it.
3. **Look up each mapped criterion's confidence tier** in the Gap-Map table below: `RELIABLE`, `PARTIAL`, or `MANUAL-ONLY`.
4. **Build the checklist in priority order**:
   - Tier 1: every `PASSED` item whose criterion is `MANUAL-ONLY` — these are the highest-risk false confidence, a scanner "pass" that tells the user almost nothing.
   - Tier 2: every `PASSED` item whose criterion is `PARTIAL` — scanner checked the mechanical part, a human still needs to judge the substance.
   - Tier 3: every `unmapped` item.
   - Carry over verbatim: every `INCOMPLETE/NEEDS REVIEW` item the scanner already flagged — never drop these, they're already a confirmed signal, just relabel with their WCAG criterion if known.
   - Exclude entirely: `RELIABLE`-tier `PASSED` items and everything in `FAILED` (failed items already have an action — fix the violation — they don't belong on a "needs manual verification" checklist).
5. **Write one line per checklist item**: the WCAG criterion name + number, a concrete 2-5 minute manual check a non-expert can actually do, and a one-sentence reason automation can't close that specific gap.
6. **Summarize**: one line at the top stating "scanner reported N checks passed; M of those need a human look before you call this compliant" plus counts for failed and incomplete.
7. **Footer caveat, always included verbatim**: this gap-map is a snapshot built from public, well-documented community/vendor consensus (not a re-validated empirical database), dated to this skill's last update — it narrows risk, it does not certify compliance.

## Gap-Map: WCAG 2.2 criterion confidence tiers
Grounded in axe-core's own "incomplete" category, Deque's and TestParty's published automated-vs-manual coverage analyses, and the W3C's Accessibility Conformance Testing (ACT) rules — qualitative tiers, not a precision percentage per criterion (no single validated per-criterion number exists publicly yet; that's the exact gap the parent project aims to build).

| WCAG 2.2 Criterion | Tier | Why |
|---|---|---|
| 1.1.1 Non-text Content | PARTIAL | Detects missing/empty `alt`, can't judge if the text is accurate or meaningful |
| 1.2.2 Captions (Prerecorded) | MANUAL-ONLY | Detects a `<track>` element's presence, can't verify caption accuracy or sync |
| 1.3.1 Info and Relationships | PARTIAL | Catches some malformed ARIA/table markup, not whether the structure reads correctly |
| 1.3.2 Meaningful Sequence | MANUAL-ONLY | Reading/DOM order has no reliable automated "correct" to check against |
| 1.4.3 Contrast (Minimum) | RELIABLE | Pure math on rendered foreground/background color — automation's strongest case |
| 1.4.4 Resize Text | PARTIAL | Can detect viewport/zoom blockers, can't verify layout stays usable at 200% |
| 1.4.11 Non-text Contrast | PARTIAL | Reliable on static states, misses hover/focus/dynamic UI states |
| 2.1.1 Keyboard | MANUAL-ONLY | Static analysis can't actually drive the keyboard through every interaction |
| 2.2.1 Timing Adjustable | MANUAL-ONLY | Requires observing a live session over time, not a static scan |
| 2.4.3 Focus Order | MANUAL-ONLY | "Logical order" is a judgment call automation can't make |
| 2.4.4 Link Purpose (In Context) | PARTIAL | Flags generic text like "click here", can't judge if context actually clarifies it |
| 2.4.6 Headings and Labels | PARTIAL | Flags missing/duplicate headings, not whether wording is descriptive |
| 2.4.7 Focus Visible | PARTIAL | Can detect `outline: none` etc., misses custom focus styles rendered too subtly |
| 3.1.2 Language of Parts | RELIABLE | `lang` attribute presence/validity is a reliable automated check |
| 3.2.4 Consistent Identification | MANUAL-ONLY | Requires comparing components across the whole site, not one page |
| 3.3.1 Error Identification | PARTIAL | Needs a triggered form-validation state; static scans usually miss dynamic states entirely |
| 3.3.2 Labels or Instructions | PARTIAL | Detects missing `<label>`, can't judge if instructions are clear |
| 4.1.2 Name, Role, Value | PARTIAL | Catches many ARIA attribute errors, can't verify custom widget behavior in every state |
| 2.5.3 Label in Name | RELIABLE | Accessible-name-vs-visible-label mismatch is reliably computable |

## Scanner Rule → WCAG mapping (axe-core rule IDs; map other tools' rule names by criterion number instead)
`image-alt`→1.1.1 · `video-caption`→1.2.2 · `aria-required-children`/`table-duplicate-name`→1.3.1 · `color-contrast`→1.4.3 · `meta-viewport`→1.4.4 · `focus-order-semantics`→2.4.3 · `link-name`→2.4.4 · `heading-order`→2.4.6 · `html-has-lang`/`html-lang-valid`→3.1.2 · `label`→3.3.2 · `aria-valid-attr-value`/`aria-roles`→4.1.2

## Output format
```
# Manual Review Checklist — <page label>
Scanner: <tool name> | Scanned: <date if given>
Summary: <N> checks passed, <F> failed, <I> flagged incomplete by the scanner itself.
Of the <N> passes, <M> need a human look before calling this compliant.

## Tier 1 — Scanner passed, but automation cannot test this (do these first)
- [ ] **<WCAG #> <Criterion name>** — <concrete 2-5 min manual check> (automation can't close this because <reason>)

## Tier 2 — Scanner passed, but only checked the mechanical part
- [ ] ...same format...

## Carried over — scanner already flagged these as needing review
- [ ] ...same format, criterion labeled if known...

## Unmapped — not in this skill's reference table yet
- [ ] <rule id> — verify manually; confidence unknown

---
Caveat: this gap-map is a snapshot of public, well-documented community/vendor
consensus on automated-vs-manual accessibility testing coverage — it is not a
re-validated empirical database. It narrows where to look; it does not certify
WCAG or ADA/Section 508 compliance.
```

## Guardrails
- Never state or imply a page is "WCAG compliant," "ADA compliant," or "accessible" as a conclusion of this checklist — it only re-prioritizes a scan the user already ran; it is not a conformance assessment.
- Never invent a confidence tier for a criterion not in the Gap-Map table above — always use `unmapped — confidence unknown`.
- Never drop or silently merge away the scanner's own `INCOMPLETE`/`needs review` items — carry every one of them into the output.
- Never claim to have seen, fetched, or re-scanned the live page — all checklist instructions must be generic, actionable steps based only on the pasted scan data, not invented specifics about that page's actual markup.
- Never present the Gap-Map's qualitative tiers as precise validated percentages — the footer caveat is mandatory on every output, not optional boilerplate to trim.
- If the pasted input isn't recognizable as scanner output (no rule IDs, no pass/fail structure), say so and ask for the real export rather than guessing at a checklist from a vague description.
