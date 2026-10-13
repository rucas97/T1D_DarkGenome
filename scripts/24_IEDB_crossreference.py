# ============================================================
# 24_IEDB_crossreference.py
# Cross-reference SIMALR binding cores against known T1D
# autoantigens and IEDB epitopes
# ============================================================

import os, csv, urllib.request, urllib.parse, json, time

os.chdir("D:/T1D_DarkGenome")

# --- Load SIMALR strong binders ---
simalr_cores = set()
with open("results/tables/MixMHC2pred_SIMALR_binders.tsv") as f:
    rd = csv.DictReader(f, delimiter="\t")
    for r in rd:
        if float(r["%Rank_best"]) < 2:
            simalr_cores.add(r["Core_best"])

print(f"SIMALR unique strong-binding cores: {len(simalr_cores)}")
for c in sorted(simalr_cores):
    print(f"  {c}")

# --- Known T1D autoantigen peptides (curated from literature) ---
KNOWN_T1D = {
    "Insulin B:9-23": "SHLVEALYLVCGERG",
    "Insulin B:11-27": "LVEALYLVCGERGFFY",
    "GAD65 555-567": "NFFRMVISNPAAT",
    "GAD65 115-127": "DVMNILLQYVVKSF",
    "IA-2 805-820": "KSLFNVSSHEDIRDE",
    "IA-2 709-724": "FVNILALVLLKHLVK",
    "ZnT8 154-169": "VFAVCLLWAVPERHG",
    "ZnT8 115-130": "QLSPQILVLTGVSTS",
    "IGRP 206-214": "HLHLLQPSL",
    "Chromogranin A": "WARQAPPAYRPQAP",
}

print(f"\n=== Known T1D autoantigen peptides ===")
for name, seq in KNOWN_T1D.items():
    print(f"  {name:25s}  {seq}")

# --- Simple overlap: any 7-mer shared? ---
def kmer_set(seq, k=7):
    return {seq[i:i+k] for i in range(len(seq) - k + 1)}

print(f"\n=== Cross-reference (7-mer overlap) ===")
for name, seq in KNOWN_T1D.items():
    kset = kmer_set(seq, 7)
    for core in simalr_cores:
        if len(core) < 7: continue
        cset = kmer_set(core, 7)
        shared = kset & cset
        if shared:
            print(f"  MATCH: {name} vs {core} → shared 7-mers: {shared}")

# --- IEDB query for T1D epitopes ---
print(f"\n=== IEDB search for T1D epitopes ===")
iedb_base = "https://query-api.iedb.org/epitope_search"
# T1D-related EFO
for query in ["type 1 diabetes", "insulin", "GAD65"]:
    params = {"search_text": query, "limit": 5}
    url = f"{iedb_base}?{urllib.parse.urlencode(params)}"
    try:
        req = urllib.request.Request(url)
        req.add_header("Accept", "application/json")
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read().decode())
            print(f"  {query}: {len(data)} epitopes")
    except Exception as e:
        print(f"  {query}: ERROR {e}")
    time.sleep(1)

print("\n=== DONE ===")