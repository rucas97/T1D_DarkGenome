# ============================================================
# 52_generate_all_figures.R
# Generates Figures 1, 2, 4, 5, 6 as PDF + PNG
# (Figure 3 reuses existing SIMALR_per_donor_corrected.png)
# Run from project root: Rscript scripts/52_generate_all_figures.R
# ============================================================

# ---- packages ----
pkgs <- c("ggplot2","dplyr","tidyr","patchwork","scales","gridExtra")
for (p in pkgs) if (!requireNamespace(p, quietly=TRUE))
  install.packages(p, repos="https://cloud.r-project.org")
suppressPackageStartupMessages({
  library(ggplot2); library(dplyr); library(tidyr)
  library(patchwork); library(scales); library(gridExtra)
})

# Auto-detect project root: walk up from script location or fall back
if (interactive() && requireNamespace("rstudioapi", quietly=TRUE) &&
    rstudioapi::isAvailable()) {
  setwd(dirname(dirname(rstudioapi::getActiveDocumentContext()$path)))
} else if (Sys.getenv("RSCRIPT_DIR") != "") {
  setwd(Sys.getenv("RSCRIPT_DIR"))
}
if (!dir.exists("results/tables")) {
  # Hard fallback — edit this to your actual path
  setwd("D:/T1D_DarkGenome")
}
cat("Working directory:", getwd(), "\n")

tab_dir <- "results/tables"
fig_dir <- "results/figures"
dir.create(fig_dir, showWarnings=FALSE, recursive=TRUE)

theme_pub <- theme_bw(base_size=10) +
  theme(
    panel.grid.minor = element_blank(),
    plot.title = element_text(face="bold", size=11),
    strip.background = element_rect(fill="grey92", color=NA),
    legend.key.size = unit(0.4, "cm"),
    axis.title = element_text(size=10)
  )
theme_set(theme_pub)

save_fig <- function(p, name, w=8, h=6) {
  tryCatch({
    ggsave(file.path(fig_dir, paste0(name, ".pdf")), p, width=w, height=h, device=cairo_pdf)
    ggsave(file.path(fig_dir, paste0(name, ".png")), p, width=w, height=h, dpi=300)
    cat(sprintf("  saved %s (%.1f x %.1f in)\n", name, w, h))
  }, error=function(e) cat(sprintf("  FAILED %s: %s\n", name, e$message)))
}

read_tsv_safe <- function(path, ...) {
  if (!file.exists(path)) { cat("  missing:", path, "\n"); return(NULL) }
  tryCatch(read.delim(path, check.names=FALSE, ...),
           error=function(e){cat("  read error:", path, "-", e$message,"\n"); NULL})
}

# ============================================================
# FIGURE 1 — Dark genome landscape / SIMALR in cytokine islets
# ============================================================
cat("\n=== Figure 1: Dark genome landscape ===\n")

deseq <- read_tsv_safe(file.path(tab_dir, "DESeq2_CYT_cytokines_vs_untreated.tsv"))
if (!is.null(deseq)) {
  # Detect gene-id column
  gcol <- intersect(c("gene_id","gene","X","...1"), colnames(deseq))[1]
  if (is.na(gcol)) gcol <- colnames(deseq)[1]
  fc_col <- intersect(c("log2FoldChange","log2FC","log2_fold_change"), colnames(deseq))[1]
  p_col  <- intersect(c("padj","padj_adj","q_value","qvalue"), colnames(deseq))[1]

  if (!is.na(fc_col) && !is.na(p_col)) {
    dd <- deseq %>%
      mutate(gene_id = .data[[gcol]],
             lfc = as.numeric(.data[[fc_col]]),
             padj = as.numeric(.data[[p_col]])) %>%
      filter(!is.na(lfc), !is.na(padj), padj > 0) %>%
      mutate(neglog10p = -log10(padj),
             sig = case_when(padj < 0.05 & abs(lfc) > 1 ~ "sig",
                             padj < 0.05 ~ "padj<0.05",
                             TRUE ~ "ns"))

    # Mark SIMALR and top dark genome targets
    dg <- read_tsv_safe(file.path(tab_dir, "dark_genome_target_list.tsv"))
    dg_ids <- if (!is.null(dg)) {
      dg_gcol <- intersect(c("gene_id","gene","name","id"), colnames(dg))[1]
      if (!is.na(dg_gcol)) as.character(dg[[dg_gcol]]) else character(0)
    } else character(0)

    dd <- dd %>%
      mutate(class = ifelse(grepl("SIMALR|LINC02528|ENSG00000226004", gene_id), "SIMALR",
                    ifelse(gene_id %in% dg_ids, "dark genome target", "other")))

    # Volcano
    p1a <- ggplot(dd, aes(lfc, neglog10p, color=class, size=class, alpha=class)) +
      geom_point() +
      scale_color_manual(values=c("other"="grey70",
                                   "dark genome target"="#E69F00",
                                   "SIMALR"="#D7191C")) +
      scale_size_manual(values=c("other"=0.5,"dark genome target"=1.2,"SIMALR"=3)) +
      scale_alpha_manual(values=c("other"=0.4,"dark genome target"=0.8,"SIMALR"=1)) +
      labs(x="log2 fold change (cytokine vs untreated)",
           y="-log10(padj)",
           title="A. Cytokine-stimulated human islets (GSE251911)",
           color="", size="", alpha="") +
      geom_hline(yintercept=-log10(0.05), linetype="dashed", color="grey50") +
      geom_vline(xintercept=c(-1,1), linetype="dashed", color="grey50") +
      theme(legend.position="top")

    # Top dark genome targets
    if (!is.null(dg) && length(dg_ids)>0) {
      top_dg <- dd %>% filter(gene_id %in% dg_ids) %>%
        arrange(desc(lfc)) %>% head(15) %>%
        mutate(gene_id = factor(gene_id, levels=rev(gene_id)))
      p1b <- ggplot(top_dg, aes(lfc, gene_id)) +
        geom_col(fill="#E69F00") +
        labs(x="log2FC", y="", title="B. Top dark genome targets") +
        theme(axis.text.y = element_text(size=7))
    } else {
      p1b <- ggplot() + theme_void() +
        annotate("text", x=0, y=0, label="dark_genome_target_list.tsv not found")
    }

    # Key pathway markers
    pathway_genes <- c("CGAS","STING1","TBK1","IRF3","DDX58","IFIH1",
                        "BBC3","CDKN1A","IL6","CXCL1","MMP3","TNFAIP3","NFKBIA")
    pd <- dd %>% filter(gene_id %in% pathway_genes) %>%
      mutate(gene_id = factor(gene_id, levels=pathway_genes[pathway_genes %in% gene_id]))
    if (nrow(pd) > 0) {
      p1c <- ggplot(pd, aes(lfc, gene_id, fill=lfc)) +
        geom_col() +
        scale_fill_gradient2(low="#4575B4", mid="white", high="#D73027",
                              midpoint=0, name="log2FC") +
        labs(x="log2FC", y="", title="C. Key DDR / NF-kB / SASP markers")
    } else p1c <- ggplot() + theme_void()

    fig1 <- (p1a / (p1b | p1c)) + plot_layout(heights=c(2,1))
    save_fig(fig1, "Fig1_dark_genome_landscape", w=10, h=9)
  } else cat("  DESeq2 columns not recognized\n")
}

# ============================================================
# FIGURE 2 — SIMALR locus architecture
# ============================================================
cat("\n=== Figure 2: Locus architecture ===\n")

locus <- read_tsv_safe(file.path(tab_dir, "islet_pchic_locus_features.tsv"))
if (!is.null(locus)) {
  # Build genomic coordinate strip plot
  locus <- locus %>%
    mutate(label = gsub("_"," ", element),
           start_mb = start_hg19 / 1e6,
           end_mb   = end_hg19 / 1e6)

  # Color by category
  p2a <- ggplot(locus) +
    geom_rect(aes(xmin=start_mb, xmax=end_mb, ymin=0, ymax=1, fill=category),
              alpha=0.7) +
    geom_text(aes(x=(start_mb+end_mb)/2, y=0.5, label=element),
              size=2.3, angle=45, hjust=0.5) +
    scale_x_continuous(limits=c(137.9, 138.35), breaks=seq(137.9,138.3,0.05)) +
    labs(x="chr6 position (Mb, hg19)", y="", title="A. 6q23 locus features") +
    theme(axis.text.y=element_blank(), axis.ticks.y=element_blank(),
          panel.grid.major.y=element_blank(),
          legend.position="bottom") +
    guides(fill=guide_legend(nrow=2))

  # Gene model overlay — draw arrows for SIMALR, TNFAIP3, PERP, OLIG3
  genes_df <- data.frame(
    gene = c("SIMALR","TNFAIP3","PERP","OLIG3"),
    start_mb = c(137.943, 138.188, 138.150, 138.300),
    end_mb   = c(137.958, 138.210, 138.180, 138.350)
  )
  genes_df <- genes_df %>% filter(end_mb >= 137.9, start_mb <= 138.35)

  p2b <- ggplot(genes_df) +
    geom_segment(aes(x=start_mb, xend=end_mb, y=gene, yend=gene),
                 size=2, color="#333333", lineend="round") +
    geom_point(aes(x=start_mb, y=gene), size=2) +
    scale_x_continuous(limits=c(137.9, 138.35)) +
    labs(x="chr6 position (Mb, hg19)", y="") +
    theme(panel.grid.minor=element_blank())

  # PanKbase HuGE — hardcoded from published values
  huge_df <- data.frame(
    trait = c("T1D","T2D","RA","SLE","Monocyte count","Neutrophil count"),
    score = c(3.0, 1.0, 3.0, 3.0, 3.0, 3.0)
  ) %>% mutate(trait = factor(trait, levels=trait[order(score)]))

  p2c <- ggplot(huge_df, aes(score, trait, fill=score)) +
    geom_col() +
    scale_fill_gradient(low="grey80", high="#D7191C", guide="none") +
    scale_x_continuous(limits=c(0,3.3), breaks=0:3) +
    labs(x="PanKbase HuGE score", y="", title="B. Independent GWAS integration")

  fig2 <- (p2a / p2b / p2c) + plot_layout(heights=c(1.5, 0.7, 1.3))
  save_fig(fig2, "Fig2_locus_architecture", w=10, h=10)
}

# ============================================================
# FIGURE 4 — NF-kB / STAT3 mechanism
# ============================================================
cat("\n=== Figure 4: NF-kB/STAT3 mechanism ===\n")

motif <- read_tsv_safe(file.path(tab_dir, "SIMALR_region_motif_scan.csv"),
                        sep=",")
if (is.null(motif)) motif <- read_tsv_safe(file.path(tab_dir, "SIMALR_region_motif_scan.csv"))

if (!is.null(motif)) {
  cat("  motif columns:", paste(colnames(motif), collapse=", "), "\n")
  # Expect: region, tf (or transcription_factor), hits/score, region_size_kb
  # Build a summary bar chart; adapt to whatever is there
  tf_col  <- intersect(c("tf","transcription_factor","TF","factor"), colnames(motif))[1]
  reg_col <- intersect(c("region","Region","location","Region_name"), colnames(motif))[1]
  hit_col <- intersect(c("hits","count","n_hits"), colnames(motif))[1]
  density_col <- intersect(c("density","per_kb","density_per_kb"), colnames(motif))[1]

  if (!is.na(tf_col) && !is.na(reg_col) && (!is.na(hit_col) || !is.na(density_col))) {
    ycol <- if (!is.na(density_col)) density_col else hit_col
    p4a <- ggplot(motif, aes(x=.data[[tf_col]], y=.data[[ycol]],
                              fill=.data[[reg_col]])) +
      geom_col(position="dodge") +
      labs(x="Transcription factor", y="Motif density",
           title="A. PWM motif density across SIMALR regions") +
      theme(axis.text.x = element_text(angle=45, hjust=1))

    # Cynn 2023 chemokine changes (hardcoded from re-analysis)
    cynn <- data.frame(
      gene = c("CXCL1","CXCL3","IL12A","CCL1","IL36G",
               "TNFAIP3","NFKBIA","RELA","NFKB1","NFKB2"),
      log2FC = c(-1.10, -0.97, -1.51, -1.64, -1.08,
                  0.022, 0.032, 0.149, -0.005, -0.159),
      q = c(0.036, 0.036, 0.016, 0.016, 0.016,
            0.999, 0.999, 0.999, 0.999, 0.999)
    ) %>% mutate(
      sig = ifelse(q < 0.05, "*", ""),
      gene = factor(gene, levels=gene[order(log2FC)])
    )

    p4b <- ggplot(cynn, aes(log2FC, gene, fill=log2FC)) +
      geom_col() +
      geom_text(aes(label=sig), x=0, hjust=0.5, vjust=0.7, size=5) +
      scale_fill_gradient2(low="#4575B4", mid="white", high="#D73027",
                            midpoint=0, name="log2FC") +
      labs(x="log2FC (SIMALR ASO vs control)",
           y="", title="B. HMDM SIMALR knockdown (GSE212381)")

    fig4 <- p4a / p4b + plot_layout(heights=c(1,1))
    save_fig(fig4, "Fig4_NFkB_STAT3_mechanism", w=10, h=8)
  } else {
    cat("  motif columns not recognized; writing raw table\n")
    write.table(motif, file.path(fig_dir, "Fig4_motif_raw.tsv"),
                sep="\t", quote=FALSE, row.names=FALSE)
  }
}

# ============================================================
# FIGURE 5 — HLA-II binding
# ============================================================
cat("\n=== Figure 5: HLA-II binding ===\n")

mix <- read_tsv_safe(file.path(tab_dir, "MixMHC2pred_SIMALR_strong.tsv"))
net <- read_tsv_safe(file.path(tab_dir, "HLA_II_predictions_v2.tsv"))

if (!is.null(mix)) {
  cat("  mix columns:", paste(colnames(mix), collapse=", "), "\n")
  # Rank column detection
  rank_col <- intersect(c("rank","Rank","%Rank","rank_pct","best_rank"), colnames(mix))[1]
  pep_col  <- intersect(c("peptide","Peptide","pep"), colnames(mix))[1]
  al_col   <- intersect(c("allele","Allele","HLA","hla"), colnames(mix))[1]

  if (!is.na(rank_col) && !is.na(pep_col)) {
    mix$rank_num <- as.numeric(mix[[rank_col]])
    p5a <- ggplot(mix, aes(x=rank_num)) +
      geom_histogram(bins=30, fill="#D7191C", color="white") +
      scale_x_continuous(trans="log10") +
      labs(x="MixMHC2pred %Rank (log scale)",
           y="Count", title="A. Predicted strong binders (rank < 2)") +
      geom_vline(xintercept=c(0.5, 1, 2), linetype="dashed",
                  color=c("darkgreen","orange","red"))
  } else p5a <- ggplot() + theme_void()

  # Rank comparison: MixMHC2pred vs NetMHCIIpan
  # Hardcoded 4 DQ8 binders (validated by both methods)
  cmp <- data.frame(
    peptide = c("EHKDGQVQAKGERPG","CEHKDGQVQAKGERP",
                "HGSDFATKMSYENPA","LHGSDFATKMSYENP"),
    mix_rank = c(0.146, 0.205, 0.463, 0.608),
    net_rank = c(0.36, 0.48, 0.22, 0.31),
    core = c("DGQVQAKGE","DGQVQAKGE","DFATKMSYE","DFATKMSYE")
  )
  p5b <- ggplot(cmp, aes(mix_rank, net_rank, color=core)) +
    geom_point(size=4) +
    geom_text(aes(label=peptide), size=2.3, vjust=-1.2) +
    geom_abline(slope=1, intercept=0, linetype="dashed", color="grey50") +
    scale_x_log10() + scale_y_log10() +
    labs(x="MixMHC2pred %Rank", y="NetMHCIIpan %Rank",
         title="B. Two-algorithm agreement (DQ8 binders)", color="Core")

  # Non-mimicry (bar: 0 shared k-mers with 1,964 known T1D epitopes)
  mimic <- data.frame(
    k = c("7-mer","8-mer","9-mer","exact"),
    shared = c(0,0,0,0),
    total = c(1964,1964,1964,1964)
  )
  p5c <- ggplot(mimic, aes(k, shared)) +
    geom_col(fill="grey60") +
    geom_text(aes(label="0"), vjust=-0.4, size=4) +
    labs(x="", y="Shared sequences with known T1D epitopes",
         title="C. No mimicry of 1,964 known T1D autoantigen epitopes") +
    ylim(0,10)

  fig5 <- (p5a | p5b) / p5c + plot_layout(heights=c(1, 0.8))
  save_fig(fig5, "Fig5_HLA_II_binding", w=10, h=8)
}

# ============================================================
# FIGURE 6 — Blood expression
# ============================================================
cat("\n=== Figure 6: Blood expression ===\n")

gse316 <- read_tsv_safe(file.path(tab_dir, "GSE316337_SIMALR_by_sample.tsv"))
gse221 <- read_tsv_safe(file.path(tab_dir, "GSE221297_SIMALR_by_donor.tsv"))

if (!is.null(gse316)) {
  gse316$group <- factor(gse316$group, levels=c("HC","T1D"))
  p6a <- ggplot(gse316, aes(group, pct_detected, fill=group)) +
    geom_boxplot(outlier.shape=NA, alpha=0.6) +
    geom_jitter(width=0.15, size=1.5, alpha=0.7) +
    scale_fill_manual(values=c("HC"="#4575B4","T1D"="#D7191C")) +
    labs(x="", y="SIMALR+ cells (%)",
         title="A. PBMC scRNA-seq (GSE316337, n=27+27)") +
    theme(legend.position="none")
} else p6a <- ggplot() + theme_void()

if (!is.null(gse221)) {
  gse221$group <- factor(gse221$group, levels=c("HC","Pre","T1D"))
  p6b <- ggplot(gse221, aes(group, pct, fill=group)) +
    geom_boxplot(outlier.shape=NA, alpha=0.6) +
    geom_jitter(width=0.15, size=2.5, alpha=0.8) +
    scale_fill_manual(values=c("HC"="#4575B4","Pre"="#E69F00","T1D"="#D7191C")) +
    labs(x="", y="SIMALR+ monocytes (%)",
         title="B. Monocyte scRNA-seq (GSE221297, n=6+3+3)") +
    theme(legend.position="none") +
    annotate("text", x=3, y=max(gse221$pct)*1.1,
             label="T1D vs Pre: p=0.053", size=3, hjust=1)
} else p6b <- ggplot() + theme_void()

fig6 <- p6a | p6b
save_fig(fig6, "Fig6_blood_expression", w=10, h=5)

cat("\n=== ALL FIGURES DONE ===\n")
cat("Outputs in:", fig_dir, "\n")
