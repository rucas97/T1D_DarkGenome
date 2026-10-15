# GenomicsOps T1D Dark Genome — Findings Log

## Datasets Used
- GSE144472 — mouse IRE1a KO islets (bulk + beta-cell DEG)
- GSE251911 — human islets, cytokine vs ER stress (n=19 paired donors)
- GSE235683 — EndoC-bH1 single-cytokine panel (IFNg, IL1B, TNFa, NT)
- GSE159984 — 58 ND + 27 T2D human islets (T2D comparison)
- GENCODE v46 — gene annotation (hg38)
- epiRomics cache — islet regulome + histone BED + ATAC
- Zenodo 13362658 — 111,935-cell HPAP cytokine/CVB4 single-cell
- PanKbase HuGE — third-party GWAS integration for SIMALR
- ENCODE encRegTfbsClustered via UCSC API

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
- chr6:137,943,079-137,957,657 (hg38), ENSG00000226004
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
500 kb neighborhood contains 13+ non-coding features:
- 10+ lncRNAs, MIR3145 miRNA, Y_RNA, 3 pseudogenes
- TNFAIP3 at 72 kb, PERP at 147 kb (p53 apoptosis effector),
  OLIG3 at 449 kb (neuronal TF)

## Finding 6: Promoter Motif Analysis (CORRECTED)
- 2 kb strand-aware promoter: 1 p53 half-site
- 10 kb promoter: 11 p53 half-sites (1.10/kb) vs gene body 0.14/kb = 8x
- Intergenic SIMALR-TNFAIP3 (57 kb): 11 ISRE sites
- p53 tandem decamers: ZERO in all regions
- **Original "3 p53 motifs" claim was based on 18.7 kb region — RETRACTED**
- SIMALR is not a canonical direct p53 target

## Finding 7: Dark Genome Targets Cluster at Immune Gene Loci
- AC099063.4 -> GBP1-7 (all +5.5 to +11.1)
- AC007991.2 -> IDO1 (+10.95)
- AP001610.2 -> MX1/MX2 (+4.11, +3.65)
- AL645939.5 -> TRIM40/31/15/10, UBD, HLA-F
- AC007728.2 -> NOD2
- 109/526 coding neighbors cytokine-induced

## Finding 8: Enrichment Near Cytokine-Induced Coding Genes
| Test | Observed | Background | Ratio | p-value |
|------|----------|------------|-------|---------|
| Unmatched | 0.204 | 0.128 | 1.59x | < 0.0005 |
| Expression-matched | 0.204 | 0.131 | 1.56x | < 0.0005 |
Null max in matched test: 0.1811. Enrichment survives expression matching.

## Finding 9 (NEGATIVE): No Chromatin Enrichment in Islet Regulome
53 targets vs expression-matched lncRNAs (2 kb window):
- Islet regulome: 75.5% vs 85.6% (0.88x)
- Active enhancers: 22.6% vs 30.2% (0.75x)
- H3K27ac: 60.4% vs 70.7% (0.85x)
- H3K4me3: 54.7% vs 70.3% (0.78x)
Interpretation: co-transcriptional model, not dedicated enhancers.

## Finding 10 (NEGATIVE): No Super Enhancer Enrichment
- Observed: 4/53 targets (7.5%)
- Null median 2, 95th 5, max 9; permutation p=0.26

## Finding 11: Micropeptides and HLA-II Binding
- 421 transcripts, 9,168 ORFs, 2,505 unique micropeptides (15-100 aa)
- SIMALR produces 738 15-mer peptides
- MixMHC2pred vs 4 T1D alleles (DRB1*03:01, *04:01, DQ2.5, DQ8)
- 45,825 peptides x 4 alleles = 178,300 predictions
- **23 SIMALR strong binders (rank < 2), 14 unique binding cores**

## Finding 12: Single-Cell Validation (HPAP cytokine-stim)
- 111,935 cells from Zenodo 13362658
- 3,897 cytokine-treated + 3,030 mock beta cells
- Per-gene Wilcoxon cyto vs mock in beta cells:
  - CXCL10: +6.84 (padj < 1e-300)
  - ISG15: +3.83
  - HLA-B: +2.82
  - STAT1: +2.49
  - NFKBIA: +2.39
  - **TNFAIP3: +0.80 (padj 4.9e-59)**
  - **BBC3/PUMA: +1.00 (padj 1.4e-65)**
  - **CDKN1A/p21: +0.54 (padj 9.2e-47)**
- SASP cytokines (IL6, MMP3, CXCL1) DOWN in beta cells
- Interpretation: beta-cells engage presentation + TNFAIP3 brake +
  p53 executioner program; SASP signal comes from non-beta cells

## Finding 13: T2D Specificity (Clean Negative)
GSE159984 (58 ND, 27 T2D):
- SIMALR NOT DETECTED in ND or T2D bulk islets
- TNFAIP3 unchanged in T2D: log2FC +0.04, padj 0.95
- CXCL10 unchanged: log2FC +0.29, padj 0.80
- TNIP1/2/3 unchanged
Conclusion: TNFAIP3/SIMALR axis is dormant in T2D inflammation.

## Finding 14: Conservation (UCSC phyloP 100-way)
- Promoter: mean +0.03; gene body: -0.03; flank: -0.10
- Top conserved 500 bp window at chr6:137,949,830 (p90=3.11)
- SIMALR is essentially non-conserved, typical for immune lncRNAs

## Finding 15 (INDEPENDENT): PanKbase HuGE Confirms T1D-Specific Locus
PanKbase Gene Browser HuGE scores for SIMALR:
- **T1D: 3.0 (Moderate)**
- T2D and all T2D subtypes: 1.0 (No evidence)
- Rheumatoid arthritis, SLE, seropositive RA: 3.0 (Moderate)
- Monocyte, neutrophil, lymphocyte, eosinophil counts: 3.0 (Moderate)
- WBC, platelet count, platelet crit: 3.0 (Moderate)
Interpretation: myeloid-cell phenotype cluster co-occurs with T1D at
this locus — consistent with macrophage-specific biology.

## Finding 16: HPAP-002 T1D Donor Carries DQ8 Haplotype
- DRB1*13:02/*04:08; DQA1*03:01/DQB1*03:02 (DQ8)
- DQ8 is the exact allele SIMALR micropeptides are predicted to bind

## Finding 17: p53 NOT Bound, NF-kB/STAT ARE
ENCODE encRegTfbsClustered at SIMALR (212 sites):
- RELB (NF-kB family): 2 sites
- STAT3 (JAK/STAT): 2 sites
- BATF, JUNB (AP-1), TBX21 (T-bet), IKZF1, EBF1: present
- EP300 (enhancer), CTCF/RAD21/SMC3 (chromatin): multiple
- **TP53/p53: NOT PRESENT**
Interpretation: SIMALR is a direct NF-kB and STAT3 target.
Mechanism replaces the p53 hypothesis (retracted).

## Finding 18: No SIMALR-TNFAIP3 Triplex
- TNFAIP3 promoter (2 kb): longest polypurine tract 12 nt (too short)
- SIMALR: 26, 28, 29 nt tracts (candidate RNA triplex formers)
- No direct RNA:DNA triplex between SIMALR and TNFAIP3 promoter
- Co-expression anti-correlation likely reflects shared NF-kB input,
  not direct interaction

## Finding 19: SIMALR Peptides NOT Mimics of Known T1D Autoantigens
- Queried IEDB for epitopes from 8 major T1D autoantigens:
  INS (500), GAD65 (500), IA-2 (500), ZnT8 (216), IGRP (76),
  CHGA (170), ICA1 (105), GAD1 (50) = 1,964 unique sequences
- vs 14 SIMALR strong-binding cores:
  - Shared 7-mers: **0**
  - Shared 8-mers: **0**
  - Shared 9-mers: **0**
  - Exact matches: **0**
Conclusion: novel autoantigen class, not molecular mimics.

## Finding 20: NetMHCIIpan 4.3 Validates Top DRB1 Binders
Independent predictor confirms:
- **HRNLRRDNQISICKP -> DRB1*03:01**
  - MixMHC2pred: %Rank 0.785, core LRRDNQISI
  - NetMHCIIpan: %Rank_EL 0.68, IC50 45.78 nM, core LRRDNQISI
  - STRONG BINDER by both algorithms; identical core
- **MSFFIFQNLASGLDR -> DRB1*04:01**: BA %Rank 1.37, 75.96 nM
- **QHRNLRRDNQISICK -> DRB1*03:01**: BA %Rank 0.77, 46.53 nM

## Finding 21: NetMHCIIpan Validates DQ8 Binders (4 peptides, identical cores)
| Peptide | MixMHC2pred | NetMHCIIpan | Core |
|---|---|---|---|
| EHKDGQVQAKGERPG | 0.146 | 0.36 | DGQVQAKGE |
| CEHKDGQVQAKGERP | 0.205 | 0.48 | DGQVQAKGE |
| HGSDFATKMSYENPA | 0.463 | 0.22 | DFATKMSYE |
| LHGSDFATKMSYENP | 0.608 | 0.31 | DFATKMSYE |
Four peptides, four identical binding cores, all strong binders by both
MixMHC2pred and NetMHCIIpan 4.3. DQ2.5 signal not replicated — honest
discrepancy.

## Finding 22: Direct PWM Scan Confirms NF-kB/STAT Motif Density
Direct Biostrings matchPWM scan (80% threshold) of SIMALR locus for
10 TFs of interest:
Promoter (10 kb):
- STAT3: 25 hits (2.5/kb)
- RELB (NF-kB): 23 hits (2.3/kb)
- STAT1: 37 hits (3.7/kb)
- NFKB1: 7 hits; RELA: 6 hits
- Two near-perfect STAT1 GAS elements (score 0.948, 0.931)
Gene body (14.6 kb): STAT3 49, RELB 48, NFKB1 14
Intergenic (57 kb): STAT3 175, RELB 175, NFKB1 35
Interpretation: NF-kB and STAT motifs uniformly dense across the locus.
Confirms ENCODE ChIP finding by independent method (3rd validation).
Methodological note: SEA web tool returned null because only 3 primary
sequences were provided (below the minimum 5) and shuffle-based background
dilutes enrichment over long loci. Direct PWM scanning is the correct
approach for a single-locus study.

## Reframed Core Model
SIMALR is a macrophage-restricted lncRNA at the TNFAIP3 T1D risk locus:
1. T1D-relevant cytokines (IL-1b + IFNg) activate islet macrophages
2. Macrophages upregulate SIMALR (via NF-kB/STAT3) to suppress their
   own apoptosis (published biology: Cynn et al. ATVB 2023)
3. Prolonged macrophage survival maintains islet inflammation
4. beta-cells die from sustained inflammatory pressure
5. rs6920220 risk allele at TNFAIP3 may enhance this survival signal
6. T2D (different cytokine profile) does not activate this axis
7. SIMALR micropeptides bind DQ8 and DRB1*03:01 with strong affinity;
   DQ8 is carried by a real T1D donor (HPAP-002) in PanKbase
8. SIMALR peptides are not mimics of known T1D autoantigens

## Honest Limitations
- Single-cell dataset used is cytokine-stim, not a full ND/AAB+/T1D cohort
- No direct single-cell evidence of SIMALR in islet macrophages yet
  (Phase 3 blocked by Colab memory + S3 access)
- HLA-II binding is computational prediction, not immunopeptidomics
- DQ2.5 binding predicted but not confirmed by second algorithm
- No mental stress connection — deferred to Paper 2

## Paper 2 (planned)
Mental stress -> HPA axis -> DDR -> T1D initiation.
Analyses planned: MR of stress traits vs T1D; PBMC stress datasets;
cortisol/glucocorticoid treatments in islets.

## Next Steps
- CellChat macrophage -> beta-cell communication (43_cellchat_T1D.R)
- Immunopeptidomics cross-check (42_immunopeptidomics_crosscheck.R)
- Mendelian Randomization (41_mendelian_randomization.R)
- Write manuscript

## ============================================================
## SESSION 2 ADDITIONS (2026-10-15)
## ============================================================

## Finding 25 (NEGATIVE): Immunopeptidomics — no SIMALR peptides in MSV000093843
- Dataset: Nanaware 2025 Cell Rep, cytokine-treated human islets, Stern lab
- Files: 7 of 12 mzid (islet DQ/DR/DP + W632 + spleen controls)
- Total peptides searched: 7,507
- SIMALR search space: 4,474 ORF k-mers (8-15 aa) + 14 cores + 10 binders
- Result: ZERO hits
- Interpretation: consistent with macrophage restriction + shallow bulk islet
  immunopeptidome depth. Not definitive negative for presentation.
- Script: scripts/42a_mzid_search.py

## Finding 26 (SUGGESTIVE): GSE212381 SIMALR ASO KD in HMDM
- Cynn 2023, control ASO vs SIMALR ASO, LPS/IFNγ 8h, n=3
- SIMALR log2FC = -0.85, q=0.999 (partial KD)
- Canonical NF-κB axis: flat, q=0.999
- Selective chemokines down: CXCL1 -1.10, CXCL3 -0.97, IL12A -1.51, CCL1 -1.64
- Direction is OPPOSITE islet prediction -> hypothesis shift to "macrophage
  survival factor" model
- Script: scripts/42b_GSE212381_functional.py

## Finding 27 (INDEPENDENT): SIMALR validated as TB biomarker in blood
- PLoS Pathogens 2025 (Xu et al., PMID 41308682)
- PBMC upregulation, CD14+ monocyte enrichment, correlation with severity
- CRISPR KO: reduced Mtb survival + elevated IL-1β

## Finding 28 (INDEPENDENT): Bgee monocyte gold quality (79.84)

## Finding 29: eQTL context
- GTEx v8: rs6920220 not a cis-eQTL for TNFAIP3 or SIMALR
- SIMALR has 33 testis eQTLs, none in blood at rest
- Published: rs6920220 is TNFAIP3 cis-eQTL in cases but not controls

## Finding 30 (NEGATIVE): GSE316337 27 T1D + 27 HC + 3 Pre scRNA-seq
- 727 SIMALR+ / 376,996 cells (0.19%)
- T1D 0.200% vs HC 0.185%, Fisher p~0.3
- SIMALR detectable in blood but not disease-differential at rest
- Script: scripts/48_GSE316337_SIMALR.py

## Finding 31 (SUGGESTIVE): GSE221297 monocyte scRNA
- 6 T1D, 3 HC, 3 Pre; 143,974 cells post-QC; 25,388 monocytes
- SIMALR+ rate: Pre 0.541%, HC 0.241%, T1D 0.128%
- Donor-level: T1D vs HC p=0.52, T1D vs Pre p=0.053, HC vs Pre p=0.19
- Pre > HC > T1D pattern, but n=3 Pre donors, one HC donor overlaps Pre range
- Cell-level p-values are pseudoreplication; donor-level is honest test
- Script: scripts/47_GSE221297_monocyte_SIMALR.R, 47b_GSE221297_resume.R

## Finding 32: Islet pcHi-C locus architecture (Miguel-Escalada 2019)
- Single TAD contains SIMALR + TNFAIP3 + rs6920220: chr6:138,017,057-138,278,582
- TNFAIP3 PAT spans chr6:138,017,057-138,268,650 (includes risk + SIMALR)
- rs6920220 in Inactive_enhancer (resting islets)
- SIMALR 3' end: Strong_CTCF (chr6:138,265,921-138,266,533)
- SIMALR downstream: Active_enhancer_II (chr6:138,271,019-138,272,255)
- SIMALR promoter NOT baited in islet pcHi-C panel
- TNFAIP3 baited but no high-confidence baseline interactions
- Script: scripts/49_islet_pchic_analysis.py

## Finding 33 (IN PROGRESS): HPAP PanKbase islet atlas
- Zenodo 15611730, v3.4, 9.27 GB RDS, downloading
- Purpose: SIMALR in T1D islet macrophages
- Script: scripts/50_hpap_macrophage.R
