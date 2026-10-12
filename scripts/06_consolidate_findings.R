# ============================================================
# 06_consolidate_findings.R
# Purpose: Produce summary figure + dark genome target list
# ============================================================

setwd("D:/T1D_DarkGenome")

sink("logs/06_consolidate_session.txt")
cat("=== Session Info ===\n"); print(sessionInfo())
cat("\n=== Timestamp ===\n"); print(Sys.time())
sink()

suppressPackageStartupMessages({
  library(data.table)
  library(ggplot2)
})

cyt <- as.data.frame(fread("results/tables/DESeq2_CYT_cytokines_vs_untreated.tsv"))
ers <- as.data.frame(fread("results/tables/DESeq2_ERS_thapsigargin_vs_DMSO.tsv"))

key_genes <- c("CXCL10","STAT1","ISG15","CGAS","STING1","TBK1","IRF3",
               "DDX58","IFIH1","TP53","CDKN1A","BBC3","GADD45A",
               "IL6","CXCL1","MMP3","CDKN2A","DDIT3","HSPA5")
key_genes <- intersect(key_genes, intersect(cyt$Symbol, ers$Symbol))

sumtab <- data.frame(
  Gene      = key_genes,
  CYT_log2FC = cyt$log2FoldChange[match(key_genes, cyt$Symbol)],
  CYT_padj   = cyt$padj[match(key_genes, cyt$Symbol)],
  ERS_log2FC = ers$log2FoldChange[match(key_genes, ers$Symbol)],
  ERS_padj   = ers$padj[match(key_genes, ers$Symbol)]
)
sumtab <- sumtab[order(-sumtab$CYT_log2FC), ]

cat("=== KEY PATHWAY GENES (CYT vs ERS) ===\n")
print(sumtab, row.names = FALSE)
fwrite(sumtab, "results/tables/summary_key_pathways.tsv", sep = "\t")

plot_df <- rbind(
  data.frame(Gene = sumtab$Gene, log2FC = sumtab$CYT_log2FC, Stress = "Cytokine"),
  data.frame(Gene = sumtab$Gene, log2FC = sumtab$ERS_log2FC, Stress = "ER stress")
)
plot_df$Gene <- factor(plot_df$Gene, levels = rev(sumtab$Gene))

p <- ggplot(plot_df, aes(x = Gene, y = log2FC, fill = Stress)) +
  geom_col(position = position_dodge(width = 0.8), width = 0.7) +
  coord_flip() +
  scale_fill_manual(values = c("Cytokine" = "#B2182B", "ER stress" = "#2166AC")) +
  geom_hline(yintercept = 0, color = "black", linewidth = 0.3) +
  labs(title = "Key pathway genes: cytokine vs ER stress in human islets",
       subtitle = "Paired DESeq2 (donor-matched), primary islets",
       x = NULL, y = "log2 fold change") +
  theme_minimal(base_size = 12) +
  theme(legend.position = "top")

ggsave("results/figures/summary_key_pathways.pdf", p, width = 7, height = 6)
ggsave("results/figures/summary_key_pathways.png", p, width = 7, height = 6, dpi = 200)

is_ncrna <- function(sym) {
  ifelse(is.na(sym), FALSE,
         grepl("^(LINC|AC[0-9]|AL[0-9]|AP[0-9]|LOC[0-9]|-AS[0-9]|MIR|SNOR|SCARNA)",
               sym, ignore.case = TRUE))
}

cyt$is_ncrna <- is_ncrna(cyt$Symbol)
nc_top <- cyt[cyt$is_ncrna & cyt$padj < 0.05 & cyt$log2FoldChange > 2, ]
nc_top <- nc_top[order(-nc_top$log2FoldChange),
                 c("Symbol","Ensembl","log2FoldChange","padj")]
fwrite(nc_top, "results/tables/dark_genome_target_list.tsv", sep = "\t")

cat("\n=== DARK GENOME TARGET LIST:", nrow(nc_top), "ncRNAs ===\n")
print(head(nc_top, 20), row.names = FALSE)

cat("\n=== DONE ===\n")
