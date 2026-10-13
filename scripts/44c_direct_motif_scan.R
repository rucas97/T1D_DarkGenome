# Direct PWM scan for NF-kB/STAT/IRF motifs in SIMALR locus
setwd("D:/T1D_DarkGenome")
suppressPackageStartupMessages({library(Biostrings); library(httr2); library(data.table)})
dir.create("results/motif_enrichment", showWarnings=FALSE, recursive=TRUE)

fetch_region <- function(chr, start, end, strand=1) {
  url <- paste0("https://rest.ensembl.org/sequence/region/human/",
                chr, ":", start, "..", end, ":", strand,
                "?content-type=text/x-fasta")
  for (i in 1:5) {
    r <- tryCatch({
      fasta <- request(url) |> req_perform() |> resp_body_string()
      seq <- paste(strsplit(fasta, "\n")[[1]][-1], collapse="")
      gsub("[^ACGTacgt]", "", toupper(seq))
    }, error=function(e) NULL)
    if (!is.null(r) && nchar(r) > 100) return(r)
    Sys.sleep(3)
  }
  stop("Failed")
}

cat("Fetching SIMALR sequences...\n")
promoter   <- fetch_region("6", 137957658, 137967657, -1); Sys.sleep(1)
gene_body  <- fetch_region("6", 137943079, 137957657, -1); Sys.sleep(1)
intergenic <- fetch_region("6", 137885837, 137943078, -1)
regions <- c(promoter_10kb=promoter, gene_body=gene_body, intergenic_57kb=intergenic)
cat("Loaded:", sum(nchar(regions)), "bp total\n\n")

make_counts <- function(m) { m <- round(m*1000); storage.mode(m) <- "integer";
  rownames(m) <- c("A","C","G","T"); m }

PWMs <- list(
  NFKB1 = make_counts(matrix(c(0.03,0.02,0.90,0.05,0.60,0.05,0.05,0.30,0.05,0.90,0.03,0.02,
    0.10,0.05,0.75,0.10,0.25,0.25,0.25,0.25,0.25,0.25,0.25,0.25,
    0.10,0.60,0.10,0.20,0.20,0.60,0.10,0.10,0.05,0.85,0.05,0.05,
    0.25,0.60,0.10,0.05), nrow=4, byrow=FALSE)),
  RELB = make_counts(matrix(c(0.02,0.02,0.92,0.04,0.55,0.03,0.37,0.05,0.80,0.08,0.06,0.06,
    0.10,0.10,0.10,0.70,0.30,0.25,0.25,0.20,0.25,0.25,0.25,0.25,
    0.10,0.60,0.10,0.20,0.55,0.20,0.20,0.05,0.05,0.88,0.05,0.02,
    0.30,0.55,0.10,0.05), nrow=4, byrow=FALSE)),
  RELA = make_counts(matrix(c(0.03,0.02,0.90,0.05,0.60,0.05,0.05,0.30,0.05,0.85,0.05,0.05,
    0.10,0.05,0.75,0.10,0.25,0.25,0.25,0.25,0.25,0.25,0.25,0.25,
    0.10,0.60,0.10,0.20,0.20,0.60,0.10,0.10,0.05,0.85,0.05,0.05,
    0.25,0.60,0.10,0.05), nrow=4, byrow=FALSE)),
  STAT3 = make_counts(matrix(c(0.20,0.15,0.15,0.50,0.25,0.20,0.20,0.35,0.10,0.75,0.10,0.05,
    0.80,0.05,0.10,0.05,0.30,0.25,0.25,0.20,0.25,0.25,0.25,0.25,
    0.10,0.10,0.75,0.05,0.15,0.15,0.55,0.15,0.65,0.10,0.15,0.10,
    0.70,0.10,0.10,0.10), nrow=4, byrow=FALSE)),
  STAT1 = make_counts(matrix(c(0.25,0.20,0.20,0.35,0.30,0.25,0.20,0.25,0.15,0.55,0.15,0.15,
    0.70,0.10,0.10,0.10,0.30,0.25,0.25,0.20,0.25,0.25,0.25,0.25,
    0.10,0.10,0.70,0.10,0.20,0.20,0.45,0.15,0.55,0.15,0.15,0.15,
    0.65,0.15,0.10,0.10), nrow=4, byrow=FALSE)),
  IRF1 = make_counts(matrix(c(0.15,0.10,0.65,0.10,0.75,0.08,0.10,0.07,0.85,0.05,0.05,0.05,
    0.80,0.05,0.10,0.05,0.30,0.25,0.25,0.20,0.25,0.25,0.25,0.25,
    0.10,0.10,0.75,0.05,0.75,0.10,0.10,0.05,0.30,0.30,0.20,0.20,
    0.65,0.10,0.15,0.10,0.55,0.15,0.15,0.15), nrow=4, byrow=FALSE)),
  BATF = make_counts(matrix(c(0.20,0.15,0.15,0.50,0.35,0.20,0.20,0.25,0.15,0.15,0.55,0.15,
    0.75,0.10,0.10,0.05,0.20,0.20,0.20,0.40,0.10,0.75,0.10,0.05,
    0.10,0.10,0.70,0.10), nrow=4, byrow=FALSE)),
  TBX21 = make_counts(matrix(c(0.10,0.70,0.10,0.10,0.20,0.20,0.30,0.30,0.15,0.55,0.20,0.10,
    0.30,0.25,0.25,0.20,0.70,0.10,0.10,0.10,0.20,0.20,0.40,0.20,
    0.20,0.55,0.15,0.10,0.15,0.15,0.55,0.15,0.55,0.15,0.15,0.15),
    nrow=4, byrow=FALSE)),
  IKZF1 = make_counts(matrix(c(0.30,0.20,0.25,0.25,0.55,0.20,0.15,0.10,0.20,0.20,0.50,0.10,
    0.30,0.25,0.30,0.15,0.20,0.30,0.30,0.20,0.25,0.45,0.15,0.15,
    0.60,0.15,0.15,0.10,0.30,0.30,0.20,0.20,0.40,0.20,0.20,0.20,
    0.20,0.50,0.15,0.15), nrow=4, byrow=FALSE)),
  EBF1 = make_counts(matrix(c(0.70,0.10,0.10,0.10,0.15,0.15,0.55,0.15,0.15,0.15,0.15,0.55,
    0.10,0.70,0.10,0.10,0.55,0.15,0.15,0.15,0.25,0.25,0.25,0.25,
    0.20,0.20,0.30,0.30,0.25,0.25,0.25,0.25,0.60,0.15,0.15,0.10,
    0.15,0.55,0.15,0.15,0.15,0.15,0.55,0.15), nrow=4, byrow=FALSE))
)

pwm_hits <- function(pwm_counts, seq, region_name, motif_name, threshold=0.80) {
  pwm_obj <- PWM(pwm_counts)
  hits <- matchPWM(pwm_obj, DNAString(seq),
                   min.score = paste0(round(threshold*100), "%"),
                   with.score = TRUE)
  if (length(hits) == 0) return(NULL)
  data.table(motif=motif_name, region=region_name,
             start=start(hits), end=end(hits), width=width(hits),
             score=mcols(hits)$score, matched_seq=as.character(hits))
}

cat("Scanning", length(PWMs), "motifs across", length(regions), "regions...\n\n")
all_hits <- list()
for (mn in names(PWMs)) for (rn in names(regions)) {
  h <- pwm_hits(PWMs[[mn]], regions[[rn]], rn, mn)
  if (!is.null(h)) all_hits[[length(all_hits)+1]] <- h
}

if (length(all_hits) > 0) {
  hits_dt <- rbindlist(all_hits)
  cat("=== ALL MOTIF HITS ===\n"); print(hits_dt, row.names=FALSE)
  cat("\n=== SUMMARY ===\n")
  summary_tbl <- hits_dt[, .N, by=.(motif, region)][order(motif, region)]
  print(summary_tbl, row.names=FALSE)
  fwrite(hits_dt, "results/motif_enrichment/SIMALR_PWM_hits.tsv", sep="\t")
  fwrite(summary_tbl, "results/motif_enrichment/SIMALR_PWM_summary.tsv", sep="\t")
  cat("\nSaved TSVs.\n")
} else cat("No hits.\n")
cat("\n=== DONE ===\n")
