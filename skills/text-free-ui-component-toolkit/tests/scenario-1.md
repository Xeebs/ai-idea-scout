# Scenario 1: Benefits-eligibility checker screen

## Input (what the user pastes)

> I'm building a benefits-eligibility checker for a rural agricultural subsidy program. Our users are low-literacy farmers, primarily Hindi speakers, in a region with sporadic mobile internet connectivity (coverage drops in and out, especially during monsoon). Here's the current screen:
>
> - Heading: "Check Your Eligibility"
> - Field label: "Enter Monthly Household Income (INR)"
> - Field label: "Enter Number of Household Members"
> - Field label: "Enter Land Size (acres)"
> - Button: "Submit"
> - Button: "Cancel"
> - Confirmation message shown after submit: "Your application has been submitted. You will be notified of your eligibility status within 5 business days."
> - Warning text shown if income exceeds threshold: "Based on the income entered, you may not qualify for this subsidy. Please review your entry before submitting."
>
> Can you redesign this as icon-and-voice-first for my users?

## Expected behavior

The skill should:
1. Produce an element-by-element table covering all 8 listed elements (heading, 3 input fields, 2 buttons, confirmation message, warning text) with no element skipped or silently merged.
2. For the three input fields, recommend a numeral-pad icon plus a spoken prompt that gives a worked example (e.g. "say or enter your monthly income, for example five thousand rupees") rather than just restating the label as voice.
3. Recommend Submit be treated as a confirm-type action — checkmark icon, consistent position — paired with a voice confirmation of what's about to happen, not a bare tap, since submitting an eligibility application is a meaningful (if not strictly irreversible) step.
4. Recommend Cancel use an X or back arrow in a distinct, consistent position from Submit.
5. Flag the confirmation message and the warning text as "informational/status" content needing full voice readout (not summarized) plus on-demand replay — and should NOT try to force the "5 business days" or the warning's conditional logic into an icon alone; this should surface explicitly under "Elements that resist icon-only treatment."
6. Explicitly address the stated sporadic connectivity — flag that the confirmation message and warning voice prompts should be either pre-cached locally or structured to degrade gracefully (e.g., queued submission state) rather than assuming a live connection at submit time.
7. Flag any domain-specific icon (e.g., a money/income pictograph, an acres/land pictograph) with a universality-risk note recommending regional validation — while treating checkmark/X/arrow as the broadly-tested baseline.
8. End with a recommendation to test the redesign with a small panel of real low-literacy farmers in the target region before shipping.
9. Not claim to produce actual icon files or installable code — frame this as a design recommendation only.

## Pass/fail criteria

- PASS if all 9 behaviors above are present and no element from the input is dropped.
- FAIL if any input field is missing from the output table, if Submit is treated as a single-tap action with no voice confirmation, if the sporadic connectivity context is not explicitly addressed, if any icon is called "universally understood" without a risk flag, or if the closing validation recommendation is missing.
