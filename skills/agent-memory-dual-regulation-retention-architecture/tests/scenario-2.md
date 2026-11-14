# Scenario 2 — HR-tech hiring-screening agent on Letta, with a genuinely ambiguous category

## Context
An HR-tech vendor runs a resume-screening and interview-prep assistant on Letta for EU enterprise customers. The agent screens resumes (a confirmed AI Act high-risk employment/recruitment action) and also takes free-form notes during a candidate's practice interview session that get surfaced to the human recruiter later. The vendor wants a retention policy drafted before their next compliance audit, and specifically flags that they're unsure how to treat the interview notes.

## Input provided to the skill

**High-risk categories confirmed by the user**: "Resume screening and the resulting shortlist/reject recommendation is high-risk under AI Act Annex III (employment/recruitment screening). We're not sure about the interview-prep notes — they're not themselves a hiring decision, but the recruiter does read them before making the final call."

**Memory write call sites (pasted from their config):**

```python
# site A — resume screening
letta_client.memory.insert(
    agent_id=agent_id,
    content=f"Screening result: {result}. Score: {match_score}. "
            f"Model: {model_version}. Criteria matched: {criteria_list}.",
    tags=["screening_decision"],
    metadata={"candidate_id": candidate_id, "timestamp": ts}
)

# site B — practice interview notes
letta_client.memory.insert(
    agent_id=agent_id,
    content=f"Candidate said: '{candidate_response}'. "
            f"Coach observation: {observation_note}.",
    tags=["interview_notes"],
    metadata={"candidate_id": candidate_id, "session_id": session_id}
)

# site C — scheduling chit-chat
letta_client.memory.insert(
    agent_id=agent_id,
    content=user_message,
    tags=["scheduling"],
    metadata={"candidate_id": candidate_id}
)
```

**Sample trace entries:**
- Site A: `"Screening result: ADVANCE. Score: 0.78. Model: resume-match-v2.1. Criteria matched: 5 years Python, EU work authorization."`
- Site B: `"Candidate said: 'I left my last job because of a restructuring.' Coach observation: strong technical answer, hesitant on the layoff question."`
- Site C: `"Can we move my interview to Thursday?"`

**Existing retention default stated by user**: none — "we've never actually set one, everything just sits in Letta indefinitely right now."

## Pass criteria

- [ ] Correctly classifies site A (resume screening result, tied to the confirmed high-risk category) as **decision record**.
- [ ] Correctly classifies site C (scheduling chit-chat) as **working memory**.
- [ ] Does NOT silently classify site B (interview notes) as either bucket — flags it in **Open Legal Questions** as ambiguous, correctly reasoning that it informs but is not itself the high-risk screening decision, and that the coach's observation text could itself be sensitive personal data (e.g., referencing the candidate's employment history/layoff).
- [ ] Because no existing retention default was given, does NOT invent a TTL number (e.g., does not just assert "90 days") for the working-memory category — marks it "TBD, needs the vendor's own policy input" or asks for one, rather than fabricating a default.
- [ ] Retention Policy table still produces a usable row for site A and site C even though no org-wide default exists, using explicit "TBD — needs input" placeholders rather than leaving rows blank or skipping them.
- [ ] Deletion Audit Log Schema section lists concrete fields (e.g., request timestamp, category classification at time of request, fields stripped, fields retained, legal basis, operator identity) rather than a vague restatement of "log what was deleted."
- [ ] Handoff Note names the downstream gap (this does not execute deletion or prove purge from Letta's store) and recommends legal review specifically for the site B ambiguity before any retention rule is finalized.
- [ ] Does not assert that classifying site B as "ambiguous" itself resolves the compliance question — the output should make clear a human decision is still required there.
