# scripts/54_clean_wjd.py
import re
from docx import Document
from docx.shared import Pt

DOCX = "manuscript.docx"
doc = Document(DOCX)

# ------------------------------------------------------------
# 1. KEEP all tables (no action)
# ------------------------------------------------------------
print(f"Tables present: {len(doc.tables)} (kept).")

# ------------------------------------------------------------
# 2. Remove sub-headings (Heading 2, 3, 4, 5).
#    Keep only the mandatory top-level sections (Heading 1):
#    Abstract, Introduction, Materials and Methods, Results,
#    Discussion, Conclusion, Acknowledgements, References,
#    Footnotes.
# ------------------------------------------------------------
KEEP_H1 = {
    "Abstract", "Introduction", "Materials and Methods", "Methods",
    "Results", "Discussion", "Conclusion", "Acknowledgements",
    "References", "Footnotes",
}

removed = 0
for para in list(doc.paragraphs):
    style = (para.style.name or "").lower()
    text = para.text.strip()
    if style.startswith("heading 2") or style.startswith("heading 3") \
       or style.startswith("heading 4") or style.startswith("heading 5"):
        para._element.getparent().remove(para._element)
        removed += 1
    elif style.startswith("heading 1") and text not in KEEP_H1:
        para._element.getparent().remove(para._element)
        removed += 1

print(f"Removed {removed} sub-heading paragraph(s).")

# ------------------------------------------------------------
# 3. Fix in-text citations and add reference list.
#    References ordered by first appearance in the manuscript.
# ------------------------------------------------------------
REFS = [
    ("chiou2021",           "Chiou J, Geusz RJ, Okino ML, et al. A multi-ethnic genome-wide association study identifies novel loci for type 1 diabetes. Nat Commun 2021; 12: 4697 [PMID: 34373454 DOI: 10.1038/s41467-021-24970-4]"),
    ("robertson2021",       "Robertson CC, Inshaw JRJ, Chim K, et al. Fine-mapping, trans-ancestral and genomic analyses identify causal variants, cells, genes and drug targets for type 1 diabetes. Nat Genet 2021; 53: 962-971 [PMID: 34045743 DOI: 10.1038/s41588-021-00880-5]"),
    ("olsson2015",          "Olsson LM, et al. rs6920220 and TNFAIP3 genotype-specific regulation in rheumatoid arthritis. Arthritis Rheumatol 2015 [PMID: 25707945]"),
    ("martin2016",          "Martin P, McGovern A, Orozco G, et al. Capture Hi-C identifies a novel causal gene, IL20RA, in the pan-autoimmune genetic susceptibility region 6q23. Genome Biol 2016; 17: 212 [PMID: 27724958 DOI: 10.1186/s13059-016-1078-x]"),
    ("cynn2023",            "Cynn E, et al. Human macrophage long intergenic non-coding RNA, SIMALR, suppresses inflammatory macrophage apoptosis via Netrin 1. Arterioscler Thromb Vasc Biol 2023 [PMID: 36799758]"),
    ("nanaware2025",        "Nanaware PP, et al. MHC class I and II immunopeptidomics of human pancreatic islets. Cell Rep 2025 [PMID: 40737125]"),
    ("xu2025",              "Xu Y, et al. LINC02528/SIMALR is a blood biomarker and functional regulator of macrophage responses in tuberculosis. PLoS Pathog 2025 [PMID: 41308682]"),
    ("consortium2020gtex",  "GTEx Consortium. The GTEx Consortium atlas of genetic regulatory effects across human tissues. Science 2020; 369: 1318-1330 [PMID: 32913098 DOI: 10.1126/science.aaz1776]"),
    ("vita2019",            "Vita R, Mahajan S, Overton JA, et al. The Immune Epitope Database (IEDB) 2018 update. Nucleic Acids Res 2019; 47: D339-D343 [PMID: 30357371 DOI: 10.1093/nar/gky1006]"),
    ("bastian2016",         "Bastian F, Parmentier G, Roux J, et al. The Bgee suite for retrieval and comparison of gene expression patterns across multiple animal species. Bioinformatics 2016; 32: 3399-3401 [PMID: 27378296 DOI: 10.1093/bioinformatics/btw372]"),
    ("miguel2019",          "Miguel-Escalada I, Bonas-Guarch S, Cebola I, et al. Human pancreatic islet three-dimensional chromatin architecture provides insights into the genetics of type 2 diabetes. Nat Genet 2019; 51: 1137-1148 [PMID: 31253979 DOI: 10.1038/s41588-019-0457-0]"),
    ("love2014",            "Love MI, Huber W, Anders S. Moderated estimation of fold change and dispersion for RNA-seq data with DESeq2. Genome Biol 2014; 15: 550 [PMID: 25516281 DOI: 10.1186/s13059-014-0550-8]"),
    ("pages2020",           "Pages H, Aboyoun P, Gentleman R, DebRoy S. Biostrings: Efficient manipulation of biological strings. R package, 2020"),
    ("gfeller2019",         "Gfeller D, Guillaume P, Michaux J, et al. Improved predictions of MHC class II antigen presentation. bioRxiv 2019 [DOI: 10.1101/589838]"),
    ("andreatta2016",       "Andreatta M, Karosiene E, Rasmussen M, et al. Accurate pan-specific prediction of peptide-MHC class II binding affinity with improved binding core identification. Immunogenetics 2016; 68: 871-880 [PMID: 27575705 DOI: 10.1007/s00251-016-0945-7]"),
    ("hao2021",             "Hao Y, Hao S, Andersen-Nissen E, et al. Integrated analysis of multimodal single-cell data. Cell 2021; 184: 3573-3587 [PMID: 34062119 DOI: 10.1016/j.cell.2021.04.048]"),
    ("stuart2019",          "Stuart T, Butler A, Hoffman P, et al. Comprehensive integration of single-cell data. Cell 2019; 177: 1888-1902 [PMID: 31178118 DOI: 10.1016/j.cell.2019.05.031]"),
]

key_to_num = {k: i + 1 for i, (k, _) in enumerate(REFS)}

def replace_citations(text):
    def repl(m):
        keys = re.findall(r'@([A-Za-z0-9_]+)', m.group(1))
        nums = sorted({key_to_num.get(k, 0) for k in keys if key_to_num.get(k)})
        return "[" + ",".join(str(n) for n in nums) + "]"
    return re.sub(r'\[([^\]]*@[^\]]+)\]', repl, text)

# Apply in-text citation replacement
replaced = 0
for para in doc.paragraphs:
    full = para.text
    if "@" in full and "[" in full:
        new = replace_citations(full)
        if new != full:
            for i, run in enumerate(para.runs):
                run.text = new if i == 0 else ""
            replaced += 1
print(f"Replaced citations in {replaced} paragraph(s).")

# ------------------------------------------------------------
# 4. Append numbered reference list under References heading
# ------------------------------------------------------------
ref_heading = None
for para in doc.paragraphs:
    if para.text.strip() == "References" and (para.style.name or "").lower().startswith("heading"):
        ref_heading = para
        break

if ref_heading is None:
    doc.add_heading("References", level=1)

# Remove any remaining pandoc placeholders
for para in list(doc.paragraphs):
    if para.text.strip() in ("::: {#refs}", ":::", "{#refs}"):
        para._element.getparent().remove(para._element)

for n, (_, text) in enumerate(REFS, 1):
    p = doc.add_paragraph(f"{n}. {text}")
    for run in p.runs:
        run.font.name = "Book Antiqua"
        run.font.size = Pt(12)
    p.paragraph_format.line_spacing = 1.5

print(f"Appended {len(REFS)} references under 'References'.")

doc.save(DOCX)
print("Saved:", DOCX)