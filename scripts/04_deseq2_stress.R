# ============================================================
# 04_deseq2_stress.R  (v2 - paths fixed, symbols mapped)
# Purpose: Paired DESeq2 on GSE251911 CYT and ERS datasets
# ============================================================

setwd("D:/T1D_DarkGenome")

sink("logs/04_deseq2_session.txt")
cat("=== Session Info ===\n"); print(sessionInfo())
cat("\n=== Timestamp ===\n"); print(Sys.time())
sink()

suppressPackageStartupMessages({
  library(data.table)
  library(DESeq2)
})

# --- Gene-symbol map
cat("Building gene-symbol map from GSE235683...\n")
symap <- fread("data/raw/GSE235683_processed_data.tsv",
               header = TRUE, sep = ",",
               select = c("ensembl", "gene_name"),
               data.table = FALSE)
colnames(symap) <- c("Ensembl", "Symbol")
symap <- symap[!duplicated(symap$Ensembl) & !is.na(symap$Symbol), ]
cat("Symbol map rows:", nrow(symap), "\n")

load_counts_paired <- function(path, treated_label, control_label) {
  cat("\n--- Loading", basename(path), "---\n")
  counts <- fread(path, header = TRUE, sep = "\t", data.table = FALSE)
  rownames(counts) <- counts$Ensembl_ID
  counts$Ensembl_ID <- NULL
  cat("Raw dims:", dim(counts), "\n")

  samples <- colnames(counts)
  donor <- sub("^Islet_([0-9]+)_.*$", "\\1", samples)
  treat <- ifelse(grepl(treated_label, samples), "treated", "control")

  stopifnot(!any(is.na(donor)), length(unique(treat)) == 2)

  colData <- data.frame(
    donor     = factor(donor),
    treatment = factor(treat, levels = c("control", "treated")),
    row.names = samples
  )
  print(table(colData$treatment))
  cat("Donors:", nlevels(colData$donor), "\n")

  list(counts = counts, colData = colData)
}

annotate_result <- function(res_df, symap) {
  res_df$Ensembl <- rownames(res_df)
  res_df <- merge(res_df, symap, by = "Ensembl", all.x = TRUE)
  res_df <- res_df[order(res_df$padj), ]
  res_df
}

# --- 1. CYT
cat("\n############ CYT (Cytokines vs Untreated) ############\n")
cyt <- load_counts_paired(
  "data/raw/GSE251911_CYT_RNA-seq_Raw_Count_Matrix.txt",
  treated_label = "Cytokines",
  control_label = "Untreated"
)

min_grp <- min(table(cyt$colData$treatment))
keep <- rowSums(cyt$counts >= 10) >= min_grp
cyt$counts <- cyt$counts[keep, ]
cat("After filtering:", nrow(cyt$counts), "genes\n")

dds_cyt <- DESeqDataSetFromMatrix(
  countData = cyt$counts,
  colData   = cyt$colData,
  design    = ~ donor + treatment
)
cat("Running DESeq2 on CYT...\n")
dds_cyt <- DESeq(dds_cyt, parallel = FALSE)

res_cyt <- results(dds_cyt, alpha = 0.05)
res_cyt <- lfcShrink(dds_cyt, coef = "treatment_treated_vs_control",
                     type = "apeglm", res = res_cyt)

res_cyt_df <- annotate_result(as.data.frame(res_cyt), symap)

cat("\nTop 15 up in Cytokines:\n")
print(head(res_cyt_df[order(-res_cyt_df$log2FoldChange),
                      c("Symbol","Ensembl","log2FoldChange","padj")], 15),
      row.names = FALSE)
cat("\nTop 15 down in Cytokines:\n")
print(head(res_cyt_df[order(res_cyt_df$log2FoldChange),
                      c("Symbol","Ensembl","log2FoldChange","padj")], 15),
      row.names = FALSE)

fwrite(res_cyt_df,
       "results/tables/DESeq2_CYT_cytokines_vs_untreated.tsv",
       sep = "\t")

# --- 2. ERS
cat("\n############ ERS (Thapsigargin vs DMSO) ############\n")
ers <- load_counts_paired(
  "data/raw/GSE251911_ERS_RNA-seq_Raw_Count_Matrix.txt",
  treated_label = "Thapsigargin",
  control_label = "DMSO"
)

min_grp <- min(table(ers$colData$treatment))
keep <- rowSums(ers$counts >= 10) >= min_grp
ers$counts <- ers$counts[keep, ]
cat("After filtering:", nrow(ers$counts), "genes\n")

dds_ers <- DESeqDataSetFromMatrix(
  countData = ers$counts,
  colData   = ers$colData,
  design    = ~ donor + treatment
)
cat("Running DESeq2 on ERS...\n")
dds_ers <- DESeq(dds_ers, parallel = FALSE)

res_ers <- results(dds_ers, alpha = 0.05)
res_ers <- lfcShrink(dds_ers, coef = "treatment_treated_vs_control",
                     type = "apeglm", res = res_ers)

res_ers_df <- annotate_result(as.data.frame(res_ers), symap)

cat("\nTop 15 up in Thapsigargin:\n")
print(head(res_ers_df[order(-res_ers_df$log2FoldChange),
                      c("Symbol","Ensembl","log2FoldChange","padj")], 15),
      row.names = FALSE)
cat("\nTop 15 down in Thapsigargin:\n")
print(head(res_ers_df[order(res_ers_df$log2FoldChange),
                      c("Symbol","Ensembl","log2FoldChange","padj")], 15),
      row.names = FALSE)

fwrite(res_ers_df,
       "results/tables/DESeq2_ERS_thapsigargin_vs_DMSO.tsv",
       sep = "\t")

saveRDS(dds_cyt,    "data/processed/dds_cyt.rds")
saveRDS(dds_ers,    "data/processed/dds_ers.rds")
saveRDS(res_cyt_df, "data/processed/res_cyt.rds")
saveRDS(res_ers_df, "data/processed/res_ers.rds")
saveRDS(symap,      "data/processed/gene_symbol_map.rds")

cat("\n=== DONE ===\n")
cat("Significant CYT:", sum(res_cyt_df$padj < 0.05, na.rm=TRUE), "\n")
cat("Significant ERS:", sum(res_ers_df$padj < 0.05, na.rm=TRUE), "\n")
