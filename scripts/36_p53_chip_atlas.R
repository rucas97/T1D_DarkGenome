# Check p53 ChIP binding at SIMALR locus via UCSC ENCODE regulatory tracks
setwd("D:/T1D_DarkGenome")
suppressPackageStartupMessages({library(httr2); library(jsonlite); library(data.table)})

url <- paste0("https://api.genome.ucsc.edu/getData/track?",
              "genome=hg38;track=encRegTfbsClustered;",
              "chrom=chr6;start=137943079;end=137957657")
resp <- request(url) |> req_perform() |> resp_body_json()
hits <- resp$encRegTfbsClustered
cat("Regulatory features in SIMALR region:", length(hits), "\n\n")

if (length(hits) > 0) {
  df <- do.call(rbind, lapply(hits, function(x) {
    data.frame(chromStart=x$chromStart, chromEnd=x$chromEnd,
               name=x$name, score=x$score, stringsAsFactors=FALSE)
  }))
  p53_hits <- df[grepl("p53|TP53|P63|P73", df$name, ignore.case=TRUE), ]
  cat("p53-family hits:", nrow(p53_hits), "\n")
  if (nrow(p53_hits) > 0) print(p53_hits)
  fwrite(df, "results/tables/SIMALR_encReg_features.tsv", sep="\t")
}
cat("\n=== DONE ===\n")
