# Scenario 1 — Small business e-commerce site, axe-core CLI output, mostly green

## Context
A small online furniture store's developer ran `npx @axe-core/cli https://example-furniture-shop.com` before a relaunch. The scan came back with a 94% pass rate and the team's instinct is to call it "accessible" and ship. They paste the following into the skill.

## Input provided

**Scanner**: axe-core (CLI v4.12)
**Page**: https://example-furniture-shop.com/checkout

**Scan output (abridged, realistic shape):**
```
Violations: 2
- color-contrast: FAIL (3 elements) — "Add to cart" button text contrast 3.2:1, needs 4.5:1
- aria-valid-attr-value: FAIL (1 element) — aria-expanded="maybe" on dropdown

Passes: 11
- image-alt: PASS (18 elements)
- html-has-lang: PASS (1 element)
- link-name: PASS (24 elements)
- heading-order: PASS (6 elements)
- label: PASS (9 elements)
- focus-order-semantics: PASS (1 element)
- aria-roles: PASS (14 elements)
- video-caption: PASS (1 element)
- meta-viewport: PASS (1 element)
- html-lang-valid: PASS (1 element)
- aria-required-children: PASS (3 elements)

Incomplete: 1
- color-contrast: INCOMPLETE (2 elements) — background image behind text, contrast can't be auto-calculated
```

## Expected output shape
- Summary line: 11 passed, 2 failed, 1 incomplete, with a stated count of how many of the 11 passes need a human look (should be most of them — `image-alt`→PARTIAL, `link-name`→PARTIAL, `heading-order`→PARTIAL, `label`→PARTIAL, `focus-order-semantics`→MANUAL-ONLY, `video-caption`→MANUAL-ONLY, `html-has-lang`/`html-lang-valid`→RELIABLE (excluded), `meta-viewport`→PARTIAL, `aria-roles`/`aria-required-children`→PARTIAL).
- Tier 1 must include `focus-order-semantics` (2.4.3, MANUAL-ONLY) and `video-caption` (1.2.2, MANUAL-ONLY) with concrete 2-5 minute manual checks (e.g. tab through the checkout flow; play the video with sound off and check captions).
- Tier 2 must include `image-alt`, `link-name`, `heading-order`, `label`, `meta-viewport`, `aria-roles`, `aria-required-children`.
- `html-has-lang` and `html-lang-valid` must NOT appear anywhere in the checklist (RELIABLE tier, excluded).
- The two `color-contrast` FAIL items must NOT appear on the checklist (failed items are excluded, they already have an action).
- The `color-contrast` INCOMPLETE item must be carried over verbatim in a "carried over" section, since it's the scanner's own flagged item.
- The mandatory caveat footer must appear in full, not paraphrased or dropped.
- Output must not claim the page "is accessible" or "is compliant" anywhere.

## Pass/fail criteria
- PASS if: all of the above mappings are correct, failed and reliable-tier items are excluded, the incomplete item is carried over, and the caveat is present verbatim or near-verbatim.
- FAIL if: any FAILED or RELIABLE-tier item appears on the checklist, the incomplete item is dropped, the caveat is missing, or the output asserts compliance.
