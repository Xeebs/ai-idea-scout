# Oral Access: A Voice-Readiness Toolkit and Scorecard for Oral-Tradition, Low-Resource Languages

- **Status**: EXPLORING (promoted 2026-11-12: evidence density — ≥3 independent institutional sources confirm the same unaddressed gap: Stanford HAI, UNDP, and the 60-signatory coalition's own Sept 2026 announcement each state voice support for oral-tradition-language communities remains unaddressed)
- **Date**: 2026-11-12
- **Topic**: Applied AI for underserved domains
- **Source**: research/2026-11-12-applied-ai-for-underserved-domains.md · P7
- **Maturity verdict**: PARTIAL — real tooling exists (UBC-NLP's AfroLID, Masakhane Web, Masakhane's AfriQA, AfriSpeech's africa-tts for 92 African languages, AI4Bharat's Airavata/IndicBias) but each is narrow — single-modality or single-region research-grade work — and doesn't close the specific gap Stanford HAI/UNDP flag: voice support for communities with strong oral traditions remains unaddressed, while the 60-signatory coalition's own Sept 2026 announcement confirms governance/workstreams are still being built out "over the coming year," not shipped.
- **Format**: BOTH

## The Gap
A ~60-signatory coalition (frontier AI labs, Masakhane, Lelapa AI, AI4Bharat, Karya, Sunbird, Anthropic) has committed to a five-year goal bringing AI to 3.4B speakers of underrepresented languages, backed by the Gates Foundation's $1B/2yr commitment (Sept 2026) — but per the coalition's own announcement, "governance and workstreams are still being developed... over the coming year." Meanwhile Stanford HAI and UNDP state current models "underperform for the 1.2 billion native speakers of low-resource languages" and that "voice support ... [is] also limited for communities with strong oral traditions" — a technical gap distinct from text-model quality, and one no existing tooling closes end to end.

## The Project
An open benchmark and data-pipeline toolkit focused specifically on ASR+TTS (not text) for oral-tradition languages lacking a standardized writing system or with low literacy — the sub-gap the Stanford HAI/UNDP source flags as unaddressed. It (1) catalogs which of the coalition's target languages have zero, research-grade, or production-grade voice coverage today, extending the audit methodology AfriSpeech already applies to 92 African languages across other orgs' territory (AI4Bharat, Sunbird); (2) packages a reusable, community-sourced voice-data collection protocol that doesn't require a written standard; and (3) publishes a running "voice-readiness scorecard" tracking whether the coalition's commitments translate into shipped ASR/TTS coverage over time, functioning as an independent accountability layer on the coalition's own stated goal.

## Tangible Impact
**Population**: the ~1.2 billion native speakers of low-resource languages Stanford HAI/UNDP cite, narrowed to communities with strong oral traditions and limited written-language infrastructure — disproportionately rural, often lower-literacy populations in Sub-Saharan Africa and South/Southeast Asia, the same regions AfriSpeech, AI4Bharat, and Sunbird already target, giving a concrete subset in the tens of millions across the languages those orgs already catalog.
**Mechanism**: these speakers are excluded from voice-based AI tools today because no one tracks or systematically builds toward ASR/TTS coverage for their specific languages; a public scorecard plus a reusable collection protocol gives the coalition and independent builders a measurable target instead of an open-ended governance commitment, and lowers the cost for any single org to add voice coverage for one more oral-tradition language.
**Measure**: (1) number of languages moved from "zero voice coverage" to "research-grade" or "production-grade" ASR/TTS on the scorecard over a 12-month window; (2) word-error-rate/intelligibility scores for newly-added languages against a native-speaker-validated held-out test set; (3) whether the coalition's own published progress reports begin citing the scorecard's categories, a proxy for whether it becomes a real accountability mechanism.

## Why Now
The coalition's Sept/Oct 2026 formation and the Gates Foundation's $1B commitment create immediate funding and attention but no measurement mechanism yet — a scorecard built now rides that momentum before the effort either delivers or quietly stalls. AfriSpeech's Nov 2026 update and AI4Bharat's active Airavata work prove the component pieces (data collection, TTS training) already work at single-org scale; they're just not catalogued or benchmarked across orgs.

## Skill Angle
Trigger: a language-community org, researcher, or the coalition itself wants to know the current voice-AI readiness of a specific language before committing resources. Inputs: the language name/code and any existing audio/text resources. The skill searches the maintained scorecard and known tooling (AfroLID, AfriSpeech, AI4Bharat, Sunbird, published papers) to produce a written readiness assessment — what coverage exists, what's missing, and a recommended first data-collection step — as a one-time per-language audit, distinct from the project's maintained, continuously-updated scorecard and collection protocol.

## MVP Sketch
Pick 5 oral-tradition languages with partial coverage visible in the digest's sources (e.g. from AfriSpeech's 92-language list or a weak-voice-support Indic language adjacent to AI4Bharat's work), manually score their current ASR/TTS state against a simple 4-tier rubric (none/research/narrow-production/broad-production), publish as a static scorecard site, and draft the collection protocol as a one-page checklist validated by outreach to one named org (Masakhane, Sunbird, or AI4Bharat). 2-4 weeks, 1-2 people plus at least one native-speaker reviewer per language.

## Risks & Open Questions
- This sits adjacent to a $1B-funded, 60-signatory coalition effort — a small independent toolkit risks redundancy with (or being ignored by) whatever the coalition's workstreams eventually produce; mitigate by positioning as a measurement/accountability layer, not a competing builder.
- Audio data collection for oral-tradition languages raises real consent/ownership questions (whose voice, whose IP) that need deliberate handling, not an afterthought.
- Without buy-in from at least one named org (Masakhane, AI4Bharat, Sunbird), the scorecard has no distribution and risks becoming another unseen one-off.
- Strongest reason this might already be solved: the coalition's "governance and workstreams... over the coming year" could quietly include exactly this kind of scorecard internally — worth re-checking coalition progress reports before building rather than assuming nothing exists.
