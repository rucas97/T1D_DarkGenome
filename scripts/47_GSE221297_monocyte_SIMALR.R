suppressPackageStartupMessages({
  library(Seurat); library(Matrix); library(ggplot2)
  library(dplyr); library(patchwork)
})

data_dir <- "/content/gse221297"
out_dir  <- "/content/drive/MyDrive/T1D_DarkGenome"
dir.create(out_dir, showWarnings=FALSE, recursive=TRUE)

samples <- list(
  c("GSM6857960_P2_CYH","T1D"), c("GSM6857961_P1_LSJ","T1D"),
  c("GSM6857962_P3_WZN","T1D"), c("GSM6857963_P4_JRT","T1D"),
  c("GSM6857964_P5_YSQ","T1D"), c("GSM6857965_P6_YSQ","T1D"),
  c("GSM6857966_NC_LZY","HC"),  c("GSM6857967_NC_QZ","HC"),
  c("GSM6857968_NC_FZH","HC"),
  c("GSM6857969_PR_WYF","Pre"), c("GSM6857970_PR_ZJL","Pre"),
  c("GSM6857971_PR_ZRY","Pre")
)

sl <- list()
for (s in samples) {
  sid <- s[1]; grp <- s[2]
  bcf <- file.path(data_dir, paste0(sid,"_barcodes.tsv.gz"))
  ftf <- file.path(data_dir, paste0(sid,"_features.tsv.gz"))
  mtf <- file.path(data_dir, paste0(sid,"_matrix.mtx.gz"))
  if (!file.exists(mtf)) { cat("SKIP:",sid,"\n"); next }
  cat("Loading:",sid,"(",grp,")\n")
  counts <- ReadMtx(mtx=mtf, cells=bcf, features=ftf, feature.column=2)
  obj <- CreateSeuratObject(counts=counts, project=sid, min.cells=3, min.features=200)
  obj$sample <- sid; obj$group <- grp
  sl[[sid]] <- obj; rm(counts); gc(verbose=FALSE)
}

merged <- merge(sl[[1]], sl[-1], add.cell.ids=names(sl), project="GSE221297")
rm(sl); gc(verbose=FALSE)
cat("Merged:", ncol(merged), "cells\n")

merged[["percent.mt"]] <- PercentageFeatureSet(merged, pattern="^MT-")
merged <- subset(merged, subset=nFeature_RNA>200 & nFeature_RNA<5000 & percent.mt<10)
cat("After QC:", ncol(merged), "cells\n")

merged <- NormalizeData(merged, verbose=FALSE)
merged <- FindVariableFeatures(merged, nfeatures=2000, verbose=FALSE)
merged <- ScaleData(merged, verbose=FALSE)
merged <- RunPCA(merged, npcs=30, verbose=FALSE)
merged <- FindNeighbors(merged, dims=1:20, verbose=FALSE)
merged <- FindClusters(merged, resolution=0.5, verbose=FALSE)
merged <- RunUMAP(merged, dims=1:20, verbose=FALSE)

saveRDS(merged, file.path(out_dir, "GSE221297_merged.rds"))
cat("RDS saved\n")

mono_markers <- c("CD14","FCGR3A","FCN1","S100A8","S100A9","LYZ","VCAN","MS4A7","CD68","CD163")
mono_markers <- mono_markers[mono_markers %in% rownames(merged)]
merged <- AddModuleScore(merged, features=list(mono_markers), name="mono_score")
cs <- merged@meta.data %>% group_by(seurat_clusters) %>%
  summarise(mean_mono=mean(mono_score1,na.rm=TRUE), n=n()) %>% arrange(desc(mean_mono))
print(cs)
mc <- as.character(cs$seurat_clusters[cs$mean_mono > 0.5])
mono <- subset(merged, subset=seurat_clusters %in% mc)
mono <- JoinLayers(mono)
cat("Monocyte cells:", ncol(mono), "\n")

mm <- mono@meta.data
mm$SIMALR <- FetchData(mono, vars="LINC02528")[,1]
gs <- mm %>% group_by(group) %>%
  summarise(n_cells=n(), pct_detected=mean(SIMALR>0)*100,
            mean_expr=mean(SIMALR), median_expr=median(SIMALR))
cat("\n=== SIMALR by group ===\n"); print(gs)
write.table(gs, file.path(out_dir,"GSE221297_SIMALR_summary.tsv"),
            sep="\t", quote=FALSE, row.names=FALSE)

for (pair in list(c("T1D","HC"), c("T1D","Pre"), c("HC","Pre"))) {
  g1<-pair[1]; g2<-pair[2]
  t <- matrix(c(
    sum(mm$SIMALR[mm$group==g1]>0), sum(mm$SIMALR[mm$group==g1]==0),
    sum(mm$SIMALR[mm$group==g2]>0), sum(mm$SIMALR[mm$group==g2]==0)
  ), nrow=2, byrow=TRUE)
  ft <- fisher.test(t)
  cat(sprintf("%s vs %s: OR=%.3f p=%.4g\n", g1, g2, ft$estimate, ft$p.value))
}
cat("\n=== DONE ===\n")
