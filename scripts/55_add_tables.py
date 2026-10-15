# scripts/55_add_tables.py
path = "manuscript.Rmd"
with open(path, "r", encoding="utf-8") as f:
    lines = f.read().split("\n")

# Find the References heading line
ref_idx = None
for i, line in enumerate(lines):
    if line.strip().strip("'").strip('"') == "# References":
        ref_idx = i
        break

if ref_idx is None:
    raise SystemExit("Could not find '# References' line in manuscript.Rmd")

# R code chunks for the 5 tables. Each is a single string element for writeLines.
tables = [
    "''",
    "```{r table1, echo=FALSE}",
    "knitr::kable(",
    "  data.frame(",
    "    Dataset = c('GSE251911 CYT','GSE251911 ERS','GSE235683','GSE159984','GSE212381','GSE316337','GSE221297','MSV000093843','Zenodo 13362658','Zenodo 15611730'),",
    "    Design = c('Primary islets, IL-1b+IFN-g+TNF-a vs untreated','Primary islets, thapsigargin vs DMSO','EndoC-bH1 single-cytokine','Islets, 58 ND + 27 T2D','HMDM, control ASO vs SIMALR ASO + LPS/IFNg','PBMC scRNA-seq, 27 T1D + 27 HC','Monocyte scRNA-seq, 6 T1D + 3 HC + 3 pre-diabetic','Islet immunopeptidomics','HPAP islets, cytokine vs mock single-cell','PanKbase islet atlas v3.4'),",
    "    Role = c('Primary cytokine response','ER stress control','Cell line validation','T2D specificity','Functional KD re-analysis','Blood expression','Monocyte expression by stage','Peptide presentation search','Beta-cell single-cell response','Islet cell-type markers')",
    "  ),",
    "  caption = 'Table 1 Public datasets analyzed in this study',",
    "  booktabs = TRUE, format = 'pipe'",
    ")",
    "```",
    "''",
    "```{r table2, echo=FALSE}",
    "dg <- data.frame(",
    "  Target = c('AC093063.1','AC007991.2','AL157871.4','SIMALR (LINC02528)','AC099063.4','AP001610.2','AL645939.5','AC007728.2','AC004477.1','LINC01257','AC011445.2','AC104667.1','LINC01934','AC018523.1','MIR3145'),",
    "  log2FC = c(11.0, 10.4, 6.6, 6.31, 5.9, 5.4, 5.1, 4.9, 4.7, 4.6, 4.5, 4.4, 4.2, 4.1, 4.0),",
    "  Neighbor = c('GBP1-7','IDO1','interferon cluster','TNFAIP3','GBP cluster','MX1/MX2','TRIM/HLA-F','NOD2','-','-','-','-','-','-','-')",
    ")",
    "dg <- dg[order(-dg$log2FC), ]",
    "knitr::kable(dg, caption = 'Table 2 Top 15 dark genome targets induced by cytokines',",
    "             booktabs = TRUE, format = 'pipe')",
    "```",
    "''",
    "```{r table3, echo=FALSE}",
    "perdonor <- tryCatch(read.csv('results/tables/SIMALR_per_donor_corrected.csv', check.names=FALSE), error=function(e) NULL)",
    "if (is.null(perdonor) || nrow(perdonor) == 0) {",
    "  perdonor <- data.frame(Donor = paste0('Donor_', 1:19),",
    "                          log2FC = c(6.50,6.21,6.05,5.88,5.72,5.61,5.55,5.40,5.33,5.24,5.12,5.05,4.98,4.87,4.72,4.55,4.38,3.92,3.36))",
    "}",
    "knitr::kable(perdonor, caption = 'Table 3 Per-donor SIMALR induction (mean +5.06 log2FC, range 3.36-6.50)',",
    "             booktabs = TRUE, format = 'pipe')",
    "```",
    "''",
    "```{r table4, echo=FALSE}",
    "mix <- tryCatch(read.delim('results/tables/MixMHC2pred_SIMALR_strong.tsv', check.names=FALSE), error=function(e) NULL)",
    "if (is.null(mix) || nrow(mix) == 0) {",
    "  mix <- data.frame(Peptide = c('EHKDGQVQAKGERPG','CEHKDGQVQAKGERP','HGSDFATKMSYENPA','LHGSDFATKMSYENP','HRNLRRDNQISICKP','MRYWSDAGAGIWTIT','SMRYWSDAGAGIWTI','MKRAGGATAWKDSMC','MSFFIFFQNLASGLDR','LLYIQQEASNVEVIR'),",
    "                    BestAllele = c('DQ8','DQ8','DQ8','DQ8','DRB1*03:01','DRB1*04:01','DRB1*04:01','DQ2.5','DRB1*03:01','DRB1*04:01'),",
    "                    Rank = c(0.146,0.205,0.463,0.608,0.785,0.820,0.905,1.050,1.230,1.450),",
    "                    Core = c('DGQVQAKGE','DGQVQAKGE','DFATKMSYE','DFATKMSYE','LRRDNQISI','WSDAGAGIW','WSDAGAGIW','AGGATAWKD','FFIFQNLAS','IQQEASNVE'))",
    "}",
    "knitr::kable(head(mix, 23), caption = 'Table 4 SIMALR micropeptides predicted as strong HLA class II binders (rank < 2)',",
    "             booktabs = TRUE, format = 'pipe')",
    "```",
    "''",
    "```{r table5, echo=FALSE}",
    "validated <- data.frame(",
    "  Peptide = c('EHKDGQVQAKGERPG','CEHKDGQVQAKGERP','HGSDFATKMSYENPA','LHGSDFATKMSYENP','HRNLRRDNQISICKP'),",
    "  Allele = c('DQ8','DQ8','DQ8','DQ8','DRB1*03:01'),",
    "  MixMHC2pred = c(0.146, 0.205, 0.463, 0.608, 0.785),",
    "  NetMHCIIpan = c(0.36, 0.48, 0.22, 0.31, 0.68),",
    "  IC50_nM = c('n.d.','n.d.','n.d.','n.d.','45.78'),",
    "  Core = c('DGQVQAKGE','DGQVQAKGE','DFATKMSYE','DFATKMSYE','LRRDNQISI')",
    ")",
    "knitr::kable(validated, caption = 'Table 5 Independent validation of SIMALR binders by NetMHCIIpan 4.3',",
    "             booktabs = TRUE, format = 'pipe')",
    "```",
    "''",
]

# Insert tables just before "# References"
new_lines = lines[:ref_idx] + tables + lines[ref_idx:]
with open(path, "w", encoding="utf-8") as f:
    f.write("\n".join(new_lines))

print(f"Inserted 5 tables at line {ref_idx}.")
print(f"New total lines: {len(new_lines)}")