# ============================================================
# 01_load_stress_data.R  (v2 - handles commas in Description)
# Purpose: Load bulk and beta-cell DEG tables from GSE144472
# ============================================================

setwd("D:/T1D_DarkGenome")

sink("logs/01_load_stress_data_session.txt")
cat("=== Session Info ===\n"); print(sessionInfo())
cat("\n=== Timestamp ===\n"); print(Sys.time())
sink()

library(data.table)

# --- 1. BULK RNA-seq: parse manually due to commas in Description
cat("Reading bulk file line-by-line...\n")
all_lines <- readLines("data/raw/GSE144461_edgeRglm_GENE_s7KO-s7WT.csv")
cat("Total lines read:", length(all_lines), "\n")

header_parts <- strsplit(all_lines[1], ",", fixed = TRUE)[[1]]
n_fields <- length(header_parts)
cat("Header has", n_fields, "fields\n")

parse_row <- function(line, n_fields) {
  parts <- strsplit(line, ",", fixed = TRUE)[[1]]
  if (length(parts) > n_fields) {
    parts <- c(parts[1:(n_fields - 1)],
               paste(parts[n_fields:length(parts)], collapse = ","))
  }
  if (length(parts) < n_fields) {
    parts <- c(parts, rep(NA_character_, n_fields - length(parts)))
  }
  parts
}

cat("Parsing", length(all_lines) - 1, "data rows...\n")
parsed <- lapply(all_lines[-1], parse_row, n_fields = n_fields)
mat    <- do.call(rbind, parsed)

bulk <- as.data.frame(mat, stringsAsFactors = FALSE)
colnames(bulk) <- c("row_id", "Ensembl", "Symbol", "logFC", "logCPM",
                    "LR", "PValue", "FDR", "Status",
                    paste0("count_", 1:8), "Description")

num_cols <- c("row_id", "logFC", "logCPM", "LR", "PValue", "FDR",
              grep("^count_", colnames(bulk), value = TRUE))
for (col in num_cols) bulk[[col]] <- as.numeric(bulk[[col]])

cat("\n========== BULK RNA-SEQ ==========\n")
cat("Dimensions:", nrow(bulk), "rows x", ncol(bulk), "cols\n")
cat("First 3 rows (key cols):\n")
print(head(bulk[, c("Ensembl", "Symbol", "logFC", "FDR", "Status")], 3))
cat("\nStatus counts:\n"); print(table(bulk$Status))

# --- 2. BETA-CELL DEG: header misaligned
beta_raw <- fread("data/raw/GSE144471_ClusterWT_KO_beta_DEG_mean.txt",
                  header = FALSE, sep = "\t", skip = 1, data.table = FALSE)

colnames(beta_raw) <- c("Ensembl", "Ensembl_dup", "pval", "qval",
                        "Symbol", "WT_mean", "KO_mean", "KO_WT_ratio")

beta <- beta_raw[, c("Ensembl", "pval", "qval", "Symbol",
                     "WT_mean", "KO_mean", "KO_WT_ratio")]

cat("\n========== BETA-CELL DEG ==========\n")
cat("Dimensions:", nrow(beta), "rows x", ncol(beta), "cols\n")
cat("First 3 rows:\n"); print(head(beta, 3))
cat("\nSummary of qval:\n"); print(summary(beta$qval))
cat("\nTop 5 genes by qval:\n")
print(head(beta[order(beta$qval), c("Symbol","qval","KO_WT_ratio")], 5))

saveRDS(bulk, "data/processed/bulk_DEG.rds")
saveRDS(beta, "data/processed/beta_DEG.rds")

cat("\n=== Done. Saved to data/processed/ ===\n")
cat("bulk rows:", nrow(bulk), "| beta rows:", nrow(beta), "\n")
