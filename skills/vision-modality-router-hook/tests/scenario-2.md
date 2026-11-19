# Scenario 2 — Zendesk webhook integration, broken attachment plumbing (plumbing-bug trap), and a thin-evidence edge case

## Input a user would actually provide

**System prompt excerpt:**
> You are Acme Support AI. When a customer attaches an image, always call `view_attachment` before composing your response, so you never answer without having looked at what they sent.

**Vision tool definition:**
```json
{
  "name": "view_attachment",
  "description": "Retrieve and view an image attached to the current Zendesk ticket by its attachment URL.",
  "parameters": {
    "type": "object",
    "properties": { "attachment_url": { "type": "string" } },
    "required": ["attachment_url"]
  }
}
```

**Integration target:** Raw webhook pre-processor sitting in front of Zendesk's ticket-received webhook.

**Traces:**

1. User: "Here's a screenshot of the error I'm seeing." [image attached]. `view_attachment` CALLED. Tool result: `"https://z-cdn.zendesk.com/attachments/8841.png?token=exp"` (a bare URL string, not actual image content — because the attachment URL had already expired by the time the tool ran). Agent response: "I wasn't able to view the image — could you re-attach it?" — agent correctly notices it has no real content, asks user to resend.
2. User: "Attaching a photo of the damaged packaging for my return." [image attached]. `view_attachment` CALLED. Tool result: empty placeholder object `{}`. Agent response: "Thanks for the photo — I can see the packaging damage on the corner." (agent hallucinates seeing content it never actually received — a serious failure, but not a "model decided not to look" failure)

## What a correct skill run should produce

- This scenario only has 2 traces total, both with attachments, both already flagged as problems — this tests the skill's **step-3 plumbing check** and its **minimum-evidence guardrail** together.
- A correct run should notice: in *both* traces, `view_attachment` WAS called (so this is not an LLM-initiated-decision problem at all — the explicit "always call" instruction is working as written). The actual failure is the tool receiving a bare expired URL / empty placeholder instead of real image bytes — a data-plumbing/attachment-delivery bug, not an architecture-routing gap.
- Given only 2 traces, a correct run should flag that this is a thin sample — but since both traces already demonstrate the tool executes before the response (ruling out the "text model doesn't decide to call vision" problem this skill targets), it's reasonable to render a plumbing-bug verdict without demanding more traces, while still noting more traces would help confirm severity.
- **Verdict**: fix-the-plumbing-first — NOT "hook warranted." A run that recommends drafting a pre-reasoning routing hook here is a clear failure: the hook would sit on top of the same broken attachment delivery and solve nothing.
- The hallucination in trace 2 (agent claiming to see damage it never received) should be flagged explicitly as a separate, more serious failure mode worth raising even though it's outside this skill's main routing-hook scope.
- No LangChain/Assistants-API adapter should be drafted as the primary recommendation here — at most, a brief note that once attachment delivery is fixed (e.g., resolving URLs server-side before passing to the tool, or fetching bytes directly instead of passing a URL), the always-call instruction already in place is probably sufficient and a routing hook may not even be needed.

## Pass/fail criteria

- PASS if the output explicitly identifies that `view_attachment` was called in both traces (so this is not the LLM-decision-architecture gap the skill is designed to fix).
- PASS if the verdict is "fix the plumbing first," not "hook warranted."
- PASS if it explicitly flags the expired-URL and empty-placeholder patterns as the root cause, per the SKILL.md step-3 guardrail.
- PASS if it flags the trace-2 hallucination (claiming to see unreceived content) as a distinct, serious issue.
- FAIL if the skill drafts a Zendesk-webhook pre-reasoning routing hook as the primary fix without first calling out that the existing "always call" instruction is already working and the real bug is downstream.
- FAIL if it asserts specific Zendesk attachment-URL expiry timing (e.g., "Zendesk URLs expire in exactly 5 minutes") as fact rather than flagging that current platform docs should be checked.
