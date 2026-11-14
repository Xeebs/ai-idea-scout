# Scenario 1 — Live production symptom: enterprise software support agent

## Context
A mid-size SaaS company (project management tool) has shipped a voice+vision support agent: a customer shares their screen and talks through a problem while the agent watches and gives step-by-step guidance. The team is seeing a specific complaint pattern in support tickets and wants a design fix before their next sprint.

## Input the user provides

> We built a voice support agent using LiveKit Agents. Customers screen-share their project dashboard and talk through issues while the agent watches and tells them where to click. Here's our architecture:
>
> 1. Typical session length: median is about 3 minutes, but the longest 10% of calls run 6-8 minutes (complex permission/workflow issues).
> 2. What it watches: our web app's dashboard — a multi-step UI workflow (customer navigates through settings menus, modals, and forms while following instructions).
> 3. Visual change frequency: pretty high — customers are clicking through screens roughly every 5-10 seconds during active troubleshooting.
> 4. Underlying model: GPT-4o realtime, no specific session-length caveats that we know of.
> 5. Latency budget: our voice turns need to stay under 1 second end-to-end, we have maybe 150-200ms of slack to spend on anything extra.
> 6. Known symptoms: yes — we've logged at least a dozen tickets where the agent tells the customer to "click the Export button in the top right" when the customer has already navigated to a different screen, or describes a modal that's already been closed. This seems to happen more on the longer calls.

Give me the structured brief.

## Pass criteria

- [ ] Output restates all six inputs and does not silently invent or omit any of them.
- [ ] Risk profile explicitly reasons about the ~30-second reference point against this agent's actual session lengths (3 min median, up to 6-8 min) and correctly characterizes this as HIGH risk given both long sessions and high change frequency (5-10s).
- [ ] Risk profile explicitly flags the ~30-second figure as one practitioner's observation, not a universal constant.
- [ ] Recommended cadence gives both a concrete fixed-timer fallback (a specific number of seconds, reasonable range ~15-25s given the stated high change frequency) AND an adaptive rule tied to detected UI change.
- [ ] Recommended anchor payload reasons against the stated ~150-200ms latency slack — should favor a lightweight diff/summary over a full frame re-sample for most anchors given the tight budget, or explicitly explain why a full re-sample is still viable within that budget.
- [ ] Cost/latency tradeoff section names the tension between the user's reported symptom (stale element references) and the tight latency slack in plain language, without hand-waving.
- [ ] Evaluation plan references using the team's own existing ticket examples (or new recordings of similar sessions) as validation data, not a generic suggestion disconnected from the scenario.
- [ ] Caveats section explicitly tells the user not to treat the brief as final without their own measurement.
- [ ] Does NOT claim to read the user's live screen share or LiveKit session — correctly frames itself as working only from the text description provided.

## Fail conditions
- Recommends a single generic cadence (e.g., "just re-anchor every 30 seconds") without reasoning against the stated change frequency and latency budget.
- Fails to connect the described symptom (stale click targets) back to the high-change-frequency UI workflow context.
- Omits the caveat about the 30-second figure's evidentiary status.
- Implies it can directly access or monitor the customer's LiveKit session.
