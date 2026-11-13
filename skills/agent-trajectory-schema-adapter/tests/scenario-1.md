# Scenario 1 — Single framework mapping (LangGraph export)

## Setup
A platform engineer at a mid-size SaaS company is evaluating whether to adopt a shared trajectory schema before building an internal trace viewer. They have one representative LangGraph run export (a customer-support triage agent that classifies a ticket and calls a lookup tool), redacted of customer data. They state the framework name.

## Input to the skill

> My trace export is from: LangGraph
>
> ```json
> {
>   "thread_id": "th_8f2a1c",
>   "checkpoint_id": "ckpt_003",
>   "created_at": "2026-11-10T14:02:11Z",
>   "messages": [
>     {
>       "id": "msg_1",
>       "type": "human",
>       "content": "Customer ticket #4821: 'My invoice shows double charge'",
>       "created_at": "2026-11-10T14:02:11Z"
>     },
>     {
>       "id": "msg_2",
>       "type": "ai",
>       "content": "Classifying as billing_dispute. Looking up invoice.",
>       "created_at": "2026-11-10T14:02:12Z",
>       "tool_calls": [
>         {
>           "id": "call_1",
>           "name": "lookup_invoice",
>           "args": { "ticket_id": "4821" }
>         }
>       ],
>       "response_metadata": {
>         "model_name": "gpt-4.1",
>         "token_usage": { "prompt_tokens": 412, "completion_tokens": 38 }
>       }
>     },
>     {
>       "id": "msg_3",
>       "type": "tool",
>       "tool_call_id": "call_1",
>       "name": "lookup_invoice",
>       "content": "{\"invoice_id\": \"INV-9931\", \"charges\": 2, \"amount_each\": 49.00}",
>       "created_at": "2026-11-10T14:02:13Z"
>     },
>     {
>       "id": "msg_4",
>       "type": "ai",
>       "content": "Confirmed duplicate charge on INV-9931. Routing to refunds queue.",
>       "created_at": "2026-11-10T14:02:14Z",
>       "response_metadata": {
>         "model_name": "gpt-4.1",
>         "token_usage": { "prompt_tokens": 480, "completion_tokens": 22 }
>       }
>     }
>   ]
> }
> ```

## Pass criteria
- [ ] Correctly fingerprints/confirms the export as LangGraph (channel-update/`messages` structure with `tool_calls`, `response_metadata.token_usage`).
- [ ] Mapping table includes, at minimum: `messages[].type` → `node_type`, `messages[].tool_calls[].name` → `tool_name`, `messages[].tool_calls[].args` → `tool_args`, `messages[].content` (on the `tool` message) → `tool_result` or `output`, `response_metadata.token_usage.{prompt_tokens,completion_tokens}` → `token_usage.*`, `response_metadata.model_name` → `model`.
- [ ] Every field actually present in the sample (`thread_id`, `checkpoint_id`, `created_at`, each `messages[]` entry's fields) appears somewhere in the table as Direct/Derived/Lossy/No equivalent — none silently dropped.
- [ ] Correctly flags that `streaming_events[]` cannot be populated from this sample (it's a post-hoc message list, not a streaming export) and states why.
- [ ] Correctly notes `lineage_refs[]` has no direct source in this sample beyond the `tool_call_id` linkage already captured as parent-child, or flags it as derivable/absent — does not fabricate a lineage graph not evidenced by the data.
- [ ] Recommended minimal subset includes node sequence, tool name/args/result, and parent-child linkage (via `tool_call_id` ↔ `id`) — not token usage or streaming, which are secondary.
- [ ] Does not claim OTel GenAI semconv or ATIF v2.0 compliance anywhere in the output.
- [ ] Does not generate adapter/importer source code.
- [ ] Output follows the structure: Framework Fingerprint / Field Mapping / Normalized Fields This Sample Cannot Populate / Recommended Minimal Subset / Caveats.

## Fail conditions
- Mapping table omits any field actually present in the sample (e.g. drops `checkpoint_id` or `thread_id` entirely instead of noting them as No equivalent/mapped to `trajectory_id`).
- Claims standards compliance for the mapped schema.
- Produces working adapter code instead of (or in addition to, unprompted) a mapping document.
- Invents a field not present in the sample (e.g. a `handoff` or `agent_invocation` node type not evidenced anywhere in this LangGraph message list).
