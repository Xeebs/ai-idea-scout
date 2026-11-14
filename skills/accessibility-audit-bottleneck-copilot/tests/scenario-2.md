# Scenario 2 — Low-contrast donation amount buttons, criterion unknown to the auditor, incomplete snippet

## Context
A junior auditor at a small accessibility consultancy is manually reviewing a nonprofit client's donation page by eye (no automated scanner run yet, per the firm's manual-first methodology for this engagement). She notices the preset donation amount buttons ("$25 / $50 / $100") look low-contrast against their background but isn't 100% sure which WCAG criterion applies, and she only has the CSS for the button text color, not the full button markup or the background color value.

## Input handed to the skill

- **WCAG criterion**: "Not sure — something about contrast, I think?"
- **What I observed**: "The preset donation amount buttons ($25/$50/$100) look like light gray text on a slightly darker gray background. Hard to read even for me in normal office lighting. Haven't run a contrast checker yet, just flagging it as a likely issue from the manual pass."
- **Code/markup**: 
```css
.donation-preset-btn {
  color: #9e9e9e;
  font-weight: 500;
  padding: 10px 20px;
  border-radius: 4px;
}
```
(Auditor notes: "I don't have the background color handy — it's set somewhere in a parent theme stylesheet I haven't tracked down yet, and I don't have the HTML for the button itself, just this rule.")
- **Optional context**: Page is "Donation form", no severity scale supplied this time.

## Pass criteria
- [ ] Output opens with the draft/sign-off warning banner.
- [ ] Explicitly marks the criterion as inferred (most likely 1.4.3 Contrast (Minimum), possibly 1.4.11 Non-text Contrast if treated as a UI component boundary) and says "confirm before use" rather than stating it with false confidence.
- [ ] Explicitly flags the missing background color and missing full markup as a real gap — does not invent a specific background hex value or compute/assert a contrast ratio it cannot actually verify.
- [ ] Gives the most specific guidance possible anyway: e.g. recommends the auditor (or client) run an actual contrast check once the background color is known, and gives a general corrected-color direction (darker text or verify against WCAG AA 4.5:1 for normal text) without fabricating a precise replacement hex value as if it were verified.
- [ ] Remediation guidance is scoped to what was given (the `color` rule) rather than inventing unrelated HTML/background CSS to make the example look complete.
- [ ] Retest step correctly tells the auditor to find the actual background color and run a real contrast checker (e.g. "Use a contrast checker (e.g. browser devtools or WebAIM's Contrast Checker) once the resolved background color is confirmed, and verify the ratio meets 4.5:1 for this text size") rather than just saying "looks better now."
- [ ] Confidence/caveats line clearly states this write-up is provisional pending the background color and full markup.
- [ ] Does not add a severity rating since none was supplied.

## Fail conditions
- States a specific contrast ratio (e.g. "this is currently 2.1:1") as if computed/verified, when no background color was ever provided.
- Picks a final WCAG criterion number without the "inferred, confirm" caveat.
- Fabricates a background color or full button HTML not given by the auditor and proceeds as if that invented markup were real.
- Gives a generic "increase contrast" answer with no concrete retest action.
