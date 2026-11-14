# Gaze Mix: An Eye-Gaze-Controlled Live Audio Mixer for AAC Users

- **Status**: PROPOSED
- **Date**: 2026-11-14
- **Topic**: Applied AI for underserved domains
- **Source**: research/2026-11-14-applied-ai-for-underserved-domains.md · P3
- **Maturity verdict**: PARTIAL — GitHub search for "eyegaze" returned only gaze-estimation research code, nothing for sound control. WebSearch found only academic/research-stage prototypes (DJeye, University of Milan 2023; Microsoft's Hands-Free Sound Jam; Cyclops, NIME 2020; Dueto, Microsoft/CMU) all oriented toward looping/track/DJ performance, none a maintained shipped product for live volume/EQ control; EyeCanDo (consumer iOS) exposes only basic playback volume, not mixing.
- **Format**: PROJECT
- **Data Sources**: CONNECTED — a standard eye-tracking SDK/API (e.g. Tobii Core SDK, or the built-in Windows Eye Control API) for gaze input, both mature and already widely deployed in AAC/AT settings; output is routed as standard OSC/MIDI control messages into existing live-sound software (a mixer app, DAW, or hardware mixer with MIDI/OSC input), a mature and universally-supported protocol layer. No manual data entry involved — the clinician/participant configures faders once, then controls them live by gaze.

## The Gap
An assistive-technology clinician asked r/accessibility on behalf of a participant (r/accessibility, "Eyegaze sound control", 2026-11-13): "most of the apps we've looked at have a lot of track control for recorded music, looping, DJ stuff, etc. anybody know of anything that might fit the bill? Anything, even better, already eyegaze friendly?" — a direct "does this exist" with no confident answer in the thread. Eye-gaze control is mature for computer navigation and AAC communication boards, but every accessible-audio option a working clinician could find is built for recorded-track/looping workflows, not live volume/EQ control a performer or participant could use in the moment.

## The Project
A focused, standalone gaze-controlled live mixer: a small number of large, high-contrast on-screen faders and EQ dials, each operable by dwell-time gaze selection (the same interaction pattern eye-gaze AAC boards already use), each mapped to a MIDI CC or OSC message that feeds into whatever mixing software or hardware the venue/clinic already runs. No track management, no looping, no performance sequencing — purely the live-control surface that the Reddit thread says is missing, built to connect to the gaze hardware (Tobii, PCEye) clinics already own rather than requiring new hardware.

## Tangible Impact
**Population**: Eye-gaze AAC users with significant motor impairment (e.g. ALS, cerebral palsy, spinal cord injury) who want to participate in live sound/music activities — a narrow but real population already served by existing gaze-AAC infrastructure in clinics, schools, and adaptive-music programs (AT clinicians regularly request custom builds for exactly this kind of individual participant need, as this thread shows).
**Mechanism**: Gives a person who currently has zero accessible option for live sound control a functional one, built on hardware and interaction patterns (dwell-select, large targets) they already use daily for communication — turning a "does this exist?" dead end into "yes, here's a working tool," enabling participation in music therapy, performance, or classroom activities that were previously staff-operated on the person's behalf.
**Measure**: (1) time for a new user to reach a target volume/EQ setting unaided, benchmarked against a sighted/manual control baseline; (2) clinician-rated functional independence gained (e.g. a validated AT outcome measure like PIADS); (3) number of distinct clinics/programs adopting it beyond the original requesting clinician.

## Why Now
Eye-tracking hardware (Tobii, PCEye) and their SDKs are now mature, affordable, and already deployed in most AAC clinics for communication use, meaning the hard problem (reliable gaze tracking) is already solved and owned by the target population — what's missing is purely the thin software layer mapping gaze to live-audio control messages, which is newly easy to build well given mature, stable OSC/MIDI libraries and gaze SDKs.

## MVP Sketch
Scope: a single-screen app with 4 faders (e.g. 2 channel volumes, master volume, one EQ band) controllable by dwell-time gaze selection via the Tobii Core SDK, each emitting MIDI CC messages into a standard DAW or hardware mixer over USB/network MIDI. Rough stack: a lightweight desktop app (Electron or native), Tobii SDK integration, a MIDI output library (e.g. RtMidi). Single experiment: have the original requesting clinician and their participant trial the 4-fader MVP against their current workaround (likely staff-operated) and measure whether the participant can independently hit a target mix within a defined time and error tolerance.

## Risks & Open Questions
- Population size is genuinely small — this is a niche AT build, not a mass-market product; worth building anyway given the concrete, otherwise-unmet need and AT Idea Scout's track record of funding similarly niche AAC tools (e.g. the existing silent-speech and AAC-vocabulary ideas in this ledger).
- Dwell-time gaze selection for continuous fader control (vs. discrete button selection) may need a different interaction pattern (e.g. gaze-and-hold-to-ramp) that hasn't been validated for this specific task — this needs real user testing, not just porting the AAC board pattern directly.
- Risk of effectively reinventing one piece of DJeye/Hands-Free Sound Jam's gaze-tracking code rather than the live-mixing-specific interaction layer that's actually missing — worth reviewing their open materials (where published) before building gaze-tracking integration from scratch.
- No existing eval protocol for "accessible live audio control" tools exists to benchmark against; the MVP experiment above would need to define its own success criteria from scratch.
