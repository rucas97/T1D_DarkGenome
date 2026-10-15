# Islet pcHi-C (Miguel-Escalada 2019) extraction
# Downloads Supplementary Data Sets, searches for SIMALR and risk region
# See session log for actual hits

import requests, re, os, zipfile
import pandas as pd

os.makedirs('/content/islet_pchic', exist_ok=True)
os.chdir('/content/islet_pchic')

url = "https://www.nature.com/articles/s41588-019-0457-0"
r = requests.get(url, headers={'User-Agent':'Mozilla/5.0'}, timeout=60)
links = re.findall(r'href="([^"]*(?:MOESM|Supplementary)[^"]*)"', r.text)
links = [l if l.startswith('http') else 'https://www.nature.com'+l for l in links]
links = sorted(set(links))

for link in links:
    fname = link.split('/')[-1].split('?')[0]
    if not fname or len(fname) < 3: continue
    if os.path.exists(fname): continue
    try:
        resp = requests.get(link, headers={'User-Agent':'Mozilla/5.0'}, timeout=120, stream=True)
        resp.raise_for_status()
        with open(fname, 'wb') as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"downloaded {fname}")
    except Exception as e:
        print(f"FAIL {link}: {e}")

# Extract zips
for zf in ['41588_2019_457_MOESM3_ESM.zip','41588_2019_457_MOESM4_ESM.zip']:
    if os.path.exists(zf):
        with zipfile.ZipFile(zf) as z:
            z.extractall(f"extracted_{zf[:20]}")

# Search by coordinates in relevant files
SIMALR   = (138260000, 138300000)
RISK     = (137990000, 138020000)
TNFAIP3  = (138180000, 138215000)

base = "extracted_41588_2019_457_MOESM/Supplementary_Data_Sets"

for fname, sheet in [
    ("Supplementary Data Set 1. Islet regulome.xlsx", "Islet Regulome"),
    ("Supplementary Data Set 7. List of TAD-like domains in human islets.xlsx", None),
    ("Supplementary Data Set 8. List of human islet PATs.xlsx", None),
    ("Supplementary Data Set 2. Enhancer-promoter assignments.xlsx", "Sheet1"),
]:
    p = os.path.join(base, fname)
    if not os.path.exists(p): continue
    xls = pd.ExcelFile(p)
    s = sheet if sheet else xls.sheet_names[0]
    df = pd.read_excel(xls, sheet_name=s, header=1)
    print(f"\n{fname}: {df.shape}, cols={list(df.columns)[:4]}")
    chr_c = [c for c in df.columns if 'chr' in str(c).lower()][:1]
    st_c = [c for c in df.columns if 'start' in str(c).lower()]
    en_c = [c for c in df.columns if 'end' in str(c).lower()]
    if not (chr_c and st_c and en_c): continue
    for label, (a, b) in [('SIMALR',SIMALR),('RISK',RISK),('TNFAIP3',TNFAIP3)]:
        m = df[df[chr_c[0]].astype(str).str.replace('chr','').str.strip().isin(['6']) &
              (pd.to_numeric(df[st_c[0]],errors='coerce').between(a,b) |
               pd.to_numeric(df[en_c[0]],errors='coerce').between(a,b))]
        if len(m):
            print(f"  {label}: {len(m)} rows")
            print(m.head(10).to_string())
