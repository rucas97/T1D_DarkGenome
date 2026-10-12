# Deep characterization of the LINC02528 / TNFAIP3 link
setwd("D:/T1D_DarkGenome")
sink("logs/09_deep_discovery_session.txt")
cat("=== Session Info ===\n"); print(sessionInfo())
sink()

suppressPackageStartupMessages({
  library(data.table); library(DESeq2)
  library(httr2); library(jsonlite)
})

cyt <- as.data.frame(fread("results/tables/DESeq2_CYT_cytokines_vs_untreated.tsv"))
ers <- as.data.frame(fread("results/tables/DESeq2_ERS_thapsigargin_vs_DMSO.tsv"))

nfkb_axis <- c("TNFAIP3","NFKB1","NFKB2","RELA","RELB","NFKBIA","NFKBIB",
               "NFKBIZ","NFKBIE","TNIP1","TNIP2","TNIP3","IKBKB","IKBKG",
               "TRAF6","TRAF3","TRAF2","RIPK1","MAP3K7","TAB1","TAB2",
               "BCL3","NFKBID","REL","CD40","LTBR","TNFRSF1A")

cat("### CYT NF-kB axis ###\n")
cyt_nfkb <- cyt[cyt$Symbol %in% nfkb_axis, c("Symbol","log2FoldChange","padj")]
print(cyt_nfkb[order(-cyt_nfkb$log2FoldChange), ], row.names = FALSE)
fwrite(cyt_nfkb, "results/tables/CYT_NFkB_axis.tsv", sep="\t")

tnf <- cyt_nfkb[cyt_nfkb$Symbol=="TNFAIP3","log2FoldChange"]
nfkb1 <- cyt_nfkb[cyt_nfkb$Symbol=="NFKB1","log2FoldChange"]
cat("TNFAIP3 log2FC:", tnf, "| Ratio to NFKB1:", tnf/nfkb1, "\n")

# Co-expression
dds_cyt <- readRDS("data/processed/dds_cyt.rds")
vsd <- vst(dds_cyt, blind = FALSE)
treated <- colData(vsd)$treatment == "treated"
vsd_t <- vsd[, treated]
LINC_ID <- "ENSG00000226004"
if (LINC_ID %in% rownames(assay(vsd_t))) {
  expr <- assay(vsd_t)
  linc <- expr[LINC_ID, ]
  cors <- apply(expr, 1, function(x) if (sd(x)==0) NA_real_ else cor(x, linc, method="spearman"))
  co_expr <- data.frame(Ensembl=names(cors), rho=as.numeric(cors))
  co_expr <- merge(co_expr, unique(cyt[,c("Ensembl","Symbol","log2FoldChange","padj")]),
                   by="Ensembl", all.x=TRUE)
  co_expr <- co_expr[order(-co_expr$rho), ]
  cat("\nTNFAIP3 rank:", which(co_expr$Symbol=="TNFAIP3"), "/", nrow(co_expr), "\n")
  cat("rho(LINC02528, TNFAIP3):", co_expr$rho[co_expr$Symbol=="TNFAIP3"], "\n")
  fwrite(co_expr, "results/tables/LINC02528_coexpression.tsv", sep="\t")
}
cat("\n=== DONE ===\n")
