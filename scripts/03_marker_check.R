# ============================================================
# 03_marker_check.R
# Purpose: Check where ER-stress, DDR, beta-identity, immune
#          markers sit in the bulk RNA-seq data.
# ============================================================

setwd("D:/T1D_DarkGenome")

sink("logs/03_marker_check_session.txt")
cat("=== Session Info ===\n"); print(sessionInfo())
cat("\n=== Timestamp ===\n"); print(Sys.time())
sink()

library(data.table)

bulk <- readRDS("data/processed/bulk_DEG.rds")

er_stress <- c("Ddit3","Hspa5","Xbp1","Atf4","Atf6","Ern1",
               "Edem1","Dnajb9","Sec61a1","Eif2ak3","Hsp90b1","Calr")

ddr_axis  <- c("Trp53","Cdkn1a","Atm","Atr","Chek1","Chek2",
               "H2afx","Parp1","Gadd45a","Mdm2","Bbc3","Bax",
               "Rrm2b","Topbp1","Rad51","Brca1","Ogg1","Neil1")

beta_id   <- c("Ins1","Ins2","Pdx1","Mafa","Nkx6-1","Slc2a2",
               "Gck","Ucn3","Trpm5","Abcc8","Kcnj11","Neurod1",
               "Foxa2","Pax6","Isl1")

immuno    <- c("Cd4","Cd8a","Cd8b1","Foxp3","Il2ra","Ifng",
               "Tnf","Il1b","Il6","Ccl2","Cxcl10","Stat1","Stat3")

check_markers <- function(gene_set, label) {
  cat("\n========================================\n")
  cat(label, "\n")
  cat("========================================\n")
  hits <- bulk[bulk$Symbol %in% gene_set,
               c("Symbol","logFC","FDR","Status")]
  hits <- hits[order(hits$logFC), ]
  if (nrow(hits) == 0) {
    cat("No markers found in the bulk table.\n")
  } else {
    print(hits, row.names = FALSE)
  }
  return(hits)
}

er_hits   <- check_markers(er_stress, "ER STRESS MARKERS")
ddr_hits  <- check_markers(ddr_axis,  "DDR MARKERS")
beta_hits <- check_markers(beta_id,   "BETA-CELL IDENTITY MARKERS")
imm_hits  <- check_markers(immuno,    "IMMUNE MARKERS")

cat("\n=== MISSING MARKERS ===\n")
cat("ER stress not found:", setdiff(er_stress, bulk$Symbol), "\n")
cat("DDR not found:      ", setdiff(ddr_axis, bulk$Symbol), "\n")
cat("Beta-id not found:  ", setdiff(beta_id, bulk$Symbol), "\n")
cat("Immune not found:   ", setdiff(immuno, bulk$Symbol), "\n")

dir.create("results/tables", showWarnings = FALSE, recursive = TRUE)
write.table(er_hits,   "results/tables/markers_ER_stress.tsv",
            sep="\t", quote=FALSE, row.names=FALSE)
write.table(ddr_hits,  "results/tables/markers_DDR.tsv",
            sep="\t", quote=FALSE, row.names=FALSE)
write.table(beta_hits, "results/tables/markers_beta_identity.tsv",
            sep="\t", quote=FALSE, row.names=FALSE)
write.table(imm_hits,  "results/tables/markers_immune.tsv",
            sep="\t", quote=FALSE, row.names=FALSE)

cat("\n=== Saved 4 marker tables ===\n")
