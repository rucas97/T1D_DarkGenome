# ============================================================
# 02_define_stress_signature.R
# Purpose: Define stress-responsive and dediff signatures
# ============================================================

setwd("D:/T1D_DarkGenome")

sink("logs/02_define_signature_session.txt")
cat("=== Session Info ===\n"); print(sessionInfo())
cat("\n=== Timestamp ===\n"); print(Sys.time())
sink()

library(data.table)

bulk <- readRDS("data/processed/bulk_DEG.rds")
beta <- readRDS("data/processed/beta_DEG.rds")

bulk_down <- bulk[bulk$FDR < 0.05 & bulk$logFC < -0.5, ]
bulk_up   <- bulk[bulk$FDR < 0.05 & bulk$logFC >  0.5, ]

cat("BULK stress (DOWN in KO):", nrow(bulk_down), "genes\n")
cat("BULK dediff (UP in KO):  ", nrow(bulk_up),   "genes\n")

beta$log2_ratio <- log2(beta$KO_WT_ratio)

beta_down <- beta[beta$qval < 0.05 & beta$log2_ratio < -0.5, ]
beta_up   <- beta[beta$qval < 0.05 & beta$log2_ratio >  0.5, ]

cat("BETA stress (DOWN in KO):", nrow(beta_down), "genes\n")
cat("BETA dediff (UP in KO):  ", nrow(beta_up),   "genes\n")

stress_core <- intersect(bulk_down$Ensembl, beta_down$Ensembl)
dediff_core <- intersect(bulk_up$Ensembl,   beta_up$Ensembl)

cat("\n=== CORE SIGNATURES (bulk intersect beta) ===\n")
cat("Stress core (IRE1a-activated):", length(stress_core), "genes\n")
cat("Dediff core (IRE1a-repressed):", length(dediff_core), "genes\n")

stress_core_tbl <- bulk_down[bulk_down$Ensembl %in% stress_core,
                             c("Ensembl","Symbol","logFC","FDR","Description")]
dediff_core_tbl <- bulk_up[bulk_up$Ensembl %in% dediff_core,
                           c("Ensembl","Symbol","logFC","FDR","Description")]

cat("\nTop 15 stress-core genes (by bulk logFC):\n")
print(head(stress_core_tbl[order(stress_core_tbl$logFC), ], 15))

cat("\nTop 15 dediff-core genes (by bulk logFC):\n")
print(head(dediff_core_tbl[order(-dediff_core_tbl$logFC), ], 15))

dir.create("results/tables", showWarnings = FALSE, recursive = TRUE)

write.table(stress_core_tbl,
            "results/tables/stress_core_signature.tsv",
            sep = "\t", quote = FALSE, row.names = FALSE)
write.table(dediff_core_tbl,
            "results/tables/dediff_core_signature.tsv",
            sep = "\t", quote = FALSE, row.names = FALSE)

writeLines(stress_core, "results/tables/stress_core_ensembl.txt")
writeLines(dediff_core, "results/tables/dediff_core_ensembl.txt")

cat("\n=== Saved 4 files to results/tables/ ===\n")
