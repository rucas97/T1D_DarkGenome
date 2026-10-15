import os, glob, csv

SIMALR_PEPTIDES = [
    "EHKDGQVQAKGERPG","CEHKDGQVQAKGERP","MRYWSDAGAGIWTIT",
    "HGSDFATKMSYENPA","SMRYWSDAGAGIWTI","MKRAGGATAWKDSMC",
    "HRNLRRDNQISICKP","MSFFIFFQNLASGLDR","MSFFIFQNLASGLDR",
    "LLYIQQEASNVEVIR",
]
SIMALR_CORES = [
    "DGQVQAKGE","WSDAGAGIW","DFATKMSYE","AGGATAWKD","SGGATAWKD",
    "LRRDNQISI","FFIFQNLAS","IQQEASNVE","WGYTPTYRE","IHFAAEILV",
    "MRYWSDAGA","IKILETEDF","ASILYPEKE","IQNATRIRL",
]

rna_seq = ""
p = "data/reference/SIMALR_URS0000BC4578.fa"
if os.path.exists(p):
    with open(p) as f:
        for line in f:
            if not line.startswith(">"): rna_seq += line.strip()
rna_seq = rna_seq.upper().replace("U","T")
print(f"SIMALR RNA length: {len(rna_seq)} nt")

CODON = {'TTT':'F','TTC':'F','TTA':'L','TTG':'L','CTT':'L','CTC':'L','CTA':'L','CTG':'L',
'ATT':'I','ATC':'I','ATA':'I','ATG':'M','GTT':'V','GTC':'V','GTA':'V','GTG':'V',
'TCT':'S','TCC':'S','TCA':'S','TCG':'S','CCT':'P','CCC':'P','CCA':'P','CCG':'P',
'ACT':'T','ACC':'T','ACA':'T','ACG':'T','GCT':'A','GCC':'A','GCA':'A','GCG':'A',
'TAT':'Y','TAC':'Y','TAA':'*','TAG':'*','CAT':'H','CAC':'H','CAA':'Q','CAG':'Q',
'AAT':'N','AAC':'N','AAA':'K','AAG':'K','GAT':'D','GAC':'D','GAA':'E','GAG':'E',
'TGT':'C','TGC':'C','TGA':'*','TGG':'W','CGT':'R','CGC':'R','CGA':'R','CGG':'R',
'AGT':'S','AGC':'S','AGA':'R','AGG':'R','GGT':'G','GGC':'G','GGA':'G','GGG':'G'}
def rc(s):
    c={'A':'T','T':'A','G':'C','C':'G','N':'N'}
    return ''.join(c.get(b,'N') for b in reversed(s))
def tr(s):
    return ''.join(CODON.get(s[i:i+3],'X') for i in range(0,len(s)-2,3))

orf = set()
if rna_seq:
    for strand in (rna_seq, rc(rna_seq)):
        for frame in range(3):
            for sub in tr(strand[frame:]).split('*'):
                for k in range(8,16):
                    for i in range(len(sub)-k+1):
                        orf.add(sub[i:i+k])
print(f"Generated {len(orf)} SIMALR ORF k-mers (8-15 aa)")

def ham(a,b):
    return sum(x!=y for x,y in zip(a,b)) if len(a)==len(b) else 999
def fuzzy(pep,core,mm=1):
    k=len(core)
    for i in range(len(pep)-k+1):
        d=ham(pep[i:i+k],core)
        if d<=mm: return (pep[i:i+k], d)
    return None

files = sorted(glob.glob("data/raw/MSV000093843/peptides/*.txt"))
all_hits=[]; summary=[]
for pf in files:
    name=os.path.basename(pf).replace(".txt","")
    peps=set(l.strip() for l in open(pf) if l.strip())
    hits=[]
    for p in peps:
        if p in SIMALR_PEPTIDES: hits.append((name,p,"EXACT_PEPTIDE",""))
        for c in SIMALR_CORES:
            if c in p: hits.append((name,p,"EXACT_CORE",c))
        if p in orf: hits.append((name,p,"ORF_DERIVED",""))
        for c in SIMALR_CORES:
            r=fuzzy(p,c,1)
            if r and r[1]==1: hits.append((name,p,"FUZZY_1MM",f"{c}->{r[0]}"))
    summary.append((name,len(peps),len(hits)))
    all_hits.extend(hits)
    print(f"  {name}: {len(peps)} peptides, {len(hits)} hits")

print("\n"+"="*70)
for n,p,h in summary: print(f"{n:50s} {p:>10d} {h:>6d}")

with open("results/tables/MSV000093843_search_summary.tsv","w",newline="") as f:
    w=csv.writer(f,delimiter="\t"); w.writerow(["file","unique_peptides","simalr_hits"]); w.writerows(summary)

if all_hits:
    print(f"\n{len(set(all_hits))} HITS")
    with open("results/tables/MSV000093843_SIMALR_hits.tsv","w",newline="") as f:
        w=csv.writer(f,delimiter="\t"); w.writerow(["file","peptide","match_type","detail"])
        for row in sorted(set(all_hits)): w.writerow(row)
else:
    print("\n*** NO SIMALR PEPTIDES FOUND ***")
