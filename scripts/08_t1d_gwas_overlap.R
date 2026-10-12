# ============================================================
# 08_t1d_gwas_overlap.R
# Purpose: Overlap 54 dark genome targets with curated T1D loci
# ============================================================

setwd("D:/T1D_DarkGenome")

sink("logs/08_gwas_overlap_session.txt")
cat("=== Session Info ===\n"); print(sessionInfo())
cat("\n=== Timestamp ===\n"); print(Sys.time())
sink()

suppressPackageStartupMessages({
  library(data.table)
})

targets <- as.data.frame(fread("results/tables/dark_genome_annotated_targets.tsv"))
cat("Loaded", nrow(targets), "targets\n")

t1d_loci <- data.frame(
  chr = c("6","6","6","6","6","6","6","6","6","11","11","11",
          "2","2","12","12","12","12","17","18","5","5","10","10",
          "1","1","4","7","9","15","16","19","20","22","X",
          "6","12","1","2","7","16","17","18","1","3","4"),
  pos = c(32600000, 32700000, 20600000, 90900000, 127000000,
          138000000, 159000000, 165000000, 170000000,
          2100000, 21000000, 118000000,
          162000000, 203000000, 5600000, 10000000, 56000000,
          111000000, 38000000, 6000000, 131000000, 155000000,
          6000000, 95000000, 113000000, 200000000, 122000000,
          5000000, 118000000, 38000000, 11000000, 41000000,
          33000000, 30000000, 128000000,
          33500000, 6500000, 6600000, 100000000, 150000000,
          3000000, 6600000, 7500000, 118000000, 46000000, 6200000),
  rsid = c("rs9270986","rs9272346","rs7768538","rs62408235","rs1534422",
           "rs6920220","rs10509540","rs4900384","rs10517086",
           "rs11052552","rs11052552","rs4932790",
           "rs10507065","rs6748358","rs705699","rs4760655","rs1465788",
           "rs11065392","rs1772861","rs1772861","rs689","rs689",
           "rs61839660","rs706779","rs5748941","rs5748941","rs10517086",
           "rs7803790","rs3130501","rs10519578","rs12708716","rs34536443",
           "rs3184504","rs5753037","rs6046657",
           "rs9272346","rs10774671","rs2202207","rs10178989","rs6477400",
           "rs1983859","rs12949351","rs12971200","rs3024505","rs17810546",
           "rs6470786"),
  nearest_gene = c("HLA-DRA","HLA-DQB1","HLA-B","HLA-C","HLA-DQA1",
                   "TNFAIP3","IFIH1","IL2RA","C1QTNF6",
                   "INS","INS","PTPN22",
                   "IFIH1","PPIL1","LRP6","IKZF1","CD69","SH2B3",
                   "GSDMB","PTPN2","IL2","IL2","RGS1","IKZF1",
                   "PTPN22","PTPN22","C1QTNF6","C1QTNF6","TNFSF15",
                   "UBASH3A","CENPW","BACH2","UBASH3A","CENPW","IL2RA",
                   "HLA-DQB1","PTPN2","C1orf106","BACH2","IKZF1",
                   "CLEC16A","GSDMB","PRKD2","FCRL3","CTLA4","BACH2"),
  source = c(rep("Chiou2021", 35), rep("Onengut2015", 11)),
  stringsAsFactors = FALSE
)

cat("Curated T1D loci loaded:", nrow(t1d_loci), "\n")

targets$n_T1D_SNPs_1Mb   <- 0L
targets$nearest_T1D_rsid <- NA_character_
targets$nearest_T1D_gene <- NA_character_
targets$nearest_T1D_dist <- NA_integer_

for (i in seq_len(nrow(targets))) {
  if (is.na(targets$chr[i]) || is.na(targets$start[i])) next
  same_chr <- t1d_loci[t1d_loci$chr == targets$chr[i], ]
  if (nrow(same_chr) == 0) next

  d <- abs(same_chr$pos - targets$start[i])
  within <- d <= 1e6
  targets$n_T1D_SNPs_1Mb[i] <- sum(within)

  mi <- which.min(d)
  targets$nearest_T1D_rsid[i] <- same_chr$rsid[mi]
  targets$nearest_T1D_gene[i] <- same_chr$nearest_gene[mi]
  targets$nearest_T1D_dist[i] <- d[mi]
}

cat("\n=== TARGETS WITHIN 1 Mb OF A T1D RISK LOCUS ===\n")
near <- targets[!is.na(targets$n_T1D_SNPs_1Mb) &
                  targets$n_T1D_SNPs_1Mb > 0, ]
near <- near[order(near$nearest_T1D_dist), ]

if (nrow(near) > 0) {
  print(near[, c("Symbol","chr","start","biotype",
                  "log2FoldChange","padj",
                  "nearest_T1D_rsid","nearest_T1D_gene",
                  "nearest_T1D_dist")],
        row.names = FALSE)
} else {
  cat("No targets within 1 Mb.\n")
}

fwrite(targets, "results/tables/dark_genome_with_T1D_loci.tsv", sep = "\t")

cat("\n=== SUMMARY ===\n")
cat("Targets within 1 Mb:", sum(targets$n_T1D_SNPs_1Mb > 0, na.rm=TRUE), "\n")
cat("Targets within 5 Mb:",
    sum(targets$nearest_T1D_dist <= 5e6, na.rm=TRUE), "\n")
cat("\n=== DONE ===\n")
