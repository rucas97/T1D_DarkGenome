import urllib.request, json

def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json'})
    with urllib.request.urlopen(req, timeout=45) as r:
        return json.loads(r.read())

print("="*60)
print("rs6920220 — T1D risk variant at the TNFAIP3/SIMALR locus")
print("="*60)

# --- GWAS Catalog: all associations for rs6920220 ---
print("\n=== GWAS Catalog: diseases associated with rs6920220 ===")
try:
    d = get("https://www.ebi.ac.uk/gwas/rest/api/singleNucleotidePolymorphisms/rs6920220/associations")
    assoc = d.get('_embedded', {}).get('associations', [])
    traits = set()
    for a in assoc:
        for t in a.get('efoTraits', []):
            traits.add(t.get('trait', '?'))
    print(f"  {len(assoc)} associations, {len(traits)} unique traits:")
    for t in sorted(traits):
        print(f"    - {t}")
except Exception as e:
    print(f"  error: {e}")

# --- GTEx: eQTLs for SIMALR across all tissues ---
print("\n=== GTEx v8: eQTLs for SIMALR (ENSG00000226004) ===")
for gid in ["ENSG00000226004", "ENSG00000226004.1"]:
    try:
        d = get(f"https://gtexportal.org/api/v2/association/singleTissueEqtl?gencodeId={gid}")
        data = d.get('data', [])
        print(f"  {gid}: {len(data)} eQTLs")
        for e in data[:10]:
            print(f"    {e.get('variantId','?')}  {e.get('tissueSiteDetailId','?'):25s}  "
                  f"NES={e.get('nes',0):+.3f}  p={e.get('pValue',1):.2e}")
        if data: break
    except Exception as e:
        print(f"  {gid}: error {e}")

# --- GTEx: eQTLs for TNFAIP3 (neighbor, positive control) ---
print("\n=== GTEx v8: eQTLs for TNFAIP3 (positive control) ===")
try:
    d = get("https://gtexportal.org/api/v2/association/singleTissueEqtl?gencodeId=ENSG00000118503.18")
    data = d.get('data', [])
    print(f"  {len(data)} eQTLs, top 5:")
    for e in data[:5]:
        print(f"    {e.get('variantId','?')}  {e.get('tissueSiteDetailId','?'):25s}  "
              f"NES={e.get('nes',0):+.3f}  p={e.get('pValue',1):.2e}")
except Exception as e:
    print(f"  error: {e}")

# --- Does GTEx have rs6920220 at all? ---
print("\n=== rs6920220 specifically — GTEx variant lookup ===")
try:
    d = get("https://gtexportal.org/api/v2/dataset/variant?variantId=rs6920220")
    print(json.dumps(d, indent=2)[:800])
except Exception as e:
    print(f"  error: {e}")

