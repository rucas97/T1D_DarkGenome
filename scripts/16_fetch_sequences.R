# Fetch all cDNA transcripts for 54 dark genome targets
setwd("D:/T1D_DarkGenome")
suppressPackageStartupMessages({library(data.table); library(httr2)})
dir.create("data/external", showWarnings=FALSE, recursive=TRUE)

targets <- as.data.frame(fread("results/tables/dark_genome_annotated_local.tsv"))
targets <- targets[!is.na(targets$Ensembl), ]

fetch_seq <- function(id, tries=5) {
  url <- paste0("https://rest.ensembl.org/sequence/id/", id,
                "?type=cdna;multiple_sequences=1;content-type=text/x-fasta")
  for (i in seq_len(tries)) {
    r <- tryCatch(request(url) |> req_perform() |> resp_body_string(), error=function(e) NULL)
    if (!is.null(r) && !grepl("^\\{", r)) return(r)
    Sys.sleep(2)
  }
  NULL
}
fasta_all <- character(); fail <- character()
for (i in seq_len(nrow(targets))) {
  id  <- targets$Ensembl[i]; sym <- targets$Symbol[i]
  cat(sprintf("[%2d/%d] %s ... ", i, nrow(targets), sym))
  seq <- fetch_seq(id)
  if (is.null(seq)) { cat("FAILED\n"); fail <- c(fail, id) }
  else {
    lines <- strsplit(seq, "\n")[[1]]
    n_rec <- sum(grepl("^>", lines))
    cat("OK (", n_rec, " transcripts)\n", sep="")
    lines[grepl("^>", lines)] <- paste0(lines[grepl("^>", lines)], " gene=", sym)
    fasta_all <- c(fasta_all, lines)
  }
  Sys.sleep(0.2)
}
writeLines(fasta_all, "data/external/dark_genome_54_transcripts.fa")
cat("Saved:", length(fasta_all), "lines,", sum(grepl("^>", fasta_all)), "transcripts\n")
