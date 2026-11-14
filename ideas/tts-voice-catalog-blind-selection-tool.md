# VoicePick: A Task-Matched Blind Selection Pipeline for Large TTS Voice Catalogs

- **Status**: PROPOSED
- **Date**: 2026-11-13
- **Topic**: Voice & multimodal agents
- **Source**: research/2026-11-13-voice-multimodal-agents-ii.md · P6
- **Maturity verdict**: PARTIAL — blind-listener TTS evaluation methodologies exist (TTS-Arena-V2, Podonos, Fish Audio's 71k-pair Bradley-Terry study, Codesota's SpeechBlind, Deccan's VoXClash) but every one compares different TTS *engines/models* against each other; none targets the narrower buyer problem of picking the single best voice out of one vendor's catalog of thousands for a specific narration/dialogue task.
- **Format**: BOTH
- **Data Sources**: CONNECTED — reads voice metadata and generates comparison clips directly via a TTS vendor's own catalog API (ElevenLabs Voice Library API is the primary target; Play.ht, Cartesia, and WellSaid expose comparable catalog/synthesis APIs) — these APIs are mature and already documented for listing voices and synthesizing sample audio. A listener-panel API (e.g. Prolific or Positly, both mature paid panel services) is used to recruit raters for the blind comparison. The one manual input is the user's own target narration/dialogue script, pasted in so all candidate voices are compared on the same real text.

## The Gap
r/speechtech's "Blind test of 32 ElevenLabs Voice Library voices for audiobooks" (2026-11-11, 125 paid listeners, 1,122 judgments) found that "'professional' voices [are] no better than instant clones, popularity predicts nothing, louder voices win" — meaning the vendor's own catalog signal (tags, popularity) is actively unreliable for picking a voice, and the poster had to design and fund their own study from scratch because nothing in the ElevenLabs library or elsewhere gave a defensible, task-specific answer. The gap-analyst confirmed general blind-TTS-evaluation methodology is well established for comparing engines, but no tool applies that rigor to the much narrower, much more common buyer question: which one voice, out of this one catalog, fits this one task.

## The Project
A pipeline that takes a target narration/dialogue script and a shortlist of candidate voice IDs pulled from a vendor's catalog API, synthesizes comparable clips for each candidate on the *same* text, runs a structured blind pairwise-comparison campaign through a listener panel, and computes a Bradley-Terry-style ranking plus dimension-specific scores (naturalness, task-fit, listener fatigue over longer clips) — replacing the vendor's unreliable popularity/tag signal with an actual, task-matched preference ranking. Judgments accumulate into a per-task, per-catalog leaderboard over time, so later users benefit from prior studies instead of re-running one from zero.

Component list: catalog-API adapter (pulls voice list + synthesizes same-script clips), panel-recruitment integration, pairwise-comparison survey generator, Bradley-Terry ranking engine, accumulating leaderboard store.

## Tangible Impact
**Population**: Independent and small-studio audiobook producers, game-dialogue studios, and app developers choosing a voice from a single vendor's narration catalog (e.g. ElevenLabs' 5,000+ English narration voices) for a real production task — the exact buyer the Reddit poster represents, who otherwise self-funds an ad hoc study (125 listeners, 1,122 judgments, real time and money) just to make one defensible choice.
**Mechanism**: Productizing the blind-test methodology turns a weeks-long, self-funded research project into a pipeline anyone can run (or, for common tasks, a leaderboard they can simply consult) — removing the vendor's misleading popularity signal from the decision entirely.
**Measure**: (1) time and cost to reach a defensible voice choice, from "weeks + a few hundred dollars in panel fees" down to "a single pipeline run or a leaderboard lookup"; (2) agreement rate between the tool's task-matched ranking and a held-out independent listener panel on the same task; (3) reduction in post-release re-casting/re-recording incidents attributable to listener complaints about the chosen voice.

## Why Now
TTS vendor catalog APIs (ElevenLabs Voice Library API chief among them) and mature panel-recruitment APIs (Prolific, Positly) already exist and are documented today — the entire pipeline is an integration and ranking-math problem, not a capability gap waiting on better models.

## Skill Angle
A companion skill takes a narration-task description plus 5-10 candidate voice IDs/names the user has already shortlisted from the catalog, and drafts a ready-to-run mini blind-test script: a balanced clip set on matched text, randomized presentation order, and a rating rubric a team can hand to even 5-10 of their own test listeners without building the full panel-recruitment pipeline. This is a one-shot design task genuinely separable from the persistent leaderboard/panel infrastructure of the full project.

## MVP Sketch
2-4 week MVP: a script that pulls N candidate voice IDs from the ElevenLabs API, synthesizes each on a user-supplied script, builds a randomized pairwise-comparison survey (e.g. via a lightweight web form), collects judgments from a small Prolific panel (20-30 raters), and outputs a Bradley-Terry ranking. Single experiment: run it against the same 32-voice set the Reddit poster already blind-tested and check whether the pipeline's ranking correlates with their published results.

## Risks & Open Questions
- Panel costs are real money per run; the MVP needs to prove the ranking is stable with a smaller, cheaper panel (20-30 raters) than the poster's 125, or the cost advantage over "just do it yourself" disappears.
- ElevenLabs' API terms-of-service around bulk synthesis for comparison/benchmarking purposes need checking before building a product around it.
- If ElevenLabs or a competitor ships an in-catalog "best fit for your script" recommender natively, this becomes a thinner wrapper — worth monitoring, since catalog-native recommendation is an obvious feature for the vendor to eventually add.
- The accumulating leaderboard is the long-term differentiator but adds real complexity (de-duplicating tasks, preventing rating gaming); the MVP should ship single-run comparisons first and defer the leaderboard.
