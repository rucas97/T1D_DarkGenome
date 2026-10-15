# scripts/57_final_fixes.py
import os, sys

if not os.path.exists("manuscript.Rmd"):
    sys.exit("Run from project root (D:/T1D_DarkGenome)")

with open("manuscript.Rmd", "r", encoding="utf-8") as f:
    rmd = f.read()

edits = []

# ============================================================
# 1. Fix xu2025 citations [6] -> [17] (2 occurrences)
# ============================================================
s1 = "decreases after anti-TB therapy[6]"
s2 = "correlates with disease severity[6]"

if s1 in rmd:
    rmd = rmd.replace(s1, "decreases after anti-TB therapy[17]")
    edits.append("Fixed xu2025 citation (Results)")
else:
    print("WARN: string not found:", s1)

if s2 in rmd:
    rmd = rmd.replace(s2, "correlates with disease severity[17]")
    edits.append("Fixed xu2025 citation (Discussion)")
else:
    print("WARN: string not found:", s2)

# ============================================================
# 2. Add pseudocount sentence to Methods
# ============================================================
old_methods = "Dark genome filtering required GENCODE biotype in {lncRNA, pseudogene, TEC} and absolute log2FC greater than 2 versus untreated."
new_methods = old_methods + " In 12 of 19 donors, SIMALR was undetected in the untreated condition; log2 fold changes were computed with a pseudocount of 1 read added to both conditions to avoid undefined values."

if "pseudocount of 1 read" in rmd:
    edits.append("Pseudocount sentence already present")
elif old_methods in rmd:
    rmd = rmd.replace(old_methods, new_methods)
    edits.append("Added pseudocount sentence to Methods")
else:
    print("WARN: Methods target not found")

# ============================================================
# 3. Convert ## Limitations to bold lead-in + split into paragraphs
# ============================================================
old_lim = "## Limitations\n\nThe study is entirely computational. Every result is derived from public datasets and from prediction algorithms; no wet-lab experiment was performed. The HLA class II binding predictions are supported by two independent algorithms with concordant cores but are not confirmed by mass spectrometry; the bulk islet immunopeptidomics search we performed was negative and cannot exclude presentation below detection limit. The public SIMALR ASO knockdown dataset available achieved only a partial knockdown (log2FC minus 0.85, q = 0.999) and cannot support causal claims about downstream chemokine effects. Islet-resident macrophages were not directly interrogated; the PanKbase islet atlas v3.4 (448,935 cells) did not detect SIMALR in any cell-type marker list, consistent with a cytokine-inducible rather than constitutive expression pattern but leaving the in situ macrophage question open. The islet capture Hi-C panel did not directly bait the SIMALR promoter, so islet chromatin evidence is at TAD level rather than at fragment level. Blood expression results are null at the disease-state level; the pre-diabetic trend is based on three donors and requires replication. Natural presentation of SIMALR peptides on HLA class II, T-cell reactivity against them, and any causal role in islet inflammation remain to be demonstrated experimentally."

new_lim = "**Limitations.** The study is entirely computational. Every result is derived from public datasets and from prediction algorithms; no wet-lab experiment was performed.\n\nThe HLA class II binding predictions are supported by two independent algorithms with concordant cores but are not confirmed by mass spectrometry. The bulk islet immunopeptidomics search we performed was negative and cannot exclude presentation below the detection limit.\n\nThe public SIMALR ASO knockdown dataset available achieved only a partial knockdown (log2FC minus 0.85, q = 0.999) and cannot support causal claims about downstream chemokine effects.\n\nIslet-resident macrophages were not directly interrogated. The PanKbase islet atlas v3.4 (448,935 cells) did not detect SIMALR in any cell-type marker list, consistent with a cytokine-inducible rather than constitutive expression pattern but leaving the in situ macrophage question open.\n\nThe islet capture Hi-C panel did not directly bait the SIMALR promoter, so islet chromatin evidence is at TAD level rather than at fragment level.\n\nBlood expression results are null at the disease-state level. The pre-diabetic trend is based on three donors and requires replication.\n\nNatural presentation of SIMALR peptides on HLA class II, T-cell reactivity against them, and any causal role in islet inflammation remain to be demonstrated experimentally."

if old_lim in rmd:
    rmd = rmd.replace(old_lim, new_lim)
    edits.append("Split Limitations into 7 paragraphs + bold lead-in")
else:
    print("WARN: Limitations block not found")

# ============================================================
# 4. Move immunopeptidomics interpretation to Discussion
# ============================================================
move_para = "This negative result is consistent with the expected biology. SIMALR is macrophage-restricted, and islet-resident macrophages represent a small fraction of total cells in whole-islet preparations. At the depth of bulk islet immunopeptidomics (approximately 3,000-4,000 peptides per HLA class II allele), a macrophage-restricted peptide is expected to fall below detection. Direct demonstration of natural presentation would require macrophage-enriched or sorted immunopeptidomics from cytokine-stimulated tissue."

if move_para in rmd:
    # Remove from Results
    rmd = rmd.replace(move_para + "\n", "", 1)
    # Add to Discussion right before the bold Limitations lead-in
    moved = "The negative immunopeptidomics result is consistent with the expected biology. SIMALR is macrophage-restricted, and islet-resident macrophages represent a small fraction of total cells in whole-islet preparations. At the depth of bulk islet immunopeptidomics (approximately 3,000-4,000 peptides per HLA class II allele), a macrophage-restricted peptide is expected to fall below detection. Direct demonstration of natural presentation would require macrophage-enriched or sorted immunopeptidomics from cytokine-stimulated tissue.\n\n"
    rmd = rmd.replace("**Limitations.**", moved + "**Limitations.**", 1)
    edits.append("Moved immunopeptidomics interpretation to Discussion")
else:
    print("WARN: immunopeptidomics interpretation paragraph not found")

# Save Rmd
with open("manuscript.Rmd", "w", encoding="utf-8") as f:
    f.write(rmd)
print("manuscript.Rmd updated.")

# ============================================================
# 5. Rewrite 56_clean_final.py with correct REFS + Footnotes
# ============================================================
new_56 = r'''# scripts/56_clean_final.py
import re
from docx import Document
from docx.shared import Pt

DOCX = "manuscript.docx"
doc = Document(DOCX)

print(f"Tables before cleanup: {len(doc.tables)} (KEPT)")

# ---- 1. Remove all Heading 2+ ----
MANDATORY_H1 = {
    "Abstract", "Introduction", "Materials and Methods", "Methods",
    "Results", "Discussion", "Conclusion", "Acknowledgements",
    "References", "Footnotes",
}
removed = 0
for para in list(doc.paragraphs):
    st = (para.style.name or "").lower()
    txt = para.text.strip()
    if st.startswith(("heading 2", "heading 3", "heading 4", "heading 5", "heading 6")):
        para._element.getparent().remove(para._element)
        removed += 1
    elif st.startswith("heading 1") and txt not in MANDATORY_H1:
        para._element.getparent().remove(para._element)
        removed += 1
print(f"Removed {removed} sub-heading(s).")

# ---- 2. Reference list, ordered by first appearance in text ----
REFS = [
    ("chiou2021", "Chiou J, Geusz RJ, Okino ML, et al. A multi-ethnic genome-wide association study identifies novel loci for type 1 diabetes. Nat Commun 2021;12:4697 [PMID: 34373454 DOI: 10.1038/s41467-021-24970-4]"),
    ("robertson2021", "Robertson CC, Inshaw JRJ, Chim K, et al. Fine-mapping, trans-ancestral and genomic analyses identify causal variants, cells, genes and drug targets for type 1 diabetes. Nat Genet 2021;53:962-971 [PMID: 34045743 DOI: 10.1038/s41588-021-00880-5]"),
    ("olsson2015", "Olsson LM, et al. rs6920220 and TNFAIP3 genotype-specific regulation in rheumatoid arthritis. Arthritis Rheumatol 2015 [PMID: 25707945]"),
    ("martin2016", "Martin P, McGovern A, Orozco G, et al. Capture Hi-C identifies a novel causal gene, IL20RA, in the pan-autoimmune genetic susceptibility region 6q23. Genome Biol 2016;17:212 [PMID: 27724958 DOI: 10.1186/s13059-016-1078-x]"),
    ("cynn2023", "Cynn E, et al. Human macrophage long intergenic non-coding RNA, SIMALR, suppresses inflammatory macrophage apoptosis via Netrin 1. Arterioscler Thromb Vasc Biol 2023 [PMID: 36799758]"),
    ("nanaware2025", "Nanaware PP, et al. MHC class I and II immunopeptidomics of human pancreatic islets. Cell Rep 2025 [PMID: 40737125]"),
    ("gtex2020", "GTEx Consortium. The GTEx Consortium atlas of genetic regulatory effects across human tissues. Science 2020;369:1318-1330 [PMID: 32913098 DOI: 10.1126/science.aaz1776]"),
    ("vita2019", "Vita R, Mahajan S, Overton JA, et al. The Immune Epitope Database (IEDB) 2018 update. Nucleic Acids Res 2019;47:D339-D343 [PMID: 30357371 DOI: 10.1093/nar/gky1006]"),
    ("bastian2016", "Bastian F, Parmentier G, Roux J, et al. The Bgee suite for retrieval and comparison of gene expression patterns across multiple animal species. Bioinformatics 2016;32:3399-3401 [PMID: 27378296 DOI: 10.1093/bioinformatics/btw372]"),
    ("miguel2019", "Miguel-Escalada I, Bonas-Guarch S, Cebola I, et al. Human pancreatic islet three-dimensional chromatin architecture provides insights into the genetics of type 2 diabetes. Nat Genet 2019;51:1137-1148 [PMID: 31253979 DOI: 10.1038/s41588-019-0457-0]"),
    ("love2014", "Love MI, Huber W, Anders S. Moderated estimation of fold change and dispersion for RNA-seq data with DESeq2. Genome Biol 2014;15:550 [PMID: 25516281 DOI: 10.1186/s13059-014-0550-8]"),
    ("pages2020", "Pages H, Aboyoun P, Gentleman R, DebRoy S. Biostrings: Efficient manipulation of biological strings. R package, 2020"),
    ("gfeller2019", "Gfeller D, Guillaume P, Michaux J, et al. Improved predictions of MHC class II antigen presentation. bioRxiv 2019 [DOI: 10.1101/589838]"),
    ("andreatta2016", "Andreatta M, Karosiene E, Rasmussen M, et al. Accurate pan-specific prediction of peptide-MHC class II binding affinity with improved binding core identification. Immunogenetics 2016;68:871-880 [PMID: 27575705 DOI: 10.1007/s00251-016-0945-7]"),
    ("hao2021", "Hao Y, Hao S, Andersen-Nissen E, et al. Integrated analysis of multimodal single-cell data. Cell 2021;184:3573-3587 [PMID: 34062119 DOI: 10.1016/j.cell.2021.04.048]"),
    ("stuart2019", "Stuart T, Butler A, Hoffman P, et al. Comprehensive integration of single-cell data. Cell 2019;177:1888-1902 [PMID: 31178118 DOI: 10.1016/j.cell.2019.05.031]"),
    ("xu2025", "Xu Y, et al. LINC02528/SIMALR is a blood biomarker and functional regulator of macrophage responses in tuberculosis. PLoS Pathog 2025 [PMID: 41308682]"),
]

# Remove any old numbered reference list if present
for para in list(doc.paragraphs):
    t = para.text.strip()
    if re.match(r"^[0-9]{1,2}\. [A-Z]", t) and ("PMID:" in t or "DOI:" in t or len(t) > 80):
        para._element.getparent().remove(para._element)

if not any(p.text.strip() == "References" and (p.style.name or "").lower().startswith("heading") for p in doc.paragraphs):
    doc.add_heading("References", level=1)

for n, (_, txt) in enumerate(REFS, 1):
    p = doc.add_paragraph(f"{n}. {txt}")
    for run in p.runs:
        run.font.name = "Book Antiqua"
        run.font.size = Pt(12)
    p.paragraph_format.line_spacing = 1.5
print(f"Appended {len(REFS)} references.")

# ---- 3. Append Footnotes section ----
if not any(p.text.strip() == "Footnotes" and (p.style.name or "").lower().startswith("heading") for p in doc.paragraphs):
    doc.add_heading("Footnotes", level=1)
    statements = [
        "Institutional review board statement: Not applicable. All analyzed datasets were previously collected and de-identified by the original studies under their own institutional review board approvals.",
        "Informed consent statement: Not applicable. Consent procedures are described in the original publications of the source datasets.",
        "Conflict-of-interest statement: The author declares no conflict of interest.",
        "Data sharing statement: All datasets analyzed in this study are publicly available through their original repositories (GEO, MassIVE, Zenodo, PanKbase). Analysis code is available from the corresponding author upon reasonable request.",
        "ARRIVE guidelines statement: Not applicable. No animal experiments were performed.",
        "STROBE statement: Not applicable. No prospective observational cohort was recruited in this study; all human data were obtained from public repositories of previously completed studies.",
        "Open-Access: This article is an open-access article that was selected by an in-house editor and fully peer-reviewed by external reviewers. It is distributed in accordance with the Creative Commons Attribution NonCommercial (CC BY-NC 4.0) license, which permits others to distribute, remix, adapt, build upon this work non-commercially, and license their derivative works on different terms, provided the original work is properly cited and the use is non-commercial. See: https://creativecommons.org/Licenses/by-nc/4.0/",
        "Provenance and peer review: Unsolicited article; Externally peer reviewed.",
        "Peer-review model: Single blind.",
        "Corresponding Author's Membership in Professional Societies: None.",
        "Specialty type: Endocrinology and Metabolism.",
        "Country/Territory of origin: Iran.",
    ]
    for t in statements:
        p = doc.add_paragraph(t)
        for run in p.runs:
            run.font.name = "Book Antiqua"
            run.font.size = Pt(12)
        p.paragraph_format.line_spacing = 1.5
    print("Added Footnotes section.")
else:
    print("Footnotes already present - skipped.")

doc.save(DOCX)
print("Saved:", DOCX)
'''

with open("scripts/56_clean_final.py", "w", encoding="utf-8") as f:
    f.write(new_56)
edits.append("Rewrote 56_clean_final.py (REFS reordered + Footnotes added)")

# ============================================================
# Summary
# ============================================================
print()
print("=" * 60)
print("EDITS APPLIED:")
for e in edits:
    print(f"  - {e}")
print("=" * 60)
print()
print("NEXT STEPS:")
print("  1. In RStudio console:")
print("       setwd('D:/T1D_DarkGenome')")
print("       rmarkdown::render('manuscript.Rmd', output_file='manuscript.docx')")
print("  2. In shell:")
print("       python scripts/56_clean_final.py")
print()