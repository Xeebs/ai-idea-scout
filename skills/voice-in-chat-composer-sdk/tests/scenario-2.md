# Scenario 2 — Vue internal tool, no backend yet, unstated provider/mode, no code pasted

## Input

An ops team describes (no code pasted) their internal warehouse-logging chat tool:

1. **Composer**: "It's a Vue 3 single-file component called `LogComposer.vue`. There's a `textarea` bound to `v-model=\"draft\"`, and a `submitLog()` method that pushes into a Pinia store called `logStore.entries` and clears `draft`. I don't have the exact code in front of me right now."
2. Frontend framework: Vue.
3. Backend runtime: "We don't have a backend server yet — right now the frontend calls a third-party logging API directly."
4. Target provider: not stated ("whichever works best, don't really know the options").
5. Interaction mode: not stated.
6. Existing auth: "There isn't really any auth yet, it's an internal tool on our VPN."

## Pass criteria

- [ ] Assumptions section explicitly flags that no real code was pasted and that reduced specificity applies — it should not silently fabricate a `LogComposer.vue` file as if it were pasted verbatim.
- [ ] Frontend diff uses `[PLACEHOLDER]`-style markers (or clearly marked, explicitly-labeled stand-ins) for the exact submit function body / Pinia action, while still correctly using the *named* pieces the user did give — `draft`, `submitLog()`, `logStore.entries` — since those names were given even without full code.
- [ ] Assumptions section states the default provider (Gemini Multimodal Live) and default mode (push-to-talk) were applied because neither was specified, and says so explicitly rather than silently picking one.
- [ ] Backend relay stub is drafted as new code (since none exists yet) rather than described as a diff to an existing file, and the output notes this is new infrastructure they don't currently have.
- [ ] Auth handshake paragraph addresses the "no auth yet" reality honestly — e.g. recommending the relay at minimum restrict connections (such as to the stated VPN/network boundary) rather than inventing a session-cookie scheme that doesn't exist in their stack.
- [ ] All three standing risk flags still present even though this is an internal/VPN tool.
- [ ] Manual follow-up checklist includes setting up the backend relay itself as a new piece of infrastructure (install deps, env vars for the provider key, deploy somewhere reachable from the frontend) since "we don't have a backend yet" changes what's actually missing.
- [ ] No claim that a ready-made third-party voice-composer SDK package exists to install.

## Fail conditions

- Output invents full file contents for `LogComposer.vue` and presents them as if they were pasted, rather than flagging the gap.
- Output silently assumes a provider/mode without saying it defaulted.
- Auth handshake invents a cookie/JWT scheme the user never described having.
- Risk flags section is dropped or shortened because the tool is "just internal."
