# Vetted Answer: A Safety-Evaluated Assistant and Advocate Review Aid for Tech-Facilitated-Abuse Questions

A survivor typing a question about stalkerware or a shared-account tracker into whatever chatbot happens to be open isn't a hypothetical — it's already the default. A USENIX Security 2026 paper (Prakash et al., arXiv 2602.17672) built its entire evaluation around that fact: "LLMs are already integrated into widely used online platforms where survivors seek support," and advocates are scarce enough that generic online tech-facilitated-abuse (TFA) information often has to stand in for one. The paper scored four LLMs against four axes — accuracy, completeness, safety, actionability — and treated the result as an open research question, not a settled one. Nobody has shipped the thing that would close it.

## The Gap

Two of the models Prakash et al. evaluated were already built specifically for intimate-partner-violence contexts — so purpose-built TFA models exist. What doesn't exist is an independently vetted one, evaluated on a fixed cadence against a real rubric, with the one failure mode that actually matters — a high-risk disclosure getting answered in-line instead of routed to a human — engineered out from the start.

The closest real attempts both fall short in instructive ways. Refuge (UK) runs a live chatbot, co-designed with a PhD researcher and tested directly with survivors, but it's scoped narrowly to device-securing guidance — not the general TFA Q&A survivors are actually bringing to whatever LLM they happen to have open. Chayn's "Little Window" chatbot ran a genuinely promising three-year survivor-tested pilot before its own team pulled it down in 2020 over safety and sustainability concerns — a direct, concrete precedent for how this category of tool can fail even with good intentions and real testing behind it. A GitHub search for "domestic violence chatbot safety assistant" turned up nothing. Narrow, discontinued, or evaluated-but-unvetted-at-scale is where every existing attempt stops.

## The Project

The centerpiece isn't a model — it's a vetting-and-escalation pipeline that sits between a question and an answer. A maintained, safety-reviewed knowledge base covers the questions survivors and advocates actually ask most: device-securing, account-separation, evidence-preservation, safety-planning around disclosure. Every answer the system gives is checked against that base rather than generated loose. Crisis-detection logic sits in front of it: a disclosure that reads as immediate danger or suicidal ideation gets routed to a human hotline handoff instead of an in-line answer — the exact failure mode an unvetted general LLM risks by trying to be helpful in the wrong moment.

The knowledge base is explicitly a living asset, not a one-time fine-tune: it's re-evaluated against the Prakash et al. accuracy/completeness/safety/actionability axes on a fixed cadence as new TFA tactics emerge, the same way the paper itself measured gaps rather than assuming a fixed answer set stays correct. A separate, advocate-facing surface lets a human reviewer get a fast second opinion on an AI-drafted answer before it ever reaches a survivor — distinct from, and a cheaper deployment path than, standing up the full always-on assistant.

## Tangible Impact

**Population**: survivors experiencing technology-facilitated abuse who need help outside advocate business hours or without advocate access, and the advocates who have to vet AI-drafted guidance before it reaches a client. This isn't a projected population — Prakash et al.'s own framing establishes it directly: survivors are already turning to platforms with embedded general LLMs specifically because advocates are scarce.

**Mechanism**: a safety-vetted knowledge layer, plus an advocate-facing review tool, raises accuracy/completeness/safety/actionability relative to an unvetted general-LLM answer — the exact four axes the cited paper measured as deficient — and gives advocates a fast second opinion instead of a binary choice between blocking AI assistance entirely or trusting it unreviewed.

**Measure**: (1) accuracy/completeness/safety/actionability scores against a baseline general-purpose LLM on the same TFA question set, replicating Prakash et al.'s own methodology directly; (2) advocate time-to-review an AI-drafted answer versus drafting one from scratch; (3) survivor-reported helpfulness and perceived safety, collected through a partner-agency pilot.

## Why Now

Before this paper, "safety-vetted" had no documented, academically grounded definition for this specific use case — nothing to build a knowledge base or test suite against. Prakash et al. hands over a citable eval methodology and a set of documented failure cases, which is what turns "build something safer" from a vibe into a testable target.

## Try It

A companion skill exists at `skills/tech-abuse-safety-vetted-assistant/`: *"Scores an AI-drafted or chatbot-generated answer to a technology-facilitated-abuse (TFA) question against a four-axis safety rubric (accuracy, completeness, safety, actionability), flags concrete gaps, and produces a revised answer — for an advocate doing a fast safety check before sending AI-assisted guidance to a survivor, or a platform auditing its own chatbot's TFA-adjacent responses."*

It's deliberately the smaller, cheaper half of this idea — a one-shot review aid, not the standing assistant service with live crisis-escalation routing described above. To use it: paste the skill's `README.md` into any AI chat tool along with the question and the candidate answer you want checked, or drop the whole `skills/tech-abuse-safety-vetted-assistant/` folder into `~/.claude/skills/` if you're using Claude Code.

The idea file is upfront about the two strongest reasons this might not be as open as it looks. First, Chayn's own team shutting down a three-year, survivor-tested pilot over sustainability concerns is a direct warning that a successful pilot alone doesn't make this viable — any real build needs a funding and maintenance plan before launch, not after. Second, the two IPV-specific models Prakash et al. cite could already cover a meaningful chunk of this if someone vetted them properly, which is worth a direct email to their maintainers before assuming greenfield. And however this gets built, the human-handoff path for a genuine emergency has to be unmissable — not a line of text buried behind a chat box a survivor might never scroll to.

---

Surfaced from `research/2026-11-13-applied-ai-underserved-domains-6th.md`, pattern `P4`.
