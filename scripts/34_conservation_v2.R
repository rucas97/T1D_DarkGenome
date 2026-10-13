# UCSC phyloP 100-way for SIMALR locus
setwd("D:/T1D_DarkGenome")
suppressPackageStartupMessages({library(httr2); library(data.table)})
gi <- fread("data/reference/gene_index.tsv", sep="\t")
simalr <- gi[gi$Ensembl == "ENSG00000226004"]
chr <- sub("^chr","",simalr$chr); start <- simalr$start - 2000; end <- simalr$end + 2000
url <- paste0("https://api.genome.ucsc.edu/getData/track?genome=hg38;track=phyloP100way;chrom=chr",
              chr, ";start=", start, ";end=", end)
resp <- request(url) |> req_perform() |> resp_body_json()
df <- data.frame(pos=sapply(resp$phyloP100way, function(x) x$start),
                 value=sapply(resp$phyloP100way, function(x) x$value))
df$region <- "flank"
df$region[df$pos >= simalr$start & df$pos <= simalr$end] <- "gene_body"
df$region[df$pos > simalr$end & df$pos <= simalr$end+2000] <- "promoter"
print(tapply(df$value, df$region, function(x)
  c(mean=round(mean(x),3), p90=round(quantile(x,0.9),2),
    max=round(max(x),2), frac_gt1=round(mean(x>1)*100,1))))
fwrite(df, "results/tables/SIMALR_phyloP_scores.tsv", sep="\t")
