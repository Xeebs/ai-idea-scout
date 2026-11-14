# Scenario 2 — Smart-light HTTP service, with a collision against an existing manifest

## Input (what the user pastes)

**App's command surface:**

```
App: hue-bridge-lite (talks to my smart lights over a local REST API)

Endpoints:
  POST /lights/living_room/on
  POST /lights/living_room/off
  POST /lights/living_room/toggle
  PUT  /lights/living_room/brightness  (body: {"level": 0-100})
```

I don't have exact trigger phrases in mind yet, just want natural ones drafted.

**Other apps' manifests already sharing the daemon:**

```json
{
  "app": "music-player",
  "intents": [
    {
      "name": "music.toggle_playback",
      "trigger_phrases": ["play or pause", "toggle the music", "turn the music on or off"],
      "callback": {"type": "exec", "target": "mpc toggle"}
    }
  ]
}
```

## Expected behavior

The skill should:
1. Extract four intents: `hue_bridge_lite.turn_on`, `hue_bridge_lite.turn_off`, `hue_bridge_lite.toggle`, `hue_bridge_lite.set_brightness` (naming may vary slightly but must be namespaced per-app and one intent per endpoint).
2. Set `callback.type: "http"` for all four with `target` built from the exact method+path given (e.g. `POST /lights/living_room/on`), and for `set_brightness`, note in the manifest or open questions that the body parameter (`level`) needs to be captured from the utterance or defaulted — not silently dropped.
3. Draft natural trigger phrases, e.g. for `toggle`: "toggle the lights", "turn the lights on or off", "flip the living room lights".
4. Detect the collision: `hue_bridge_lite.toggle`'s drafted phrases (something like "toggle the lights"/"turn the lights on or off") are a near-match in structure to `music.toggle_playback`'s "toggle the music"/"turn the music on or off" — same core verb+object pattern ("toggle X", "turn X on or off") that an STT engine could plausibly confuse if the object word is misheard. The skill must surface this as a collision rather than silently drafting phrases and ignoring the comparison, and must propose a disambiguating rewrite for each side (e.g. "toggle the lights" keeps "lights" explicit vs. "toggle the music" keeps "music" explicit — or recommend adding an app-name prefix convention) rather than picking one.
5. None of the four intents should be flagged destructive (turning lights on/off/toggling/dimming is reversible, not delete/send/pay/shutdown-shaped).
6. Open questions list should include: how brightness `level` gets captured from a spoken number, and the toggle-phrase collision needing a developer decision.

## Pass/fail criteria

- PASS if: all 4 intents appear with `http` callbacks using the literal method+path given, the brightness parameter gap is surfaced (not dropped), the toggle-phrase collision against `music.toggle_playback` is explicitly caught and reported in the Collision report table with a proposed disambiguation for both sides, no intent is wrongly marked destructive, and the JSON is valid.
- FAIL if: the skill misses the collision entirely (reports "no collisions found" despite the overlapping manifest being provided), invents an endpoint/body field not given, auto-picks one app's phrase as the winner instead of presenting both, or flags a light-toggle action as destructive.
