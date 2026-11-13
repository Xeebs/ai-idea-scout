# Scenario 1 — E-commerce checkout flow (HTML provided)

## Input

**Flow being audited**: checkout: cart → shipping → payment → confirm

**Page 1 — Cart**:
```html
<main>
  <h1>Your Cart</h1>
  <div class="cart-item">
    <img src="hoodie.jpg" alt="Charcoal hoodie, size M">
    <span>Charcoal Hoodie (M)</span>
    <input type="number" value="1" aria-label="Quantity for Charcoal Hoodie">
    <button onclick="removeItem(1)"><img src="trash.svg"></button>
  </div>
  <div id="cart-total">Total: $64.00</div>
  <button class="btn-primary" onclick="goToShipping()">Continue</button>
</main>
```
(Note: `#cart-total` updates via JS whenever quantity changes, with no `aria-live` attribute. The trash-can remove button has no `aria-label` or visible text — only an `<img>` with no `alt`.)

**Page 2 — Shipping**:
```html
<main>
  <h2>Shipping Address</h2>
  <form>
    <input type="text" name="fullname" placeholder="Full Name">
    <input type="text" name="address" placeholder="Address">
    <input type="text" name="city" placeholder="City">
    <button type="submit">Submit</button>
  </form>
</main>
```
(No `<label>` elements — only placeholder text, which disappears on input and isn't reliably exposed as an accessible name in all screen-reader/voice contexts. The submit button just says "Submit" with no indication this advances to payment.)

**Page 3 — Payment**:
```html
<main>
  <h2>Payment</h2>
  <form>
    <input type="text" placeholder="Card Number">
    <input type="text" placeholder="Expiry">
    <input type="text" placeholder="CVV">
    <div role="button" tabindex="0" onclick="placeOrder()" class="btn-primary">Submit</div>
  </form>
</main>
```
(The "Place Order" action — which charges the card — is implemented as a `<div role="button">` labeled only "Submit," visually and semantically identical in style/role to the shipping form's low-stakes "Submit" button on Page 2.)

## Pass criteria

The output must:
1. Produce a verdict table covering all three pages, with Page 3 (Payment) marked **NOT-READY** or **NEEDS-FIXES** (not READY).
2. In the findings table, flag the Page 3 "Submit" div-as-button as **Critical** severity, explicitly because it's a high-stakes payment-triggering action that is visually/semantically indistinguishable from a low-stakes "Submit" elsewhere in the flow (Page 2) — this is the single most important catch in this scenario.
3. In the Stakes-Classification Map, list the Page 3 button as HIGH-STAKES with a disambiguation recommendation (e.g., relabel to "Place Order — $64.00" and/or convert to a real `<button>` element).
4. Flag the Page 1 trash-can icon button as missing an accessible name (icon-only, no `aria-label`, no alt text) — a voice-navigability issue.
5. Flag the Page 1 `#cart-total` update as missing an `aria-live` region.
6. Flag Page 2's placeholder-only form fields as missing explicit `<label>` elements.
7. Classify Page 1's "Continue," quantity field, and Page 2's address fields as LOW-STAKES (not flagged as needing confirmation gating) — the audit should not over-flag genuinely low-stakes navigation.
8. Include the required scope note disclaiming WCAG/legal compliance certification.

## Fail conditions

- Marking Page 3 READY, or failing to flag the ambiguous "Submit" payment button as Critical/high-stakes.
- Inventing markup/elements not shown above (e.g., claiming there's a confirmation modal that isn't in the provided HTML).
- Treating this as a generic WCAG audit without the stakes-classification map and scope note.
