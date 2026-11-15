# Choosing the reporting guideline

Purpose: compare a paper against the checklist for its design. Missing items are *reporting gaps*, not automatically scientific errors, but a missing item (e.g. no randomisation method, no sample-size rationale) often blocks assessment and replication.

Workflow: identify design -> pick guideline -> walk the checklist -> list missing/contradicted items as findings (severity by effect on assessability). Do not fabricate item numbers from memory; if you need the exact item text, fetch it from EQUATOR (`https://www.equator-network.org/`) or the guideline's own site.

Status column: **VERIFIED** = version/details confirmed by web search while building this skill (Sep 2026). **KNOWN** = standard guideline from general knowledge; confirm the current version on EQUATOR before citing item counts or years.

| Design | Guideline | Notes | Status |
|---|---|---|---|
| Randomised trial | **CONSORT 2025** (30-item checklist + flow diagram) | Supersedes CONSORT 2010, which should no longer be used. Published in BMJ, JAMA, Lancet, Nat Med, PLoS Med (Apr 2025). | VERIFIED |
| Trial protocol | **SPIRIT 2025** | Companion to CONSORT 2025. | VERIFIED |
| Clinical prediction model (regression or ML) | **TRIPOD+AI** (BMJ 2024;385:e078378; 27 items) | Supersedes TRIPOD 2015. Risk-of-bias companion: **PROBAST+AI** (BMJ 2025;388). | VERIFIED |
| Animal experiments | **ARRIVE 2.0** (2020): "Essential 10" + "Recommended Set" (11) = 21 items | Essential 10 = study design, sample size, inclusion/exclusion, randomisation, blinding, outcome measures, statistical methods, experimental animals, experimental procedures, results. | VERIFIED (counts); item list KNOWN |
| Quantitative real-time PCR | **MIQE 2.0** (Clin Chem 2025) | Revises the 2009 MIQE; covers sample handling, assay design/validation, data analysis. | VERIFIED |
| Systematic review / meta-analysis | PRISMA 2020 (27 items) | Also: AMSTAR 2 for appraising reviews; RoB 2 / ROBINS-I for included studies. | KNOWN |
| Observational (cohort, case-control, cross-sectional) | STROBE | Genetic association extension: STREGA. | KNOWN |
| Diagnostic accuracy | STARD 2015 | AI extension STARD-AI in preparation as of TRIPOD+AI publication. | KNOWN |
| Qualitative | COREQ (interviews/focus groups), SRQR | | KNOWN |
| Case report | CARE | | KNOWN |
| Economic evaluation | CHEERS 2022 | | KNOWN |
| Quality improvement | SQUIRE 2.0 | | KNOWN |
| Functional genomics / microarray / sequencing | MIAME / MINSEQE (data deposition) | Also check accession numbers resolve. | KNOWN |
| No matching guideline | Search the EQUATOR library; otherwise use generic taxonomy in `error-taxonomy.md` | | - |

## Trial-specific checks worth doing even without the full checklist (from the guide)
Randomisation method and allocation concealment; blinding and who was blinded; primary outcome pre-specified and matching the registry; flow of participants with numbers at every stage; deviations from protocol; harms reported; analysis population (ITT vs per-protocol) stated; results for all pre-specified outcomes.

## Risk-of-bias tools (appraising, not reporting)
RoB 2 for randomised trials; ROBINS-I for non-randomised interventions; PROBAST(+AI) for prediction models; AMSTAR 2 for systematic reviews. Use them when the user asks "how reliable is the evidence", not for line-level error hunting.
