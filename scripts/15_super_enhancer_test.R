# Permutation test: super enhancer overlap in dark genome targets vs background
setwd("D:/T1D_DarkGenome")
sink("logs/15_super_enhancer_session.txt")
suppressPackageStartupMessages(library(data.table))

bed_dir <- "data/raw/epiromics_extracted/epiromics_cache_data"
se <- fread(file.path(bed_dir, "BED_Annotation/Human_Regulome_hg38_Super_Enhancers.bed"),
            sep="\t", header=FALSE, data.table=TRUE, select=1:3,
            col.names=c("chr","start","end"))
se[, chr := as.character(chr)]
setorder(se, chr, start)
se_idx <- list()
for (c in unique(se$chr)) {
  sub <- se[chr == c]
  se_idx[[c]] <- list(starts = as.numeric(sub$start), ends = as.numeric(sub$end))
}
overlap <- function(chr_i, s_i, e_i, window=2000) {
  d <- se_idx[[chr_i]]; if (is.null(d)) return(0L)
  hi <- findInterval(e_i + window, d$starts); if (hi == 0) return(0L)
  sum(d$ends[1:hi] >= (s_i - window))
}
targets <- as.data.frame(fread("results/tables/dark_genome_annotated_local.tsv"))
targets <- targets[!is.na(targets$chr) & !is.na(targets$start), ]
obs_n <- sum(sapply(seq_len(nrow(targets)), function(i)
  overlap(targets$chr[i], targets$start[i], targets$end[i]) > 0))

gi  <- fread("data/reference/gene_index.tsv", sep="\t")
cyt <- as.data.frame(fread("results/tables/DESeq2_CYT_cytokines_vs_untreated.tsv"))
cyt$Ensembl <- sub("\\..*$", "", cyt$Ensembl)
lncrnas <- gi[gene_type == "lncRNA" & !is.na(start)]
lncrnas <- merge(lncrnas, cyt[,c("Ensembl","baseMean")], by="Ensembl", all.x=TRUE)
lncrnas <- lncrnas[!is.na(baseMean) & baseMean > 10]

set.seed(42); n_perm <- 5000; perm_n <- integer(n_perm)
for (k in 1:n_perm) {
  s <- sample(nrow(lncrnas), nrow(targets))
  perm_n[k] <- sum(sapply(seq_along(s), function(i) {
    idx <- s[i]
    overlap(lncrnas$chr[idx], lncrnas$start[idx], lncrnas$end[idx]) > 0
  }))
}
cat("Observed:", obs_n, "of", nrow(targets), "\n")
cat("Null median:", median(perm_n), " 95th:", quantile(perm_n, 0.95), " max:", max(perm_n), "\n")
cat("Permutation p-value:", mean(perm_n >= obs_n), "\n")
cat("=== DONE ===\n")
