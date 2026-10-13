# Find ORFs >= 8 aa in all transcripts of dark genome lncRNAs
setwd("D:/T1D_DarkGenome")
suppressPackageStartupMessages(library(Biostrings))

seqs <- readDNAStringSet("data/external/dark_genome_54_transcripts.fa")
cat("Loaded", length(seqs), "transcripts\n")

codon_table <- c(
  TTT="F",TTC="F",TTA="L",TTG="L",CTT="L",CTC="L",CTA="L",CTG="L",
  ATT="I",ATC="I",ATA="I",ATG="M",GTT="V",GTC="V",GTA="V",GTG="V",
  TCT="S",TCC="S",TCA="S",TCG="S",CCT="P",CCC="P",CCA="P",CCG="P",
  ACT="T",ACC="T",ACA="T",ACG="T",GCT="A",GCC="A",GCA="A",GCG="A",
  TAT="Y",TAC="Y",TAA="*",TAG="*",CAT="H",CAC="H",CAA="Q",CAG="Q",
  AAT="N",AAC="N",AAA="K",AAG="K",GAT="D",GAC="D",GAA="E",GAG="E",
  TGT="C",TGC="C",TGA="*",TGG="W",CGT="R",CGC="R",CGA="R",CGG="R",
  AGT="S",AGC="S",AGA="R",AGG="R",GGT="G",GGC="G",GGA="G",GGG="G"
)
translate <- function(nt) {
  if (nchar(nt) < 3) return("")
  idx <- seq(1, nchar(nt) - 2, 3)
  codons <- substring(nt, idx, idx + 2)
  paste(codon_table[codons], collapse = "")
}
find_orfs <- function(nt, min_aa=8) {
  aa <- translate(nt); if (nchar(aa) < min_aa) return(NULL)
  chars <- strsplit(aa, "")[[1]]; hits <- list(); start_idx <- NA_integer_
  for (i in seq_along(chars)) {
    if (chars[i] == "M" && is.na(start_idx)) start_idx <- i
    else if (chars[i] == "*" && !is.na(start_idx)) {
      pep_len <- i - start_idx
      if (pep_len >= min_aa) {
        hits[[length(hits)+1]] <- list(length=pep_len,
          peptide = paste(chars[start_idx:(i-1)], collapse=""))
      }
      start_idx <- NA_integer_
    }
  }
  if (!is.na(start_idx)) {
    pep_len <- length(chars) - start_idx + 1
    if (pep_len >= min_aa) {
      hits[[length(hits)+1]] <- list(length=pep_len,
        peptide = paste(chars[start_idx:length(chars)], collapse=""))
    }
  }
  hits
}
revcomp <- function(s) {
  s <- chartr("ACGTacgt", "TGCAtgca", s)
  paste(rev(strsplit(s, "")[[1]]), collapse = "")
}

results <- list()
for (i in seq_along(seqs)) {
  name <- names(seqs)[i]; s <- toupper(as.character(seqs[[i]]))
  gene_sym <- sub(".*gene=([^ ]+).*", "\\1", name)
  if (gene_sym == name) gene_sym <- NA_character_
  for (f in 0:2) {
    sub <- if (f == 0) s else substring(s, f + 1)
    for (o in find_orfs(sub, 8) %||% list()) {
      results[[length(results)+1]] <- data.frame(transcript=name, gene=gene_sym,
        strand="+", frame=f+1, orf_aa=o$length, peptide=o$peptide,
        stringsAsFactors=FALSE)
    }
  }
  rc <- revcomp(s)
  for (f in 0:2) {
    sub <- if (f == 0) rc else substring(rc, f + 1)
    for (o in find_orfs(sub, 8) %||% list()) {
      results[[length(results)+1]] <- data.frame(transcript=name, gene=gene_sym,
        strand="-", frame=f+1, orf_aa=o$length, peptide=o$peptide,
        stringsAsFactors=FALSE)
    }
  }
}
`%||%` <- function(a, b) if (is.null(a)) b else a
orf_df <- do.call(rbind, results)
orf_df <- orf_df[order(-orf_df$orf_aa), ]
fwrite(orf_df, "results/tables/dark_genome_ORFs.tsv", sep="\t")
cat("Total ORFs:", nrow(orf_df), "  >=30 aa:", sum(orf_df$orf_aa >= 30), "\n")
