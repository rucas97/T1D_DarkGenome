# Diagnostic: resolve SIMALR direction inconsistency
setwd("D:/T1D_DarkGenome")
suppressPackageStartupMessages(library(DESeq2))
dds_cyt <- readRDS("data/processed/dds_cyt.rds")
simalr_id <- "ENSG00000226004"
cd <- as.data.frame(colData(dds_cyt))
cd$raw <- as.numeric(counts(dds_cyt, normalized=FALSE)[simalr_id, ])
cd$norm <- as.numeric(counts(dds_cyt, normalized=TRUE)[simalr_id, ])
print(cd[, c("donor","treatment","raw","norm")], row.names=FALSE)

wide <- reshape(cd[, c("donor","treatment","raw")],
                idvar="donor", timevar="treatment", direction="wide")
colnames(wide) <- c("donor","control_raw","treated_raw")
wide$diff <- wide$treated_raw - wide$control_raw
cat("\nMean diff:", mean(wide$diff), " Positive:", sum(wide$diff>0), "\n")
