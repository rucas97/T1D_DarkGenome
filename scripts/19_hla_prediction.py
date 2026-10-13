# IEDB NextGen API HLA-II prediction (stdlib only — no requests needed)
import os, sys, time, json, urllib.request, urllib.error, csv

os.chdir("D:/T1D_DarkGenome")
IEDB_API = "https://api-nextgen-tools.iedb.org/api/v1/pipeline"
RESULTS_API = "https://api-nextgen-tools.iedb.org/api/v1/results"

t1d_alleles = ["HLA-DRB1*03:01", "HLA-DRB1*04:01",
               "HLA-DQA1*05:01/DQB1*02:01", "HLA-DQA1*03:01/DQB1*03:02"]

with open("results/tables/hla2_15mers.txt") as f:
    peptides = [l.strip() for l in f if l.strip() and 12 <= len(l.strip()) <= 20]
print(f"Loaded {len(peptides):,} 15-mer peptides", flush=True)

def http_post(url, data, timeout=180):
    body = json.dumps(data).encode()
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode() if e.fp else str(e)
    except Exception as e:
        return None, str(e)

def http_get(url, timeout=120):
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode() if e.fp else str(e)
    except Exception as e:
        return None, str(e)

def submit(batch, allele):
    payload = {"pipeline_id": "", "run_stage_range": [1,1],
        "stages": [{"stage_number": 1, "tool_group": "mhcii",
            "input_sequence_text": "\n".join(batch),
            "input_parameters": {"alleles": allele, "peptide_length_range": None,
                "predictors": [{"type": "binding", "method": "netmhciipan_el"}]}}]}
    s, b = http_post(IEDB_API, payload)
    if s != 200: return None
    try: return json.loads(b).get("result_id")
    except: return None

# NOTE: Large batches (5000) do NOT complete on IEDB. Use 1000.
# For actual completion, use MixMHC2pred locally (scripts/23).
# This script retained for reproducibility of the API attempt.
print("This script is retained for API reproducibility.", flush=True)
print("For actual predictions use MixMHC2pred — see scripts/23.", flush=True)
