# Build small gene index from GTF for fast offline queries
setwd("D:/T1D_DarkGenome")
suppressPackageStartupMessages(library(data.table))

cat("Loading GENCODE GTF...\n")
gtf <- fread("data/reference/gencode.v46.annotation.gtf",
             sep="\t", header=FALSE, skip=5,
             col.names=c("chr","source","feature","start","end",
                         "score","strand","frame","attributes"),
             data.table=TRUE, showProgress=FALSE)

genes <- gtf[feature == "gene"]
cat("Gene rows:", nrow(genes), "\n")

parse_attr <- function(x, key) {
  m <- regmatches(x, regexpr(paste0(key, ' "[^"]+"'), x))
  if (length(m)==0) return(NA_character_)
  sub(paste0(key, ' "([^"]+)"'), "\\1", m)
}
genes[, gene_id_v := sapply(attributes, parse_attr, key="gene_id")]
genes[, gene_name := sapply(attributes, parse_attr, key="gene_name")]
genes[, gene_type := sapply(attributes, parse_attr, key="gene_type")]
genes[, Ensembl   := sub("\\..*$", "", gene_id_v)]

gene_index <- genes[, .(Ensembl, chr, start, end, strand, gene_name, gene_type)]
cat("Total genes:", nrow(gene_index), "\n")
cat("Protein-coding:", sum(gene_index$gene_type=="protein_coding"), "\n")
cat("lncRNA:", sum(gene_index$gene_type=="lncRNA"), "\n")

dir.create("data/reference", showWarnings=FALSE, recursive=TRUE)
fwrite(gene_index, "data/reference/gene_index.tsv", sep="\t")
cat("Saved gene_index.tsv —",
    round(file.info("data/reference/gene_index.tsv")$size/1e6, 1), "MB\n")
