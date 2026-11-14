# Scenario 2 — Support-ticket CRM bundle, manual-paste manifest, no live server

## Input given to the skill

User note: "We don't have a live MCP connection set up yet in this chat — here's our tool manifest as JSON, pasted from our server's source code (it matches what `tools/list` would return). Domain: this is a support-ticket CRM bundle our AI agent uses to handle customer tickets."

Tool manifest:

```json
[
  {"name": "list_contacts", "description": "List contacts matching a search query.", "inputSchema": {"query": "string"}},
  {"name": "get_contact", "description": "Fetch full details for one contact.", "inputSchema": {"contact_id": "string"}},
  {"name": "create_ticket", "description": "Open a new support ticket for a contact.", "inputSchema": {"contact_id": "string", "subject": "string"}},
  {"name": "update_ticket_status", "description": "Change a ticket's status, e.g. open, pending, resolved.", "inputSchema": {"ticket_id": "string", "status": "string"}},
  {"name": "close_ticket", "description": "Permanently close a ticket. No further updates allowed after this.", "inputSchema": {"ticket_id": "string"}},
  {"name": "send_email", "description": "Send an email to a contact.", "inputSchema": {"contact_id": "string", "subject": "string", "body": "string"}},
  {"name": "delete_contact", "description": "Permanently remove a contact and all associated data.", "inputSchema": {"contact_id": "string"}},
  {"name": "merge_contacts", "description": "Merge two duplicate contact records into one, keeping the newer contact_id.", "inputSchema": {"primary_contact_id": "string", "duplicate_contact_id": "string"}}
]
```

No live connection — this is the manual-fallback path. No custom assertion names given.

## Pass criteria

The output must:
1. Open by acknowledging this is the manual/pasted-manifest path (or at minimum not claim it ran a live `tools/list` call) — consistent with the Connected-primary/Manual-fallback Data Sources framing.
2. Include a **Required-Precondition** scenario: `create_ticket` before `update_ticket_status` or `close_ticket` (a ticket must exist before its status changes), citing the shared `ticket_id` field across tools as schema-linked evidence.
3. Include a **Near-Miss Distractor** scenario pairing `update_ticket_status` (set to "resolved") against `close_ticket` — these two are the clearest distractor pair in this manifest (similar effect, different permanence), and/or `delete_contact` vs. `merge_contacts` (similar effect — removing a duplicate record — very different data-loss consequences).
4. Include a **Forbidden-Order** scenario involving `delete_contact` — e.g. `delete_contact` should never fire before/instead of `merge_contacts` when the intent was deduplication, or `close_ticket` should never be callable again after itself (double-close) — labeled with an appropriate confidence tier since nothing here is as explicit as scenario 1's `transfer_funds` text.
5. List `send_email`, `list_contacts`, and `get_contact` in Manifest Gaps only if their descriptions are genuinely too thin to support a scenario — otherwise correctly leave them out of Gaps and simply not generate scenarios involving them.
6. Stay within roughly 2-3 scenarios per category for this 8-tool manifest (not forcing a scenario into every category if the evidence is weak — e.g. Redundant-Call may legitimately come back thin since no tool here is obviously over-called).

## Fail conditions

- Claims to have made a live MCP call despite this being the pasted-JSON path.
- Misses the `update_ticket_status`-vs-`close_ticket` or `delete_contact`-vs-`merge_contacts` distractor pair entirely — these are the single clearest signal in this manifest, so omitting both would mean the skill isn't doing its core job.
- Treats `delete_contact` → data loss risk as "explicit" confidence when the manifest never states an ordering dependency in words — must be labeled schema-linked or domain-inferred, not explicit.
- Produces a generic "test each tool happy path" output instead of sequencing-specific scenarios (that would mean the skill collapsed into the generic per-tool testing tools it's supposed to differentiate from).
