---
title: "Who Said That: Speaker-Identified Multimodal Memory for Shared Voice Agents"
date: 2026-11-12
topic: Voice & multimodal agents
---

Ask a shared smart speaker to remind you about your dentist appointment, and there's a decent chance it mentions your sibling's dentist appointment too — or your partner's dietary restriction gets recommended to you at dinner. Every voice agent that lives in a household or a shared office kiosk today runs on one assumption that quietly breaks the moment more than one person talks to it: that there's a single "user" whose preferences and facts all pile into the same bucket.

## The Gap

The research team behind EgoMem names the exact assumption that's failing: "earlier memory agents assume known user identities, clear session boundaries, and text-only input, and those assumptions fail in full-duplex omnimodal use." In plain terms — most voice-agent memory was designed for one person talking to one device in discrete sessions, and shared devices violate every part of that design. A household smart speaker or an office kiosk doesn't get neat session boundaries; it gets a rotating cast of speakers, often mid-conversation, with no login step and no wake-word ritual per person. Blend everyone's facts into one profile and you get the familiar failure mode: one person's calorie-tracking note surfacing in someone else's grocery suggestion, or a kid's homework reminder read out to a parent.

The research world has noticed. M2A points out that "most personalization is static, while users keep refining their preferences," and ships a dual-layer memory architecture built to be incrementally edited rather than just appended to. VoxPolyMem goes further, explicitly targeting multi-party speaker attribution across sessions — and on its own benchmark (VoxPolyBench) it scores 85.0, a full 23.6 points ahead of its strongest baseline. That's a meaningful jump, and it's evidence the underlying problem is tractable, not just aspirational.

But "tractable in a paper" and "shipped in a product" are different claims. Every implementation of continuous, speaker-identified, boundary-free memory found so far is a 2025–2026 research paper (EgoMem, M2A, VoxPolyMem, HARMONI), evaluated on a benchmark its own authors built. No production voice-agent platform — not Vapi, not Retell, not LiveKit, not Pipecat — claims this as a shipped feature. And the gap isn't for lack of raw ingredients: real, narrow tools already exist on both halves of the problem. `alexwboles/voice-memory` and its sibling `callrecall-ai` are functioning, MIT-licensed, single-maintainer projects that give a voice agent per-caller memory — just for one speaker per call, not a household of overlapping voices. On the identification side, LiveKit paired with Speechmatics ships production-grade real-time speaker diarization — but with no persistent memory layer attached to it. The pieces exist. Nobody has bolted them together into something a family or a small team could actually run.

## The Project

The idea is a memory layer that sits between an existing voice-agent stack and its users, doing one job well: identify who's speaking inside continuous audio with no explicit session start or stop, attribute every new fact or preference to that specific person, and let those per-person memories be corrected incrementally as life changes — all without anyone logging in or saying a special wake phrase first.

Concretely, it's four pieces working together. A continuous speaker-ID front end (built on commodity diarization/voice-ID, not a research-grade jointly-trained model) listens across the whole interaction rather than per-utterance. A per-speaker memory store holds each person's facts and preferences separately, with support for editing a fact later rather than just appending new ones on top of stale ones. A low-confidence fallback handles the moment voice-ID isn't sure who's talking — asking a short disambiguating question instead of silently guessing and risking a cross-contamination error. And a dedicated cross-contamination test suite exists specifically to catch the failure mode that defines this problem: does the system ever apply person A's preference to person B. That last piece matters because it's the one thing a demo can get away with skipping and a real deployment can't.

This isn't a new app bolted around an existing assistant — it's a memory backend meant to plug into the voice-agent stacks that already exist, replacing the single blended-profile default most of them ship with today.

## Tangible Impact

**Population**: multi-person households and small shared workspaces using a shared voice-agent device — e.g., family members using one smart-speaker-style assistant, or a small team using a shared office kiosk voice agent — where a single blended memory currently causes visible errors (recommending one person's dietary restriction to another, repeating another person's calendar details).

**Mechanism**: correctly attributing facts and preferences per speaker, continuously and without a login step, removes the cross-contamination errors that currently make shared voice agents feel unreliable or mildly invasive to the people who share the device, and lets each person get personalized responses without administrative setup.

**Measure**: per-speaker fact-attribution accuracy on a multi-person test household/office corpus; cross-contamination error rate (wrong-person preference applied); user-reported "it doesn't remember me correctly" incident rate in a pilot deployment.

## Try It

No companion Claude Code skill exists for this idea yet — it's tagged `Format: PROJECT`, reflecting that the core value here is in the built memory-and-diarization infrastructure itself, not a prompt-driven task a skill could wrap. If that changes, a skill version would show up at `skills/speaker-identified-multimodal-voice-memory/` and this section will be updated to link it.

Worth being honest about the risks before anyone runs at this: voice-ID gets noticeably less reliable between similar-sounding speakers — siblings, for instance, which is exactly the household case this is built for — so the fallback question has to be genuinely graceful or the feature reads as broken rather than careful. Continuous voice identification inside someone's home also raises real consent questions that need a clear answer before any deployment, not an afterthought. There's no public labeled multi-person household corpus to build against yet, which makes early validation slow and uncertain to generalize. And if confidence stays low often enough in real noisy environments, the system may lean on disambiguation questions so frequently that it undermines the entire "no login step" pitch that makes this worth building in the first place.

---

Surfaced from `research/2026-11-12-voice-multimodal-agents-ii.md`, pattern `P4`.
