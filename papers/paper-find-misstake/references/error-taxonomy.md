# Error taxonomy and check procedures

Source: condensed from the user-supplied Arabic guide ("دليل أكاديمي صارم لاكتشاف الأخطاء في الأوراق العلمية والتحقق من دقة المعلومات"), sections 1-2, plus additions marked **[+]** that come from the verified sources listed in `sources.md`.

Contents
1. Claim types (classify before verifying)
2. Typographical and editorial
3. Numbers, units, conversions
4. Internal consistency
5. Design and methodology
6. Data collection and quality
7. Statistical analysis
8. Figures, tables, images
9. References, citations, overlapping publication
10. Interpretation and conclusions
11. Ethics, transparency, disclosure

---

## 1. Claim types
Classify each claim before checking it, because each type is verified differently.
- **Fact or definition** -> compare with a reliable source.
- **Original result** -> trace to the study's own data and analysis.
- **Interpretation or conclusion** -> test whether results and design support it.
- **Opinion or recommendation** -> must be marked as such, not as a finding.
- **Procedural description** -> must be detailed enough to repeat.

Opening the cited source matters more than confirming it exists: does it support *this* claim, is the quote in context, are authors/journal/year/volume/pages/DOI right, is it a primary source where one is needed, is the date suitable for a fast-moving topic.

Uncertainty is not error. Check that uncertainty is shown (CI, SD vs SE, detection limits, prediction intervals).

## 2. Typographical and editorial (usually minor)
- Spelling, punctuation, decimal separators, brackets, dashes, symbols.
- Same author/institution/material/device spelled differently in different places.
- Wrong numbering of figures/tables/equations/sections; cross-references to items that do not exist.
- Abbreviation used before definition, or two abbreviations for one term.
- Leftover editor comments, tracked changes, placeholder alt-text, text from another template.
- Case that carries meaning: gene vs protein symbols, units (mM vs Mm).
- Duplicated paragraph, missing sentence, inconsistent heading and reference style.

**Procedure:** build a glossary of terms, symbols, units and names; check each item's use in title, abstract, body, tables, figures, appendices.

## 3. Numbers, units, conversions (never accept "looks plausible")
- Same number in abstract, results, tables, figures, conclusion.
- Sums, percentages, means recomputed.
- Unit conversions (mg/g, mL/L, IU), SI prefixes (µ, m, k); absolute vs relative vs log units.
- Decimal places match measurement precision (no false precision); scientific notation exponents.
- True zero vs missing vs below detection limit.
- **Denominator of every percentage** (whole sample vs subgroup).
- n (people) vs measurements vs experimental units; mean vs median vs rate vs total.

**Procedure:** recompute every derived value from raw data or table; note formula, denominator, unit. Use `scripts/check_numbers.py` (`percent`, `sum`, `grim`).

## 4. Internal consistency
- Flow diagram n = Table 1 n = analysed n in results.
- Excluded = before - after.
- Sample size compatible with degrees of freedom. **[+]** For a two-group t-test df = n1 + n2 - 2; one-way ANOVA df2 = N - k; correlation df = N - 2.
- Means/SDs compatible with raw values or range.
- Category totals equal overall total (allow rounding).
- Direction of effect in text = figure; arm labels consistent; hypothesis = analysis = conclusion.
- Variable definition in Methods = in Results.
- Different n across models -> explained?

Document each conflict with page, paragraph, table/figure, first value, conflicting value.

## 5. Design and methodology
Check method before results: a typo list is worthless if the design cannot support the conclusion.
- Testable research question; design fits the question (cross-sectional cannot establish temporal order).
- Population, sample, inclusion/exclusion criteria defined; selection, survivor, non-response bias.
- Sample size justification or power analysis when appropriate.
- Primary outcome/variables defined before analysis; operational definitions.
- Confounders considered; fair comparison group; baseline comparability.
- Trials: randomisation, allocation concealment, blinding, protocol deviations explained.
- Unit of analysis = unit of randomisation/measurement; **technical replicates not treated as biological replicates**.
- Measurement can separate real change from noise; instrument validation/calibration reported.
- Causal claims justified by design.
- Compare reporting with the guideline for the design -> `reporting-guidelines.md`.

## 6. Data collection and quality
- Data source described and verifiable; rules for missing, outlying, invalid values (missing not at random?).
- Duplicates; entry/coding errors; swapped columns.
- Data changed or excluded after seeing results? justification?
- Cut-points or definitions changed during analysis?
- Cleaning/transformation reproducible; data and software versions logged.
- Participants vs observations (repeated measures).
- Sample representative or cherry-picked?
- If data/code are withheld, the reason and the alternative verification route are stated.

## 7. Statistical analysis
**Test and model choice:** fits variable type, distribution, design; independence or correlated-data model; assumptions checked; one- vs two-sided justified in advance; sample size vs number of parameters; missing-data handling; confounders without over-fitting; multiple-comparison correction; exploratory vs confirmatory separated; correlation not turned into causation.

**Presentation:** effect size (not p alone), CI or other uncertainty, actual n per analysis, point estimate with units, exact p or enough precision, statistical vs practical significance, correct interpretation of CI and p, null/negative results shown.

**Red flags needing extra scrutiny:** hypothesis/outcome changed after seeing data; subgroup or cut-point chosen because it "worked"; one analysis shown out of many; "proved"/"disproved" language; p inconsistent with effect size and CI; means without spread in skewed data; ignored measurement uncertainty.

Key reference statements (ASA): p is not the probability the hypothesis is true, not effect size or importance, and should not be the sole basis for conclusions.
**[+]** Non-significant != no effect. **[+]** "Significant in group A but not in group B" is not evidence of a difference between A and B; test the interaction/difference directly.
**[+]** Recompute p from the statistic with `scripts/check_numbers.py pvalue|scan|ci`.

## 8. Figures, tables, images
- Axis starts at zero when needed; scale equal and sensible; units/symbols/labels clear.
- Error bars defined (SD, SE, CI); n of points/bars = n of cases.
- Hidden, cropped, or selected points explained; colour legible in greyscale/colour-blind.
- Same data shown twice as if independent.
- Microscopy, blots, scans: processing that changes interpretation; original files kept; adjustments applied uniformly and disclosed.
- Caption states sample, analysis, unit, n. Table separates raw from derived.
- **[+]** Look for duplicated/overlapping image regions across panels and across figures; a published screen of 20,621 papers found ~3.8% with problematic images (Bik et al. 2016). Visual inspection in chat can only *flag*; it cannot confirm manipulation.

## 9. References, citations, overlapping publication
- Every in-text citation in the list and vice versa; DOI/PMID/accession valid.
- Reference supports the specific statement, not just the topic.
- **Retracted or substantially corrected articles cited without note** -> check retraction databases (`verification-tools.md`).
- Over-reliance on weak/non-peer-reviewed sources for strong claims; reviews/opinions presented as original results.
- Prior publication or shared data disclosed; legitimate reuse vs duplicate publication/salami slicing; selective quoting that hides opposing results.
- ICMJE: overlapping publication can double-count data; errors that invalidate results may require substantial correction or retraction.

## 10. Interpretation and conclusions
- Conclusion restates data or exceeds it? Correlation -> causation? Generalised to populations not sampled?
- Sample size, bias, imprecision acknowledged? Unexpected/contrary findings discussed?
- Primary vs secondary/exploratory findings separated; limitations real, not ceremonial.
- Recommendations proportional to strength of evidence.
- Conclusion rests on results, not on abstract/title language.
- Prefer graded wording: "results suggest" / "are consistent with" rather than "prove".

## 11. Ethics, transparency, disclosure
Ethics committee/IRB approval (with identifier), informed consent or waiver justification, trial/protocol registration, conflicts of interest and funding role, author contributions and corresponding author, data/code/material availability or reasons, AI-tool disclosure if policy requires, peer-review integrity indicators.
Missing disclosure is not automatically a scientific error, but it can block assessment of reliability or hide an undeclared conflict. Report it as a transparency gap.
