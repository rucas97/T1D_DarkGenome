# Which single cytokine induces SIMALR in EndoC-bH1 (GSE235683)?
setwd("D:/T1D_DarkGenome")
suppressPackageStartupMessages(library(data.table))
dt <- fread("data/raw/GSE235683_processed_data.tsv", sep=",", header=TRUE, data.table=FALSE)

simalr_row <- dt[dt$ensembl == "ENSG00000226004" |
                 grepl("SIMALR|LINC02528", dt$gene_name, ignore.case=TRUE), ]
cat("SIMALR row found:", nrow(simalr_row), "\n")
if (nrow(simalr_row) > 0) print(simalr_row)

targets <- c("TNFAIP3","NFKBIA","STAT1","ISG15","CXCL10","BBC3","CDKN1A","PERP")
for (g in targets) {
  r <- dt[dt$gene_name == g, ]
  if (nrow(r) > 0) {
    cat(sprintf("\n=== %s ===\n", g))
    sample_cols <- colnames(dt)[sapply(dt, is.numeric)]
    vals <- as.numeric(r[1, sample_cols]); names(vals) <- sample_cols
    grp <- sub("^.*-(IFNg|IL1B|TNFa|NT)$", "\\1", names(vals))
    print(round(tapply(vals, grp, mean), 4))
  }
}
