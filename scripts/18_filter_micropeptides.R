# Filter ORFs to realistic micropeptide candidates (15-100 aa)
setwd("D:/T1D_DarkGenome")
suppressPackageStartupMessages(library(data.table))

orfs <- as.data.frame(fread("results/tables/dark_genome_ORFs.tsv"))
gi <- fread("data/reference/gene_index.tsv", sep="\t")
pc_genes <- gi[gene_type == "protein_coding", gene_name]
orfs <- orfs[!(orfs$gene %in% pc_genes), ]
orfs_f <- orfs[orfs$orf_aa >= 15 & orfs$orf_aa <= 100, ]
orfs_f <- orfs_f[grepl("^M", orfs_f$peptide), ]
orfs_u <- orfs_f[!duplicated(orfs_f$peptide), ]
cat("Unique micropeptides:", nrow(orfs_u), "\n")

make_kmers <- function(pep, k) {
  if (nchar(pep) < k) return(character())
  sapply(1:(nchar(pep) - k + 1), function(i) substr(pep, i, i + k - 1))
}
hla1_kmers <- unique(unlist(lapply(orfs_u$peptide, make_kmers, k=9)))
hla2_kmers <- unique(unlist(lapply(orfs_u$peptide, make_kmers, k=15)))

fwrite(orfs_u, "results/tables/micropeptide_candidates.tsv", sep="\t")
writeLines(hla1_kmers, "results/tables/hla1_9mers.txt")
writeLines(hla2_kmers, "results/tables/hla2_15mers.txt")
cat("HLA-I 9mers:", length(hla1_kmers), " HLA-II 15mers:", length(hla2_kmers), "\n")
