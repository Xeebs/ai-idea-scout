# Scenario 1 — Missing accessible name on an icon-only button (checkout flow)

## Context
A freelance accessibility consultant is doing a manual keyboard-nav and screen-reader walkthrough of a mid-size e-commerce client's checkout page ahead of a VPAT engagement. She hits the "remove item" button in the cart drawer during a NVDA pass and it announces only "button" — no indication of what it removes.

## Input handed to the skill

- **WCAG criterion**: 4.1.2 Name, Role, Value (Level A)
- **What I observed**: "Tabbing to the trash-can icon button in each cart line item, NVDA announces just 'button' with no label. Visually it's an icon-only button with no visible text, so sighted mouse users rely on the trash icon, but screen-reader users get zero context about what the button does or which item it removes."
- **Code/markup**:
```html
<button class="cart-item__remove" onclick="removeItem(142)">
  <svg class="icon-trash" aria-hidden="true">
    <use href="#icon-trash"></use>
  </svg>
</button>
```
- **Optional context**: Page is "Cart drawer", built in React (this is the rendered output), client's severity scale is Critical/Serious/Moderate/Minor and this would be "Serious."

## Pass criteria
- [ ] Output opens with the draft/sign-off warning banner.
- [ ] Correctly identifies/confirms criterion 4.1.2 (Name, Role, Value) without needing to infer — the auditor supplied it.
- [ ] Client-facing description names screen-reader users specifically (not generic "users with disabilities") and explains the practical consequence (can't tell which item is being removed, or that a remove action exists at all).
- [ ] Technical finding correctly identifies the root cause: no accessible name on the `<button>` — the `aria-hidden="true"` SVG correctly removes the icon from the accessibility tree but nothing replaces it with text.
- [ ] Remediation guidance gives a corrected code example that is a direct edit of the pasted snippet (e.g. adding `aria-label="Remove item"` or visually-hidden text), not a generic unrelated icon-button example, and ideally references making the label specific per item (e.g. including the item name) since the auditor flagged "which item it removes" as part of the problem.
- [ ] Retest step is concrete and names the actual tool/technique used (e.g. "Tab to each remove button in NVDA + Firefox/Chrome and confirm it announces something like 'Remove [item name], button'"), not a vague "test with a screen reader."
- [ ] Echoes back "Serious" severity only because the auditor supplied that scale — does not invent a severity label if that line is removed in a variant run.
- [ ] Does not attempt to audit anything else on the page beyond this one button.

## Fail conditions
- Treats this as an invitation to audit the whole cart drawer or checkout page.
- Produces a generic "add aria-label to your button" answer disconnected from the actual snippet (e.g. shows an unrelated `<button aria-label="...">Click</button>` example that doesn't match the SVG+icon structure given).
- Omits the draft/sign-off banner.
- States the WCAG criterion with an "inferred" caveat even though the auditor explicitly supplied it.
