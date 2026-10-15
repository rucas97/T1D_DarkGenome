import subprocess, os, re

SIMALR_IDS = ["LINC02528","SIMALR","ENSG00000226004","RP11-10J5.1","105378020"]

DATASETS = {
    "GSE33440":  "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE33nnn/GSE33440/matrix/",
    "GSE154609": "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE154nnn/GSE154609/matrix/",
    "GSE239501": "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE239nnn/GSE239501/suppl/",
}

for gse, url in DATASETS.items():
    print(f"\n{'='*60}\n{gse}\n{'='*60}")
    try:
        r = subprocess.run(["curl","-sS","--max-time","60","-H","User-Agent: Mozilla/5.0",url],
                          capture_output=True, text=True, timeout=90)
        html = r.stdout
    except Exception as e:
        print(f"  error: {e}"); continue
    files = re.findall(r'href="([^"]+\.(?:txt|csv|tsv|xlsx|gz))"', html, re.I)
    if not files:
        print("  no files listed"); continue
    for f in files[:5]:
        fname = f.split("/")[-1]
        local = f"data/raw/T1D_PBMC/{gse}_{fname}"
        os.makedirs("data/raw/T1D_PBMC", exist_ok=True)
        try:
            subprocess.run(["curl","-sS","--fail","--max-time","300","-H","User-Agent: Mozilla/5.0","-o",local,url+fname],
                          timeout=360, check=True)
        except Exception as e:
            print(f"  FAIL {fname}: {e}"); continue
        print(f"  downloaded {fname}")
