# Rubric: dimensions, anchors, gates, bands

Contents
1. Dimensions and weights
2. Anchors (0-4) per dimension
3. How D1, D3, D4 are derived from finding verdicts
4. Gates (caps)
5. Ratings-file schema (input to `score.py aggregate`)
6. Bands and structural (provisional) mode

---

## 1. Dimensions and weights

| ID | Dimension | Weight | Question it answers |
|---|---|---|---|
| D1 | Accuracy of findings (precision) | 25 | Of the findings that can be checked, how many are real? |
| D2 | Evidence and traceability | 15 | Can a reader find each issue and reproduce it from what is written? |
| D3 | Coverage of material issues (recall) | 20 | Did the review catch what matters, especially design and analysis flaws? |
| D4 | Severity and confidence calibration | 10 | Do severity and confidence labels match the effect on the claim and the strength of evidence? |
| D5 | Neutral wording and integrity boundary | 10 | Is it free of intent language and accusation, and does it leave integrity decisions to editors? |
| D6 | Honest scope and transparency | 8 | Does it say what was and was not checked, which tools, which limits, and what was found consistent? |
| D7 | Interpretation and actionability | 7 | Bottom line first, reliability of the central claim stated, ordered findings, author questions, action level as suggestion? |
| D8 | Format and language fit | 5 | Template followed, user's language, phone-sized, no padding? |

Total 100. Weights follow the first skill's own priorities: truth and effect on conclusions first, then proof, then coverage, then presentation.

## 2. Anchors (0-4)

Use the anchor that best fits; half points allowed. Score what is in the report, not what you suspect the reviewer meant.

**D1 Accuracy (if not derived)**
- 4: all checkable findings reproduce; none overreach.
- 3: one minor slip (wrong decimal, wrong page) in an otherwise correct set.
- 2: roughly one in five findings fails or overreaches.
- 1: about half fail.
- 0: most fail, or findings are not tied to anything in the paper.

**D2 Evidence and traceability**
- 4: every finding has exact location, the exact text or number, and a calculation or comparison source; quotes match the paper; pages match.
- 3: nearly all; a few locations approximate but flagged as such.
- 2: locations or evidence missing for several moderate+ findings; quotes paraphrased without saying so.
- 1: mostly impressions ("numbers look off", "methods seem weak").
- 0: no locations, or locations/quotes/numbers shown to be wrong or invented (also triggers gate G1).

**D3 Coverage (if not derived)**
- 4: caught all material issues in your reference list; design and analysis flaws included.
- 3: missed only minor/moderate items.
- 2: missed one substantial item, or the whole methods layer was skimmed.
- 1: missed several substantial items, or reviewed language only.
- 0: missed the flaw that determines whether the central claim stands (also triggers gate G3).
For a paper that is genuinely sound on what was checkable, a short review that says so and shows what it checked scores 4.

**D4 Calibration (if not derived)**
- 4: severity tracks effect on the claim; confidence tracks reproducibility; critical used only with strong independent evidence.
- 3: occasional one-level drift.
- 2: systematic inflation or deflation, or high confidence on assumption-dependent findings.
- 1: severity unrelated to effect (typos graded substantial, design flaw graded minor).
- 0: labels absent or arbitrary.

**D5 Neutral wording and integrity boundary**
- 4: describes discrepancies, not people; graded verbs; names alternative legitimate choices; asks for clarification where evidence is incomplete; defers integrity decisions to editors/institutions.
- 3: one or two loaded phrases, no accusation.
- 2: repeated loaded or certain-sounding language ("clearly wrong") where evidence is partial.
- 1: implies bad faith.
- 0: asserts fabrication, falsification, manipulation or fraud without an official finding to attribute (also gate G2).

**D6 Honest scope and transparency**
- 4: states version/file, what was and was not assessed, tools run and their blind spots, route used for reference/retraction checks; has a real "checked and consistent" list; "not assessed" used wherever it applies.
- 3: minor omissions.
- 2: scope partly implied; tools unnamed; consistent items not listed.
- 1: silence reads as full coverage.
- 0: claims checks that were not done (for example "not retracted" from memory; also gate G4).

**D7 Interpretation and actionability**
- 4: bottom line states the central claim and how far it survives the findings; findings ordered by severity; questions for authors resolve flagged issues; action level suggested with reason.
- 3: all present, one weak.
- 2: findings listed without a verdict on the claim, or action level absent.
- 1: a list of issues with no prioritisation.
- 0: no usable conclusion.

**D8 Format and language fit**
- 4: follows the first skill's template; right language; compact table first; minor items grouped; offers a file instead of dumping one.
- 3: small deviations.
- 2: bloated or mixed-up structure; wrong language for terms.
- 1: hard to scan on a phone.
- 0: unusable format.

## 3. How D1, D3, D4 are derived

`score.py aggregate` computes them from your per-finding verdicts unless you give a manual score (manual overrides, with a note).

Verdict weights for precision (D1):
| verdict | counts as | in denominator |
|---|---|---|
| confirmed | 1.0 | yes |
| misgraded (real issue, severity two or more levels off) | 1.0 | yes (penalty goes to D4) |
| partial (core right, detail wrong: page, number, wording) | 0.5 | yes |
| not_error (defensible choice, rounding-level, acceptable) | 0 | yes |
| false_positive | 0 | yes |
| overreach (interpretation beyond evidence, or intent language) | 0 | yes |
| unverifiable | - | no (reported separately) |

Precision -> D1: >=0.95 -> 4; >=0.85 -> 3; >=0.70 -> 2; >=0.50 -> 1; else 0.

Reference-set recall (D3) = severity-weighted share of real issues the review caught, where the reference set = confirmed/partial/misgraded findings + your `missed` list. Weights: minor 1, moderate 2, substantial 4, critical 8. Recall -> D3: >=0.90 -> 4; >=0.75 -> 3; >=0.55 -> 2; >=0.35 -> 1; else 0. Because the reference set includes the review's own correct findings, this is an upper bound on true recall; say so.

Calibration (D4) = share of assessed findings with acceptable severity (`severity_ok` true, one level of tolerance) and `confidence_ok` not false (`"under"` = underconfident, counts 0.5): >=0.90 -> 4; >=0.75 -> 3; >=0.60 -> 2; >=0.40 -> 1; else 0.

## 4. Gates (caps on the final total)

| Gate | Trigger | Cap |
|---|---|---|
| G1 fabricated_evidence | A quote, page, number, or reference in a finding is shown not to exist in the paper or source (not a paraphrase or page-numbering difference) | 60 |
| G2 misconduct_assertion | Asserts or implies fabrication/falsification/fraud/manipulation by the authors without attributing an official finding | 70 |
| G3 missed_overturning_flaw | Misses a flaw that determines whether the central claim stands (for example cell-level tests as sole evidence for a headline DE claim, confounded design) | 75 |
| G4 unverified_integrity_claim | States "not retracted", "no overlap", "no image problems" or similar without a stated route/check | 80 |
| auto: precision < 0.50 | computed | 60 |

Caps use the lowest applicable value. Say which gate fired and why; show the uncapped score too.

## 5. Ratings-file schema (`eval.json`)

```json
{
  "title": "Paper or report name",
  "mode": "full",
  "lang": "en",
  "findings": [
    {"id": "1", "verdict": "confirmed", "severity_claimed": "substantial",
     "severity_ok": true, "confidence_ok": true, "note": "t(28)=2.31 gives p=.028, paper says .08"},
    {"id": "2", "verdict": "false_positive", "severity_claimed": "moderate",
     "severity_ok": false, "note": "pseudobulk used; see Methods p. 4"}
  ],
  "missed": [
    {"desc": "Donors per group not stated; DE at cell level", "severity": "substantial",
     "location": "Methods p. 4, Fig. 2", "evidence": "n = 41,200 nuclei, no donor count"}
  ],
  "scores": {"D2": 3, "D5": 4, "D6": 3, "D7": 3, "D8": 4},
  "notes":  {"D2": "2 of 14 locations approximate", "D5": "no intent language"},
  "gates":  {"fabricated_evidence": false, "misconduct_assertion": false,
             "missed_overturning_flaw": false, "unverified_integrity_claim": false},
  "fixes": ["Add donor counts per group to every DE claim", "Grade finding 4 as moderate"],
  "limits": ["Supplementary table S2 not available"]
}
```
Required manual scores: D2, D5, D6, D7, D8 (and D1/D3/D4 when `findings` is empty or mode is structural). `mode` is `full` or `structural`.

## 6. Bands and structural mode

| Total | Band | Meaning |
|---|---|---|
| 90-100 | Excellent | Reliable; fix cosmetic items only |
| 75-89 | Good | Usable; fix the listed items before relying on it |
| 60-74 | Needs revision | Some findings or labels cannot be trusted as written |
| <60 | Unreliable | Do not use without redoing the flagged parts |

Structural mode (no paper): D1 and D3 are not scored; D4 only if you can judge it from the text; remaining weights are rescaled to 100, the total is capped at 85, and the band is prefixed "Provisional". The sentence "findings not verified against the paper" appears in the headline.
