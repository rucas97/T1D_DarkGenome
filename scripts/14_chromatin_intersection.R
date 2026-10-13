# Chromatin context of 54 dark genome targets (islet regulome, enhancers, histones)
setwd("D:/T1D_DarkGenome")
sink("logs/14_chromatin_session.txt")
cat("=== Session Info ===\n"); print(sessionInfo())
sink()

suppressPackageStartupMessages({library(data.table); library(ggplot2)})

bed_dir <- "data/raw/epiromics_extracted/epiromics_cache_data"
read_bed <- function(path) {
  dt <- fread(path, sep="\t", header=FALSE, data.table=TRUE, select=1:4, fill=TRUE, showProgress=FALSE)
  setnames(dt, 1:3, c("chr","start","end"))
  if (ncol(dt) >= 4) setnames(dt, 4, "name") else dt[, name := NA_character_]
  dt[, chr := as.character(chr)]; dt[, start := as.numeric(start)]; dt[, end := as.numeric(end)]
  dt[!is.na(chr) & !is.na(start) & !is.na(end)]
}
islet_reg  <- read_bed(file.path(bed_dir, "BED_Annotation/Human_Islet_Regulome_hg38.bed"))
active_enh <- read_bed(file.path(bed_dir, "BED_Annotation/Human_Regulome_hg38_Active_Enhancers.bed"))
super_enh  <- read_bed(file.path(bed_dir, "BED_Annotation/Human_Regulome_hg38_Super_Enhancers.bed"))
h3k27ac    <- read_bed(file.path(bed_dir, "Histone/H3k27ac_hg38.bed"))
h3k4me1    <- read_bed(file.path(bed_dir, "Histone/H3K4me1_hg38.bed"))
h3k4me3    <- read_bed(file.path(bed_dir, "Histone/H3K4me3_hg38.bed"))

make_index <- function(bed) {
  setorder(bed, chr, start)
  idx <- list()
  for (c in unique(bed$chr)) {
    sub <- bed[chr == c]
    idx[[c]] <- list(starts = as.numeric(sub$start), ends = as.numeric(sub$end))
  }
  idx
}
overlap_count <- function(idx, chr_i, s_i, e_i) {
  d <- idx[[chr_i]]; if (is.null(d)) return(0L)
  hi <- findInterval(e_i, d$starts); if (hi == 0) return(0L)
  sum(d$ends[1:hi] >= s_i)
}
idx_islet  <- make_index(islet_reg);  idx_active <- make_index(active_enh)
idx_super  <- make_index(super_enh);  idx_h3k27  <- make_index(h3k27ac)
idx_h3k4m1 <- make_index(h3k4me1);    idx_h3k4m3 <- make_index(h3k4me3)

targets <- as.data.frame(fread("results/tables/dark_genome_annotated_local.tsv"))
targets <- targets[!is.na(targets$chr) & !is.na(targets$start), ]
WINDOW <- 2000
count_all <- function(chr_i, s_i, e_i) {
  s2 <- s_i - WINDOW; e2 <- e_i + WINDOW
  c(islet = overlap_count(idx_islet, chr_i, s2, e2),
    active = overlap_count(idx_active, chr_i, s2, e2),
    super = overlap_count(idx_super, chr_i, s2, e2),
    h3k27ac = overlap_count(idx_h3k27, chr_i, s2, e2),
    h3k4me1 = overlap_count(idx_h3k4m1, chr_i, s2, e2),
    h3k4me3 = overlap_count(idx_h3k4m3, chr_i, s2, e2))
}
obs_mat <- t(sapply(seq_len(nrow(targets)), function(i)
  count_all(targets$chr[i], targets$start[i], targets$end[i])))
obs_df <- as.data.frame(obs_mat)
obs_df$Symbol <- targets$Symbol; obs_df$chr <- targets$chr; obs_df$start <- targets$start
fwrite(obs_df, "results/tables/chromatin_target_overlaps.tsv", sep="\t")
cat("Targets with >=1 islet overlap:", sum(obs_df$islet > 0), "/", nrow(obs_df), "\n")
cat("=== DONE ===\n")
