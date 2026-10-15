import urllib.request, json

def get(url, timeout=60):
    req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0','Accept':'application/json'})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())

print("="*70)
print("GTEx v8: cis-eQTLs for TNFAIP3")
print("="*70)
for gid in ["ENSG00000118503.16","ENSG00000118503.17"]:
    try:
        u = f"https://gtexportal.org/api/v2/association/singleTissueEqtl?gencodeId={gid}&datasetId=gtex_v8"
        d = get(u)
        data = d.get('data', [])
        print(f"  {gid}: {len(data)} eQTLs")
        for e in data[:10]:
            print(f"    {e.get('variantId','?')}  {e.get('tissueSiteDetailId','?'):30s}  NES={e.get('nes',0):+.3f}  p={e.get('pValue',1):.2e}")
        break
    except Exception as e:
        print(f"  {gid}: {e}")

print("\n" + "="*70)
print("GTEx v8: cis-eQTLs for SIMALR")
print("="*70)
for gid in ["ENSG00000226004.1","ENSG00000226004.2","ENSG00000226004.3"]:
    try:
        u = f"https://gtexportal.org/api/v2/association/singleTissueEqtl?gencodeId={gid}&datasetId=gtex_v8"
        d = get(u)
        data = d.get('data', [])
        print(f"  {gid}: {len(data)} eQTLs")
        for e in data[:10]:
            print(f"    {e.get('variantId','?'):18s}  {e.get('tissueSiteDetailId','?'):30s}  NES={e.get('nes',0):+.3f}")
        if data: break
    except Exception as e:
        print(f"  {gid}: {e}")

print("\n" + "="*70)
print("GTEx v8: eQTLs at rs6920220")
print("="*70)
try:
    u = "https://gtexportal.org/api/v2/association/singleTissueEqtl?variantId=rs6920220&datasetId=gtex_v8"
    d = get(u)
    print(f"  {len(d.get('data',[]))} eQTLs")
except Exception as e:
    print(f"  {e}")
