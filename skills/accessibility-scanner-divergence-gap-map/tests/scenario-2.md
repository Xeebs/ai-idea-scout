# Scenario 2 — Nonprofit's Lighthouse report, unfamiliar rule names, no scan yet for a second user

## Context A (main test): Lighthouse output with rule names not in the bundled axe-core table
A nonprofit's volunteer webmaster runs Chrome DevTools Lighthouse (not axe-core) against their donation page and pastes the accessibility section, which uses Lighthouse's own audit IDs rather than axe-core rule IDs.

## Input provided

**Scanner**: Lighthouse (Chrome DevTools, accessibility category)
**Page**: https://example-nonprofit.org/donate

**Scan output (abridged):**
```
Passed audits:
- "image-alt": Image elements have [alt] attributes — 7 elements
- "color-contrast": Background and foreground colors have sufficient contrast ratio — 15 elements
- "link-name": Links have a discernible name — 9 elements
- "tabindex": No element has a [tabindex] value greater than 0 — 1 element
- "video-caption": Video elements contain a <track> element — 1 element

Failed audits:
- "label": Form elements have associated labels — 2 elements missing labels (donation amount field, email field)

Manual checks Lighthouse does not score automatically:
- Logical tab order
- Interactive elements indicate their purpose and state
```

## Expected output shape
- Scanner is correctly identified as Lighthouse, and the skill maps by criterion rather than refusing just because the rule IDs ("image-alt", "color-contrast", "link-name", "video-caption") happen to overlap with axe-core naming in this case — these should map cleanly: image-alt→1.1.1 (PARTIAL), color-contrast→1.4.3 (RELIABLE, excluded), link-name→2.4.4 (PARTIAL), video-caption→1.2.2 (MANUAL-ONLY).
- `tabindex` is NOT in the skill's bundled mapping table — it must appear under "Unmapped" labeled "confidence unknown, verify manually," not silently dropped and not guessed into a tier.
- The two "Manual checks Lighthouse does not score automatically" items (tab order, interactive element state) are a form of the tool's own "needs review" signal — these should be carried over into the output (tab order maps cleanly to 2.4.3 Focus Order if the skill recognizes the description; if it can't confidently map the second one by description alone, it should still be preserved, labeled unmapped rather than dropped).
- The failed "label" audit (donation/email fields) must NOT appear on the checklist — it's a FAILED item with its own fix-it action, not a verify-manually item.
- `color-contrast` must NOT appear on the checklist (RELIABLE tier).
- Caveat footer present verbatim.
- Summary line accounts for all passed/failed/manual-check counts accurately.

## Context B (secondary, smaller check): user has no scan yet
A second, much shorter interaction: someone says "can you check if my site is accessible?" with no scan output and no scanner named.

## Expected behavior
- The skill must NOT fabricate scan results or guess at a checklist from a vague description.
- It must ask the user to run a real scanner first (e.g. naming `npx @axe-core/cli <url>` or Chrome DevTools Lighthouse) and return with the actual output.

## Pass/fail criteria
- PASS if: Context A correctly maps overlapping-named rules by criterion, correctly isolates `tabindex` as unmapped rather than dropping or mis-tiering it, excludes the failed label audit and the reliable contrast check, carries over the manual-check items, includes the caveat; AND Context B refuses to fabricate a checklist and asks for real scan output instead.
- FAIL if: `tabindex` is silently dropped or assigned a tier without basis, the failed label audit appears on the checklist, or Context B produces a fabricated accessibility assessment without real scan data.
