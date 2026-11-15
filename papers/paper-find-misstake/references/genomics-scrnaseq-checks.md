# Genomics / transcriptomics / single-cell checks

Load this file when the paper involves RNA-seq, single-cell or single-nucleus RNA-seq (scRNA-seq / snRNA-seq), enrichment analysis, network inference, or any omics pipeline. These are the errors that generic statistics checklists miss.

Contents
A. Unit of replication (pseudoreplication)
B. Double dipping (circular analysis)
C. Batch, donor, and covariate confounding
D. Preprocessing and QC reporting
E. Cell-type annotation and composition
F. Multiple testing, thresholds, enrichment
G. Trajectory / pseudotime
H. Gene identifiers and spreadsheet corruption
I. Networks (PPI / GRN)
J. Sex-stratified and subgroup claims
K. Data, code, versions
L. Machine-learning add-on
M. Cell-cell communication and chromatin accessibility

Evidence tags: **[lit]** = supported by a cited paper in `sources.md`; **[std]** = standard practice from general methodological knowledge (no single citation).

---

## A. Unit of replication (pseudoreplication) [lit]
Cells/nuclei from one donor are not independent replicates of the condition. Treating each cell as a sample in a cell-level test (e.g. Wilcoxon on cells) ignores between-donor variation, inflates confidence, and favours highly expressed genes (Squair et al. 2021, Nat Commun 12:5692). Pseudobulk aggregation per donor and cell type followed by edgeR/DESeq2/limma-type models performed best in benchmarks (Squair 2021; Murphy & Skene 2022). An eLife reanalysis of the first Alzheimer's snRNA-seq dataset reported that under the original cell-level (pseudoreplication) analysis the number of DEGs per cell type tracked cell counts almost perfectly, a pattern absent in the pseudobulk reanalysis (eLife 2023, RP90214).

Red flags:
- "n" in the statistics is the number of cells/nuclei; donors are not stated per group.
- Thousands of DEGs from a handful of donors per group.
- DEG count tracking cell-type abundance (more cells -> more DEGs).
- Donor count per group <= 3 with strong claims.
Ask: donors per group, cells per donor per cell type, whether donor is a random effect or pseudobulk unit, minimum cells per donor-cell type.
Severity guide: cell-level testing as the sole evidence for a headline DE claim = **substantial to critical for that claim** (it does not by itself make other analyses invalid).

## B. Double dipping (circular analysis) [lit]
Clustering on the expression data and then testing the same genes/data for DE between those clusters gives inflated p-values even under the null (Neufeld et al. 2024, Biostatistics 25:270; Lähnemann et al. 2020 list it among grand challenges). The same applies to testing genes along a pseudotime estimated from the same data. Remedies in the literature: count splitting / data thinning, selective-inference corrections. Seurat's own documentation warns that p-values for cluster markers should be interpreted cautiously.
Red flags: cluster-marker p-values presented as confirmatory evidence; DE between clusters defined by those same genes; "significant along pseudotime" without correction.
Not a flaw: using cluster markers descriptively to name clusters, if not claimed as inferential.

## C. Batch, donor, and covariate confounding [std]
- Condition perfectly confounded with batch, sequencing run, library prep day, or site -> group effect cannot be separated from batch. Ask for a donor x batch x condition table.
- Sex, age, post-mortem interval, RNA quality, APOE genotype, and pathology staging unbalanced between groups and not modelled (human brain studies).
- Integration/batch-correction applied, then DE done on corrected values without justification; over-correction removing real biology.
- AD vs control defined how (clinical diagnosis, Braak, CERAD, combined criteria)? Criteria stated and applied consistently?
- Sex and age ratio differ between disease groups and are not modelled: a sex-vs-disease overlap can arise without any biology.

## D. Preprocessing and QC reporting [std]
Nuclei before/after QC per donor (must reconcile with counts in text/figures); thresholds for genes/UMIs/mitochondrial or ribosomal fraction; ambient RNA and doublet handling; normalisation; number of HVGs, PCs, clustering resolution; integration method; software and versions; random seeds. Numbers of nuclei in abstract vs methods vs figure legends must agree.

## E. Cell-type annotation and composition [std]
- Annotation supported by named marker genes and a reference, not by cluster number alone; annotation after clustering on the same data is descriptive.
- Proportion differences tested at donor level with methods suited to compositional data; proportions of one type change when another changes.
- Tiny clusters driving conclusions; clusters that correspond to donor/batch.

## F. Multiple testing, thresholds, enrichment [std]
- FDR (e.g. Benjamini-Hochberg) across all tested genes; thresholds for logFC and adjusted p stated; "significant" not based on nominal p across 10^4 genes.
- Over-representation analysis needs the right background (genes actually tested/expressed), not the whole genome; state database versions, ID mapping, multiple-testing correction across terms, and term redundancy handling.
- GSEA vs ORA choice justified; gene-set ranking metric stated.
- Reported enrichment not cherry-picked from many libraries without correction.
- Features chosen in one dataset and tested in another is cross-assay, not circular. It still needs held-out validation.

## G. Trajectory / pseudotime [std]
Trajectory inference (e.g. Slingshot, Monocle) is exploratory: root/start cluster choice, number of lineages, and dimensionality-reduction dependence must be stated. UMAP/t-SNE distances and cluster sizes are not quantitative. "Progression" claims from a cross-sectional snapshot are hypotheses about ordering, not observed time. DE along pseudotime is subject to double dipping (B).

## H. Gene identifiers and spreadsheet corruption [lit]
Excel with default settings converts symbols such as SEPT2 or MARCH1 to dates; about one-fifth of genomics papers with supplementary Excel gene lists were affected (Ziemann et al. 2016, Genome Biol 17:177), and the problem continued to accumulate (Abeysooriya et al. 2021, PLoS Comput Biol). HGNC later renamed affected human genes (e.g. MARCH1 -> MARCHF1, SEPT1 -> SEPTIN1).
Check supplementary tables for date-like or scientific-notation strings in gene columns (e.g. "1-Mar", "2-Sep", "2.31E+13"); mixed human/mouse capitalisation; Ensembl ID versions; genome build/annotation version (GRCh37/hg19 vs GRCh38) consistent across steps; ortholog mapping if species differ.

## I. Networks (PPI / GRN) [std]
- Network inference output is a prediction; edges are not demonstrated regulation without orthogonal validation (ChIP, perturbation, curated TF-target databases).
- Database names, versions, evidence thresholds (e.g. interaction score cut-off) stated; TF annotation source stated.
- Hub/centrality claims need a null (degree-preserving randomisation or comparison with random gene sets).
- Network seeded from DEGs inherits every upstream error in A-C.

## J. Sex-stratified and subgroup claims [std]
"Significant in males, not in females" is not evidence of a sex difference; test the interaction or contrast directly. Report donors per sex per group; small strata give unstable DE and enrichment.
Two-list overlap (RRHO, Venn): lists that share samples are not independent (balance: see C).

## K. Data, code, versions [std]
Accession numbers (GEO, EGA, Synapse/controlled-access portals) resolve and match the analysed cohort; if access is controlled, the access route is stated; code repository and package versions available; processed object or count matrices deposited.

## L. Machine-learning add-on [std; see TRIPOD+AI in reporting-guidelines.md]
Data leakage (feature selection or normalisation before train/test split; same donor in train and test); no independent external validation; metric unsuited to class imbalance (accuracy); no calibration or uncertainty; hyper-parameters tuned on the test set; no comparison with a simple baseline.

## M. Cell-cell communication and chromatin accessibility [std]
CellChat or ATAC differences need a named test, donors per group and n per group. Probabilities and peak plots alone are descriptive. A claim built on them (for example "supports diagnosis") needs that test.
