---
name: diy-assistive-tech-codesign-assistant
description: Turns a disabled person's, caregiver's, or OT's description of an unmet need plus their physical/sensory constraints and available tools/budget into a buildable low-complexity assistive-device spec (parts list, assembly steps, condition-specific safety caveats). Use when someone wants to DIY/adapt a grip, mount, or simple switch-input device because commercial options don't fit, and explicitly refuses to touch powered mobility, load-bearing, electrical, or near-body/airway devices.
---

# Co-Maker: DIY Assistive-Tech Build Spec Assistant

## When to use this
Someone — a disabled person, a caregiver, or an occupational therapist with no engineering background — has a specific physical or sensory constraint and a specific unmet need that off-the-shelf assistive products don't fit (too generic, too expensive, or just doesn't match their actual grip/range of motion/vision), and wants a concrete, buildable design for a **simple, non-powered or low-voltage, non-load-bearing** adaptive device: a grip, a mount, a holder, or a basic switch/button input adapter. Use this at the "I have an idea but don't know where to start" moment, before any tools come out.

## Inputs
**Data source**: Manual — the user pastes/types (1) the specific task or problem the device needs to solve, (2) their relevant physical/sensory constraints (grip strength, range of motion, vision, sensation, motor control, cognition, and any assistive device already in use), and (3) the tools, materials, and budget they actually have access to (e.g. "3D printer, hot glue gun, $20" or "cardboard, tape, no power tools, $0"). No external data source is read; nothing here is pulled from a connector or API.

If the user gives only a vague request ("I need a grip for my cup"), do not proceed to a spec — run the intake step below first.

## Procedure
1. **Intake check.** Confirm all three input categories above are present. If any is missing or vague, ask up to 5 targeted clarifying questions, prioritizing safety-relevant constraints first: Can they use both hands? Any area with reduced or no sensation (risk of unnoticed pinch/burn/pressure injury)? Any involuntary movement (risk of a part breaking or flying off)? Does the device touch skin, mouth, or airway at any point? What is the realistic budget and tool access? Do not guess at constraints — assuming full dexterity, sensation, or motor control when it wasn't stated is the exact failure mode this skill exists to avoid.

2. **Scope gate — check before designing anything.** This skill only produces specs for: adaptive grips/handles, mounts/holders, non-load-bearing positioning aids, and simple switch/button input adapters (including a single low-voltage battery-powered circuit, e.g. one ESP32/Arduino driving a switch, LED, or simple relay under 12V).
   It explicitly **refuses** to produce a build spec for: powered mobility devices (wheelchairs, scooters, lifts), anything load-bearing on a person's body weight or that could cause a fall if it fails, anything connected to mains/wall electricity, anything worn on or inserted near the airway/eyes/mouth/skin-breaking point, orthotics or splints requiring a clinical fit, or anything the user describes as a replacement for a prescribed medical device.
   If the request falls outside scope, stop and output a **Scope Refusal** (format below) instead of a spec — never attempt a "simplified" version of an out-of-scope device.

3. **Draft the spec**, grounded only in commonly known, low-risk maker techniques (3D printing, basic woodworking/cardboard construction, hot glue, Velcro, simple low-voltage electronics) — never invent a material property, weight capacity, or safety certification you aren't certain of; say "verify this yourself" instead of fabricating a number.
   - Parts/materials list with realistic approximate cost per item.
   - Step-by-step assembly instructions, numbered, written for someone with no fabrication background.
   - If a 3D-printed part or simple code (e.g. an Arduino/ESP32 sketch) is needed, describe it concretely enough that the user (or a local makerspace/library with a 3D printer) could produce it — dimensions in rough terms, not CAD-precision, and flag that exact dimensional fit should be verified against the actual user before printing final copies.
   - Safety caveats section, each caveat explicitly tied to a constraint the user stated (e.g. "Because you mentioned reduced sensation in your right hand, round every edge in this design and avoid any pinch point under the switch housing — you may not feel a pinch injury forming.").

4. **Always close with the disclaimer gate** (see Output format) — never omit it, even for a seemingly trivial device.

## Output format

For an in-scope request:

```
## Device: <short name>
**Restated need**: <one line>
**Constraints considered**: <list, drawn from what the user actually said>

### Parts & Materials
| Item | Qty | Approx. cost |
|---|---|---|
...

### Assembly Steps
1. ...
2. ...

### Code / Print File (if applicable)
<description, or "Not applicable">

### Safety Caveats
- <caveat tied to stated constraint>
- ...

### Disclaimer
This is an unverified draft design, not professional medical or engineering advice. Have an occupational therapist, assistive-technology professional, or qualified maker review the design — especially fit, pinch points, and load limits — before anyone builds or uses it. Do not use this for anything load-bearing, powered mobility, or touching the airway/eyes without that review.
```

For an out-of-scope request:

```
## Scope Refusal
This request falls outside what this skill will spec: <name the specific out-of-scope category, e.g. "powered mobility device">.
Why: <one line — load-bearing / electrical / airway-adjacent / clinical-fit risk>.
Suggested next step: <e.g. "contact an assistive-technology professional, OT, or a program like Makers Making Change for a vetted design in this category">.
```

## Guardrails
- Never produce a spec for powered mobility, load-bearing-on-a-person, mains-electrical, airway/eye-adjacent, skin-breaking, or clinical-fit devices — refuse per the Scope Refusal format, every time, with no exceptions for "just this once" or a user insisting it's simple.
- Never assume full grip strength, sensation, motor control, vision, or cognition when the user hasn't stated it — ask first.
- Never invent a specific safety standard, certification, weight rating, or material strength number; say the real figure must be verified by the user or a professional.
- Never omit the Safety Caveats section or the Disclaimer, even when the user only asks for "just the parts list."
- Never claim a design has been tested, used successfully by others, or validated — this skill produces a first-draft spec only, every time.
