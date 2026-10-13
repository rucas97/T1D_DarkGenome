# ============================================================
# diagnose_iedb.py
# Compare a completed job (825 peptides) vs a stuck job (5000)
# Print full JSON structure of both.
# ============================================================

import json, urllib.request

RESULTS_API = "https://api-nextgen-tools.iedb.org/api/v1/results"

def fetch(rid):
    url = f"{RESULTS_API}/{rid}"
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/json")
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode())

# One small batch (825 peptides — reported "got 825")
SMALL_RID = "a527e8ce-27ea-4025-b74e-a9d31bf6b161"
# One large batch (5000 peptides — reported "preview only")
LARGE_RID = "262e02d9-b0f9-4844-9401-b02092580b0e"

for label, rid in [("SMALL (825)", SMALL_RID), ("LARGE (5000)", LARGE_RID)]:
    print(f"\n{'='*60}")
    print(f"{label}: {rid}")
    print('='*60)
    try:
        j = fetch(rid)
    except Exception as e:
        print(f"  FETCH FAILED: {e}")
        continue

    # Top-level keys
    print(f"  Top-level keys: {list(j.keys())}")
    data = j.get("data", {})
    print(f"  data keys: {list(data.keys())}")

    for i, res in enumerate(data.get("results", [])):
        print(f"\n  --- result[{i}] ---")
        print(f"  type: {res.get('type')}")
        cols = res.get("table_columns", [])
        print(f"  column count: {len(cols)}")
        for c in cols:
            print(f"    - {c['name']}")
        rows = res.get("table_data", [])
        print(f"  row count: {len(rows)}")
        if rows:
            print(f"  first row: {rows[0]}")

        # Check if there's a status field indicating pending computation
        if "status" in res:
            print(f"  STATUS: {res['status']}")
        if "message" in res:
            print(f"  MESSAGE: {res['message']}")