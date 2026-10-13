# Parse IEDB NetMHCIIpan predictions (from HLA_II_predictions_raw.tsv if available)
import os, csv
os.chdir("D:/T1D_DarkGenome")
path = "results/tables/HLA_II_predictions_raw.tsv"
if not os.path.exists(path):
    print("No IEDB predictions file. Use MixMHC2pred pipeline (scripts/23).")
    raise SystemExit
with open(path) as f:
    rows = list(csv.DictReader(f, delimiter="\t"))
print(f"Total predictions: {len(rows):,}")
strong = [r for r in rows if r.get("netmhciipan_el_percentile") and
          float(r["netmhciipan_el_percentile"]) < 2]
print(f"Strong binders (<2 percentile): {len(strong):,}")
