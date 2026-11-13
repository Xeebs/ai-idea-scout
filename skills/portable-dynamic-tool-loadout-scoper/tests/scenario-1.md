# Scenario 1 — On-call engineering agent triaging a production incident

## Input

**Catalog (22 tools registered on a LangGraph on-call agent):**
1. `github_get_issue` — fetch a GitHub issue's title, body, labels, and comments by number
2. `github_comment_on_issue` — post a comment on a GitHub issue
3. `github_search_code` — search code across the org's repos by keyword
4. `github_create_pr` — open a pull request from a branch
5. `datadog_get_logs` — query Datadog logs by service and time range
6. `datadog_get_metrics` — query Datadog metrics (latency, error rate, throughput) by service
7. `pagerduty_get_incident` — fetch an open PagerDuty incident's details and timeline
8. `pagerduty_ack_incident` — acknowledge a PagerDuty incident
9. `slack_post_message` — post a message to a Slack channel
10. `slack_search_messages` — search Slack message history by keyword
11. `jira_create_ticket` — create a new Jira ticket
12. `jira_search_tickets` — search Jira tickets by keyword/status
13. `linear_create_issue` — create a new Linear issue
14. `linear_search_issues` — search Linear issues by keyword
15. `notion_search_pages` — full-text search across the team's Notion workspace
16. `confluence_search_pages` — full-text search across the team's Confluence space
17. `google_drive_search` — search files in the team's shared Google Drive
18. `calendar_get_events` — read upcoming calendar events
19. `calendar_create_event` — create a calendar event
20. `email_send` — send an email
21. `aws_describe_instance` — fetch metadata/status for an EC2 instance by ID
22. `audit_log_write` — mandatory logging tool, must always run

**Task/step**: "The agent just received a new GitHub issue reporting that the `/checkout` API is returning 500 errors intermittently in production. Investigate root cause using logs/metrics and post a triage comment on the issue with findings."

**Max loadout size**: 10
**Always-include**: `audit_log_write`

## Pass/Fail Criteria

Pass requires the output to:

1. Include `github_get_issue`, `github_comment_on_issue`, `datadog_get_logs`, `datadog_get_metrics`, and `audit_log_write` as Core/Mandatory — these are unambiguously needed for "investigate via logs/metrics and comment on the issue."
2. Include `audit_log_write` regardless of relevance scoring, labeled Mandatory, per the always-include input.
3. Exclude, or classify Irrelevant/excluded-over-budget, tools with no plausible connection to this step: `calendar_create_event`, `email_send`, `jira_create_ticket`, `linear_create_issue`, `google_drive_search`, `confluence_search_pages`, `notion_search_pages` — none of these serve "investigate a 500 error and comment on the GitHub issue."
4. Flag at least one real overlap/ambiguity group — e.g. `jira_search_tickets` vs `linear_search_issues` vs `notion_search_pages` vs `confluence_search_pages` all plausibly "search for related past incidents," or `pagerduty_get_incident` as a plausible-but-not-certain source of correlated timeline data vs `datadog_get_logs`/`datadog_get_metrics`.
5. Stay within or near the max loadout size of 10 (small overage acceptable only if clearly justified, e.g. mandatory tool pushing it to 11).
6. Give a one-line reason for every one of the 22 tools, included or excluded — no tool left unexplained.
7. State a confidence flag (HIGH is expected here since the task is concrete and the Core set is clear-cut).

Fail if: any of the five unambiguously Core tools is excluded without an explicit, justified reason; `audit_log_write` is dropped; more than 2 tools are left without a stated rationale; or no overlap/ambiguity is flagged despite the catalog containing four overlapping "search" tools.
