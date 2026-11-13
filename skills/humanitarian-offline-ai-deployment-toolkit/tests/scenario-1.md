# Scenario 1 — Mosquito-species classifier for a vector-control field team

## Input

A regional NGO vector-control program (modeled on the kind of work VectorCam does) is building a smartphone app that photographs captured mosquitoes and classifies the species on-device, to help field workers distinguish malaria-carrying Anopheles from other species without shipping samples to a lab.

Details the user provides:
- Domain/task: "Mosquito species classification from a photo taken on a field worker's phone, to flag malaria-vector species on the spot."
- Model: "A MobileNetV3-based CNN, already fine-tuned, exported to TFLite, roughly 15MB."
- Target device: "Mid-range Android phones used by field staff — typically 4GB RAM, 64GB storage."
- Connectivity tier: "Field workers are in rural areas for days at a time with no signal, then return to a district office with Wi-Fi every 3-5 days."
- Update/log sync need: "We want to pull classification logs (species, location, timestamp) back to a central database when staff return to Wi-Fi, and occasionally push model updates as we retrain."

## Pass criteria

- [ ] Classifies device class as phone and connectivity tier as "occasional Wi-Fi/cell window" without needing to ask (both were clearly stated).
- [ ] Packaging recommendation correctly identifies the 15MB TFLite model as comfortably under the RAM threshold for a 4GB device (well under 40%) and does not demand aggressive quantization or flag a hardware mismatch.
- [ ] Inference runtime recommendation points to a mobile-native runtime (TFLite runtime itself, MediaPipe, or ONNX Runtime Mobile) appropriate for a phone-class CNN — not llama.cpp (which is LLM-oriented and wrong for this case).
- [ ] Sync recommendation proposes a queue-and-reconcile protocol (local write-ahead log, push/pull on connection detection) matched to the "returns every 3-5 days" window, covering both the log-pull and model-update-push directions the user asked for.
- [ ] Field-condition checklist includes cold-start load time, multi-day dropped-connection behavior, partial/out-of-order sync, low-battery/storage degradation, and a real-field-use usability pass — all five categories from the SKILL.md procedure, tailored to this phone/vector-control context (not generic placeholders).
- [ ] Out of Scope section explicitly states this doesn't validate the classifier's biological/species-ID accuracy and doesn't cover implementation — just plumbing.
- [ ] Does not invent a specific measured latency or battery-drain number not supplied by the user.

## Fail conditions

- Treats this as a laptop/SBC deployment or recommends llama.cpp.
- Silently assumes a different connectivity tier than the one stated.
- Skips the sync recommendation despite the user explicitly stating both push and pull needs.
- Claims the plan has been field-validated.
