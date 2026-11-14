# Co-Maker: DIY Assistive-Tech Build Spec Assistant

A prompt template that turns "I need to build/adapt something because nothing on the market fits me" into a concrete, buildable design — a parts list, assembly steps, and safety caveats specific to your situation. Works in any AI chat tool; no special setup required.

## Who this is for

Disabled people, caregivers, and occupational therapists (OTs) with **no engineering background** who have a specific physical or sensory need that commercial assistive products don't fit well, and who want to build or adapt something simple themselves: a grip, a mount/holder, a positioning aid, or a basic switch/button input device. This is explicitly scoped **away from** anything powered-mobility, load-bearing on a person, connected to mains electricity, or touching the airway/eyes/skin-breaking point — those need a professional, not a DIY spec, and the prompt below is designed to refuse those and say so.

## What it needs from you

This only works with what you type in — it doesn't look anything up or connect to any device or account. Before you paste the prompt, have ready:

1. **The specific task or problem** your device needs to solve (not "I need help with my hands" — "I need to open jars one-handed" or "I need a way for my child to press a button to activate a toy").
2. **Your relevant physical/sensory constraints**: grip strength, range of motion, vision, areas of reduced or no sensation, involuntary movement, cognition, and any assistive device you already use.
3. **What tools, materials, and budget you actually have**: a 3D printer, a soldering iron, cardboard and tape, an Arduino/ESP32 kit already on hand, and a rough dollar budget.

If you leave any of these vague, the assistant will ask you a few follow-up questions before giving you a design — that's expected, not a bug; skipping this step is how unsafe designs happen.

## The prompt

Copy everything below the line, fill in your own details in place of the brackets, and paste it into any AI chat tool.

---

You are helping me design a simple DIY assistive device. Here is my situation:

**Need**: [describe the specific task or problem]
**My constraints**: [grip strength, range of motion, vision, sensation, motor control, cognition, existing assistive devices — be specific, don't assume I'll fill in gaps]
**Tools/materials/budget I have**: [e.g. "3D printer, hot glue gun, $20" or "cardboard, tape, no power tools, $0"]

Before designing anything:
1. If any of the above is missing or too vague to design safely around, ask me up to 5 targeted clarifying questions — prioritize safety-relevant ones first (can I use both hands, do I have any area with reduced/no sensation, any involuntary movement, does the device touch skin/mouth/airway, what's my real budget and tool access). Do not guess at my abilities.
2. Check scope: you will only design adaptive grips/handles, mounts/holders, non-load-bearing positioning aids, or simple switch/button input adapters (including one low-voltage battery-powered circuit under 12V, like a single Arduino/ESP32 driving a switch or LED). You will refuse — and tell me why, plus suggest I contact an OT, assistive-tech professional, or a program like Makers Making Change instead — if my request is a powered mobility device, anything load-bearing on my body weight, anything connected to mains electricity, anything worn on or near my airway/eyes/mouth, a skin-breaking device, an orthotic/splint needing a clinical fit, or a replacement for a device I was prescribed.
3. If in scope, give me:
   - A parts/materials list with approximate cost per item.
   - Numbered, beginner-friendly assembly steps.
   - If a 3D-printed part or simple code is needed, describe it concretely (rough dimensions, what the code does) and tell me to verify exact fit against my own body/device before printing a final copy.
   - A Safety Caveats section where every caveat is tied to a constraint I actually told you about (e.g. "because you have reduced sensation in your right hand, round every edge and avoid this pinch point — you may not feel an injury forming").
   - A closing disclaimer: this is an unverified first-draft design, not professional medical or engineering advice, and I should have an OT or qualified maker review it — especially fit, pinch points, and load limits — before building or using it.

Never invent a specific safety certification, weight rating, or material strength number — tell me to verify it myself if you're not certain. Never assume full dexterity, sensation, or motor control I haven't described. Never skip the Safety Caveats section or the disclaimer, even if I only ask for the parts list.

---

## What you'll get back

Either:
- **A build spec** — restated need, the constraints the assistant used, a parts/cost table, numbered assembly steps, a code/print-file description if relevant, a Safety Caveats list tied to your actual stated constraints, and a disclaimer recommending professional review before building.
- **A scope refusal** — a clear statement that your request falls outside safe DIY territory (powered mobility, load-bearing, electrical, airway-adjacent, or clinical-fit), why, and where to go instead (an OT, assistive-tech professional, or a program like Makers Making Change).

## Limits — read this before you build anything

- This produces a **first draft only**. It has not been tested, fitted to your body, or reviewed by anyone qualified. Have an occupational therapist, assistive-technology professional, or experienced maker check fit, pinch points, and load limits before you build or use anything from it.
- It will not, and should not, design powered mobility devices, anything load-bearing on a person, anything on mains electricity, anything near the airway/eyes/mouth, or a replacement for a device you were actually prescribed. If you ask for one of these and it doesn't refuse, stop and don't build it — report it as a bug in the prompt, not a safe design.
- It doesn't remember past sessions or share designs with anyone else building something similar — each run is a one-shot draft. If you want a shared library of past designs other people can search, that's a larger, persistent project this one-shot prompt intentionally doesn't try to be.
