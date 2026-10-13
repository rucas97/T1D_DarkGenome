# Polypurine tract finder for RNA:DNA triplex candidates
# between SIMALR and TNFAIP3 promoter
setwd("D:/T1D_DarkGenome")
suppressPackageStartupMessages({library(httr2); library(data.table)})

fetch_seq <- function(chr, start, end, strand=1, tries=6) {
  region <- paste0(chr, ":", start, "..", end, ":", strand)
  url <- paste0("https://rest.ensembl.org/sequence/region/human/",
                region, "?content-type=text/x-fasta")
  for (i in 1:tries) {
    r <- tryCatch(request(url) |> req_perform() |> resp_body_string(),
                  error=function(e) NULL)
    if (!is.null(r) && grepl("^>", r)) {
      return(paste(toupper(unlist(strsplit(r, "\n"))[-1]), collapse=""))
    }
    Sys.sleep(5)
  }
  NULL
}

cat("Fetching SIMALR (gene body, minus strand)...\n")
simalr <- fetch_seq("6", 137943079, 137957657, -1)
cat("  Length:", nchar(simalr), "bp\n")
Sys.sleep(2)

cat("Fetching TNFAIP3 promoter (2 kb upstream)...\n")
tnfaip3_prom <- fetch_seq("6", 137865214, 137867213, 1)
if (!is.null(tnfaip3_prom)) cat("  Length:", nchar(tnfaip3_prom), "bp\n")

find_pu_tracts <- function(seq, min_len=10) {
  is_pu <- grepl("[AG]", strsplit(seq, "")[[1]])
  r <- rle(is_pu); ends <- cumsum(r$lengths)
  starts <- c(1, head(ends, -1) + 1)
  hits <- list()
  for (i in seq_along(r$values)) {
    if (r$values[i] && r$lengths[i] >= min_len) {
      hits[[length(hits)+1]] <- list(start=starts[i], end=ends[i],
                                     length=r$lengths[i],
                                     seq=substr(seq, starts[i], ends[i]))
    }
  }
  hits
}

if (!is.null(tnfaip3_prom)) {
  cat("\n=== Polypurine tracts >= 10 nt in TNFAIP3 promoter ===\n")
  tn <- find_pu_tracts(tnfaip3_prom, 10)
  cat("Found:", length(tn), "tracts\n")
  for (h in tn) cat(sprintf("  pos %5d-%5d (%2d nt): %s\n",
                            h$start, h$end, h$length, h$seq))
}
if (!is.null(simalr)) {
  cat("\n=== Top 20 polypurine tracts in SIMALR ===\n")
  sm <- find_pu_tracts(simalr, 10)
  sm <- sm[order(-sapply(sm, function(x) x$length))]
  for (h in head(sm, 20)) cat(sprintf("  pos %5d-%5d (%2d nt): %s\n",
                                       h$start, h$end, h$length, h$seq))
}
saveRDS(list(tnfaip3=tnfaip3_prom, simalr=simalr),
        "data/processed/triplex_sequences.rds")
cat("\n=== DONE ===\n")
