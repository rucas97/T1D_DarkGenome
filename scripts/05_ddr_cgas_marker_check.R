# ============================================================
# 05_ddr_cgas_marker_check.R
# Purpose: Query CYT and ERS results for DDR, cGAS/STING, IFN,
#          ER-stress, senescence, and non-coding RNAs
# ============================================================

setwd("D:/T1D_DarkGenome")

sink("logs/05_marker_check_session.txt")
cat("=== Session Info ===\n"); print(sessionInfo())
cat("\n=== Timestamp ===\n"); print(Sys.time())
sink()

library(data.table)

cyt <- as.data.frame(fread("results/tables/DESeq2_CYT_cytokines_vs_untreated.tsv"))
ers <- as.data.frame(fread("results/tables/DESeq2_ERS_thapsigargin_vs_DMSO.tsv"))

query_markers <- function(df, genes, label) {
  cat("\n========================================\n")
  cat(label, "\n")
  cat("========================================\n")
  hits <- df[df$Symbol %in% genes & !is.na(df$Symbol), ]
  hits <- hits[order(-hits$log2FoldChange), ]
  if (nrow(hits) == 0) {
    cat("No markers found.\n")
  } else {
    print(hits[, c("Symbol","log2FoldChange","padj")], row.names = FALSE)
  }
  invisible(hits)
}

ddr_p53 <- c("TP53","CDKN1A","GADD45A","MDM2","BBC3","RRM2B",
             "TNFRSF10B","BAX","ATR","ATM","CHEK1","CHEK2",
             "H2AFX","TP53BP1","RAD51","BRCA1","OGG1","PARP1")

cgas_sting <- c("CGAS","MB21D1","STING1","TMEM173","TBK1","IRF3",
                "IRF7","IFNB1","IFNA1","IFNA2","NFKB1","RELA",
                "DDX58","MDA5","IFIH1","MAVS")

interferon <- c("STAT1","STAT2","IRF1","IRF9","ISG15","MX1","MX2",
                "OAS1","OAS2","OAS3","IFIT1","IFIT3","IFITM1",
                "IFITM2","IFITM3","B2M","HLA-A","HLA-B","HLA-C",
                "TAP1","PSMB8","PSMB9","NLRC5","CIITA")

er_stress <- c("DDIT3","HSPA5","XBP1","ATF4","ATF6","ERN1",
               "EDEM1","DNAJB9","SEC61A1","EIF2AK3","HSP90B1",
               "CALR","PDIA3","HYOU1","SEL1L")

senescence <- c("CDKN1A","CDKN2A","GLB1","LMNB1","SERPINE1",
                "IL6","IL8","CXCL1","CXCL2","MMP3","MMP9")

cat("\n\n########## CYTOKINE-TREATED ISLETS ##########\n")
cyt_p53  <- query_markers(cyt, ddr_p53,     "CYT: p53/DDR axis")
cyt_cgas <- query_markers(cyt, cgas_sting,  "CYT: cGAS/STING/IFN")
cyt_ifn  <- query_markers(cyt, interferon,  "CYT: Interferon-stimulated")
cyt_er   <- query_markers(cyt, er_stress,   "CYT: ER stress markers")
cyt_sen  <- query_markers(cyt, senescence,  "CYT: Senescence markers")

cat("\n\n########## THAPSIGARGIN-TREATED ISLETS ##########\n")
ers_p53  <- query_markers(ers, ddr_p53,     "ERS: p53/DDR axis")
ers_cgas <- query_markers(ers, cgas_sting,  "ERS: cGAS/STING/IFN")
ers_ifn  <- query_markers(ers, interferon,  "ERS: Interferon-stimulated")
ers_er   <- query_markers(ers, er_stress,   "ERS: ER stress markers")
ers_sen  <- query_markers(ers, senescence,  "ERS: Senescence markers")

fwrite(cyt_p53,  "results/tables/CYT_p53_DDR.tsv",  sep="\t")
fwrite(cyt_cgas, "results/tables/CYT_cGAS_STING.tsv", sep="\t")
fwrite(cyt_ifn,  "results/tables/CYT_interferon.tsv", sep="\t")
fwrite(ers_p53,  "results/tables/ERS_p53_DDR.tsv",  sep="\t")
fwrite(ers_cgas, "results/tables/ERS_cGAS_STING.tsv", sep="\t")
fwrite(ers_ifn,  "results/tables/ERS_interferon.tsv", sep="\t")

cat("\n\n########## NON-CODING RNA CENSUS ##########\n")

is_ncrna <- function(sym) {
  ifelse(is.na(sym), FALSE,
         grepl("^(LINC|AC[0-9]|AL[0-9]|AP[0-9]|LOC[0-9]|-AS[0-9]|MIR|SNOR|SCARNA)",
               sym, ignore.case = TRUE))
}

cyt$is_ncrna <- is_ncrna(cyt$Symbol)
ers$is_ncrna <- is_ncrna(ers$Symbol)

cat("CYT: ncRNA significant (padj<0.05):",
    sum(cyt$is_ncrna & cyt$padj < 0.05, na.rm=TRUE), "\n")
cat("CYT: ncRNA up (log2FC>2, padj<0.05):",
    sum(cyt$is_ncrna & cyt$log2FoldChange > 2 & cyt$padj < 0.05, na.rm=TRUE), "\n")
cat("CYT: ncRNA down (log2FC<-2, padj<0.05):",
    sum(cyt$is_ncrna & cyt$log2FoldChange < -2 & cyt$padj < 0.05, na.rm=TRUE), "\n")

cat("\nERS: ncRNA significant (padj<0.05):",
    sum(ers$is_ncrna & ers$padj < 0.05, na.rm=TRUE), "\n")

top_ncrna_cyt <- cyt[cyt$is_ncrna & cyt$padj < 0.05, ]
top_ncrna_cyt <- top_ncrna_cyt[order(-top_ncrna_cyt$log2FoldChange), ]

cat("\nTop 20 ncRNAs induced by cytokines:\n")
print(head(top_ncrna_cyt[, c("Symbol","log2FoldChange","padj")], 20),
      row.names = FALSE)

fwrite(top_ncrna_cyt,
       "results/tables/CYT_ncRNA_all_significant.tsv",
       sep = "\t")

cat("\n=== DONE ===\n")
