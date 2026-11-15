# Benchmark: testing paper-find-misstake with planted errors

Use when the user wants to test, tune, or compare versions of the first skill, or wants a recall number that does not depend on the evaluator's own judgement.

Contents
1. Seeded-error protocol
2. Matching findings to the answer key
3. Metrics
4. Comparing versions (regression)
5. Cautions

---

## 1. Seeded-error protocol

1. Take a paper's text (`pdftotext -layout`, keep page breaks) or any short article. Prefer a paper the first skill has not seen in this conversation.
2. Plant known errors and write an answer key:
```bash
python <skill-path>/scripts/seed_errors.py paper.txt --n 8 --seed 11 --out-dir bench/
# writes bench/paper_seeded.txt and bench/truth.json
```
   Operations: p-value flipped across .05, sample size changed in one place, percentage shifted, direction word flipped, degrees of freedom changed, causal verb substituted for "associated with", letter-swap typo. Each seeded item records line, page, original and mutated snippet, category, severity.
3. Give `paper_seeded.txt` to `paper-find-misstake` in a fresh conversation with a neutral prompt ("review this paper"). Do not mention seeded errors.
4. Save its report as `bench/review.md`.

The planted items are the ground truth for recall. Anything else the review reports is either a genuine pre-existing issue in the source paper (verify, count as confirmed) or a false positive.

## 2. Matching findings to the answer key

Write `bench/matches.json`:
```json
{"findings": [
  {"id": "1", "truth_id": "S3", "verdict": "confirmed"},
  {"id": "2", "truth_id": null,  "verdict": "confirmed",   "note": "real issue already in source paper"},
  {"id": "3", "truth_id": null,  "verdict": "false_positive"}
]}
```
A finding matches a planted error when it points to the same location (line or page and snippet) and identifies the same defect. Matching by number alone is not enough; the finding must say what is wrong. Judge matches blind to the review's confidence labels.

## 3. Metrics

```bash
python <skill-path>/scripts/score.py bench bench/truth.json bench/matches.json
```
Returns: recall (planted errors found / planted), severity-weighted recall, per-category recall, precision (matched or confirmed findings / all assessed findings), F1, list of missed planted errors, severity-calibration agreement, and a note on sample size.

Reading the numbers: recall below about 0.6 on numeric seeds means the numbers step (Step 4 of the first skill) is not being executed; low recall on interpretive seeds (causal verb, direction flip) points at Step 8; low precision with many `false_positive` verdicts points at the counter-review step.

## 4. Comparing versions

1. Snapshot the old skill: `cp -r /mnt/skills/user/paper-find-misstake /tmp/pfm-old`.
2. Use the same seeded paper and seed for both versions; run each in a fresh conversation.
3. Compare per-category recall, precision, severity calibration, and the evaluation total from `score.py aggregate`. Report differences as counts ("found 6 of 8 vs 7 of 8"), not as percentages, with a small-sample warning.
4. Repeat with at least 3 different seeds or papers before claiming improvement.

## 5. Cautions

- Eight seeds give coarse numbers: one miss moves recall by 12 points. Treat results as diagnostics, not as a leaderboard.
- Planted errors are easier than real ones (they are local and arithmetic). High seeded recall does not show the review catches design flaws; use the coverage audit on real papers for that.
- If the same seed set is used to tune the skill repeatedly, the skill can overfit to the operations. Rotate seeds and papers.
- Mutations can accidentally create a second, unintended inconsistency. Read the seeded diff before running.
- Never publish a benchmarked paper as if the planted errors were real; keep the seeded copy and key private.
