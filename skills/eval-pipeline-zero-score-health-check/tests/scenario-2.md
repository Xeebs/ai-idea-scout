# Scenario 2 — deepeval custom metric collapsed to a constant default, 15-sample run, no schedule given

## Input

**Config (deepeval test file, `test_summarization_quality.py`):**
```python
from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from deepeval.metrics import BaseMetric

class SummaryFaithfulness(BaseMetric):
    def __init__(self, threshold: float = 0.5):
        self.threshold = threshold

    def measure(self, test_case: LLMTestCase) -> float:
        try:
            response = self.model.generate(self._build_prompt(test_case))
            self.score = self._parse_score(response)
        except Exception:
            self.score = self.threshold  # fall back to threshold on any error
        self.success = self.score >= self.threshold
        return self.score

    def is_successful(self) -> bool:
        return self.success

metric = SummaryFaithfulness(threshold=0.5)

def test_faithfulness(test_case):
    assert_test(test_case, [metric])
```

**Most recent run output (JSON export, 15 samples, trimmed):**
```json
{
  "run_timestamp": "2026-11-13T09:15:00Z",
  "test_results": [
    {"name": "sample_1", "metrics_data": [{"name": "SummaryFaithfulness", "score": 0.5, "success": true}]},
    {"name": "sample_2", "metrics_data": [{"name": "SummaryFaithfulness", "score": 0.5, "success": true}]},
    {"name": "sample_3", "metrics_data": [{"name": "SummaryFaithfulness", "score": 0.5, "success": true}]},
    {"name": "sample_4", "metrics_data": [{"name": "SummaryFaithfulness", "score": 0.5, "success": true}]},
    {"name": "sample_5", "metrics_data": [{"name": "SummaryFaithfulness", "score": 0.5, "success": true}]},
    {"name": "sample_6", "metrics_data": [{"name": "SummaryFaithfulness", "score": 0.5, "success": true}]},
    {"name": "sample_7", "metrics_data": [{"name": "SummaryFaithfulness", "score": 0.5, "success": true}]},
    {"name": "sample_8", "metrics_data": [{"name": "SummaryFaithfulness", "score": 0.5, "success": true}]},
    {"name": "sample_9", "metrics_data": [{"name": "SummaryFaithfulness", "score": 0.5, "success": true}]},
    {"name": "sample_10", "metrics_data": [{"name": "SummaryFaithfulness", "score": 0.5, "success": true}]},
    {"name": "sample_11", "metrics_data": [{"name": "SummaryFaithfulness", "score": 0.5, "success": true}]},
    {"name": "sample_12", "metrics_data": [{"name": "SummaryFaithfulness", "score": 0.5, "success": true}]},
    {"name": "sample_13", "metrics_data": [{"name": "SummaryFaithfulness", "score": 0.5, "success": true}]},
    {"name": "sample_14", "metrics_data": [{"name": "SummaryFaithfulness", "score": 0.5, "success": true}]},
    {"name": "sample_15", "metrics_data": [{"name": "SummaryFaithfulness", "score": 0.5, "success": true}]}
  ]
}
```

**Schedule:** none provided — user says this only runs on-demand before releases, no cron/CI schedule.

## Pass criteria

- Correctly identifies deepeval from the `BaseMetric`/`assert_test`/`LLMTestCase` imports.
- Flags Signature 2 (constant-score collapse): all 15 samples score exactly `0.5`, which is well above the ~10-sample threshold for a confident finding — High severity.
- Independently flags the config-pattern root cause: `except Exception: self.score = self.threshold` — the fallback silently sets the score to exactly the threshold value on *any* error, which both (a) marks every erroring sample as `success: true` (since `score >= threshold` is true when score equals threshold) and (b) is exactly why every sample converged on the same number.
- Correctly states this is almost certainly a "didn't compute" case, not a "legitimately scored 0.5 fifteen times in a row" case — explains that the suspiciously exact repetition across all 15 samples, combined with the except-block fallback setting the score to the threshold, points to the measure() call failing silently every time (e.g. the underlying `self.model.generate()` call erroring on every sample) rather than genuine faithfulness scores.
- Correctly skips Signature 3 (schedule gap) since no schedule was provided, and says so explicitly rather than guessing at an expected cadence.
- Gives a concrete fix: e.g. "don't fall back to `self.threshold` in the except block — re-raise, or set a distinct sentinel (e.g. `self.score = None` plus an `error` field) so a measurement failure can never be mistaken for a passing score, and make `is_successful()` return False when that sentinel is set."
- Lists "clean checks" correctly noting Signature 1 (zero/null score) was not triggered (every sample has a non-null numeric score) — useful context showing the audit didn't just flag everything.

## Fail criteria

- Misses the constant-score collapse despite 15 identical values.
- Treats `0.5` across all 15 samples as plausible genuine scoring without flagging the except-block pattern that explains it.
- Invents or assumes a schedule/cadence that wasn't given.
- Declares this definitively a "the model is just mediocre at faithfulness" result without flagging the much stronger didn't-compute explanation evident from the code.
- Fails to note that `success: true` on every sample is itself suspicious given the except-block logic (i.e. doesn't connect the dots between the two pasted artifacts).
