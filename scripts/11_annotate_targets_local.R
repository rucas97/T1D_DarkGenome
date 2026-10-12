# Fully offline annotation of 54 dark genome targets
setwd("D:/T1D_DarkGenome")
sink("logs/11_annotate_local_session.txt")
cat("=== Session Info ===\n"); print(sessionInfo())
sink()

suppressPackageStartupMessages(library(data.table))

gi  <- fread("data/reference/gene_index.tsv", sep="\t")
cyt <- as.data.frame(fread("results/tables/DESeq2_CYT_cytokines_vs_untreated.tsv"))
cyt$Ensembl <- sub("\\..*$", "", cyt$Ensembl)

targets <- as.data.frame(fread("results/tables/dark_genome_target_list.tsv"))
annot <- gi[gi$Ensembl %in% targets$Ensembl,
            c("Ensembl","chr","start","end","strand","gene_name","gene_type")]
targets_annot <- merge(targets, annot, by="Ensembl", all.x=TRUE)
cat("Targets annotated:", sum(!is.na(targets_annot$chr)), "/", nrow(targets_annot), "\n")
fwrite(targets_annot, "results/tables/dark_genome_annotated_local.tsv", sep="\t")

targets_ok <- targets_annot[!is.na(targets_annot$chr), ]
setDT(gi); setkey(gi, chr, start, end)

all_nb <- list()
for (i in seq_len(nrow(targets_ok))) {
  c_i <- targets_ok$chr[i]; s_i <- targets_ok$start[i]; e_i <- targets_ok$end[i]
  nb <- gi[chr==c_i & end>=(s_i-500000) & start<=(e_i+500000)]
  if (nrow(nb)==0) next
  nb <- copy(nb)
  nb[, target_symbol := targets_ok$Symbol[i]]
  nb[, dist_to_target := pmin(abs(start-s_i), abs(end-e_i))]
  all_nb[[length(all_nb)+1]] <- nb
}
nb_all <- rbindlist(all_nb)
nb_all <- merge(nb_all, cyt[,c("Ensembl","Symbol","log2FoldChange","padj")],
                by="Ensembl", all.x=TRUE)
fwrite(nb_all, "results/tables/all_targets_neighbors_local.tsv", sep="\t")
cat("Neighbor records:", nrow(nb_all), "\n")

pc <- nb_all[gene_type=="protein_coding" & !is.na(log2FoldChange)]
pc <- pc[order(-abs(log2FoldChange))]
cat("\nTop 30 coding neighbors by cytokine response:\n")
print(head(pc[,.(target_symbol, gene_name, dist_to_target, log2FoldChange, padj)], 30),
      nrows=30)
cat("\nNeighbors induced (log2FC>0.5, padj<0.05):",
    sum(pc$padj<0.05 & pc$log2FoldChange>0.5, na.rm=TRUE), "/", nrow(pc), "\n")
