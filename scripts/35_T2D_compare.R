# Check whether SIMALR/TNFAIP3 axis is T1D-specific vs T2D
setwd("D:/T1D_DarkGenome")
suppressPackageStartupMessages(library(data.table))

t2d <- fread("data/raw/GSE159984/GSE159984_de-t2d.tsv.gz", sep="\t",
             header=TRUE, data.table=FALSE)
cat("T2D DE table rows:", nrow(t2d), "\n")

check <- c("ENSG00000226004","ENSG00000118503","ENSG00000050730",
           "ENSG00000168884","ENSG00000145901","ENSG00000169245",
           "ENSG00000136244")
for (id in check) {
  r <- t2d[t2d$gene_id == id, ]
  if (nrow(r) > 0) {
    cat(sprintf("%-20s %-12s log2FC=%+.3f  padj=%.3g\n",
                id, r$short_id[1], r$log2FoldChange[1], r$padj[1]))
  } else {
    cat(sprintf("%-20s NOT DETECTED in T2D or ND islets\n", id))
  }
}
