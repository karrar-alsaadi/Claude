---
name: paper-evaluation
description: Evaluate the quality of a review report produced by the paper-find-misstake skill (or any critical review of a scientific paper). Audits each finding (confirmed / partial / false positive / overreach / unverifiable) against the paper, checks quotes, numbers and pages, measures what the review missed, tests severity and confidence calibration, wording neutrality and honest scope, then returns a weighted 0-100 scorecard with gates, verdict and fix list. Includes a report linter, score aggregator, seeded-error benchmark, dark HTML scorecard. Use whenever the user asks to evaluate, grade, score, audit, validate, double-check or benchmark the output of paper-find-misstake, asks "are these findings real", "what did the review miss", "how good was the analysis", or wants to test or improve that skill. In Arabic, e.g. قيّم نتائج مهارة إيجاد الأخطاء، هل هذه الملاحظات صحيحة، ماذا فات المراجعة. Not for reviewing a paper itself (paper-find-misstake), one quote (paper-find-text), or research ideas (check-idea).
---

# paper-evaluation

Judge a review of a scientific paper: are its findings true, proven, well-graded, complete, and fairly worded? Return a score the user can trust and a list of what to fix.

Why this exists: a review report looks authoritative whether or not it is right. A fabricated page number, an inflated severity, a missed design flaw, or the word "fraud" each does damage that formatting hides. The evaluator's job is to re-derive, not to admire. Same discipline as the first skill: every verdict needs a location and evidence, intent is never inferred, and "could not verify" is an honest verdict, never a hidden negative.

Core stance: evaluate the **review**, not the paper's authors. Say "the finding does not reproduce at the stated location", never "the reviewer invented it", unless the evidence leaves no other reading (and then describe the evidence, not the motive).

## Inputs and mode

1. **Review report**: text in chat, a file under `/mnt/user-data/uploads/`, or the report just produced in this conversation. Chat text: save it to `review.md` before Step 1. If none exists, ask once for it, or offer to run `paper-find-misstake` first.
2. **The paper** (PDF/DOCX/text/DOI): needed to verify. Extract with `pdftotext -layout paper.pdf paper.txt` (keeps `\f` page breaks) or the `file-reading` / `pdf-reading` skills. Uploaded or already in context counts.
3. **Mode.** Paper available -> **full audit** (all 8 dimensions). No paper -> **structural audit**: only form, evidence-specificity, wording, honesty, actionability can be judged; label the result *provisional*, it cannot exceed 85, and say what verification would add. Never present a structural audit as proof the findings are right.
4. **Scope.** Default is a full audit. If the report is long, audit all critical and substantial findings, all numerical ones, and a stated sample of the rest.
5. **Language.** Reply in the user's language (Arabic if they wrote Arabic). Keep gene names, statistics, tool names in English. Scripts accept Arabic and English reports, Arabic-Indic digits included.
6. **If the report came from Claude in this same conversation**, say so and be stricter, not softer: authors over-credit their own work.

Skill path: `<skill-path>` is the folder containing this SKILL.md (user-installed: `/mnt/skills/user/paper-evaluation`). The first skill's path is `/mnt/skills/plugins/paper-find-misstake` or `/mnt/skills/user/paper-find-misstake`.

## Workflow

Order matters. Reading the review first anchors you to its list; build your own view of the paper before you grade its findings.

**Step 1. Lint the report (fast leads, not verdicts).**
```bash
python <skill-path>/scripts/audit_report.py review.md --paper paper.txt --out audit.json
python <skill-path>/scripts/audit_report.py review.md --paper paper.txt --brief
```
It parses findings (English or Arabic template), flags missing fields, vague locations, thin evidence, intent language, severity/confidence oddities, absent sections, and checks whether each quoted text/number actually occurs in the paper and on the cited page. A flag is a lead to verify by hand; a clean lint does not mean the findings are right.

**Step 2. Independent pass on the paper, before judging findings.** Write in a few lines: the central claim; the claim map; the 5-10 highest-risk places given the design (`references/coverage-audit.md` section 1 has the must-check matrix by study type; omics/scRNA-seq papers also use `/mnt/skills/plugins/paper-find-misstake/references/genomics-scrnaseq-checks.md`). Run `python /mnt/skills/plugins/paper-find-misstake/scripts/check_numbers.py scan paper.txt` for your own numeric reference list. This becomes your **reference list**, each item with a location.

**Step 3. Audit finding by finding** (`references/finding-audit.md`). For each: locate it in the paper; re-derive the claim (recompute, re-read, re-trace the reference); confirm each number belongs to the analysis the finding names; assign one verdict (confirmed, partial, not_error, false_positive, overreach, unverifiable); check severity against effect on the claim (one level off is tolerated, two is a miss); check the confidence label; check the wording. Do not copy the review's reasoning as your evidence. If you cannot check something, the verdict is `unverifiable`, which is neither a pass nor a fail.

**Step 4. Coverage audit** (`references/coverage-audit.md`). Compare the review with your reference list. Every omission you claim needs a location and evidence, and must be something an adequate review of this scope should have caught. Spot-check 2-3 items from the review's "checked and consistent" section: false reassurance is worse than a missed typo. A sound paper with few findings is not low coverage; a thin review of a flawed paper is.

**Step 5. Process audit.** Honest scope ("not assessed" used, tools named, route stated for reference checks, no "not retracted" from memory), the 10-question completion test, action level phrased as a suggestion, template followed, bottom line first, language matches the user's.

**Step 6. Score.** Fill the ratings file (schema in `references/rubric.md` section 5), then:
```bash
python <skill-path>/scripts/score.py aggregate eval.json --out result.json
```
It derives precision (D1), reference-set recall (D3) and calibration (D4) from your finding verdicts, takes your manual scores for the other dimensions, applies the gates, and returns total, caps, and band. Manual scores need a one-line reason; use the anchors in `references/rubric.md`.

**Step 7. Counter-review your own evaluation.** Before writing: Is every negative verdict backed by a quote, number, or location in the paper? Did I mark as `false_positive` something I merely could not check? Did I penalise a defensible methodological choice (name the legitimate alternative)? Did length, tone, or polish sway the score? Did I invent a missed issue to look thorough? Downgrade or drop any verdict that fails. Evaluator errors are errors of the same kind the review can make.

**Step 8. Report** (`references/report-template.md`). Verdict and score first, then the scorecard, finding audit, omissions, calibration and wording flags, a fix list (at most 7 items, ordered by effect), and the limits of this evaluation. If the same failure recurs across reports, add the pattern -> fix mapping from `references/failure-patterns.md` (for improving `paper-find-misstake` itself).

## Rules that keep the evaluation honest

- **Verdicts need evidence.** Quote the paper (short), give the number, or the recomputation. Never invent page numbers or quotes. If you cannot locate it exactly, say where you saw it approximately and lower confidence.
- **Unverifiable is not wrong.** Findings that depend on supplements, raw data, paywalled references, or images you cannot see are `unverifiable` and sit outside the precision denominator; report how many.
- **Do not reward volume, polish, or severity.** One design flaw that undermines the central claim outweighs twenty verified typos. A review that inflates severity is mis-calibrated even if every finding is real.
- **Defensible disagreement is not error.** One- vs two-sided tests, pooling choices, SE vs SD, descriptive use of cluster markers: if experts could differ, it is `not_error` or `partial`, with the alternative named.
- **No intent language** about anyone: not the paper's authors, not the reviewer. Describe discrepancies. Integrity decisions belong to journals and institutions.
- **Say what you did and did not do**: "recomputed with check_numbers.py", "opened the cited paper's abstract", "not assessed: supplementary file".
- **Do not rewrite the review or the paper** unless asked. Provide corrections and a fix list instead.
- **Tools are leads.** audit_report.py and score.py structure the work; they do not replace reading the paper.
- **Gates are real.** Fabricated evidence, an unattributed misconduct assertion, a missed flaw that overturns the central claim, or an unverified integrity claim cap the total regardless of other scores (`references/rubric.md` section 4).

## Output (mobile-first)

Lead with one line: score/100, band, mode (full or provisional). Then a compact scorecard table (8 dimensions), a short findings-audit table (id, verdict, one-line reason), omissions (each with location), flags, the fix list, and limits. Full detail only for critical and substantial items; group the rest. End with one line offering an HTML scorecard (dark, high-contrast, RTL-aware: `score.py html`) or a Word/PDF report. Create a file only if asked.

## Bundled resources

- `references/rubric.md`: 8 dimensions, weights, 0-4 anchors, gates, bands, ratings-file schema. Read before scoring.
- `references/finding-audit.md`: verdict definitions, verification recipes by error category, severity and confidence calibration tests, domain traps (scRNA-seq), legitimate-alternative list. Read in Step 3.
- `references/coverage-audit.md`: must-check matrix by study type, building the reference list, weighted recall, false-reassurance spot-checks. Read in Steps 2 and 4.
- `references/benchmark.md`: seeded-error benchmark, regression comparison of skill versions, sample-size cautions. Read when the user wants to test or compare versions of `paper-find-misstake`.
- `references/failure-patterns.md`: recurring failure -> likely cause -> fix in the first skill.
- `references/report-template.md`: evaluation report skeleton (English and Arabic), wording rules, Arabic glossary.
- `scripts/audit_report.py`: report parser/linter and quote, number and page checker (`--paper`).
- `scripts/score.py`: `aggregate` (scores and gates), `bench` (precision/recall against known issues), `html` (dark scorecard).
- `scripts/seed_errors.py`: plants known errors in a paper's text and writes the answer key for benchmarks.
- `evals/`: test prompts and fixtures used to validate this skill (kept in the source folder, not in the packaged file).

## Limits (state when relevant)

Cannot see raw data, unpublished protocols, or full-resolution images; OCR can corrupt digits; recall is measured against your own reference list (a lower bound on omissions, not proof of completeness) unless you run a seeded benchmark. This evaluation supports, and does not replace, expert peer review, and it never establishes misconduct.
