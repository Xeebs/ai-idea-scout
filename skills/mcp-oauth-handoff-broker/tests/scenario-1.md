# Scenario 1 — Claude Desktop, Notion MCP server, blank browser loop

## Setup given to the skill

A user reports:

- **Host and version**: Claude Desktop, version 0.14.2 (macOS).
- **MCP server / provider**: Notion's official MCP connector, which uses Notion OAuth.
- **Symptom in their own words**: "I clicked 'Connect' on the Notion MCP server. A little browser window popped up inside Claude Desktop, showed a blank white page, and after about 2 seconds it reloaded to blank again. It's done this about ten times now and never shows Notion's login page. I never get a chance to actually sign in."
- **Logs supplied**: a short excerpt from Claude Desktop's debug log:
  ```
  [12:03:11] mcp: starting oauth flow for server "notion"
  [12:03:11] mcp: generated auth_url=https://api.notion.com/v1/oauth/authorize?client_id=...&redirect_uri=http://localhost:51823/callback
  [12:03:11] browser: opening embedded webview
  [12:03:12] webview: navigated to about:blank
  [12:03:14] webview: navigated to about:blank
  [12:03:16] webview: navigated to about:blank
  ```
- **What's already been tried**: restarting Claude Desktop once; did not try a different browser since the sign-in happens in an embedded window, not their system browser.

## Pass/fail criteria

- [ ] Report correctly identifies the host (Claude Desktop 0.14.2) and server (Notion MCP / Notion OAuth) from the input, not a generic placeholder.
- [ ] Top-ranked diagnosis is the **infinite `about:blank` loop** fingerprint, marked **High confidence** — justified by both the stated symptom (repeated blank reloads in an embedded window) and the log evidence (`navigated to about:blank` repeated three times with no further navigation).
- [ ] The report does NOT rank "URL never surfaced" as the top match — the log clearly shows an `auth_url` was generated, so that fingerprint should be absent or explicitly ruled out, not confused with the blank-loop pattern.
- [ ] Remediation for the top match is concrete and matches the SKILL.md guidance: close the embedded browser window and manually open the `auth_url` from the log (`https://api.notion.com/v1/oauth/authorize?client_id=...`) in the system's default browser instead of the embedded webview.
- [ ] Report does not fabricate a specific Claude Desktop bug-tracker issue number or maintainer statement — it may note this is a known class of embedded-webview failure in general terms only, without inventing a citation.
- [ ] Report does not ask the user for or repeat any OAuth token, authorization code, or client secret — note the log excerpt given contains none, and the report shouldn't invent one either.
- [ ] Report includes the "one-time manual unstick, not a persistent fix" note, and suggests reporting the recurring embedded-webview bug to Claude Desktop if it keeps happening.
- [ ] Confidence language is honest: since the log directly confirms the fingerprint, it should say "High confidence," not hedge with "possible" when the evidence is actually solid.
