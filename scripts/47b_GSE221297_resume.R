suppressPackageStartupMessages({
  library(Seurat); library(ggplot2); library(dplyr)
})

out_dir <- "/content/drive/MyDrive/T1D_DarkGenome"
merged  <- readRDS(file.path(out_dir, "GSE221297_merged.rds"))
cat("Loaded:", ncol(merged), "cells\n")

mono_markers <- c("CD14","FCGR3A","FCN1","S100A8","S100A9","LYZ","VCAN","MS4A7","CD68","CD163")
mono_markers <- mono_markers[mono_markers %in% rownames(merged)]
merged <- AddModuleScore(merged, features=list(mono_markers), name="mono_score")
cs <- merged@meta.data %>% group_by(seurat_clusters) %>%
  summarise(mean_mono=mean(mono_score1,na.rm=TRUE), n=n()) %>% arrange(desc(mean_mono))
mc <- as.character(cs$seurat_clusters[cs$mean_mono > 0.5])
mono <- subset(merged, subset=seurat_clusters %in% mc)
mono <- JoinLayers(mono)
cat("Monocyte cells:", ncol(mono), "\n")

mm <- mono@meta.data
mm$SIMALR <- FetchData(mono, vars="LINC02528")[,1]

donor_tab <- mm %>% group_by(group, sample) %>%
  summarise(n=n(), sim_plus=sum(SIMALR>0),
            pct=sim_plus/n*100, .groups="drop") %>%
  arrange(group, desc(pct))
cat("\n=== Per-donor SIMALR+ rate ===\n")
print(donor_tab, n=40)
write.table(donor_tab, file.path(out_dir,"GSE221297_SIMALR_by_donor.tsv"),
            sep="\t", quote=FALSE, row.names=FALSE)

cat("\n=== Donor-level tests ===\n")
kt <- kruskal.test(pct ~ group, data=donor_tab)
cat(sprintf("Kruskal-Wallis: chi2=%.3f, p=%.4g\n", kt$statistic, kt$p.value))

d_hc  <- donor_tab$pct[donor_tab$group=="HC"]
d_t1d <- donor_tab$pct[donor_tab$group=="T1D"]
d_pre <- donor_tab$pct[donor_tab$group=="Pre"]

cat(sprintf("T1D vs HC:  W=%.0f p=%.4g\n", wilcox.test(d_t1d,d_hc,exact=FALSE)$statistic,
            wilcox.test(d_t1d,d_hc,exact=FALSE)$p.value))
cat(sprintf("T1D vs Pre: W=%.0f p=%.4g\n", wilcox.test(d_t1d,d_pre,exact=FALSE)$statistic,
            wilcox.test(d_t1d,d_pre,exact=FALSE)$p.value))
cat(sprintf("HC  vs Pre: W=%.0f p=%.4g\n", wilcox.test(d_hc,d_pre,exact=FALSE)$statistic,
            wilcox.test(d_hc,d_pre,exact=FALSE)$p.value))

c1 <- wilcox.test(mm$SIMALR[mm$group=="T1D"], mm$SIMALR[mm$group=="HC"])
c2 <- wilcox.test(mm$SIMALR[mm$group=="T1D"], mm$SIMALR[mm$group=="Pre"])
c3 <- wilcox.test(mm$SIMALR[mm$group=="HC"],  mm$SIMALR[mm$group=="Pre"])
cat(sprintf("\nCell-level T1D vs HC:  p=%.4g\n", c1$p.value))
cat(sprintf("Cell-level T1D vs Pre: p=%.4g\n", c2$p.value))
cat(sprintf("Cell-level HC  vs Pre: p=%.4g\n", c3$p.value))
