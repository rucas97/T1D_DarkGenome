# Per-donor SIMALR induction — CORRECTED column order
setwd("D:/T1D_DarkGenome")
suppressPackageStartupMessages({library(DESeq2); library(ggplot2)})

dds_cyt <- readRDS("data/processed/dds_cyt.rds")
simalr_id <- "ENSG00000226004"
cd <- as.data.frame(colData(dds_cyt))
cd$norm <- as.numeric(counts(dds_cyt, normalized = TRUE)[simalr_id, ])

donors <- unique(cd$donor)
wide <- data.frame(donor=donors, control=NA_real_, treated=NA_real_)
for (i in seq_along(donors)) {
  d <- donors[i]
  wide$control[i] <- cd$norm[cd$donor == d & cd$treatment == "control"]
  wide$treated[i] <- cd$norm[cd$donor == d & cd$treatment == "treated"]
}
wide$log2FC <- log2((wide$treated + 1) / (wide$control + 1))
wide <- wide[order(-wide$log2FC), ]
print(wide, row.names = FALSE)
cat("\nMean log2FC:", round(mean(wide$log2FC),2), " Donors UP:", sum(wide$log2FC>0), "/", nrow(wide), "\n")
write.csv(wide, "results/tables/SIMALR_per_donor_corrected.csv", row.names=FALSE)

wide$donor <- factor(wide$donor, levels=wide$donor)
p <- ggplot(wide, aes(x=donor, y=log2FC)) +
  geom_col(fill="#B2182B", color="black", linewidth=0.3) +
  geom_hline(yintercept=0, linewidth=0.4) +
  labs(title="SIMALR induction by cytokines — 19 donors",
       x="Donor", y="log2FC (treated / control)") +
  theme_minimal(base_size=11) +
  theme(axis.text.x=element_text(angle=45, hjust=1))
ggsave("results/figures/SIMALR_per_donor_corrected.pdf", p, width=8, height=5)
ggsave("results/figures/SIMALR_per_donor_corrected.png", p, width=8, height=5, dpi=200)
