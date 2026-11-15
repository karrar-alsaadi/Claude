# Finding audit: how to judge each finding

Contents
1. Verdicts
2. Verification recipes by category
3. Severity calibration test
4. Confidence calibration test
5. Wording test
6. Legitimate alternatives (not errors)
7. Domain traps: scRNA-seq / omics
8. Worked examples

---

## 1. Verdicts (one per finding)

- **confirmed**: the issue exists at the stated place, the evidence in the finding reproduces, the description is accurate.
- **partial**: the core issue is real but a detail is wrong: page number off, one figure misquoted, wrong test named, a stated consequence overstated. Say which detail.
- **not_error**: the thing flagged is a defensible choice, rounding-level difference, or consistent once the omitted context is read (section 6). Name the alternative.
- **false_positive**: the claim is wrong: the number the review calls inconsistent is consistent; the quoted sentence says something else; the reference does support the claim.
- **overreach**: the observation is true but the finding goes beyond it: infers intent, asserts the data are wrong, treats an inconsistency as proof of an error in the underlying data.
- **unverifiable**: you cannot check it with what you have (supplement, raw data, paywalled source, image at full resolution). State what would settle it. Do not convert to false_positive.

When two verdicts fit, choose the one that is best supported by evidence you hold, and say why the other was rejected.

## 2. Verification recipes

**Typographical.** Find the string; confirm it is an error and not a style choice (British/American spelling, gene vs protein case). Cosmetic: confirmed if present; severity should be minor.

**Numerical.** Open the exact table or sentence. Recompute the figure yourself:
```bash
python /mnt/skills/plugins/paper-find-misstake/scripts/check_numbers.py percent --num 24 --den 96 --reported 25.0 --find-denominator
python /mnt/skills/plugins/paper-find-misstake/scripts/check_numbers.py sum --parts 40,38,20 --total 100
python /mnt/skills/plugins/paper-find-misstake/scripts/check_numbers.py grim --mean 3.45 --n 28
```
Use the decimals as printed (they set the rounding tolerance). A discrepancy within rounding is `not_error`. Check the review quoted the numbers exactly. Confirm the other place the review cites (abstract vs Table 2) really says what the review says it says.

**Statistical.** Recompute with `check_numbers.py pvalue` / `ci` / `scan`. Then ask: is the test the review assumes the one the paper used? (A "wrong p-value" computed with a two-sided test is `not_error` if the paper states one-sided with justification; the first skill's script reports the one-tailed reading, so check that note.) Design claims (pseudoreplication, no multiplicity control, outcome switching) are verified by reading Methods and the analysis description, not by recomputation: find the sentence that shows the paper did, or did not, do the thing.

**Methodological.** Locate the design statement the finding relies on. Decide whether the flaw is present, whether it affects the specific claim cited, and whether the paper already addressed it (limitations paragraph, supplement). If addressed, the review's finding is `partial` (flaw real, already acknowledged) or `not_error` (fully mitigated).

**Referencing.** If the paper is available and the cited source is accessible, open the source (abstract at minimum) and test whether it supports the claim. For retraction or correction claims, require a stated route (Retraction Watch database, PubMed notice, publisher page, CrossRef). "Not retracted" without a route triggers gate G4. If you cannot reach the source, `unverifiable`.

**Ethical / transparency.** Search the paper for the identifier, consent statement, registration, funding, conflicts, data/code statements. Absent -> the finding is confirmed as a transparency gap; the review must not call it a scientific error (that would be a wording or calibration fault).

**Interpretive.** Put the conclusion sentence next to the result it rests on. Confirm the review's reading of both. A causal-language finding is confirmed when the design is observational and the verb is causal ("causes", "leads to", "drives"); it is `not_error` when the paper hedges ("associated with", "consistent with").

## 3. Severity calibration test

Severity is effect on the paper's claims (same rule as the first skill). For each finding ask:

1. Does it change a number or a test outcome that a claim rests on? -> at least substantial.
2. Does it undermine the design basis of a headline claim? -> substantial or critical.
3. Does it only hinder understanding or replication? -> moderate.
4. Cosmetic only? -> minor.
5. Does it suggest an integrity problem that warrants formal investigation, with strong independent evidence? -> critical (rare; most reviewers will never have grounds).

`severity_ok` = the review's grade is within one level of yours. Two or more levels apart is `misgraded` for verdict purposes if the issue is otherwise real. Record the direction (inflation / deflation) because patterns matter more than single cases.

Common inflations: typos or rounding slips graded substantial; critical used for a single recomputed p-value. Common deflations: pseudoreplication, confounding with batch, or causal overreach graded moderate when it underlies the headline claim.

## 4. Confidence calibration test

Use the first skill's scale. **High** only when reproducible from numbers printed in the paper (recomputation, arithmetic, two quoted places that contradict). **Medium** when it depends on a stated assumption (test type inferred, OCR text, methodological judgement experts could debate). **Low** for patterns or impressions that need data the reviewer lacks.

`confidence_ok` is false when: high confidence rests on an assumption the finding itself states; a methodological opinion is labelled high; low confidence is attached to a plain arithmetic contradiction (underconfidence is also miscalibration: set `"under"`, it counts 0.5).

## 5. Wording test

Flag: intent words (fabricated, falsified, manipulated, fraud, faked; in Arabic تزوير، تلاعب، احتيال، فبركة، تزييف); people-focused phrasing ("the authors misreported"); unhedged certainty beyond the evidence ("clearly", "proves"); calling a transparency gap a scientific error; verdicts on retraction. `audit_report.py` lists candidates with context; confirm by reading, since negated contexts ("this does not imply fraud") are fine and quoted official findings may be attributed.

## 6. Legitimate alternatives (usually `not_error`, or `partial` if the paper fails to justify them)

- One-sided test with a pre-stated directional hypothesis.
- Rounding differences within the last printed digit; percentages summing to 99-101.
- SE vs SD when the figure legend states which one.
- Welch vs Student t-test; non-parametric test with justified assumptions.
- Pooled vs per-group variance, where stated.
- Per-protocol or modified intention-to-treat analyses, if declared and reasoned.
- Different n between analyses because of documented missing data.
- Cluster markers used descriptively to name clusters (not inferential).
- Trajectory inference presented as exploratory ordering.
- Citing a review instead of a primary source for background statements (not for the paper's own results).

## 7. Domain traps: scRNA-seq / snRNA-seq / omics

True flaws a good review should catch (see the first skill's genomics checklist): cell-level DE as the sole evidence (pseudoreplication), double dipping after clustering or along pseudotime, donor/batch/sex/age/PMI confounding, DE count tracking cell count, ORA with the whole genome as background, networks read as demonstrated regulation, sex-difference claims from "significant in one sex only".

False-positive traps the review may fall into (verify before accepting):
- Flagging pseudoreplication when the paper aggregates to pseudobulk per donor, or uses a mixed model with donor as a random effect. Read Methods.
- Flagging double dipping for descriptive marker lists.
- Demanding FDR where the paper reports adjusted p-values (check the column name: `p_val_adj` from Seurat is Bonferroni over all genes in the object; it is adjusted but conservative).
- Calling a small donor count "an error" instead of a power/uncertainty limitation. It is a limitation and the finding should be graded by how strongly the paper claims.
- Mixing up the sample (donor) with nuclei counts when checking "n" reconciliation.

## 8. Worked examples

*Confirmed.* Finding: "Table 2 gives category total 248, listed values sum to 258." You add 120+80+58 = 258; the text on p. 6 says 258. -> confirmed; severity moderate or substantial depending on whether denominators feed a test. Review said substantial and named the percentages built on it -> severity_ok true.

*Partial.* Finding quotes "p = .08" but the paper prints "p = .008" in the abstract and ".08" in Results. The inconsistency is real but the review cited only one place and called it a typo-level slip while recomputation shows the test crosses .05. -> partial; note the missing second location and the under-graded severity.

*False positive.* Finding: "cell-level Wilcoxon used for DE (pseudoreplication)". Methods p. 5: "pseudobulk counts per donor and cell type, DESeq2". -> false_positive, and the review loses precision plus a D2 mark if it quoted text the paper does not contain.

*Overreach.* Finding: "the two sample sizes cannot both be right; the data appear manipulated." The inconsistency is real (120 vs 96) but the sentence asserts intent. -> overreach; trigger gate G2; the fix is "please clarify".
