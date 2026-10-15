suppressPackageStartupMessages({
  library(Seurat); library(ggplot2); library(dplyr)
})

# Step 1: inspect
rds_files <- list.files('/content/hpap', pattern='\\.rds$', full.names=TRUE, ignore.case=TRUE)
cat("Found RDS:", rds_files, "\n")

obj <- readRDS(rds_files[1])
cat("Loaded:", ncol(obj), "cells,", nrow(obj), "genes\n")
cat("Metadata columns:\n")
print(colnames(obj@meta.data))
cat("\nFirst rows:\n")
print(head(obj@meta.data, 3))
cat("\nSIMALR present? ",
    any(c("LINC02528","SIMALR","ENSG00000226004") %in% rownames(obj)), "\n")

# Step 2 (uncomment after confirming metadata columns):
# ct_col <- "cell_type"      # <-- adjust after inspecting
# ds_col <- "disease"        # <-- adjust after inspecting
# donor_col <- "donor"       # <-- adjust after inspecting
#
# mac_labels <- grep("macro|myeloid|CD14|monocyte|immune",
#                    unique(obj@meta.data[[ct_col]]), ignore.case=TRUE, value=TRUE)
# mac <- subset(obj, cells=colnames(obj)[obj@meta.data[[ct_col]] %in% mac_labels])
# simalr <- "LINC02528"
# mac$SIMALR <- FetchData(mac, vars=simalr)[,1]
#
# donor_tab <- mac@meta.data %>%
#   group_by(!!sym(donor_col), !!sym(ds_col)) %>%
#   summarise(n=n(), sim_plus=sum(SIMALR>0), pct=sim_plus/n*100, .groups="drop")
# print(donor_tab, n=50)
