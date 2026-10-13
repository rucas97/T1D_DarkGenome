# ============================================================
# 22_rerun_small_batches.py
# Re-run HLA-II prediction with batches small enough to compute
# Fixed polling: waits for netmhciipan_el_percentile to appear
# Resumable: skips batches already in the output file
# ============================================================

import os, json, time, csv, urllib.request, urllib.error
from pathlib import Path

os.chdir("D:/T1D_DarkGenome")

API_SUBMIT = "https://api-nextgen-tools.iedb.org/api/v1/pipeline"
API_RESULT = "https://api-nextgen-tools.iedb.org/api/v1/results"

BATCH_SIZE = 1000
OUT_PATH = "results/tables/HLA_II_predictions_full.tsv"

t1d_alleles = [
    "HLA-DRB1*03:01",
    "HLA-DRB1*04:01",
    "HLA-DQA1*05:01/DQB1*02:01",
    "HLA-DQA1*03:01/DQB1*03:02",
]

with open("results/tables/hla2_15mers.txt") as f:
    peptides = [l.strip() for l in f if l.strip() and 12 <= len(l.strip()) <= 20]
print(f"Loaded {len(peptides):,} peptides", flush=True)
print(f"Batch size: {BATCH_SIZE}  →  {(len(peptides)+BATCH_SIZE-1)//BATCH_SIZE} batches per allele", flush=True)
print(f"Total batches: {4 * ((len(peptides)+BATCH_SIZE-1)//BATCH_SIZE)}", flush=True)

# --- Resume: skip alleles/batches already saved ---
done_keys = set()
if os.path.exists(OUT_PATH):
    with open(OUT_PATH) as f:
        rd = csv.DictReader(f, delimiter="\t")
        for row in rd:
            done_keys.add((row["allele"], row["batch_id"]))
    print(f"Resuming: {len(done_keys)} batches already done", flush=True)

# --- HTTP helpers ---
def http_post(url, data, timeout=180):
    body = json.dumps(data).encode()
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, (e.read().decode() if e.fp else str(e))
    except Exception as e:
        return None, str(e)

def http_get(url, timeout=120):
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, (e.read().decode() if e.fp else str(e))
    except Exception as e:
        return None, str(e)

def submit(peps, allele):
    payload = {
        "pipeline_id": "",
        "run_stage_range": [1, 1],
        "stages": [{
            "stage_number": 1,
            "tool_group": "mhcii",
            "input_sequence_text": "\n".join(peps),
            "input_parameters": {
                "alleles": allele,
                "peptide_length_range": None,
                "predictors": [{"type": "binding", "method": "netmhciipan_el"}]
            }
        }]
    }
    status, body = http_post(API_SUBMIT, payload)
    if status != 200:
        print(f"    submit {status}: {body[:200]}", flush=True)
        return None
    try:
        return json.loads(body).get("result_id")
    except Exception:
        return None

def poll_until_scored(rid, max_wait=1200):
    """Wait until the result contains netmhciipan_el_percentile."""
    url = f"{API_RESULT}/{rid}"
    start = time.time()
    while time.time() - start < max_wait:
        status, body = http_get(url)
        if status == 200:
            try:
                j = json.loads(body)
                for res in j["data"]["results"]:
                    cols = [c["name"] for c in res.get("table_columns", [])]
                    if "netmhciipan_el_percentile" in cols:
                        return j
            except Exception:
                pass
        elapsed = int(time.time() - start)
        print(f"    waiting... {elapsed}s", flush=True)
        time.sleep(20)
    return None

# --- Output file setup ---
HEADER = ["allele", "batch_id", "peptide", "core", "score", "percentile"]
write_header = not os.path.exists(OUT_PATH)
out_fh = open(OUT_PATH, "a", newline="")
writer = csv.writer(out_fh, delimiter="\t")
if write_header:
    writer.writerow(HEADER)
    out_fh.flush()

# --- Main loop ---
for allele in t1d_alleles:
    print(f"\n{'='*60}\n{allele}\n{'='*60}", flush=True)
    n_batches = (len(peptides) + BATCH_SIZE - 1) // BATCH_SIZE

    for bi in range(n_batches):
        batch_id = f"b{bi+1:03d}"
        if (allele, batch_id) in done_keys:
            print(f"  {batch_id}: already done", flush=True)
            continue

        batch = peptides[bi*BATCH_SIZE : (bi+1)*BATCH_SIZE]
        print(f"  {batch_id} ({len(batch)} peptides)...", flush=True)

        # Retry submission up to 3 times
        rid = None
        for attempt in range(3):
            rid = submit(batch, allele)
            if rid: break
            print(f"    submit retry {attempt+1}", flush=True)
            time.sleep(10)
        if rid is None:
            print(f"    giving up on this batch", flush=True)
            continue
        print(f"    rid={rid[:8]}", flush=True)

        j = poll_until_scored(rid)
        if j is None:
            print(f"    TIMEOUT — skipping", flush=True)
            continue

        n_saved = 0
        for res in j["data"]["results"]:
            cols = [c["name"] for c in res.get("table_columns", [])]
            if "netmhciipan_el_percentile" not in cols:
                continue
            idx = {n: cols.index(n) for n in ["peptide", "netmhciipan_el_core",
                                              "netmhciipan_el_score",
                                              "netmhciipan_el_percentile"]}
            for row in res["table_data"]:
                writer.writerow([
                    allele, batch_id,
                    row[idx["peptide"]],
                    row[idx["netmhciipan_el_core"]],
                    row[idx["netmhciipan_el_score"]],
                    row[idx["netmhciipan_el_percentile"]],
                ])
                n_saved += 1
            break
        out_fh.flush()
        print(f"    saved {n_saved}", flush=True)
        time.sleep(3)

out_fh.close()
print(f"\n=== DONE ===\nOutput: {OUT_PATH}", flush=True)