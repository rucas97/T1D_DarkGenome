# ============================================================
# 19_hla_prediction.py  (v2 — stdlib only, no external deps)
# Predict HLA class II binding via IEDB NextGen API
# ============================================================

import os
import sys
import time
import json
import urllib.request
import urllib.error
import csv
from pathlib import Path

os.chdir("D:/T1D_DarkGenome")

IEDB_API = "https://api-nextgen-tools.iedb.org/api/v1/pipeline"
RESULTS_API = "https://api-nextgen-tools.iedb.org/api/v1/results"

t1d_alleles = [
    "HLA-DRB1*03:01",
    "HLA-DRB1*04:01",
    "HLA-DQA1*05:01/DQB1*02:01",
    "HLA-DQA1*03:01/DQB1*03:02",
]

# --- Load peptides ---
with open("results/tables/hla2_15mers.txt") as f:
    peptides = [line.strip() for line in f if line.strip() and 12 <= len(line.strip()) <= 20]

print(f"Loaded {len(peptides):,} 15-mer peptides", flush=True)

# --- HTTP helpers using stdlib only ---
def http_post(url, data, timeout=180):
    body = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8") if e.fp else str(e)
    except Exception as e:
        return None, str(e)

def http_get(url, timeout=120):
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8") if e.fp else str(e)
    except Exception as e:
        return None, str(e)

def submit_job(peptides_batch, allele, method="netmhciipan_el"):
    sequence_text = "\n".join(peptides_batch)
    payload = {
        "pipeline_id": "",
        "run_stage_range": [1, 1],
        "stages": [{
            "stage_number": 1,
            "tool_group": "mhcii",
            "input_sequence_text": sequence_text,
            "input_parameters": {
                "alleles": allele,
                "peptide_length_range": None,
                "predictors": [{
                    "type": "binding",
                    "method": method
                }]
            }
        }]
    }
    status, body = http_post(IEDB_API, payload)
    print(f"    submit status: {status}", flush=True)
    if status != 200:
        print(f"    body: {body[:300]}", flush=True)
        return None
    try:
        return json.loads(body).get("result_id")
    except Exception as e:
        print(f"    JSON parse error: {e}", flush=True)
        print(f"    body: {body[:300]}", flush=True)
        return None

def poll_result(result_id, max_wait=1800):
    url = f"{RESULTS_API}/{result_id}"
    start = time.time()
    while time.time() - start < max_wait:
        status, body = http_get(url)
        if status == 200:
            try:
                j = json.loads(body)
                data = j.get("data", {})
                results = data.get("results", [])
                for res in results:
                    if res.get("table_data"):
                        return j
            except Exception:
                pass
        elapsed = int(time.time() - start)
        print(f"    polling... {elapsed}s", flush=True)
        time.sleep(15)
    return None

# ============================================================
# SMOKE TEST
# ============================================================
print("\n=== SMOKE TEST: 10 peptides, DRB1*04:01 ===", flush=True)
test_peps = peptides[:10]
rid = submit_job(test_peps, "HLA-DRB1*04:01")
if rid is None:
    print("SMOKE TEST FAILED — IEDB API not responding", flush=True)
    sys.exit(1)
print(f"  Result ID: {rid}", flush=True)
print("  Polling for results...", flush=True)

result = poll_result(rid, max_wait=900)
if result is None:
    print("SMOKE TEST TIMED OUT", flush=True)
    sys.exit(1)

print("  SMOKE TEST PASSED\n", flush=True)
sample = result.get("data", {}).get("results", [{}])[0]
print("  Sample response keys:", list(sample.keys()), flush=True)
if sample.get("table_columns"):
    print("  Columns:", [c.get("name") for c in sample["table_columns"]], flush=True)
if sample.get("table_data"):
    print(f"  Got {len(sample['table_data'])} rows", flush=True)
    print("  First row:", sample["table_data"][0], flush=True)

# ============================================================
# FULL RUN
# ============================================================
print("\n" + "="*60, flush=True)
print("FULL RUN", flush=True)
print("="*60, flush=True)

BATCH_SIZE = 5000
all_rows = []
col_names = None

for allele in t1d_alleles:
    print(f"\n=== {allele} ===", flush=True)
    n_batches = (len(peptides) + BATCH_SIZE - 1) // BATCH_SIZE
    print(f"  {n_batches} batches of {BATCH_SIZE}", flush=True)

    for bi in range(n_batches):
        batch = peptides[bi*BATCH_SIZE : (bi+1)*BATCH_SIZE]
        print(f"  Batch {bi+1}/{n_batches} ({len(batch)} peptides)...", flush=True)

        rid = submit_job(batch, allele)
        if rid is None:
            print("    Submit failed, skipping batch", flush=True)
            continue
        print(f"    Result ID: {rid}", flush=True)

        result = poll_result(rid, max_wait=1800)
        if result is None:
            print("    Poll timed out", flush=True)
            continue

        data = result.get("data", {})
        for res in data.get("results", []):
            cols = res.get("table_columns", [])
            rows = res.get("table_data", [])
            if not rows:
                continue
            if col_names is None:
                col_names = [c["name"] for c in cols] + ["allele"]
            for row in rows:
                all_rows.append(list(row) + [allele])
            print(f"    Got {len(rows)} predictions", flush=True)
            break

        time.sleep(5)

# ============================================================
# Save combined results
# ============================================================
if all_rows and col_names:
    out_path = "results/tables/HLA_II_predictions_raw.tsv"
    with open(out_path, "w", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(col_names)
        w.writerows(all_rows)
    print(f"\n=== DONE ===", flush=True)
    print(f"Total predictions: {len(all_rows):,}", flush=True)
    print(f"Saved to {out_path}", flush=True)
else:
    print("\nNo results collected", flush=True)