# Clear Signal: A Self-Service Smart-Device and Cloud-Account Abuse Auditor for DV Survivors

A smartwatch gets handed back after a breakup. The relationship is over, the physical object is gone — but the cloud account it was ever linked to keeps quietly reporting a location anyway. That's a real, documented case. The safety advice survivors actually get for this entire category of risk, across most agencies, still stops at one line: turn off phone location tracking. Everything past that line — smart-home co-owner access, a legacy shared Apple ID, a location-sharing app member list that still includes an ex — is left to a manual checklist and whatever a stretched advocate happens to know.

## The Gap

Refuge (UK) has reported a "significant rise" in abuse cases misusing wearables and AI, and the smartwatch case above is one of theirs — a device that kept surveilling its former owner through a linked cloud account well after it was physically recovered. That's not a one-off: a 2026 SSWR conference study found that within most agencies, the *only* explicit tech-safety strategy taught to clients is disabling phone location tracking, and advocates themselves self-reported feeling undereducated on tech-related safety planning more broadly. The same study's own proposed fix — a "Technology Abuse Clinic" — is a staffing model: get cybersecurity experts on-call for advocates to consult. It's not a tool, and it doesn't exist yet as anything survivors can use directly.

The research behind this idea went looking for something closer to a self-service version and came up short in an informative way. GitHub turns up a cluster of stalkerware scanners — GetByeBye, selfguard, Zero, StealthDetect, and others — but every one of them scans a single phone for spyware apps. None of them look at cross-account linkage, smart-home co-owner lists, or a wearable's cloud tail after the device itself is gone. The closest real matches to what's actually needed are explicitly human-run: a paid forensic audit service, the Salvation Army's advocate-staffed remote tech health check, a manual worksheet from eSafety.gov.au. No automated tool audits a survivor's own linked devices and accounts for what an abuser can still see.

## The Project

The design here deliberately avoids the thing that would make it dangerous: it never asks for a password. A survivor, or an advocate working alongside them, uploads screenshots of account-security and device-sharing settings pages they're already logged into on their own terms — Google Security Checkup, Apple ID's device list, Find My or Life360's member lists, a smart-home app's co-owner screen, shared calendar or photo-album permissions. The tool pattern-matches those screenshots against a maintained database of known abuser tactics by platform and produces a prioritized report: what to revoke, in what order, and why.

The ordering matters as much as the detection. Not every revoke is safe to do immediately — pulling someone off a shared photo album is usually silent, but removing smart-lock access is often instantly obvious to the other party. A report that flags a risk without flagging its detectability could put someone in more danger than the checklist it's replacing. That's the actual hard part of this project: not the pattern-matching, but keeping the tactics database current as platforms change their settings UIs constantly, and never letting the tool imply a clean result is a guarantee rather than a point-in-time snapshot.

## Tangible Impact

**Population**: domestic violence survivors in the immediate post-separation period whose former partner retains or retained shared access to smart devices or cloud accounts. CDC estimates roughly 41 million US women and 26 million US men have experienced contact sexual violence, physical violence, and/or stalking by an intimate partner in their lifetime; NNEDV's Safety Net surveys report a majority of advocates' clients disclose tech-facilitated stalking specifically.

**Mechanism**: surfaces abuser-linked access points in minutes that a manual advocate checklist — which the SSWR study found stops at "turn off phone location" — would miss, closing the specific cross-account/smart-home blind spot the study's advocates admitted they aren't trained to check.

**Measure**: (1) number of abuser-linked access points found per audit vs. the baseline manual-checklist detection rate (measurable via a side-by-side pilot with a partner DV agency); (2) time to complete an audit (minutes, vs. advocates' self-reported ad hoc/undereducated process); (3) survivor-reported reduction in unexplained "they always know where I am" incidents after remediation, tracked at 30/90 days.

## Try It

A companion skill exists at `skills/survivor-account-device-abuse-auditor/`: *"Reviews screenshots of account-security and device-sharing settings pages (Google, Apple, smart-home apps, location-sharing apps) to flag leftover ex-partner access points, in priority order, for a domestic violence survivor or the advocate helping them. Use when someone hands over settings screenshots and asks 'what here can my ex still see/control' rather than asking for general digital-safety advice."*

To use it: paste the skill's `README.md` into any AI chat tool along with the settings screenshots you want reviewed, or drop the whole `skills/survivor-account-device-abuse-auditor/` folder into `~/.claude/skills/` if you're using Claude Code. It opens with a fixed safety banner every single time — reviewing this on a device the other person could see, or acting on a flagged item without planning for its detectability, can itself create risk — and it will never accept a password, login link, or OAuth connection from you; it only ever reads what you choose to show it in a screenshot.

The idea file is honest about where this could already exist without anyone outside finding it: an advocacy org could have an unpublished internal version of this checklist already, which is worth direct outreach before assuming the field is empty. It's also explicit that a pattern-match audit is a floor, not a guarantee — it can only catch tactics already in its database, and platform settings pages change often enough that the database needs real, ongoing maintenance or it quietly goes stale and gives false reassurance.

---

Surfaced from `research/2026-11-13-applied-ai-underserved-domains-6th.md`, pattern `P3`.
