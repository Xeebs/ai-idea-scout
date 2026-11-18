# NavKit: A Shared Agent Scaffolding Toolkit for AI Care-Navigation Agents

In a single 30-day window, three separate teams built three separate AI agents to help patients navigate the same broken system — and none of them will ever reuse a line of each other's code. That's not a coincidence of timing. It's what happens when a problem is real enough that everyone keeps hitting it, but nobody has built the shared layer underneath it yet.

## The Gap

HemaVajra built an AI calling agent for health navigation. Neravu built a financial-assistance navigator for cancer patients. MedHaul won a $500,000 prize for AI-powered medical transport coordination. All three surfaced in the same hackathon repo, `karlmehta/code-for-a-billion`, within the same month — HemaVajra's calling agent (issue #140, 2026-11-14), Neravu's navigator (issue #78, 2026-11-09), and MedHaul's transport win reported separately on 2026-10-20. Each team solved one slice of the same underlying problem — calling, financial navigation, transport — completely independently, with no shared scaffolding between them.

This isn't a new observation nobody's tried to fix. An 18F eligibility-rules prototype attempted a shared layer back in 2018 and has been stale ever since. The DiMe Society has proposed a shared, evidence-based navigation framework — but no published code exists for it. What's left is a scattering of narrow, closed-source point products (Benefit Navigator for caseworkers, Eleos's Medicaid-coverage scanner) that solve adjacent problems without solving this one. The next team that wants to build a care-navigation agent still starts from zero, exactly like these three just did.

## The Project

NavKit is an open agent-scaffolding toolkit that provides the three reusable building blocks every care-navigation agent ends up hand-building anyway: a configurable eligibility-rules engine (load a program's published rules once, then query it against any patient profile), a calling-agent scaffold wired to a telephony API with a scripted-but-adaptive flow for the navigation calls that come up constantly — insurance verification, appointment scheduling, benefits inquiries — and a transport-coordination connector that books and tracks medical rides through existing ride-booking APIs. Tying all three together is a shared case-tracking data model, so a single patient's navigation history — eligibility checks run, calls made, rides booked — lives in one record instead of scattered across three disconnected tools.

The centerpiece isn't any one of these pieces individually — Twilio Voice and Uber Health already exist and are mature. The centerpiece is that nobody has wired them together into a toolkit a navigator program can actually adopt instead of commissioning a bespoke build, the way all three source projects just did.

## Tangible Impact

**Population**: Low-income and uninsured patients who need active help navigating health-system bureaucracy — cancer patients specifically (Neravu's target) and more broadly the roughly 25 million uninsured and the much larger Medicaid-eligible-but-under-enrolled U.S. population (KFF estimates) who rely on hospital or nonprofit patient-navigator programs that are themselves understaffed and under-resourced; and, directly, the small nonprofit/hospital tech teams who would otherwise build a bespoke calling, financial-navigation, or transport-coordination agent from zero, as HemaVajra, Neravu, and MedHaul each just did.

**Mechanism**: A navigator program today either hires more human navigators — expensive, hard to scale — or a tech-capable team builds a narrow bespoke agent per task, with no reuse across teams, as the three hackathon examples just demonstrated. A shared scaffold lets a navigator program assemble a working calling + eligibility + transport agent in weeks using existing building blocks, multiplying how many patients a fixed navigator-hour budget can reach — and lets the next hackathon team start from working infrastructure instead of from zero.

**Measure**: (1) patients navigated per navigator-hour before and after toolkit adoption — the capacity multiplier; (2) missed-appointment / no-show rate for patients using toolkit-coordinated transport versus the program's prior baseline; (3) time-to-deploy a new navigation agent for a new assistance program — toolkit-enabled weeks versus the multi-month hackathon-to-pilot timeline each of the three source projects implicitly took.

## Why Now

Twilio Voice and Uber Health/Lyft Pass are both mature, already-adopted APIs purpose-built for exactly the calling and medical-transport legs this gap needs — the infrastructure underneath is no longer the hard part. And three independent teams building the same three slices within one 30-day window is a direct signal that demand for the integrated version exists right now, before a fourth team builds yet another one-off agent nobody else can reuse.

## Try It

A companion skill, [`care-navigation-agent-toolkit`](../skills/care-navigation-agent-toolkit/), handles the one piece of this that can't yet be automated via a connector: *"Drafts a structured, cited eligibility-rules configuration from a benefits/assistance program's published policy document, flagging every ambiguous or missing criterion for a human navigator to resolve before the ruleset goes live."*

A navigator or program coordinator hands it a program's published eligibility policy — pasted PDF text, a copied webpage section, a manual excerpt — and gets back a structured ruleset ready to configure into the toolkit's eligibility engine, with every ambiguous or missing criterion flagged for human sign-off before it ever touches a real patient. To use it: paste the README into any AI chat tool, or drop the `care-navigation-agent-toolkit/` folder into `~/.claude/skills/` for Claude Code.

It is explicitly *not* for determining any individual patient's real eligibility, placing calls, or booking transport — it only prepares the input the toolkit needs; a human stays in the loop on every ruleset before go-live.

## Risks & Open Questions

Financial-assistance eligibility rules vary by state, program, and change frequently — a stale or misconfigured ruleset giving a patient wrong eligibility information is a real harm risk that needs an explicit human-review gate before any live deployment, not just an MVP convenience. Calling agents interacting with insurers or providers on a patient's behalf raise real consent and liability questions — is the agent actually authorized to act for this patient — that need a clear legal answer before broad adoption, not just technical plumbing. MedHaul's $500k prize may already be funding it toward a more general platform that overlaps this scope, which is worth checking directly before building a competing scaffold from zero. And toolkit adoption ultimately requires navigator programs to trust an agent with real patient interactions; a pilot's results need to be genuinely convincing, not just technically functional, before a second program will adopt it.

---

Surfaced from `research/2026-11-17-applied-ai-for-underserved-domains.md`, pattern `P5`.
