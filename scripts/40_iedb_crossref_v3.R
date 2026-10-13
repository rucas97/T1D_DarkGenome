# Cross-reference SIMALR binding cores against IEDB T1D epitopes
setwd("D:/T1D_DarkGenome")
suppressPackageStartupMessages({library(httr2); library(jsonlite); library(data.table)})

simalr <- fread("results/tables/MixMHC2pred_SIMALR_strong.tsv")
cores <- unique(simalr$Core_best)
cat("SIMALR cores:", length(cores), "\n")

uniprot_map <- list(
  INS="P01308", GAD2="Q05329", PTPRN="Q16849", SLC30A8="Q8IWU4",
  G6PC2="Q9NQR9", CHGA="P10645", ICA1="Q05084", GAD1="Q99259"
)
iedb_base <- "https://query-api.iedb.org/epitope_search"
iedb_seqs <- character()

for (gene in names(uniprot_map)) {
  uniprot <- uniprot_map[[gene]]
  url <- paste0(iedb_base, "?parent_source_antigen_iri=eq.UNIPROT:", uniprot,
                "&select=structure_description,parent_source_antigen_names&limit=500")
  cat("\n===", gene, "(", uniprot, ") ===\n")
  r <- tryCatch(request(url) |> req_perform() |> resp_body_json(),
                error=function(e) { cat("  ERROR:", conditionMessage(e), "\n"); NULL })
  if (!is.null(r) && length(r) > 0) {
    cat("  Retrieved", length(r), "epitopes\n")
    for (ep in r) {
      seq <- ep$structure_description
      if (!is.null(seq) && is.character(seq) && nchar(seq) >= 7) {
        seq_clean <- gsub("\\s*\\+.*$", "", seq)
        seq_clean <- gsub("[^ACDEFGHIKLMNPQRSTVWY]", "", toupper(seq_clean))
        if (nchar(seq_clean) >= 7) iedb_seqs <- c(iedb_seqs, seq_clean)
      }
    }
  }
  Sys.sleep(1)
}

curated <- c("SHLVEALYLVCGERG","LVEALYLVCGERGFFY","ALWMRLLPLL",
             "DVMNILLQYVVKSF","NFFRMVISNPAAT","KSLFNVSSHEDIRDE",
             "FVNILALVLLKHLVK","QLSPQILVLTGVSTS","VFAVCLLWAVPERHG",
             "HLHLLQPSL","WARQAPPAYRPQAP")
all_seqs <- unique(c(iedb_seqs, curated))
cat("\nTotal T1D sequences:", length(all_seqs), "\n")

kmer <- function(seq, k=7) {
  if (nchar(seq) < k) return(character())
  sapply(1:(nchar(seq)-k+1), function(i) substr(seq, i, i+k-1))
}
core_kmers <- unique(unlist(lapply(cores, kmer)))
t1d_kmers  <- unique(unlist(lapply(all_seqs, kmer)))
shared <- intersect(core_kmers, t1d_kmers)

cat("\n=== SHARED 7-MERS ===\n")
if (length(shared) > 0) { cat("FOUND", length(shared), "\n"); print(shared) }
else cat("No shared 7-mers.\n")

cat("\n=== EXACT MATCHES ===\n")
exact <- intersect(cores, all_seqs)
if (length(exact) > 0) print(exact) else cat("None.\n")

writeLines(all_seqs, "results/tables/T1D_autoantigen_sequences.txt")
if (length(shared) > 0)
  writeLines(shared, "results/tables/SIMALR_T1D_shared_7mers.txt")
cat("\n=== DONE ===\n")
