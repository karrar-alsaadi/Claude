# Report template, severity, wording

Contents
1. Report skeleton
2. Finding template (Arabic and English)
3. Severity scale
4. Confidence scale
5. Wording rules
6. Action ladder
7. Completion test (10 questions)
8. Arabic terminology

---

## 1. Report skeleton
Write the report in the user's language (Arabic if they wrote Arabic; keep technical terms, gene names, statistics notation in English). Lead with the bottom line. No process narration before it.

1. **Bottom line** (3-5 lines): central claim; overall reliability of that claim given what you checked; count of findings by severity; the 1-3 findings that matter most.
2. **Scope and limits**: what version/file, what you reviewed (language / method / statistics / references / images), what you could not assess (raw data, supplementary files, images at full resolution, paywalled references) and which tools you ran.
3. **Central claim and evidence map** (short table: claim -> supporting table/figure/reference -> verdict).
4. **Findings**, ordered by severity then by order in paper. Use the finding template. One issue per finding.
5. **Checked and found consistent** (important: shows coverage, prevents the reader assuming unmentioned = unchecked).
6. **Questions for the authors** (only those that would resolve a flagged issue).
7. **Suggested action level** (section 6) - as a suggestion, with the reason.

Length: a mobile chat reader sees about a screen at a time. Put the bottom line and the severity table first; give full finding detail for substantial/critical items and compress minor items into one grouped list (still with locations). Offer a file (docx/pdf) at the end; do not create one unless asked.

## 2. Finding template
Use this for every finding that is moderate or above; minor items may be grouped as "location | text | suggested fix".

English
```
Finding #:
Category: typographical / numerical / methodological / statistical / referencing / ethical / interpretive
Severity: minor / moderate / substantial / critical
Exact location: page, paragraph, line, table or figure
Text or number in question:
Verifiable description of the problem:
Evidence, calculation, or comparison source:
Possible effect on results or interpretation:
Suggested correction or question for the authors:
Confidence: high / medium / low
```

Arabic (from the source guide)
```
رقم الملاحظة:
تصنيف الخطأ: طباعي / رقمي / منهجي / إحصائي / مرجعي / أخلاقي / تفسيري
درجة الأثر: طفيفة / متوسطة / جوهرية / حرجة
الموضع الدقيق: الصفحة، الفقرة، السطر، الجدول أو الشكل
النص أو الرقم محل الملاحظة:
وصف المشكلة القابل للتحقق:
الدليل أو الحساب أو المصدر المقارن:
الأثر المحتمل في النتائج أو التفسير:
التصحيح المقترح أو السؤال المطلوب من المؤلف:
درجة الثقة في الملاحظة: عالية / متوسطة / منخفضة
```

Neutral model finding: "Table 2 gives the category total as 248, but the listed values sum to 258; the text on p. 6 also says 258. Please clarify which is correct and whether it changes the denominators or the statistical analysis."

## 3. Severity scale (effect on understanding and conclusions)
- **Minor (طفيفة):** does not change understanding or results: spelling, formatting, cosmetic cross-reference.
- **Moderate (متوسطة):** may hinder understanding or replication: missing unit, wrong cross-reference, incomplete method detail, rounding-level numeric slip that does not alter a test outcome.
- **Substantial (جوهرية):** could change a result or interpretation: a calculation error that affects a test, mismatched sample size, p-value that crosses the significance threshold when recomputed, design flaw that undermines a specific claim, causal claim without design support.
- **Critical (حرجة):** makes the results unreliable or indicates an integrity problem that warrants formal investigation. Reserve for cases with strong, independent evidence; most reviewers will never have grounds to use it.

Severity is about effect on the claim, not number of errors. One design flaw outranks twenty typos.

## 4. Confidence scale
- **High:** reproducible from numbers printed in the paper (e.g. recomputed p-value, arithmetic, internal contradiction between two quoted places).
- **Medium:** depends on an assumption you state (e.g. test type inferred, denominators assumed, OCR text, methodological judgement that experts may debate).
- **Low:** a pattern or impression that needs information you do not have (e.g. suspected image reuse from a low-resolution figure).
Say what would raise or lower it. Wording in the paper that settles the point (for example "a P-value" vs "adjusted") raises confidence.

## 5. Wording rules
- Describe the discrepancy, not the authors. "Table 2 and the text disagree on n" not "the authors misreported".
- Never infer intent. A numerical inconsistency proves an inconsistency that needs an explanation; it does not prove error in the data, let alone misconduct. Do not use words such as fabricated, falsified, manipulated, fraud unless the user quotes an official finding; then attribute it.
- Use "needs clarification" when evidence is insufficient to decide.
- Separate accepted methodological disagreement from error. Name the alternative legitimate choice.
- Rounding differences are reported separately from substantive differences.
- Graded verbs for conclusions: "suggests", "is consistent with" - and call out "proves/demonstrates" when the design cannot support it.
- If you could not check something, say "not assessed" (never silently omit).

Not acceptable: "The authors faked the sample."
Acceptable: "The reported denominators differ between the abstract (120) and Methods (96); please clarify."

## 6. Action ladder (what a finding can lead to)
Reviewers suggest; editors and institutions decide.
1. **Editorial correction:** small errors that do not change meaning (typo, cross-reference).
2. **Substantial correction:** error affects a number, analysis, or methods description, but a clear correction exists and conclusions survive it.
3. **Expression of concern:** credible concerns exist, evidence is incomplete, or an investigation is not finished. It is not a substitute for a correction when the error is known and specific.
4. **Retraction:** a mechanism to correct the record and protect readers, not a punishment; may be considered when major errors or data/image problems make results and conclusions unreliable, whether honest error or misconduct (COPE retraction guidelines).
The final decision on investigation or retraction belongs to the editorial body or the institution, never to an individual reviewer working from isolated signals. Direct integrity concerns to the journal editor or the institution's research-integrity office (see COPE guidance).

## 7. Completion test
The review is complete when you can answer:
1. What is the paper's central claim?
2. What data support it and can they be traced?
3. Are the design, measurement, and analysis adequate for the question?
4. Are numbers, units, and calculations consistent and re-checkable?
5. Are uncertainty and effect size presented properly?
6. Do conclusions match the strength of evidence and the study's limits?
7. Are there issues with references, overlapping publication, or ethical disclosure?
8. Which errors are fixable and which could change the paper's reliability?
9. What documented evidence supports each finding?
10. Is the language of the report precise, neutral, and non-accusatory?
If an important question cannot be answered for lack of information, the correct finding is to state the gap and ask for clarification, not to assume an answer.

## 8. Arabic terminology
| English | Arabic |
|---|---|
| central claim | الادعاء المركزي |
| internal consistency | الاتساق الداخلي |
| pseudoreplication | التكرار الزائف (معاملة المشاهدات غير المستقلة كأنها مستقلة) |
| double dipping / circular analysis | الاستخدام المزدوج للبيانات / التحليل الدائري |
| confounding | التشويش (العوامل المربكة) |
| batch effect | أثر الدفعة |
| multiple comparisons | المقارنات المتعددة |
| effect size | حجم الأثر |
| confidence interval | فاصل الثقة |
| reporting guideline | قائمة الإبلاغ |
| expression of concern | التعبير عن القلق |
| retraction | السحب |
| correction | التصحيح |
| replicate (biological / technical) | تكرار (بيولوجي / تقني) |
| overlapping publication | النشر المتداخل |
| conflict of interest | تضارب المصالح |
