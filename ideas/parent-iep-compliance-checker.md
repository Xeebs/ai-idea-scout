# IEP Watch: A Parent-Facing, State-Specific IDEA Compliance Checker

- **Status**: PROPOSED
- **Date**: 2026-11-13
- **Topic**: Applied AI for underserved domains
- **Source**: research/2026-11-13-applied-ai-underserved-domains-5th.md · P6
- **Maturity verdict**: PARTIAL — vendor tools (MagicSchool, Gemini EDU/Copilot workflows, OpenEduCat) are all teacher-facing goal generators, and the one explicit compliance caveat found tells the teacher to check their own output, not an independent party to check the school's. One real parent-facing implementation exists (SENTINEL·IEP, transcribing meetings and flagging IDEA/FAPE/FERPA conflicts) but it's indie/demo-scale (free Cloudflare Pages hosting), explicitly defers to attorneys on actual violations, has unverified "multi-AI" accuracy claims, and checks against federal IDEA only, not state-specific requirements.
- **Format**: BOTH
- **Data Sources**: MANUAL — the parent uploads/pastes the actual IEP document (or a transcript/notes from the IEP meeting) their school produced. No public API exposes a specific student's IEP (FERPA-protected, school-controlled), so a CONNECTED version isn't viable — the document the parent already has in hand is the only available input.

## The Gap

Every AI special-education tool found assumes the school-side professional is the user, drafting goals and accommodations for a teacher to review against their own state's rules. The parent — who has the least IDEA-compliance expertise and the most at stake — has no equivalent tool to check whether what the school produced actually meets the legal bar. SENTINEL·IEP is a genuine attempt at the parent-facing version but is demo-scale, federal-only, and meeting-transcription-focused rather than document-review-focused.

## The Project

A parent uploads their child's actual IEP document (PDF or pasted text) along with their state. The tool checks it against that state's specific IDEA implementation requirements (present-levels documentation, measurable-goal standards, least-restrictive-environment justification, procedural-safeguards notice timing) — not just federal IDEA in the abstract — and produces a flagged list of likely compliance gaps in plain language, each tied to the specific IDEA/state provision it may violate. For each flag, it drafts a short, specific written request the parent can send the school (e.g., "request measurable baseline data for goal #3") rather than a vague complaint. A running history lets a parent track a child's IEP across school years and compare versions for regressions.

## Tangible Impact

**Population**: Parents of the roughly 7.3 million US students served under IDEA (National Center for Education Statistics), the large majority of whom have no special-education attorney or paid advocate and must evaluate a document written by school professionals in specialized compliance language they were never trained to read.

**Mechanism**: Translating a document the parent already has into specific, state-grounded compliance flags and ready-to-send requests closes the information-asymmetry gap between the school (which has IDEA-compliance training) and the parent (who doesn't), making it realistically possible for a parent without a paid advocate to catch and act on a compliance gap before it becomes a due-process dispute.

**Measure**: (1) number of flagged gaps a parent actually sends to the school as a written request, and the school's response rate/outcome; (2) time from receiving an IEP to identifying a specific actionable gap, vs. self-reported baseline (often "didn't know where to start"); (3) rate of flags independently confirmed as valid by a special-education advocate reviewing a sample, as an accuracy check.

## Why Now

Document-understanding and state-specific regulatory-rule retrieval are both mature, cheap LLM-application techniques today; the only new ingredient this needs over SENTINEL·IEP's existing attempt is curating actual state-by-state IDEA implementation rules into a structured rule pack, which is tedious but not technically novel.

## Skill Angle

An "IEP Compliance Flag & Letter Drafter" skill: the parent pastes their child's IEP document text and names their state; the skill flags likely compliance gaps against that state's IDEA requirements and drafts a specific written request per flag. This is the single-document judgment task; the full project additionally tracks a child's IEP history across multiple school years to catch regressions over time, which needs persistent per-child storage the skill doesn't carry.

## MVP Sketch

Scope to 2-3 states with well-documented IDEA implementation guidance (e.g., California, Texas, New York) and build a manually curated rule pack per state. Stack: document upload + LLM compliance-check prompt grounded in the state rule pack, output as a flagged checklist with drafted request letters. Single experiment: partner with a parent-advocacy nonprofit (e.g., a state Parent Training and Information Center, which IDEA itself funds in every state) to have 15-20 parents run a real IEP through the tool and have an advocate independently review the flags for accuracy.

## Risks & Open Questions

- SENTINEL·IEP's own disclaimer (it doesn't determine actual legal violations) applies equally here — the product must stay framed as "things to ask about," never "legal determinations," to avoid both liability and false parent confidence.
- State-by-state rule curation is the real bottleneck and doesn't shrink with scale the way the underlying LLM logic does; starting narrow and partnering with a state PTI center for rule-accuracy review is close to mandatory.
- A false-negative (missing a real compliance gap) could give a parent false reassurance about an IEP that's actually inadequate — accuracy validation against real advocate review before any public launch is non-negotiable.
- SENTINEL·IEP or a similar indie project could extend to state-specific document review first, closing this gap faster than a new entrant — worth checking its actual roadmap/activity before committing to build from scratch versus contributing to or forking it.
