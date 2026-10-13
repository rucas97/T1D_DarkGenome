# ============================================================
# 21_refetch_results.py
# Re-fetch IEDB results using saved result IDs
# Fetches raw JSON, saves as one row per peptide prediction
# ============================================================

import os, json, time, csv, urllib.request, urllib.error

os.chdir("D:/T1D_DarkGenome")

RESULTS_API = "https://api-nextgen-tools.iedb.org/api/v1/results"

KNOWN_IDS = {
    "HLA-DRB1*03:01": [
        "262e02d9-b0f9-4844-9401-b02092580b0e",
        "2ab6673a-47d1-47b4-9896-85586ccc5a69",
        "439192cd-f3b7-4bd2-9775-c816a90c52c3",
        "fe237938-45c5-4a34-b5ce-738b7c919e52",
        "65420dca-dffa-43e1-9e77-1a8c0a5089f4",
        "52d112cb-258b-41f7-85d8-78cde6466d08",
        "fb58a718-0414-4aac-96b5-3e58a129e16e",
        "52adbfef-66f8-47ea-9375-bf60aa2ef929",
        "a527e8ce-27ea-4025-b74e-a9d31bf6b161",
    ],
    "HLA-DRB1*04:01": [
        "76e82a78-8532-460f-bcda-c24d5708d284",
        "c6999f07-532a-4749-a07e-e430b74d9e72",
        "6f8b7235-7096-435e-9529-efec8727c8c3",
        "4a90c4a9-3edc-41fb-978e-5524e4df66ee",
        "f50e94df-58b7-4755-aa50-b895d0815cfa",
        "0c433711-db19-4651-988e-abec699f0069",
        "6cd1dd22-fa27-46e8-bd68-58207729f9a7",
        "56f62fea-1a71-476d-9f09-6615750f7846",
        "055cc862-194b-47db-aa6f-9a3a5b68ac6c",
        "6e6fffae-46a3-40fa-bc4c-65462dae4bb2",
    ],
}

def fetch_result(rid, tries=5):
    url = f"{RESULTS_API}/{rid}"
    for i in range(tries):
        try:
            req = urllib.request.Request(url)
            req.add_header("Accept", "application/json")
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.loads(r.read().decode())
        except Exception as e:
            print(f"    retry {i+1}/{tries}: {e}", flush=True)
            time.sleep(5)
    return None

# ------------------------------------------------------------
# Get the FULL column list from the first successful result
# so we know exactly which indices correspond to what.
# ------------------------------------------------------------
print("Fetching first result to learn column layout...\n")
probe = fetch_result(KNOWN_IDS["HLA-DRB1*03:01"][0])
if probe is None:
    print("FATAL: cannot reach IEDB")
    raise SystemExit(1)

for res in probe["data"]["results"]:
    cols = res.get("table_columns", [])
    if cols:
        print("=== Column layout from probe ===")
        for i, c in enumerate(cols):
            print(f"  [{i}] {c['name']}")
        print()
        probe_col_names = [c["name"] for c in cols]
        break

# We want these specific columns
WANT = ["peptide", "allele", "netmhciipan_el_core",
        "netmhciipan_el_score", "netmhciipan_el_percentile",
        "median_percentile", "length", "start", "end"]
IDX = {name: probe_col_names.index(name)
       for name in WANT if name in probe_col_names}
print("Will extract columns:", list(IDX.keys()))
print()

# ------------------------------------------------------------
# Now fetch all results and extract the wanted columns
# ------------------------------------------------------------
header = ["allele"] + list(IDX.keys())
all_rows = []

for allele, ids in KNOWN_IDS.items():
    print(f"\n=== {allele} ===")
    for k, rid in enumerate(ids, 1):
        print(f"  [{k}/{len(ids)}] {rid[:8]}...", flush=True)
        j = fetch_result(rid)
        if j is None:
            print("    FAILED")
            continue

        for res in j["data"]["results"]:
            cols = res.get("table_columns", [])
            rows = res.get("table_data", [])
            if not rows:
                continue
            col_names = [c["name"] for c in cols]
            if "netmhciipan_el_percentile" not in col_names:
                print(f"    preview only ({len(rows)} rows, no scores)")
                continue

            # Use this result's column order (may differ from probe)
            idx_this = {name: col_names.index(name)
                        for name in IDX if name in col_names}
            n = 0
            for row in rows:
                extracted = [allele]
                for name in IDX.keys():
                    if name in idx_this:
                        extracted.append(row[idx_this[name]])
                    else:
                        extracted.append("")
                all_rows.append(extracted)
                n += 1
            print(f"    got {n} predictions")
            break

print(f"\n=== TOTAL COLLECTED: {len(all_rows):,} ===")

if all_rows:
    out_path = "results/tables/HLA_II_predictions_v2.tsv"
    with open(out_path, "w", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(header)
        w.writerows(all_rows)
    print(f"Saved {len(all_rows):,} rows to {out_path}")
else:
    print("No results collected. All jobs may have expired.")