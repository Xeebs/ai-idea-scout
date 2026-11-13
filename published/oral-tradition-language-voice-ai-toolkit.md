# Oral Access: A Voice-Readiness Toolkit and Scorecard for Oral-Tradition, Low-Resource Languages

A $1B coalition of frontier AI labs, NGOs, and the Gates Foundation just promised to bring AI to 3.4 billion speakers of underrepresented languages. Nobody has promised to measure whether it actually happens — and for the languages that matter most here, text progress won't tell you anything, because the thing that's missing isn't a chatbot. It's a voice.

## The Gap

In September 2026, a roughly 60-signatory coalition — Anthropic and other frontier AI labs alongside Masakhane, Lelapa AI, AI4Bharat, Karya, and Sunbird — announced a five-year effort to bring AI to 3.4 billion speakers of underrepresented languages, backed by a $1B/2-year Gates Foundation commitment. It's a serious list of names and a serious number. It's also, by the coalition's own account, not yet a plan: its own announcement states that "governance and workstreams are still being developed... over the coming year." That's an admission that there is nothing to hold accountable yet, only an intention.

Meanwhile, Stanford HAI and UNDP have been specific about where current models actually fall short for the 1.2 billion native speakers of low-resource languages they cite — and it isn't just translation quality. Voice support, they note, is "also limited for communities with strong oral traditions." That's a distinct, narrower technical problem from the general low-resource-language quality gap everyone already talks about: languages that never developed (or don't primarily use) a standardized writing system can't be served by a pipeline built around aligned text transcripts, no matter how good the underlying model gets. Real tooling already exists in this space — AfroLID, AfriSpeech's ASR/TTS catalog spanning 92 African languages, Masakhane's AfriQA, AI4Bharat's Airavata — but each one is narrow: single-modality, single-region, research-grade. None of it closes the specific ASR+TTS pairing gap for oral-tradition communities, and none of it is tracking whether the coalition's billion-dollar commitment is actually converting into shipped voice coverage versus staying a governance document.

## The Project

Oral Access is an open benchmark and data-pipeline toolkit built specifically around ASR and TTS — not text models — for languages with no standardized writing system or a strong oral tradition. It does three things. First, it catalogs which of the coalition's target languages have zero, research-grade, or production-grade voice coverage today, extending the audit approach AfriSpeech already runs for its own 92-language catalog outward into AI4Bharat's and Sunbird's territory, so the picture spans orgs instead of staying siloed inside each one's own dashboard. Second, it packages a reusable, community-sourced voice-data collection protocol that doesn't assume a written standard exists — because for this population, a text-transcript-first pipeline is the wrong starting point entirely. Third, and this is the part that makes it more than a tooling exercise: it publishes a running "voice-readiness scorecard" that tracks, over time, whether the coalition's stated commitments actually turn into shipped ASR/TTS coverage — functioning as an independent accountability layer sitting on top of a very well-funded, very new effort that currently has no external measurement attached to it at all.

The centerpiece isn't a model. It's the scorecard and the protocol that make "voice support is limited" into something you can watch change — or watch fail to change — language by language, month by month.

## Tangible Impact

**Population**: the ~1.2 billion native speakers of low-resource languages Stanford HAI/UNDP cite, narrowed to communities with strong oral traditions and limited written-language infrastructure — disproportionately rural, often lower-literacy populations in Sub-Saharan Africa and South/Southeast Asia, the same regions AfriSpeech, AI4Bharat, and Sunbird already target, giving a concrete subset in the tens of millions across the languages those orgs already catalog.

**Mechanism**: these speakers are excluded from voice-based AI tools today because no one tracks or systematically builds toward ASR/TTS coverage for their specific languages; a public scorecard plus a reusable collection protocol gives the coalition and independent builders a measurable target instead of an open-ended governance commitment, and lowers the cost for any single org to add voice coverage for one more oral-tradition language.

**Measure**: (1) number of languages moved from "zero voice coverage" to "research-grade" or "production-grade" ASR/TTS on the scorecard over a 12-month window; (2) word-error-rate/intelligibility scores for newly-added languages against a native-speaker-validated held-out test set; (3) whether the coalition's own published progress reports begin citing the scorecard's categories, a proxy for whether it becomes a real accountability mechanism.

## Try It

A companion Claude Code skill is available at [`skills/oral-tradition-language-voice-ai-toolkit/`](../skills/oral-tradition-language-voice-ai-toolkit/). Its one-line job, per its own `SKILL.md`: "Produces a sourced voice-AI (ASR/TTS) readiness audit for one specific oral-tradition or low-resource language, with a 4-tier score, named evidence, and a recommended first data-collection step." It's meant for the moment a language-community org, researcher, or grant officer needs a documented answer — before committing funding or starting a data-collection effort — to "what's the real voice-AI state of this one language, and what should happen next?"

This is a one-time, per-language audit, not the maintained cross-language scorecard the fuller project would publish — but it's the part you can use today. To try it: paste the contents of the skill's `README.md` into any AI chat tool along with the language details you have (name, region, any known resources), or drop the `skills/oral-tradition-language-voice-ai-toolkit/` folder into `~/.claude/skills/` if you're running Claude Code.

## Risks worth sitting with

This project is deliberately shaped to sit beside a $1B-funded, 60-signatory coalition rather than compete with it — and that's the biggest risk, not a side note. A small independent toolkit built now could end up redundant with whatever the coalition's own workstreams eventually produce, or simply get ignored by an effort with vastly more funding and institutional weight. Worth saying plainly: the coalition's own "governance and workstreams... over the coming year" language could already include exactly this kind of internal scorecard — which means the right first move isn't to start building, it's to check the coalition's own progress reports before assuming the gap is actually open. There are also real consent and ownership questions in collecting oral-tradition voice data — whose voice, whose IP — that need deliberate handling from day one, not a retrofit. And without buy-in from at least one named org already working this territory (Masakhane, AI4Bharat, Sunbird), a scorecard has no distribution and risks becoming exactly the kind of unseen one-off it's trying to prevent everyone else from producing.

---

Surfaced from `research/2026-11-12-applied-ai-for-underserved-domains.md`, pattern `P7`.
