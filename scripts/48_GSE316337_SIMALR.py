import gzip, re, csv
from collections import defaultdict

PBMC = "data/raw/T1D_PBMC"

titles, diseases = [], []
with gzip.open(f"{PBMC}/GSE316337_series_matrix.txt.gz","rt") as f:
    for line in f:
        if line.startswith("!Sample_title"):
            titles = re.findall(r'"([^"]*)"', line)
        elif line.startswith("!Sample_characteristics_ch1") and "disease state" in line:
            diseases = re.findall(r'"([^"]*)"', line)
        if titles and diseases: break

prefix_to_group = {}
for t, d in zip(titles, diseases):
    m = re.search(r's+ample_(\d+)', t, re.IGNORECASE)
    if m:
        num = m.group(1)
        grp = "T1D" if "T1D" in d else ("HC" if "HC" in d else "?")
        prefix_to_group[num] = grp

print(f"Mapped {len(prefix_to_group)} samples")

cell_prefix = {}
bc_order = []
with gzip.open(f"{PBMC}/GSE316337_GSE316337_barcodes.tsv.gz","rt") as f:
    for line in f:
        bc = line.strip()
        if not bc: continue
        bc_order.append(bc)
        m = re.match(r'^(\d+)_', bc)
        if m: cell_prefix[bc] = m.group(1)

print(f"{len(cell_prefix)} cells with prefix")

simalr_cells = []
with open(f"{PBMC}/GSE316337_LINC02528_counts.tsv") as f:
    for line in f:
        parts = line.strip().split()
        if len(parts) != 2: continue
        col_idx = int(parts[0]) - 1
        val = float(parts[1])
        if 0 <= col_idx < len(bc_order):
            bc = bc_order[col_idx]
            sample_num = cell_prefix.get(bc, "?")
            grp = prefix_to_group.get(sample_num, "?")
            simalr_cells.append((bc, sample_num, grp, val))

print(f"SIMALR+ cells: {len(simalr_cells)}")

total_per_prefix = defaultdict(int)
for bc, prefix in cell_prefix.items(): total_per_prefix[prefix] += 1
simalr_per_prefix = defaultdict(int)
for bc, pref, grp, val in simalr_cells: simalr_per_prefix[pref] += 1

group_total = defaultdict(int); group_simalr = defaultdict(int)
for prefix, n in total_per_prefix.items():
    grp = prefix_to_group.get(prefix, "?")
    group_total[grp] += n
    group_simalr[grp] += simalr_per_prefix.get(prefix, 0)

print(f"\n{'Group':8s} {'Total':>12s} {'SIMALR+':>10s} {'Pct':>8s}")
for grp in ["T1D","HC","?"]:
    if grp in group_total:
        tot = group_total[grp]; sim = group_simalr[grp]
        pct = sim/tot*100 if tot else 0
        print(f"{grp:8s} {tot:>12d} {sim:>10d} {pct:>7.3f}%")

rows = []
for prefix in sorted(total_per_prefix, key=lambda x: int(x) if x.isdigit() else 9999):
    tot = total_per_prefix[prefix]
    sim = simalr_per_prefix.get(prefix, 0)
    grp = prefix_to_group.get(prefix, "?")
    pct = sim/tot*100 if tot else 0
    rows.append((prefix, grp, tot, sim, pct))

with open("results/tables/GSE316337_SIMALR_by_sample.tsv","w",newline="") as f:
    w = csv.writer(f, delimiter="\t")
    w.writerow(["sample_prefix","group","total_cells","simalr_pos_cells","pct_detected"])
    w.writerows(rows)
