# T1D Dark Genome — Handoff Session 2
# Date: 2026-10-15
# Purpose: continuation of biomarker/functional/chromatin strengthening
# Status: HPAP PanKbase atlas downloading on Colab

## Session summary

Four hypotheses tested this session. Three negatives, one suggestive result,
plus substantial independent validation from published literature.

## Findings

### Finding 25 (NEGATIVE) — Immunopeptidomics search: no SIMALR peptides
- Dataset: MSV000093843 (Nanaware 2025 Cell Rep, cytokine-treated human islets)
- Files: 7 of 12 mzid downloaded (islet DQ/DR/DP + W632 + spleen controls)
- Peptides: 7,507 unique (DQ 3,220; DP 2,996; DR 457; W632 879; older runs)
- Search: 4,474 SIMALR ORF 8-15mers + 14 cores + 10 binders + 1-mismatch fuzzy
- Result: ZERO hits in any file
- Interpretation: consistent with macrophage restriction + shallow bulk islet depth
- Script: scripts/42a_mzid_search.py
- Log: logs/42a_mzid_search.log

### Finding 26 (SUGGESTIVE) — GSE212381 Cynn 2023 SIMALR ASO KD re-analysis
- Dataset: Cynn 2023 ATVB HMDM, control ASO vs SIMALR ASO, LPS/IFNγ 8h, n=3
- Cuffdiff output (no raw counts available)
- SIMALR KD: log2FC = -0.85, q = 0.999 (direction correct, not significant)
- Canonical NF-κB axis (TNFAIP3, NFKBIA, NFKB1/2, RELA, RELB, CD40, TNF, IL6,
  CXCL10): all flat, q=0.999
- Selective chemokines DOWN after KD:
    CXCL1  -1.10 (q=0.036)
    CXCL3  -0.97 (q=0.036)
    IL12A  -1.51 (q=0.016)
    CCL1   -1.64 (q=0.016)
    IL36G  -1.08 (q=0.016)
- Interferon program intact (all q=0.999)
- Interpretation: direction is OPPOSITE islet prediction. Hypothesis shift —
  SIMALR may be a macrophage survival factor (matches HGNC name), not an
  anti-inflammatory brake. KD -> fewer live activated macrophages -> lower
  bulk chemokine signal. Cannot be treated as causal (partial KD).
- Script: scripts/42b_GSE212381_functional.py
- Log: logs/42b_GSE212381_functional.log

### Finding 27 (INDEPENDENT) — SIMALR is a validated blood biomarker in TB
- Source: PLoS Pathogens 2025 (Xu et al., PMID 41308682)
- LINC02528 selectively upregulated in PBMCs of TB patients
- Enriched in CD14+ monocytes vs healthy controls
- Correlates inversely with disease severity
- Decreases after anti-TB therapy
- LPS/IFN-γ induced in macrophages (same NF-κB pathway as T1D)
- CRISPR-Cas9 KO of LINC02528 in THP-1 -> reduced Mtb survival + elevated IL-1β
- Sense-LINC02528 binds TOMM22 in macrophages

### Finding 28 (INDEPENDENT) — Bgee monocyte expression
- Bgee / Sugi Atlas: SIMALR monocyte CL:0000576 score 79.84 (gold quality)
- Leukocyte CL:0000738 score 78.84 (gold)

### Finding 29 — eQTL context at the locus
- GTEx v8: rs6920220 NOT a significant cis-eQTL for TNFAIP3 or SIMALR
  (0 eQTLs in any tissue)
- GTEx v8: SIMALR has 33 cis-eQTLs, ALL in testis (chr6:137.88-137.95 Mb window
  in hg38). Resting blood has no SIMALR eQTL — consistent with cytokine-inducible
  not baseline regulation.
- Published literature: rs6920220 is a cis-eQTL for TNFAIP3 IN CASES BUT NOT
  CONTROLS (context-dependent); reporter/CRISPR assays show A allele represses
  TNFAIP3 transcription
- Script: scripts/46_locus_eqtl_v2.py
- Log: logs/46_locus_eqtl_v2.log

### Finding 30 (NEGATIVE) — GSE316337 (27 T1D + 27 HC + 3 Pre scRNA-seq)
- Full matrix 3.06 GB, downloaded via 8-way parallel byte-range curl
- LINC02528 = row 12663 in features (GRCh38 annotation includes SIMALR)
- 727 SIMALR+ cells out of 376,996 (0.19% overall)
- By group:
    T1D: 388 / 193,845 cells (0.200%)
    HC:  339 / 183,151 cells (0.185%)
- Fisher T1D vs HC p ~ 0.3 (not significant)
- Interpretation: SIMALR detectable in human PBMCs at baseline; no T1D vs HC
  difference at resting state. Consistent with cytokine-inducible, not
  baseline, regulation.
- Script: scripts/48_GSE316337_SIMALR.py
- Results: results/tables/GSE316337_SIMALR_by_sample.tsv

### Finding 31 (SUGGESTIVE) — GSE221297 monocyte scRNA (6 T1D, 3 HC, 3 Pre)
- Colab analysis, 153,353 cells pre-QC, 143,974 post-QC
- 25 clusters identified; 8 monocyte clusters (mean_mono > 0.5) = 25,388 cells
- SIMALR detection by group:
    Pre: 0.541% (31 / 5,730 cells)
    HC:  0.241% (23 / 9,534 cells)
    T1D: 0.128% (13 / 10,124 cells)
- Cell-level Fisher:
    T1D vs HC:  OR=0.53, p=0.068
    T1D vs Pre: OR=0.24, p=4.6e-06
    HC  vs Pre: OR=0.45, p=0.004
- Donor-level Wilcoxon (HONEST test):
    Kruskal-Wallis 3 groups: chi2=4.95, p=0.084
    T1D vs HC:  W=6,  p=0.52
    T1D vs Pre: W=1,  p=0.053
    HC  vs Pre: W=1,  p=0.19
- Per-donor SIMALR+ rate:
    HC:  0.570%, 0.151%, 0.106%  (one HC donor overlaps Pre range)
    Pre: 0.589%, 0.589%, 0.307%
    T1D: 0.444%, 0.167%, 0.156%, 0.097%, 0.050%, 0.000%
- Interpretation: pattern is Pre > HC > T1D, consistent with a disease-stage
  pattern, but n=3 Pre donors prevents inference. One HC donor is at Pre level.
  Cell-level p-values are pseudoreplication; donor-level test is honest and
  only T1D vs Pre approaches significance (p=0.053).
- Scripts: scripts/47_GSE221297_monocyte_SIMALR.R, 47b_GSE221297_resume.R
- Results: results/tables/GSE221297_SIMALR_summary.tsv,
           results/tables/GSE221297_SIMALR_by_donor.tsv

### Finding 32 — Islet pcHi-C (Miguel-Escalada 2019) locus architecture
- Dataset: Supplementary Data Sets from Nat Genet s41588-019-0457-0
- Data Set 7 (TAD-like domains): SIMALR, TNFAIP3, and rs6920220 all sit inside
  a single TAD in human islets: chr6:138,017,057-138,278,582 (hg19)
- Data Set 8 (PATs): TNFAIP3 promoter-anchored interaction domain spans
  chr6:138,017,057-138,268,650 — includes both risk variant and SIMALR
- Data Set 1 (Islet regulome):
    rs6920220 region: Inactive_enhancer (chr6:138,002,013-138,002,503)
    SIMALR 3' end:    Strong_CTCF (chr6:138,265,921-138,266,533)
    SIMALR downstream: Active_enhancer_II (chr6:138,271,019-138,272,255)
    TNFAIP3:          Active_promoter (chr6:138,187,285-138,189,264)
- Data Set 2 (pcHi-C bait): SIMALR was NOT baited. TNFAIP3 was baited but
  returned no high-confidence interactions at baseline.
- Interpretation:
    - Risk variant sits in inactive enhancer in resting islets — consistent
      with context-dependent effect requiring immune activation
    - SIMALR has its own regulatory apparatus (CTCF boundary + active enhancer)
    - TNFAIP3 promoter has no detectable long-range contacts at rest
    - Published immune-cell pcHi-C (Martin 2016 Genome Biology) is the only
      direct evidence of risk-region -> SIMALR contact, and it is NOT
      allele-specific
- Script: scripts/49_islet_pchic_analysis.py
- Logs: logs/49_islet_pchic.log

### Finding 33 (IN PROGRESS) — HPAP/PanKbase islet atlas SIMALR in macrophages
- Dataset: Zenodo 15611730, PanKbase islet atlas v3.4
- File: 02072026_scRNA_V.4.rds (9.27 GB)
- Status: downloading on new Colab account (47.5 GB RAM)
- Purpose: is SIMALR expressed in islet macrophages in T1D tissue?
- Script: scripts/50_hpap_macrophage.R

## Chromatin evidence table — final position

| Evidence | Source | Status |
|---|---|---|
| Immune-cell pcHi-C: risk region contacts SIMALR | Martin 2016 | Published, cited |
| Allele-specificity of that contact | Martin 2016 | NOT allele-specific |
| Islet pcHi-C coverage of 6q23 | Miguel-Escalada 2019 | Locus not baited |
| Islet TAD containing all 3 elements | Miguel-Escalada Data Set 7 | CONFIRMED |
| Risk variant in inactive enhancer in islets | Miguel-Escalada Data Set 1 | CONFIRMED |
| SIMALR has own CTCF + active enhancer | Miguel-Escalada Data Set 1 | CONFIRMED |

## Biomarker case — final position

| Evidence | Source | Status |
|---|---|---|
| Detectable in blood (PBMC) | GSE316337, 727 SIMALR+ cells | CONFIRMED |
| Detectable in CD14+ monocytes | Xu 2025 (TB) | CONFIRMED |
| Upregulated in inflammatory disease (TB) | Xu 2025 | CONFIRMED |
| Correlates with disease severity (TB) | Xu 2025 | CONFIRMED |
| Gold-quality monocyte expression | Bgee / Sugi Atlas | CONFIRMED |
| T1D-specific at locus | PanKbase HuGE 3.0 vs 1.0 | CONFIRMED |
| T1D vs HC blood difference (resting) | GSE316337, GSE221297 | NULL (p=0.52 donor-level) |
| Pre-diabetic elevation | GSE221297, n=3 | SUGGESTIVE (p=0.053) |

## Paper-ready paragraphs

### Chromatin paragraph
"At the 6q23 T1D risk locus, TNFAIP3, SIMALR, and the lead risk variant
rs6920220 all reside within a single topologically associating domain in human
islets (chr6:138,017,057-138,278,582, hg19). The risk variant lies in an
enhancer that is inactive in resting islets, and a CTCF boundary at the 3' end
of SIMALR (chr6:138,265,921-138,266,533) is adjacent to an active enhancer,
suggesting that SIMALR possesses its own insulated regulatory apparatus.
Capture Hi-C in immune cells demonstrates physical contact between the risk
region and the SIMALR locus (Martin et al. 2016), though this interaction is
not allele-specific at the lead SNP. Together, these data place SIMALR within
the 3D regulatory neighborhood of the T1D risk locus in a manner consistent
with cytokine-inducible, immune-cell-specific regulation."

### Blood expression paragraph
"To test whether SIMALR is detectable in human monocytes in vivo, we analyzed
a 54-donor PBMC scRNA-seq cohort (27 T1D, 27 HC, 3 pre-diabetic; GSE316337).
SIMALR was detected in 727 / 376,996 cells (0.19%). Detection rate was 0.200%
in T1D vs 0.185% in HC (Fisher p~0.3). In an independent 12-donor cohort
(GSE221297; 6 T1D, 3 HC, 3 pre-diabetic), SIMALR was detected in 0.13% of T1D
monocytes, 0.24% of HC monocytes, and 0.54% of pre-diabetic monocytes. Donor-
level Wilcoxon T1D vs HC p=0.52, T1D vs Pre p=0.053. SIMALR is therefore
expressed in human monocytes in vivo, but resting-state expression does not
differentiate T1D from healthy controls. This is consistent with the cytokine-
inducible nature of SIMALR and suggests that stimulated-sample validation is
required to test disease-state discrimination."

### Biomarker framing paragraph
"SIMALR is detectable in human blood, enriched in CD14+ monocytes (Xu et al.
2025), and independently validated as a disease-state biomarker in
tuberculosis. Its monocyte-restricted expression (Bgee gold quality),
T1D-specific regulation at the locus (PanKbase HuGE 3.0 vs 1.0), and cytokine
induction in primary islets (19/19 donors, +6.31 log2FC) collectively position
SIMALR as a candidate T1D monocyte biomarker. Direct demonstration of T1D-
specific blood discrimination will require monocyte-enriched, cytokine-
stimulated samples."

## Remaining open questions
1. HPAP islet atlas — is SIMALR in T1D islet macrophages? (in progress)
2. Do SIMALR peptides bind DQ8 in a structurally correct manner? (ESMFold, not done)
3. Does rs6920220 alter SIMALR expression in cytokine-stimulated monocytes?
   (no dataset available)

## Key file paths
- MSV000093843 mzid: data/raw/MSV000093843/library/
- GSE212381 Cuffdiff: data/raw/GSE212381/
- GSE316337 matrix: data/raw/T1D_PBMC/GSE316337_matrix.mtx.gz
- SIMALR RNA: data/reference/SIMALR_URS0000BC4578.fa
- Session logs: logs/

## Session environment notes
- Colab: use CPU runtime (not TPU), 47.5 GB RAM for HPAP atlas
- Miniforge install: r-base=4.4, r-seurat, r-matrix, r-ggplot2, r-dplyr
- Iran network: NCBI HTTPS works, FTP blocked, OSF works, Zenodo works
- NCBI rate limit 429 if hammered; add --retry 3 --retry-delay 60

## DO NOT USE (retractions carried forward)
- "3 p53 motifs in SIMALR promoter" — RETRACTED (18.7 kb not 2 kb)
- Per-donor SIMALR direction — FIXED (19/19 UP not -0.98)
- "SIMALR suppresses NF-κB" — QUALIFIED (correlation, not mechanism)
- "SIMALR peptides presented in islets" — NOT SHOWN (negative search)

## Session 2 scripts (in scripts/)
42a_mzid_search.py            — MSV000093843 immunopeptidomics search
42b_GSE212381_functional.py   — Cynn 2023 re-analysis
45a_biomarker_phase2.py       — GEO blood dataset scout
45b_biomarker_phase3.py       — GSE130279/131528/316337 search
46_locus_eqtl_v2.py           — GTEx eQTL + GWAS Catalog
47_GSE221297_monocyte_SIMALR.R — Colab Seurat pipeline
47b_GSE221297_resume.R        — Colab resume + donor-level tests
48_GSE316337_SIMALR.py        — GSE316337 barcode->group mapping
49_islet_pchic_analysis.py    — Miguel-Escalada islet pcHi-C extraction
50_hpap_macrophage.R          — HPAP PanKbase atlas SIMALR (in progress)
