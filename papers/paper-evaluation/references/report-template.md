# Evaluation report template and wording

Contents
1. Skeleton
2. Scorecard table
3. Finding-audit table and per-finding note
4. Omission entry
5. Fix-list entry
6. Wording rules
7. Arabic version and glossary

---

## 1. Skeleton (write in the user's language; lead with the verdict)

1. **Verdict line**: `Score X/100 (band). Mode: full audit | provisional structural audit.` One sentence on reliability: can the review be relied on as written, and for what? Mention any gate that fired and the uncapped score.
2. **Scorecard** (section 2).
3. **Top strengths and top weaknesses**: two lines each, most consequential first.
4. **Finding audit** (section 3): counts by verdict first (confirmed / partial / not_error / false_positive / overreach / unverifiable), then a compact table; full notes only for items that are not confirmed, and for critical/substantial confirmed ones if brief.
5. **Omissions** (section 4): each with location and evidence; say recall is against your reference list.
6. **Calibration and wording flags**: severity inflation/deflation pattern, confidence issues, loaded phrases with location.
7. **Fix list**: at most 7, ordered by effect on the report's reliability.
8. **Limits of this evaluation**: files not seen, items unverifiable, sampled vs complete, whether the report was produced in the same conversation.

Phone-sized screens: items 1-2 fit one screen; keep tables to 3-4 columns; group confirmed minor findings in one line ("14 minor findings checked: 13 confirmed, 1 partial").

## 2. Scorecard table

| Dimension | Score (0-4) | Weight | Points | Why (one line) |
|---|---|---|---|---|
| D1 Accuracy | 3.5 | 25 | 21.9 | 12 of 13 checkable findings confirmed |
| D2 Evidence | 3.0 | 15 | 11.3 | locations exact except 2 approximate |
| D3 Coverage | 2.0 | 20 | 10.0 | missed donor-level replication issue |
| D4 Calibration | 3.0 | 10 | 7.5 | one critical should be moderate |
| D5 Wording | 4.0 | 10 | 10.0 | neutral throughout |
| D6 Scope | 3.0 | 8 | 6.0 | tools named; no "not assessed" list |
| D7 Actionability | 3.0 | 7 | 5.3 | action level present, no claim verdict |
| D8 Format | 4.0 | 5 | 5.0 | template followed |

## 3. Finding-audit table and note

| # | Verdict | Severity (review -> yours) | Note |
|---|---|---|---|
| 1 | confirmed | substantial -> substantial | sum is 258 not 248 (Table 2) |
| 4 | false_positive | moderate -> n/a | pseudobulk per donor, Methods p. 5 |
| 7 | overreach | substantial -> moderate | 120 vs 96 is real; "manipulated" is not supported |

For each non-confirmed finding give: what the paper actually says (location, short quote under 15 words or the number), what the review said, what to change.

## 4. Omission entry

```
Missed #: <id>
Location: <page/section/table/figure>
Issue: <one sentence>
Evidence: <number, quote under 15 words, or calculation>
Your severity: minor / moderate / substantial / critical
Why a review of this scope should have caught it: <one clause>
```

## 5. Fix-list entry

`<change to make> | because <finding or omission id> | effect: <which dimension improves>`

Example: `Add donor count per group beside every DE statement | because omission M1 | effect: D3, D7`.

## 6. Wording rules

- Describe the report's content, not the reviewer's character or motives. "The quoted sentence does not appear on page 4" not "the reviewer made it up".
- Same no-intent rule applies to the paper's authors: report discrepancies, not conduct.
- Use "does not reproduce", "not found at the stated location", "needs clarification" where evidence is partial.
- Graded verbs for your own conclusions ("suggests", "is consistent with") and say what would change your mind.
- Say "not assessed" or "unverifiable" for what you could not check; never leave silence to imply coverage.
- Give praise only where it is earned and specific; do not pad.
- Name the legitimate alternative whenever you rate something `not_error`.

## 7. Arabic version and glossary

Arabic skeleton: **الحكم** (الدرجة من 100، التصنيف، نمط التقييم: كامل / أولي بنيوي) -> **بطاقة الدرجات** -> **أبرز نقاط القوة والضعف** -> **تدقيق الملاحظات** -> **ما فات المراجعة** -> **المعايرة والصياغة** -> **قائمة الإصلاح** -> **حدود هذا التقييم**.

| English | Arabic |
|---|---|
| evaluation | تقييم |
| scorecard | بطاقة الدرجات |
| precision (share of findings that are real) | الدقة (نسبة الملاحظات الصحيحة) |
| recall / coverage | التغطية (نسبة المشكلات المهمة التي رُصدت) |
| confirmed | مؤكَّدة |
| partially correct | صحيحة جزئيًا |
| not an error (defensible choice) | ليست خطأ (خيار مقبول) |
| false positive | إنذار خاطئ |
| overreach | تجاوز للدليل |
| unverifiable | تعذّر التحقق |
| severity calibration | معايرة درجة الأثر |
| confidence calibration | معايرة درجة الثقة |
| gate / cap | سقف الدرجة |
| reference list | قائمة مرجعية |
| fix list | قائمة الإصلاح |
| provisional (structural audit) | أولي (تدقيق بنيوي) |
| false reassurance | طمأنة خاطئة |
| seeded errors | أخطاء مزروعة للاختبار |
