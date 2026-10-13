# Spatial phyloP profile across SIMALR locus
setwd("D:/T1D_DarkGenome")
suppressPackageStartupMessages({library(httr2); library(data.table); library(ggplot2)})
simalr <- list(start=137943079, end=137957657)
url <- paste0("https://api.genome.ucsc.edu/getData/track?genome=hg38;track=phyloP100way;chrom=chr6;start=",
              simalr$start-2000, ";end=", simalr$end+2000)
resp <- request(url) |> req_perform() |> resp_body_json()
df <- data.table(pos=sapply(resp$phyloP100way, function(x) x$start),
                 value=sapply(resp$phyloP100way, function(x) x$value))
df[, region := "flank"]
df[pos >= simalr$start & pos <= simalr$end, region := "gene_body"]
df[pos > simalr$end & pos <= simalr$end+2000, region := "promoter"]
print(df[, .(n=.N, mean=round(mean(value),3), p90=round(quantile(value,0.9),2),
             max=round(max(value),2), frac_gt1=round(mean(value>1)*100,1)), by=region])
min_pos <- min(df$pos); max_pos <- max(df$pos)
df[, window := cut(pos, breaks=seq(min_pos, max_pos, by=500), labels=FALSE, include.lowest=TRUE)]
win_df <- df[, .(pos=mean(pos), mean=mean(value), p90=quantile(value,0.9), max=max(value)),
             by=window][order(pos)]
print(head(win_df[order(-p90), .(pos, mean=round(mean,3), p90=round(p90,2), max=round(max,2))], 10))
fwrite(win_df, "results/tables/SIMALR_phyloP_windows.csv", sep=",")
