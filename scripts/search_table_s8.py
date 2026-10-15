# ============================================================
# search_table_s8.py
# Search Nanaware et al. Table S8 (mmc8.xlsx) for SIMALR peptides
# Table S8 = MHC-I/II peptides eluted from human pancreatic islets
# ============================================================

import pandas as pd
import os

# --- Path to mmc8.xlsx (in Windows Downloads folder) ---
file_path = os.path.expanduser("~/Downloads/mmc8.xlsx")
if not os.path.exists(file_path):
    file_path = "/c/Users/Salman/Downloads/mmc8.xlsx"

print(f"Looking for: {file_path}")
print(f"Exists: {os.path.exists(file_path)}")

# --- Load all sheets so we know what we have ---
xls = pd.ExcelFile(file_path)
print(f"\nSheets in workbook: {xls.sheet_names}")

# --- Our SIMALR peptides and cores ---
simalr_peptides = [
    "EHKDGQVQAKGERPG", "CEHKDGQVQAKGERP", "MRYWSDAGAGIWTIT",
    "HGSDFATKMSYENPA", "SMRYWSDAGAGIWTI", "MKRAGGATAWKDSMC",
    "HRNLRRDNQISICKP", "MSFFIFFQNLASGLDR", "MSFFIFQNLASGLDR",
    "LLYIQQEASNVEVIR"
]

simalr_cores = [
    "DGQVQAKGE", "WSDAGAGIW", "DFATKMSYE", "AGGATAWKD", "SGGATAWKD",
    "LRRDNQISI", "FFIFQNLAS", "IQQEASNVE", "WGYTPTYRE", "IHFAAEILV",
    "MRYWSDAGA", "IKILETEDF", "ASILYPEKE", "IQNATRIRL"
]

# --- Search across every sheet that has a 'Peptide' column ---
for sheet in xls.sheet_names:
    try:
        df = pd.read_excel(xls, sheet_name=sheet)
    except Exception as e:
        print(f"\n[{sheet}] could not read: {e}")
        continue

    # Find the peptide column
    pep_col = None
    for c in df.columns:
        if str(c).strip().lower() == "peptide":
            pep_col = c
            break
    if pep_col is None:
        continue

    df[pep_col] = df[pep_col].astype(str)
    print(f"\n{'='*60}")
    print(f"Sheet: {sheet}  ({len(df)} rows, peptide column='{pep_col}')")
    print('='*60)

    # --- Exact matches ---
    exact = df[df[pep_col].isin(simalr_peptides)]
    if len(exact) > 0:
        print("\n*** EXACT SIMALR PEPTIDE MATCHES ***")
        print(exact.to_string())
    else:
        print("No exact SIMALR peptide matches.")

    # --- Core substring matches ---
    core_hits = []
    for core in simalr_cores:
        m = df[df[pep_col].str.contains(core, na=False, regex=False)]
        if len(m) > 0:
            core_hits.append((core, m))

    if core_hits:
        print("\n*** CORE SUBSTRING MATCHES ***")
        for core, m in core_hits:
            print(f"\n  Core: {core}")
            cols = [c for c in [pep_col, "Gene", "Protein", "known autoantigen",
                                "Pancreas", "T1D", "cytokines beta"] if c in m.columns]
            print(m[cols].to_string(index=False))
    else:
        print("No core substring matches.")

print("\n=== SEARCH COMPLETE ===")
