import csv

fn = "data/raw/GSE212381/GSE212381_ctrl_ASO_8h_gene_exp.diff"

rows = {}
with open(fn) as f:
    r = csv.DictReader(f, delimiter="\t")
    for row in r:
        try:
            row["log2fc"]   = float(row["log2(fold_change)"])
            row["qval"]     = float(row["q_value"])
            row["pval"]     = float(row["p_value"])
            rows[row["gene_id"]] = row
        except: pass

print(f"Genes parsed: {len(rows)}")

print("\n--- Sanity check: SIMALR (LINC02528) ---")
for g in ["SIMALR","LINC02528","ENSG00000226004"]:
    if g in rows:
        r = rows[g]
        print(f"  {g}: log2FC={r['log2fc']:.3f} q={r['qval']:.3g} status={r['status']}")

print("\n--- NF-kB axis genes ---")
nfkb = ["TNFAIP3","NFKBIA","NFKB1","NFKB2","RELA","RELB","CD40","TNF","IL6",
        "IL1B","CXCL10","CXCL1","CCL2","NFKBIZ","TNIP1","TNIP2","TNIP3"]
for g in nfkb:
    if g in rows:
        r = rows[g]
        sig = "*" if r["qval"] < 0.05 else " "
        print(f"  {sig} {g:10s} log2FC={r['log2fc']:+.3f}  q={r['qval']:.3g}")

print("\n--- Interferon / LPS response genes ---")
isg = ["ISG15","STAT1","IRF1","GBP1","GBP2","MX1","MX2","OAS1","IFIT1","IFIT3"]
for g in isg:
    if g in rows:
        r = rows[g]
        sig = "*" if r["qval"] < 0.05 else " "
        print(f"  {sig} {g:8s} log2FC={r['log2fc']:+.3f}  q={r['qval']:.3g}")

print("\n--- Top 20 up after KD ---")
ok = [r for r in rows.values() if r["status"]=="OK" and r["qval"]<0.05]
for r in sorted(ok, key=lambda x:-x["log2fc"])[:20]:
    print(f"  {r['gene_id']:12s} log2FC={r['log2fc']:+.3f} q={r['qval']:.3g}")

print("\n--- Top 20 down after KD ---")
for r in sorted(ok, key=lambda x:x["log2fc"])[:20]:
    print(f"  {r['gene_id']:12s} log2FC={r['log2fc']:+.3f} q={r['qval']:.3g}")
