# GenomicsOps T1D Dark Genome — Findings Log

## Datasets
- **GSE144472** — mouse IRE1α KO islets (bulk + β-cell DEG)
- **GSE251911** — human islets, cytokine vs ER stress (n=19 donors paired)
- **GSE235683** — EndoC-βH1 cytokine panel (symbol map + supporting)
- **GENCODE v46** — gene annotation (chr, coords, biotype)
- **epiromics cache** — ATAC-seq (pending extraction)

## Finding 1: Immunogenic DDR Is Activated in Cytokine-Treated Human Islets
- 14,048 / 21,172 genes significant (padj<0.05)
- cGAS/STING fully induced: CGAS +1.29, STING1 +0.67, TBK1 +0.72, IRF3 +0.63
- RNA sensors: DDX58 (RIG-I) +3.03, IFIH1 (MDA5) +2.87
- p53 axis: BBC3 (PUMA) +1.59, CDKN1A (p21) +0.74
- SASP: IL6 +3.41, CXCL1 +3.52, CXCL2 +2.51, MMP3 +2.24
- **Contrast**: ER stress (thapsigargin) does NOT activate cGAS/STING

## Finding 2: 54 Dark Genome Elements Induced >4-fold by Cytokines
- 48 / 54 non-coding (41 lncRNA, 5 pseudogene, 2 TEC)
- Top: AC093063.1 +11.0, AC007991.2 +10.4, AL157871.4 +6.6
- Total ncRNAs significant: 1,799

## Finding 3: LINC02528 = SIMALR at TNFAIP3 T1D Risk Locus
- chr6:137,943,079-137,957,657, ENSG00000226004
- HGNC name: SIMALR (Stress-Induced Major Autoimmunity-Linked RNA)
- +6.31 log2FC, padj 2.9e-45 in cytokines
- Nearest T1D SNP: rs6920220 (TNFAIP3 locus), 59 kb
- AL355304.1 also in same locus (+3.14 log2FC, padj 6.2e-76)

## Finding 4: LINC02528 Marks an NF-κB-Low State
- TNFAIP3 ranks 21079/21172 for co-expression (rho = −0.679)
- Entire canonical NF-κB axis anti-correlated with LINC02528:
  NFKBIA −0.742, RELA −0.739, NFKB2 −0.728, TNFAIP3 −0.679,
  RELB −0.658, CD40 −0.605, NFKB1 −0.530
- Positively correlated genes: neuronal/structural (SYNE1, ZFP82, NLGN4X)
- Interpretation: LINC02528 marks a dedifferentiated, NF-κB-suppressed state

## Finding 5: Non-Coding Stress-Integration Hub
500 kb neighborhood of SIMALR:
- 13+ non-coding features (10 lncRNAs, MIR3145, Y_RNA, pseudogenes)
- TNFAIP3 at 72 kb (NF-κB brake, T1D risk)
- PERP at 147 kb (p53 apoptosis effector)
- OLIG3 at 449 kb (neuronal TF)

## Finding 6: SIMALR Promoter Contains 3 p53 Motifs
Motif scan on gene + 2 kb upstream (18.7 kb total):
- NF-κB: 1 site, ISRE: 1 site, GAS: 1 site, **p53: 3 sites**
- Connects: cytokine stress → DDR → p53 → SIMALR

## Finding 7: Dark Genome Targets Cluster at Immune Gene Loci
- AC099063.4 → GBP1-7 cluster (all +5.5 to +11.1)
- AC007991.2 → IDO1 (+10.95)
- AP001610.2 → MX1/MX2 (+4.11, +3.65)
- AC007728.2 → NOD2 (+3.86)
- AL645939.5 → TRIM40/31/15/10, UBD, HLA-F
- AC040162.1 → PSMB10, AC068989.1 → DDX60, AC124319.1 → RNF213
- 109/526 (20.7%) coding neighbors cytokine-induced

## Finding 8: Enrichment Survives Expression Matching
| Test | Observed | Background | Ratio | p-value |
|---|---|---|---|---|
| Unmatched | 0.204 | 0.128 | **1.59×** | < 0.0005 |
| Expression-matched | 0.204 | 0.131 | **1.56×** | < 0.0005 |

Null max (matched): 0.1811 — observed 0.204 exceeds all 5,000 draws.
Enrichment is NOT explained by location bias or expression selection.

## Central Model
Cytokine stress  immunogenic DDR (cGAS/STING + p53)
 p53 binds SIMALR promoter (3 p53 sites)
 SIMALR transcription  6.3
 Two divergent ß-cell states emerge:
(1) NF-?B-high: canonical response
(2) SIMALR-high: NF-?B-suppressed, dedifferentiated
 Patients shifting to (2) lose immune tolerance
at TNFAIP3 T1D risk locus

## Files
- scripts/01-13  full analysis pipeline
- results/tables/  30+ TSV tables and figures
- results/figures/  4 summary plots
- logs/  reproducibility records

## Next Steps
- Extract ATAC from epiromics cache (double-gzip)
- Intersect 54 targets with chromatin accessibility
- HLA binding prediction of SIMALR-derived peptides
- Draft Results section
