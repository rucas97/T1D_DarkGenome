# Parse MixMHC2pred output, filter strong binders, cross-reference SIMALR
import os, csv
os.chdir("D:/T1D_DarkGenome")

INPUT = "results/tables/MixMHC2pred_full.txt"
with open(INPUT) as f:
    lines = f.readlines()
hdr_idx = next(i for i, ln in enumerate(lines)
               if not ln.startswith("#") and "Peptide" in ln)
header = lines[hdr_idx].rstrip("\n").split("\t")
rows = []
for ln in lines[hdr_idx+1:]:
    parts = ln.rstrip("\n").split("\t")
    if len(parts) == len(header):
        rows.append(dict(zip(header, parts)))
print(f"Parsed {len(rows):,} peptide rows")
rank_cols = [c for c in header if c.startswith("%Rank_") and c != "%Rank_best"]

strong = [r for r in rows if float(r["%Rank_best"]) < 2]
good   = [r for r in rows if float(r["%Rank_best"]) < 5]
print(f"Strong (<2): {len(strong):,}  Good (<5): {len(good):,}")

# SIMALR cross-reference
simalr_peps = set()
with open("results/tables/micropeptide_candidates.tsv") as f:
    for row in csv.DictReader(f, delimiter="\t"):
        if row.get("gene") == "LINC02528":
            pep = row.get("peptide", "")
            if len(pep) >= 15:
                for i in range(len(pep) - 14):
                    simalr_peps.add(pep[i:i+15])
print(f"SIMALR 15-mers: {len(simalr_peps)}")

simalr_strong = [r for r in strong if r["Peptide"] in simalr_peps]
simalr_good   = [r for r in good   if r["Peptide"] in simalr_peps]
print(f"SIMALR strong binders: {len(simalr_strong)}")
print(f"SIMALR good binders: {len(simalr_good)}")

keys = ["Peptide","BestAllele","%Rank_best","Core_best"] + rank_cols
if simalr_good:
    with open("results/tables/MixMHC2pred_SIMALR_binders.tsv","w",newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys, delimiter="\t", extrasaction="ignore")
        w.writeheader()
        for r in sorted(simalr_good, key=lambda x: float(x["%Rank_best"])):
            w.writerow(r)
    print("Saved SIMALR binders TSV")
