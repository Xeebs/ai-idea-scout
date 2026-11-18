# Dialect Commons: A Reusable Toolkit for Community-Sourced Dialect and Colloquial-Speech Data Collection

Of the world's 7,000-plus living languages, the Gates Foundation counts more than 6,000 as "digitally disadvantaged" — invisible to voice AI because nobody has collected the speech data to train on. Two efforts have cracked the problem at real scale: Masakhane built a community-sourced data pipeline across roughly 50 African languages, and Lesan AI built bespoke tooling to capture Tigrinya speech that "you cannot find online, including colloquial speech and dialects." Both prove the approach works. Neither left behind something the next community could pick up and run themselves.

## The Gap

Masakhane and Lesan each solved the same underlying problem — how do you capture spontaneous, dialectal speech that was never written down, with a community of native speakers doing the collecting and the checking — but each solved it from scratch, as a custom, grant-funded, multi-year organizing effort. That leaves the other thousands of under-resourced languages and dialects with no shared tool to copy, only two existence proofs to admire from a distance.

The obvious candidate for "just reuse this" is Mozilla Common Voice — mature, widely adopted, actively maintained. But Common Voice is built for scripted, read-aloud sentence collection for ASR training. It was never designed to capture the kind of free, spontaneous, colloquial speech that defines a dialect — which is precisely the gap Lesan AI had to build custom infrastructure to close. A search for anything generalizing Masakhane's or Lesan's approach into a reusable platform turned up nothing: no GitHub repo, no shipped product, no paper. The closer-but-still-not-it options are thin, too: SANTLR is a 2019 academic toolkit that's gone stale, and a 2025 Interspeech "Akan impaired-speech cookbook" is real but scoped to a single language.

## The Project

Dialect Commons is a self-hostable data-collection platform purpose-built for spontaneous, colloquial, dialect speech — not scripted ASR sentences. Contributors answer open-ended elicitation prompts (describe your day, explain a local recipe, answer a question a community member submitted) as voice notes sent through WhatsApp or Telegram, the channels they're already using rather than a dedicated app they'd have to install. A general-purpose ASR model produces a draft transcript, which then routes to community moderators — native speakers — who correct it, tag dialect and region, and confirm consent before anything enters the dataset.

The part that actually replaces Masakhane's and Lesan's months of bespoke engineering is a lightweight admin console: a language-community organizer sets up prompts, consent language, and moderator roles and launches a real, moderated collection campaign in hours instead of building infrastructure from nothing. The project is explicit that the ASR step is a draft, not the deliverable — for genuinely under-resourced languages there's often no decent model to transcribe from yet, so the native-speaker moderation step is where the actual value sits. This is a moderated collection tool, not an automated one, and it says so.

## Tangible Impact

**Population**: Grassroots language-preservation groups, diaspora community organizations, and small NLP researcher collectives working on the thousands of dialects and under-resourced languages outside the ~50 Masakhane covers and the single Tigrinya effort Lesan built for — the Gates Foundation's own estimate puts this at over 6,000 languages with no comparable data-collection infrastructure today.

**Mechanism**: Today, a community wanting to bootstrap voice AI for its own dialect must either repeat Masakhane's multi-year, grant-funded organizing effort or Lesan's custom engineering build from nothing. A ready-to-deploy, WhatsApp-native collection toolkit removes that build cost, so a community group with no engineering capacity can launch a real moderated collection campaign directly.

**Measure**: (1) time from "we want to start collecting" to first 100 validated audio clips for a new community (toolkit-enabled vs. Masakhane/Lesan's reported multi-month organizing timelines); (2) hours of native-speaker-validated spontaneous/dialect speech collected per community per month; (3) number of distinct language/dialect communities onboarded within the first year, as a direct test of whether the "thousands of communities with no toolkit" gap is real demand or just discussion.

## Try It

A companion skill exists at `skills/dialect-speech-community-data-collection-toolkit/` — it drafts the three launch artifacts a community organizer needs before starting a spontaneous/colloquial speech data-collection campaign for an under-resourced language or dialect: a consent & IP disclosure script, an open-ended elicitation prompt set tuned to surface colloquial speech, and a native-speaker moderator review rubric. Use before launching any such campaign, not after.

To use it: paste the contents of its `README.md` into any AI chat tool (ChatGPT, Claude, etc.) and give it your language/dialect, region, intended use of the data, who's organizing, and your collection channel. If you use Claude Code, drop the whole `dialect-speech-community-data-collection-toolkit/` folder into `~/.claude/skills/` instead and it'll be available automatically.

The skill is explicitly a pre-launch drafting aid, not a legal clearance or a replacement for the platform itself — it will not claim its draft consent script is legally sufficient, and it will flag the gap plainly if you don't give it the legal/governance context it needs to do better.

## Risks & Open Questions

- Consent and IP ownership for recorded speech is legally and culturally sensitive per community; a one-size-fits-all consent flow will not work everywhere and needs local legal input before any real launch, not just a generic ToS.
- Moderator recruitment — native speakers willing to review and tag submissions — may be the actual bottleneck, not the collection technology itself, and that needs validating directly with a pilot community before building more collection features.
- Masakhane's own tooling, or a similar effort, may already be generalizing internally in ways invisible to public search; a direct outreach check before building a parallel platform is warranted.
- Draft-ASR quality for genuinely under-resourced languages will be poor at launch, since there's often no model to transcribe from yet — the moderator-correction step, not the ASR step, is the real value here, and the project needs to stay honest about that.

Surfaced from `research/2026-11-17-applied-ai-for-underserved-domains.md`, pattern `P2`.
