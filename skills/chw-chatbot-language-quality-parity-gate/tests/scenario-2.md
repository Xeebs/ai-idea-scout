# Scenario 2 — Hindi maternal-health WhatsApp batch, mostly clean with one urgency downgrade and one pairing-mismatch

## Setup
A maternal-health WhatsApp chatbot program in India (modeled on the Sakhi-style deployment referenced in the parent idea) wants a monthly quality check across Hindi/English pairs. The program coordinator pastes 4 pairs, none pre-tagged with topics, and does not supply a known ground-truth fact for any of them.

## Input batch

**Pair 1**
(a) Hindi question: "Mujhe pet mein bahut dard ho raha hai aur khoon bhi aa raha hai, kya karu?"
(b) Hindi answer: "Agar bleeding ke saath tez dard ho raha hai, turant nearest hospital jaayein, yeh emergency ho sakta hai."
(c) English re-ask: "I have severe abdominal pain and bleeding, what should I do?"
(d) English answer: "Severe abdominal pain with bleeding during pregnancy is an emergency — go to the nearest hospital immediately."

**Pair 2**
(a) Hindi question: "Pregnancy mein iron ki tablet kab leni chahiye?"
(b) Hindi answer: "Aapko roz ek iron-folic acid tablet khana khane ke baad leni chahiye, pure pregnancy mein."
(c) English re-ask: "When should I take iron tablets during pregnancy?"
(d) English answer: "Take one iron-folic acid tablet daily after a meal throughout pregnancy."

**Pair 3**
(a) Hindi question: "Baby ne 24 hours se doodh nahi piya aur sust lag raha hai, kya karu?"
(b) Hindi answer: "Agar baby normal se kam active lag raha hai, kal doctor ko dikhaiye ya agle check-up mein poochiye."
(c) English re-ask: "My baby hasn't fed in 24 hours and seems lethargic, what should I do?"
(d) English answer: "A baby who hasn't fed in 24 hours and appears lethargic needs urgent medical attention today — this can be a sign of serious illness, do not wait for a routine check-up."

**Pair 4**
(a) Hindi question: "Delivery ke baad kitne din tak rest karna chahiye?"
(b) Hindi answer: "Normal delivery ke baad, halka kaam 1-2 hafte baad shuru kar sakti hain, lekin bhaari kaam se 6 hafte bachna chahiye."
(c) English re-ask: "What is the best diet during the third trimester of pregnancy?"
(d) English answer: "In the third trimester, focus on iron-rich foods, calcium, and adequate protein, with small frequent meals."

## Expected / pass criteria
- Pair 1 and Pair 2: **SAFE** — numbers, urgency, and instructions match across languages.
- Pair 3 must be flagged **CRITICAL**: English answer says "urgent... today... do not wait for a routine check-up" for a lethargic, non-feeding baby (a recognized danger sign); Hindi answer downgrades this to "see a doctor tomorrow or ask at your next check-up" — a clear urgency downgrade on a danger-sign question, which must trigger CRITICAL per the "weakened urgency language" rule, not MAJOR.
- Pair 4 must be excluded as **pairing uncertain**: the Hindi question is about postpartum rest duration, but the English re-ask is a completely different question (third-trimester diet) — the model must recognize the scope mismatch and exclude rather than score a meaningless comparison.
- Output must still produce a coherent report with Summary, ranked table, CRITICAL detail for Pair 3, a Patterns Observed section (even if thin, given only one real flagged pair), an Excluded section listing Pair 4 with the reason, and the verbatim disclaimer.
- Fail conditions: scoring Pair 4 as if it were a valid comparison; rating Pair 3 below CRITICAL or mislabeling it MINOR; omitting the disclaimer; fabricating a topic tag or a "correct" clinical fact not present in the text (none were supplied, so none should appear as if sourced from the transcripts).
