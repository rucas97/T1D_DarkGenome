# Diagnostic: dump UCSC regulatory feature structure at SIMALR locus
setwd("D:/T1D_DarkGenome")
suppressPackageStartupMessages({library(httr2); library(jsonlite)})

url <- paste0("https://api.genome.ucsc.edu/getData/track?",
              "genome=hg38;track=encRegTfbsClustered;",
              "chrom=chr6;start=137943079;end=137957657")
resp <- request(url) |> req_perform() |> resp_body_json()
cat("Top-level names:", paste(names(resp), collapse=", "), "\n\n")
cat("Structure of encRegTfbsClustered:\n")
str(resp$encRegTfbsClustered, max.level=2)
cat("\nFirst 3 items fully:\n")
hits <- resp$encRegTfbsClustered
for (i in 1:min(3, length(hits))) {
  cat("--- item", i, "---\n"); print(hits[[i]])
}
