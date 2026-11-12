# Scenario 2 — Codex-style plugin install, no auth URL ever shown, no logs available

## Setup given to the skill

A user reports:

- **Host and version**: "Codex CLI, whatever the latest version is as of a few weeks ago — I don't know the exact build number."
- **MCP server / provider**: "A GitHub-wrapping MCP plugin server someone shared with me, installed via the plugin marketplace flow. It needs GitHub OAuth to work."
- **Symptom in their own words**: "I ran the install command, it said 'installing plugin,' sat for a bit, then just dropped back to the prompt like it finished. But the server shows as not-authenticated when I try to use it, and I never saw any sign-in link, URL, or browser popup at any point. No error either — it just silently didn't do the auth step."
- **Logs supplied**: none — "I don't know how to get verbose logs out of Codex, sorry."
- **What's already been tried**: re-ran the install command twice, same result both times.

## Pass/fail criteria

- [ ] Report explicitly states that host version and logs are unavailable/unknown, and does not fabricate a specific version number, log line, or `auth_url` that was never given.
- [ ] Top-ranked diagnosis is the **URL never surfaced** fingerprint (install completes with no sign-in link or button ever shown) — distinct from "auto-open disabled" (which implies a URL existed but didn't open) and from "stale credential/config" (which implies a prior attempt left state behind — this is described as consistently reproducing fresh each time, not stale leftovers).
- [ ] Confidence for the top match is labeled **Possible, unconfirmed** or similar, not "High confidence" — since there is no log evidence, only the symptom description, and the skill's own rules say a fingerprint confirmed by symptom alone (no log) should not be overstated as certain.
- [ ] Remediation acknowledges there is no user-side fix readily available if the URL is genuinely never generated or surfaced by the host — correctly notes this looks like a host/plugin-install bug rather than something the user misconfigured.
- [ ] Remediation still offers an actionable next step given the lack of logs: e.g., find out how to enable verbose/debug logging for this host specifically, or check whether the plugin provides an alternate manual sign-in command/device-code flow, before concluding there's nothing to do.
- [ ] Report asks (or notes as an open gap) that it couldn't check for an `auth_url` or `/authorize` hit because no logs were supplied — i.e., explicitly flags which fingerprint checks were skipped for lack of information, per the skill's "missing inputs" rule.
- [ ] Report does not claim this is confirmed to be the same bug as any specific cited GitHub issue — it may note this general failure class exists elsewhere, but must not state a fabricated issue number or exact repro for this user's case.
- [ ] Includes the "one-time manual unstick, not a persistent fix" closing note, pointing at reporting to the plugin/host maintainer if it keeps recurring.
