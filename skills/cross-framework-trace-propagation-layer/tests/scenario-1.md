# Scenario 1 — LangGraph orchestrator calling a CrewAI research crew, empty response returned

## Setup

A team runs a LangGraph orchestrator that, partway through a workflow, invokes a CrewAI
research crew to gather background facts before continuing. On one production run the
orchestrator's final answer came back with an empty "research findings" field. The team
exported traces separately from Phoenix (LangGraph side) and from CrewAI's built-in trace
log (CrewAI side) — there is no live propagation installed, so these are two disconnected
exports of the same request.

## Input handed to the skill

**One-line description**: "LangGraph orchestrator calls a CrewAI research crew mid-workflow
to gather background facts; the crew's output should feed into a `research_findings` field
on the next LangGraph node, but that field came back empty in the final answer."

**LangGraph export (Phoenix, JSON excerpt, timestamps UTC)**:
```
[
  {"span": "orchestrator.plan", "start": "2026-11-10T14:02:01.100Z", "end": "2026-11-10T14:02:01.900Z"},
  {"span": "orchestrator.invoke_crew", "start": "2026-11-10T14:02:01.910Z", "end": "2026-11-10T14:02:09.400Z",
   "input": {"topic": "Q3 regional sales anomalies", "deadline_minutes": 5}},
  {"span": "orchestrator.merge_findings", "start": "2026-11-10T14:02:09.410Z", "end": "2026-11-10T14:02:09.600Z",
   "input": {"research_findings": null}, "note": "received null, expected object"}
]
```

**CrewAI export (CrewAI trace log, JSON excerpt, timestamps UTC)**:
```
[
  {"span": "crew.kickoff", "start": "2026-11-10T14:02:02.000Z", "end": "2026-11-10T14:02:02.050Z",
   "input": {"topic": "Q3 regional sales anomalies", "deadline_minutes": 5}},
  {"span": "agent.researcher.task", "start": "2026-11-10T14:02:02.060Z", "end": "2026-11-10T14:02:08.900Z",
   "output": {"summary": "Found 3 anomalies in EMEA region Q3, largest -14% in retail channel."}},
  {"span": "crew.timeout_guard", "start": "2026-11-10T14:02:08.910Z", "end": "2026-11-10T14:02:08.950Z",
   "note": "task exceeded internal 5s soft deadline, result discarded per timeout policy, returning null"}
]
```

## Expected output / pass criteria

A passing run of the skill must:

1. Produce a merged timeline with all 6 spans in roughly correct chronological order
   across both files.
2. Find a **HIGH-confidence payload match** linking `orchestrator.invoke_crew`'s input
   (`topic`, `deadline_minutes`) to `crew.kickoff`'s input — same values, near-identical
   timestamps.
3. Correctly identify, from `crew.timeout_guard`'s note, that the researcher's result
   (`agent.researcher.task`'s output summary) was actually produced successfully but was
   discarded by CrewAI's own internal timeout policy before being returned to the caller —
   and surface this as the likely fault point, not a vague "something went wrong in the
   crew."
4. State the fault point as: the crew's soft deadline (5s per the orchestrator's own
   `deadline_minutes` input) was exceeded by the researcher task's actual duration
   (~6.8s), triggering `crew.timeout_guard` to discard a result that had, in fact, already
   been produced.
5. List this reasoning as grounded in payload/timestamp evidence actually present in the
   files, not fabricated.
6. Include a "Next step" line suggesting live propagation for this LangGraph↔CrewAI pair.
7. Not claim certainty beyond what the timeout_guard note and timestamps support — it's
   fine to state this fault point with high confidence since it's directly evidenced, but
   the report must still distinguish this from any lower-confidence inferences it makes
   elsewhere (there shouldn't be any other major inferences needed in this scenario since
   payload matches cover the whole chain).

**Fail** if the skill: misses the timeout_guard's explanatory note and instead guesses the
crew failed outright; fails to connect the 5s deadline passed in from the orchestrator to
the timeout threshold that fired; or produces a report without the required six sections.
