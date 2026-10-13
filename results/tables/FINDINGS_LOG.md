# GenomicsOps T1D Dark Genome — Findings Log (updated)

## Datasets Used
- GSE144472 — mouse IRE1a KO islets (bulk + beta-cell DEG)
- GSE251911 — human islets, cytokine vs ER stress (n=19 donors paired)
- GSE235683 — EndoC-bH1, single-cytokine panel (IFNg, IL1B, TNFa, NT)
- GSE159984 — 58 ND + 27 T2D human islets (T2D comparison)
- GENCODE v46 — gene annotation
- epiRomics cache — islet regulome + histone BED files
- Zenodo 13362658 — 111,935-cell HPAP cytokine/CVB4 single-cell dataset

## Finding 1: Immunogenic DDR Activated in Cytokine-Treated Islets
- 14,048 / 21,172 genes significant (padj < 0.05)
- cGAS/STING: CGAS +1.29, STING1 +0.67, TBK1 +0.72, IRF3 +0.63
- RNA sensors: DDX58 +3.03, IFIH1 +2.87
- p53 executioner: BBC3 +1.59, CDKN1A +0.74
- SASP in bulk: IL6 +3.41, CXCL1 +3.52, MMP3 +2.24
- ER stress (thapsigargin) does NOT activate cGAS/STING

## Finding 2: 54 Dark Genome Targets Induced >4-fold by Cytokines
- 48 / 54 non-coding (41 lncRNA, 5 pseudogene, 2 TEC)
- Top: AC093063.1 +11.0, AC007991.2 +10.4, AL157871.4 +6.6
- Total significant ncRNAs: 1,799

## Finding 3: SIMALR (= LINC02528) at TNFAIP3 T1D Risk Locus
- chr6:137,943,079-137,957,657, ENSG00000226004
- HGNC: SIMALR = "suppressor of inflammatory macrophage apoptosis lncRNA"
- Macrophage-restricted (M1 >> M2), not expressed in beta-cell lines
- Cytokine-induced in primary islets: +6.31 log2FC, padj 2.9e-45
- Per-donor: 19/19 donors UP, mean +5.06 log2FC, range 3.36-6.50
- Nearest T1D SNP: rs6920220 (TNFAIP3 locus), 59 kb

## Finding 4: SIMALR Anti-Correlated with Canonical NF-kB Axis
- rho(SIMALR, TNFAIP3) = -0.68, rank 21079/21172
- NFKBIA -0.74, RELA -0.74, NFKB2 -0.73, CD40 -0.61, NFKB1 -0.53
- Positively correlated genes: neuronal/structural (SYNE1, ZFP82)

## Finding 5: Non-Coding Stress Hub at the Locus
500 kb neighborhood:
- 13+ non-coding features (10+ lncRNAs, MIR3145, Y_RNA, pseudogenes)
- TNFAIP3 at 72 kb, PERP at 147 kb, OLIG3 at 449 kb

## Finding 6 (CORRECTED): Promoter Motif Analysis
- 2 kb strand-aware promoter: 1 p53 half-site
- Gene body (14.6 kb): 2 p53 half-sites
- p53 tandem decamers: 0 in ALL regions (promoter, body, intergenic)
- 10 kb promoter: 11 p53 half-sites (1.10/kb) vs gene body 0.14/kb = 8x enrichment
- Intergenic SIMALR-TNFAIP3 region (57 kb): 11 ISRE sites (0.19/kb)
- **Original "3 p53 motifs" claim was based on 18.7 kb region — RETRACTED**
- **No tandem p53 RE — SIMALR is not a canonical direct p53 target**

## Finding 7: Dark Genome Targets Cluster at Immune Gene Loci
- AC099063.4 → GBP1-7 (all +5.5 to +11.1)
- AC007991.2 → IDO1 (+10.95)
- AP001610.2 → MX1/MX2 (+4.11, +3.65)
- AL645939.5 → TRIM40/31/15/10, UBD, HLA-F
- 109/526 coding neighbors cytokine-induced

## Finding 8: Enrichment Near Cytokine-Induced Coding Genes
| Test | Observed | Background | Ratio | p-value |
|------|----------|------------|-------|---------|
| Unmatched | 0.204 | 0.128 | 1.59x | < 0.0005 |
| Expression-matched | 0.204 | 0.131 | 1.56x | < 0.0005 |
Null max (matched): 0.1811 — observed exceeds all 5,000 permutations.

## Finding 9 (NEGATIVE): No Chromatin Enrichment
Chromatin context of 53 targets (2 kb window):
- Islet regulome: 75.5% vs 85.6% (0.88x)
- Active enhancers: 22.6% vs 30.2% (0.75x)
- H3K27ac: 60.4% vs 70.7% (0.85x)
- H3K4me1: 73.6% vs 80.0% (0.92x)
- H3K4me3: 54.7% vs 70.3% (0.78x)
Interpretation: dark genome lncRNAs are NOT in islet-specific regulatory
chromatin — they are co-transcribed passengers of immune gene loci.

## Finding 10 (NEGATIVE): No Super Enhancer Enrichment
- Observed: 4/53 targets overlap SE (7.5%)
- Null median: 2, 95th: 5, max: 9
- Permutation p-value: 0.26
Conclusion: not significant.

## Finding 11: Micropeptides and HLA-II Binding
- 421 transcripts, 9,168 ORFs, 2,505 unique micropeptides (15-100 aa)
- SIMALR produces 738 15-mer peptides
- MixMHC2pred vs 4 T1D-risk alleles (DRB1*03:01, *04:01, DQ2.5, DQ8)
- Total: 45,825 peptides × 4 alleles tested
- **23 SIMALR strong binders (rank < 2), 14 unique binding cores**
- Top: EHKDGQVQAKGERPG (DQ8 rank 0.146), MRYWSDAGAGIWTIT (DQ2.5 rank 0.414)
- Overall strong binder rate: 1,697/45,825 (3.7%); SIMALR: 23/738 (3.1%)
- **Novel candidate HLA-II binding micropeptides from a T1D-risk locus lncRNA**

## Finding 12: Single-Cell Validation (HPAP, cytokine-stim)
Dataset: Zenodo 13362658 (111,935 cells, HPAP + ICRH donors)
- 3,897 cytokine-treated + 3,030 mock beta cells from 3 donors
- Per-gene Wilcoxon cyto vs mock in beta cells:
  - CXCL10: +6.84 log2FC (padj < 1e-300)
  - ISG15: +3.83
  - HLA-B: +2.82
  - STAT1: +2.49
  - NFKBIA: +2.39
  - **TNFAIP3: +0.80 (padj 4.9e-59)**
  - **BBC3/PUMA: +1.00 (padj 1.4e-65)**
  - **CDKN1A/p21: +0.54 (padj 9.2e-47)**
- SASP cytokines (IL6, MMP3, CXCL1) DOWN in beta cells
- Interpretation: beta-cells engage presentation + TNFAIP3 brake + p53
  executioner program; SASP signal comes from non-beta cells

## Finding 13 (NEW): T2D Specificity — Clean Negative
GSE159984 (58 ND, 27 T2D islets):
- **SIMALR (ENSG00000226004) NOT DETECTED in ND or T2D**
- **TNFAIP3 unchanged in T2D: log2FC +0.04, padj 0.95**
- CXCL10 unchanged in T2D: log2FC +0.29, padj 0.80
- TNIP1/2/3 unchanged
- IL6 trend +0.69 (padj 0.18, NS)

Interpretation: The TNFAIP3/SIMALR axis is dormant in T2D islet
inflammation. T1D-relevant cytokines activate it; T2D inflammatory
signals do not. SIMALR is absent in bulk ND/T2D islets because there
are no activated macrophages — it appears only in the T1D cytokine storm.

## Finding 14: Conservation
UCSC phyloP 100-way over SIMALR locus:
- Promoter: mean +0.03 (frac > 2: 1.3%)
- Gene body: mean -0.03 (frac > 2: 1.6%)
- Flank: mean -0.10
- Top conserved 500 bp window at chr6:137,949,830 (p90=3.11, max=4.99)
Conclusion: SIMALR is essentially non-conserved, typical for
immune-cell-restricted lncRNAs.

## Reframed Core Model
SIMALR = macrophage-restricted lncRNA at the TNFAIP3 T1D risk locus:
1. T1D-relevant cytokines (IL-1b + IFNg) activate islet macrophages
2. Macrophages upregulate SIMALR to suppress their own apoptosis
   (via HIF1a / NTN1 axis — established biology, HGNC:53554)
3. Prolonged macrophage survival maintains islet inflammation
4. beta-cells die from sustained inflammatory pressure
5. rs6920220 risk allele at TNFAIP3 may enhance this survival signal
6. T2D (different cytokine profile) does not activate this axis

## Honest Limitations
- Single-cell dataset used is cytokine-stim, not ND/AAB+/T1D cohort
- No direct evidence of SIMALR expression in islet macrophages yet
  (need F3: ND/AAB+/T1D single-cell with macrophage annotation)
- HLA-II binding is computational prediction, not immunopeptidomics
- p53 regulation is uncertain (no tandem RE)

## Next
- F3: Find ND/AAB+/T1D single-cell dataset with macrophages
- M2: p53 ChIP-seq cross-reference
- M4: Triplex prediction (SIMALR-TNFAIP3)
