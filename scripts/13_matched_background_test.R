# Enrichment test with expression-matched background
setwd("D:/T1D_DarkGenome")
sink("logs/13_matched_session.txt")
cat("=== Session Info ===\n"); print(sessionInfo())
sink()

suppressPackageStartupMessages({library(data.table); library(ggplot2)})

gi  <- fread("data/reference/gene_index.tsv", sep="\t")
cyt <- as.data.frame(fread("results/tables/DESeq2_CYT_cytokines_vs_untreated.tsv"))
cyt$Ensembl <- sub("\\..*$", "", cyt$Ensembl)
cyt$induced <- !is.na(cyt$padj) & cyt$padj<0.05 & cyt$log2FoldChange>0.5

targets <- as.data.frame(fread("results/tables/dark_genome_annotated_local.tsv"))
targets <- targets[!is.na(targets$chr), ]

lncrnas_all <- gi[gene_type=="lncRNA" & !is.na(start)]
bm <- cyt[,c("Ensembl","baseMean")]
lncrnas_all <- merge(lncrnas_all, bm, by="Ensembl", all.x=TRUE)
lncrnas_all <- lncrnas_all[!is.na(baseMean) & baseMean>10]
cat("Expressed lncRNAs:", nrow(lncrnas_all), "\n")

coding <- gi[gene_type=="protein_coding"]
coding <- merge(coding, cyt[,c("Ensembl","induced")], by="Ensembl", all.x=TRUE)
coding <- coding[!is.na(induced)]
setorder(coding, chr, start)

chr_index <- list()
for (c in unique(coding$chr)) {
  sub <- coding[chr==c]
  chr_index[[c]] <- list(starts=as.numeric(sub$start),
                         cum_ind=c(0, cumsum(as.integer(sub$induced))))
}

fast_count <- function(chr_i, s_i, e_i, window=500000) {
  d <- chr_index[[chr_i]]
  if (is.null(d)) return(c(n=0L, n_ind=0L))
  lo <- findInterval(s_i-window, d$starts)
  hi <- findInterval(e_i+window, d$starts)
  if (hi<=lo) return(c(n=0L, n_ind=0L))
  c(n=as.integer(hi-lo), n_ind=as.integer(d$cum_ind[hi]-d$cum_ind[lo]))
}

obs_mat <- matrix(0L, nrow=nrow(targets), ncol=2)
for (i in seq_len(nrow(targets)))
  obs_mat[i,] <- fast_count(targets$chr[i], targets$start[i], targets$end[i])
colnames(obs_mat) <- c("n","n_ind")
obs <- as.data.frame(obs_mat)
obs_v <- obs[obs$n>0, ]
obs_frac <- sum(obs_v$n_ind)/sum(obs_v$n)
cat("Observed fraction:", round(obs_frac,4), "\n")

n_bg <- min(10000, nrow(lncrnas_all))
set.seed(42)
perm <- sample(nrow(lncrnas_all), n_bg)
bg_mat <- matrix(0L, nrow=n_bg, ncol=2)
for (i in seq_len(n_bg))
  bg_mat[i,] <- fast_count(lncrnas_all$chr[perm[i]],
                            lncrnas_all$start[perm[i]],
                            lncrnas_all$end[perm[i]])
colnames(bg_mat) <- c("n","n_ind")
bg_v <- bg_mat[bg_mat[,1]>0, ]
bg_frac <- sum(bg_v[,2])/sum(bg_v[,1])
cat("Background fraction:", round(bg_frac,4), "\n")

n_perm <- 5000
perm_fracs <- numeric(n_perm)
for (k in 1:n_perm) {
  s <- sample(nrow(lncrnas_all), nrow(targets))
  tn <- 0L; ti <- 0L
  for (i in seq_along(s)) {
    r <- fast_count(lncrnas_all$chr[s[i]],
                     lncrnas_all$start[s[i]],
                     lncrnas_all$end[s[i]])
    if (r["n"]>0) { tn <- tn + r["n"]; ti <- ti + r["n_ind"] }
  }
  perm_fracs[k] <- if (tn>0) ti/tn else NA_real_
}
perm_clean <- perm_fracs[is.finite(perm_fracs)]
p_val <- mean(perm_clean >= obs_frac)

cat("\n=== MATCHED ENRICHMENT ===\n")
cat("Observed:", round(obs_frac,4), "| Background:", round(bg_frac,4), "\n")
cat("Ratio:", round(obs_frac/bg_frac, 2), "x | p =", p_val, "\n")
cat("Null 99th:", round(quantile(perm_clean, 0.99), 4), "| Max:", round(max(perm_clean), 4), "\n")

plot_df <- data.frame(perm_frac=perm_clean)
p <- ggplot(plot_df, aes(x=perm_frac)) +
  geom_histogram(bins=50, fill="grey70", color="white") +
  geom_vline(xintercept=obs_frac, color="#B2182B", linewidth=1, linetype="dashed") +
  labs(title="Enrichment vs expression-matched background",
       subtitle=paste0("Observed=", round(obs_frac,4),
                       " | Background=", round(bg_frac,4),
                       " | p=", p_val),
       x="Fraction of induced coding neighbors", y="Permutations") +
  theme_minimal(base_size=12)
ggsave("results/figures/enrichment_matched.pdf", p, width=7, height=5)
ggsave("results/figures/enrichment_matched.png", p, width=7, height=5, dpi=200)
