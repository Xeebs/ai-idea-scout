---
name: text-free-ui-component-toolkit
description: Turns a text-heavy screen description into an icon-and-voice-first redesign recommendation for low-literacy, low-connectivity users, drawing on validated "text-free UI" research (Microsoft Research's Text-Free UIs studies, Hello Ujjivan's shipped design principles). Use when a developer or designer is adapting a screen for low-literacy users and needs a concrete, element-by-element redesign spec — not for generating or shipping actual icon assets or code.
---

# Text-Free UI Redesign Advisor

## When to use this
A developer, designer, or product manager building a tool for low-literacy users (benefits-eligibility checkers, health/vaccination trackers, civic-services screens, agricultural advisory tools, etc.) has a specific screen that is currently text-heavy and wants to know how to redesign it as icon-and-voice-first. Reach for this skill at that exact moment: an existing screen's content is already known (pasted or described), and the question is "how do I make this text-free for my low-literacy, possibly low-connectivity users?"

Do NOT use this for: generating actual icon image assets, writing production voice/ASR/TTS integration code, running a usability study, or designing a brand-new screen from a blank page with no existing content to redesign from. This skill produces a design recommendation document, not shippable code or icon files — it is a one-shot design-review aid, not the maintained component library the full project would ship.

## Inputs
**Data source**: Manual — the user pastes or describes the existing screen's content and layout (visible text labels, form fields, buttons/actions, confirmation or status messages — a screenshot description works if no literal text dump is available) plus the target users' language(s) and connectivity context. Nothing is read from any connector, screenshot-parsing API, or live app — if a user pastes an actual image, treat it as a described screenshot and ask them to transcribe the visible text/elements if it isn't already machine-readable to you.

Required, per screen:
1. **Screen content inventory** — every distinct text element: labels, field names, button text, confirmation/status messages, links, headings.
2. **Target context** — the users' primary spoken language(s), literacy level if known, and connectivity reality (reliable, intermittent, or sporadic/offline-first).

Optional, if available: the app's domain (banking, health, civic, agriculture), existing brand icons/colors to reuse, target platform (mobile web, native app, USSD/IVR fallback).

## Procedure
1. **Inventory and classify each element.** List every text element the user provided and classify it into one of these types: Input field, Action/button (confirm, cancel, submit, delete, navigate, alert/warning), Informational display (a value, date, or status), Navigation/link, Confirmation or status message.
2. **Map each element to an icon-and-voice treatment** using this reference table as the baseline, adapting the icon description to the domain:

   | Element type | Icon treatment | Voice prompt pattern |
   |---|---|---|
   | Confirm/submit | Filled checkmark, consistent position (e.g. bottom-right) | "Press here to confirm: [plain restatement of the action]." |
   | Cancel/back | X or left arrow, opposite position from confirm | "Press here to go back without saving." |
   | Delete/irreversible action | Trash/warning icon + distinct color, never same position as confirm | "This cannot be undone. Press again to confirm, or wait to cancel." |
   | Alert/warning | Triangle or exclamation, high contrast | Full plain-language readout of the warning, not a summary |
   | Navigate forward/next | Right arrow | "Press here to continue to [next step name]." |
   | Informational value (date, amount, count) | Pictograph relevant to the domain (calendar, coin stack, person icon) + large numerals, never icon alone | Full voice readout of the value in the user's language, on-demand replay |
   | Input field | Icon representing what's being entered (microphone for voice input, numeral pad for numbers) | Spoken prompt describing exactly what to say or enter, with an example |
   | Navigation/link | Icon distinct from action buttons (e.g. compass/list icon) | "Press here to see [destination]." |

3. **Apply layout and flow conventions**, each justified by name:
   - One primary action per screen (Hello Ujjivan / Microsoft Research low-literacy comprehension finding: multiple competing actions on one screen measurably hurt task completion for low-literacy users).
   - Consistent icon placement across screens (same action = same position everywhere) so users build spatial muscle memory instead of re-reading.
   - Never rely on color alone to distinguish actions — pair every color distinction with a shape/icon distinction.
   - Provide an on-demand audio replay control on every screen with voice content — low-literacy users often need a second listen, and sporadic connectivity means they can't just reload text.
   - Irreversible or high-stakes actions (submit, delete, mark-as-complete) get a two-step icon-plus-voice confirmation, never a single tap.
4. **Flag connectivity constraints explicitly.** If the user named intermittent or sporadic connectivity, state whether each voice prompt needs to be a pre-cached/locally-stored audio file versus a live cloud TTS call, and flag any flow step that silently assumes connectivity (e.g. a "submit and get instant confirmation" flow, or a "remind me later" scheduling action, that needs an offline queued-state design instead).
4b. **Flag multi-language voice production explicitly.** If the user named more than one target language (or a language mix), state plainly that every voice prompt script needs to be produced and validated separately per language — never assume a script or recording transfers from one language to another — and list which elements' voice prompts are most context-sensitive (idioms, numeral/date formats) and therefore highest-risk to translate literally.
5. **Flag icon-universality risk per icon.** For every icon recommended, note explicitly whether it is a broadly-tested convention (checkmark, X, arrow) or a domain-specific pictograph that has NOT been validated for the user's specific region/culture, and recommend regional validation before shipping anything not in the broadly-tested set. Never state an icon is "universally understood" without this caveat.
6. **Flag elements that resist icon-only treatment.** Numeric data, legal/consent text, or anything requiring precision should get voice narration plus large-numeral display rather than being forced into a pictograph — say so explicitly rather than inventing a shaky icon.
7. **Cite the research basis honestly.** When a recommendation traces to a specific named source (Microsoft Research's Text-Free UIs study population and findings, Hello Ujjivan's publicly described design principles), name it. When a recommendation is a general usability principle rather than a specific cited finding, label it "general usability principle" instead of implying it came from a specific study. Never invent a statistic, participant count, or finding that wasn't already established.
8. **Close with a validation recommendation.** Always end by recommending the redesigned screen be tested with a small panel of real target-population users before shipping, mirroring the validation methodology the underlying research itself used — this skill produces a design recommendation, not a substitute for testing with real users.

## Output format
```
## Text-Free Redesign: <screen name>

**Context**: <target language(s)>, literacy context, connectivity: <reliable/intermittent/sporadic>

### Element-by-element redesign

| Original text/element | Type | Icon recommendation | Voice prompt script | Rationale | Universality risk |
|---|---|---|---|---|---|
| <pasted text> | <type> | <icon description> | <script> | <cited source OR "general usability principle"> | <validated convention / needs regional testing> |

(one row per element provided — never skip or merge elements)

### Layout & flow recommendations
- <ordering, confirmation pattern, audio replay, one-action-per-screen notes>

### Connectivity notes
- <which voice content needs local caching vs. live TTS; any flow steps that assume connectivity>

### Language notes
- <if multiple target languages: which voice prompts must be produced/validated per language, and which are highest-risk to translate literally — omit this section only if a single target language was given>

### Elements that resist icon-only treatment
- <any element flagged in step 6, with the recommended voice+numeral fallback>

### Before shipping
- Recommend testing this redesign with a small panel of real target-population users (same methodology the underlying research used) before shipping. This is a design recommendation, not the maintained component library — asset production and code integration are separate work.
```

## Guardrails
- Never claim any icon is "universally understood" without a universality-risk flag — icon comprehension is not universal across cultures/regions, even for seemingly standard icons.
- Never invent a research statistic, participant count, or named finding that wasn't already established in the conversation or widely documented — label anything not traceable to a specific named source as a "general usability principle."
- Never recommend an irreversible or high-stakes action (submit, delete, mark-as-done) be triggered by a single icon tap with no voice confirmation step.
- Never ignore a stated sporadic/intermittent connectivity context — always address whether voice content needs local caching versus a live API call.
- Never ignore a stated multi-language target context — always state that voice scripts need per-language production/validation, never assume one recording transfers across languages.
- Never skip or silently merge elements from the user's provided content inventory — every element they listed gets its own row in the output table.
- Never present this skill's output as the actual maintained icon/voice component library, installable code, or shipped assets — it is a one-time design recommendation for one screen; say so explicitly if the user seems to expect installable deliverables.
- Never skip the closing recommendation to validate with real target-population users before shipping.
