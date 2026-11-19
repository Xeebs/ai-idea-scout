# Text-Free UI Redesign Advisor

A prompt template for turning a text-heavy screen into an icon-and-voice-first redesign recommendation for low-literacy, low-connectivity users. Paste this whole document into any AI chat tool, then paste in your screen content and context as described below.

## When to use this

You're building or adapting a product screen (a benefits-eligibility checker, a health or vaccination tracker, a civic-services form, an agricultural advisory tool, a banking flow, etc.) for users who have low literacy, and possibly intermittent or no reliable internet connectivity. You already know what the current screen says and does — you just need a concrete plan for replacing its text with icons and voice prompts, instead of re-deriving that plan from design-research papers yourself.

This is not for: generating actual icon image files, writing production voice/ASR/TTS integration code, running a real usability study with real users, or designing a brand-new screen with no existing content to start from. It produces a written redesign recommendation for one screen at a time — a design-review document, not installable code or icon assets.

## What to hand over

**Data source: Manual.** You paste or describe this yourself — nothing here is read automatically from any app, screenshot tool, or API.

Required:
1. **The screen's content, element by element** — every label, field name, button, confirmation message, warning, and link currently on the screen. If you only have a screenshot, transcribe its visible text/elements into a list (or describe them precisely) rather than just attaching the image.
2. **Target context** — the users' primary spoken language(s), their literacy level if known, and their connectivity reality: reliable, intermittent, or sporadic/offline-first.

Optional but helpful: the app's domain (banking, health, civic services, agriculture), any existing brand icons or colors you want to keep using, and the target platform (mobile web, native app, USSD/IVR fallback).

## What the AI should do (the procedure)

Ask the AI to follow these steps in order:

1. **Inventory and classify each element** you listed into one of: Input field, Action/button (confirm, cancel, submit, delete, navigate, alert/warning), Informational display (a value/date/status), Navigation/link, or Confirmation/status message.

2. **Map each element to an icon-and-voice treatment**, using this baseline table (adapt the icon description to the specific domain, but keep the pattern):

   | Element type | Icon treatment | Voice prompt pattern |
   |---|---|---|
   | Confirm/submit | Filled checkmark, always in the same position (e.g. bottom-right) on every screen | "Press here to confirm: [plain restatement of the action]." |
   | Cancel/back | X or left arrow, opposite position from confirm | "Press here to go back without saving." |
   | Delete/irreversible action | Trash/warning icon in a distinct color, never in the confirm button's position | "This cannot be undone. Press again to confirm, or wait to cancel." |
   | Alert/warning | Triangle or exclamation icon, high contrast | Full plain-language readout of the warning — never just a summary |
   | Navigate forward/next | Right arrow | "Press here to continue to [next step name]." |
   | Informational value (date, amount, count) | A domain pictograph (calendar, coin stack, person icon) plus large numerals — never the icon alone | Full voice readout of the value, with an on-demand replay option |
   | Input field | An icon for what's being entered (microphone for voice input, numeral pad for numbers) | A spoken prompt describing exactly what to say or enter, with a worked example |
   | Navigation/link | An icon visually distinct from action buttons (e.g. a compass or list icon) | "Press here to see [destination]." |

3. **Apply these layout and flow rules**, and name the reason for each when writing them up:
   - One primary action per screen — competing actions on one screen measurably hurt task completion for low-literacy users in the research this pattern is based on.
   - The same action always sits in the same screen position across the whole app, so users build spatial memory instead of re-reading.
   - Never distinguish two actions by color alone — always pair a color difference with a shape/icon difference.
   - Every screen with voice content gets an on-demand audio replay control — users often need a second listen, and on a bad connection they can't just reload text.
   - Irreversible or high-stakes actions (submit, delete, mark-as-done) always get a two-step icon-plus-voice confirmation, never a single tap.

4. **Call out connectivity constraints by name.** If you told it your connectivity is intermittent or sporadic, it must say which voice prompts need to be pre-cached/stored locally versus which can rely on a live cloud TTS call, and flag any step in the flow that silently assumes a live connection (like "submit and get instant confirmation," or a "remind me later" scheduling action) so you can redesign it as a queued/offline-safe state instead.

4b. **Call out multi-language voice production by name.** If you named more than one target language, it must say plainly that every voice prompt script needs to be produced and validated separately per language — never assume a script or recording transfers from one language to another — and flag which elements' prompts are highest-risk to translate literally (idioms, numeral/date formats).

5. **Flag icon-universality risk on every icon it recommends.** A checkmark, X, or arrow is a broadly-tested convention; anything more domain-specific (a particular pictograph for "harvest," for instance) has NOT been validated for your specific region or culture, and should be flagged as needing local testing before you ship it. It should never tell you an icon is "universally understood" without this caveat — icon comprehension is genuinely not universal the way claimed conventions sometimes assume.

6. **Flag anything that resists icon-only treatment.** Numeric data, legal or consent text, or anything needing precision should get voice narration plus large-numeral display instead of being forced into a shaky pictograph — it should say so explicitly rather than inventing an icon that doesn't really work.

7. **Be honest about where each recommendation comes from.** When a recommendation traces to specific named design research (for example, Microsoft Research's published Text-Free UIs studies, or the publicly described design principles behind shipped products like Hello Ujjivan), it should name that source. When it's a general usability rule of thumb rather than a specific cited finding, it should label it "general usability principle" rather than implying a study backs the exact number or detail. It should never invent a statistic or finding that isn't already established.

8. **Always end with a validation recommendation** — test the redesigned screen with a small panel of real target-population users before shipping, the same way the underlying research validated its own patterns. This is a design recommendation, not a substitute for real user testing.

## Output format to request

Ask for the output structured exactly like this:

```
## Text-Free Redesign: <screen name>

**Context**: <target language(s)>, literacy context, connectivity: <reliable/intermittent/sporadic>

### Element-by-element redesign

| Original text/element | Type | Icon recommendation | Voice prompt script | Rationale | Universality risk |
|---|---|---|---|---|---|
| <your pasted text> | <type> | <icon description> | <script> | <named source OR "general usability principle"> | <validated convention / needs regional testing> |

(one row per element you provided — nothing skipped or merged)

### Layout & flow recommendations
- <ordering, confirmation pattern, audio replay, one-action-per-screen notes>

### Connectivity notes
- <which voice content needs local caching vs. live TTS; any flow step that silently assumes connectivity>

### Language notes
- <if you named multiple target languages: which voice prompts must be produced/validated per language, and which are highest-risk to translate literally — omit if you gave a single target language>

### Elements that resist icon-only treatment
- <any such element, with the recommended voice+numeral fallback>

### Before shipping
- A reminder to test this redesign with a small panel of real target-population users before shipping.
```

## Guardrails — the AI should never

- Call any icon "universally understood" without flagging the universality risk.
- Invent a research statistic, study, or participant count that wasn't already established — anything not traceable to a named source gets labeled "general usability principle" instead.
- Recommend an irreversible or high-stakes action be triggered by a single icon tap with no voice confirmation step.
- Ignore a stated intermittent/sporadic connectivity context — it must always address local caching versus live TTS calls.
- Ignore a stated multi-language target context — it must always flag per-language voice script production/validation.
- Skip or merge elements from your content inventory — every element you listed gets its own row in the output.
- Imply the output is installable code, shipped icon assets, or a maintained component library — it's a one-time design recommendation for one screen.
- Skip the closing recommendation to validate with real target-population users before shipping.
