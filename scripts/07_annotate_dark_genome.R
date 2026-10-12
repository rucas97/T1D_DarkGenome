# ============================================================
# 07_annotate_dark_genome.R
# Purpose: Annotate 54 ncRNAs with Ensembl coordinates + biotype
# ============================================================

setwd("D:/T1D_DarkGenome")
sink("logs/07_annotate_session.txt")
cat("=== Session Info ===\n"); print(sessionInfo())
cat("\n=== Timestamp ===\n"); print(Sys.time())
sink()

suppressPackageStartupMessages({
  library(data.table)
  library(jsonlite)
  library(httr2)
})

targets <- as.data.frame(fread("results/tables/dark_genome_target_list.tsv"))
cat("Target ncRNAs:", nrow(targets), "\n")

cat("\nBulk-querying Ensembl (single POST)...\n")
resp <- request("https://rest.ensembl.org/lookup/id") |>
  req_headers(`Content-Type` = "application/json",
              `Accept` = "application/json") |>
  req_body_json(list(ids = targets$Ensembl)) |>
  req_perform()

j <- resp_body_json(resp)
cat("Returned records:", length(j), "\n")

annot <- do.call(rbind, lapply(names(j), function(id) {
  r <- j[[id]]
  if (is.null(r$seq_region_name)) {
    return(data.frame(Ensembl = id, chr = NA, start = NA, end = NA,
                      strand = NA, biotype = NA, stringsAsFactors = FALSE))
  }
  data.frame(Ensembl = id,
             chr     = as.character(r$seq_region_name),
             start   = as.numeric(r$start),
             end     = as.numeric(r$end),
             strand  = as.integer(r$strand),
             biotype = r$biotype,
             stringsAsFactors = FALSE)
}))

targets <- merge(targets, annot, by = "Ensembl", all.x = TRUE)
cat("Biotype distribution:\n")
print(table(targets$biotype, useNA = "ifany"))

fwrite(targets, "results/tables/dark_genome_annotated_targets.tsv", sep = "\t")

cat("\n=== TOP 20 ANNOTATED TARGETS ===\n")
print(head(targets[order(-targets$log2FoldChange),
                  c("Symbol","chr","start","end","biotype",
                    "log2FoldChange","padj")], 20), row.names = FALSE)

cat("\n=== DONE ===\n")
