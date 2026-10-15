from docx import Document
from docx.shared import Pt
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

DOCX = "manuscript.docx"
doc = Document(DOCX)

REFS = [
    "Chiou J, Geusz RJ, Okino ML, et al. A multi-ethnic genome-wide association study identifies novel loci for type 1 diabetes. Nat Commun 2021;12:4697 [PMID: 34373454 DOI: 10.1038/s41467-021-24970-4]",
    "Robertson CC, Inshaw JRJ, Chim K, et al. Fine-mapping, trans-ancestral and genomic analyses identify causal variants, cells, genes and drug targets for type 1 diabetes. Nat Genet 2021;53:962-971 [PMID: 34045743 DOI: 10.1038/s41588-021-00880-5]",
    "Olsson LM, Lindqvist AK, Kallberg H, et al. A case-control study of rheumatoid arthritis identifies an eQTL for TNFAIP3 at the 6q23 risk locus. Arthritis Rheum 2015 [PMID: 25707945]",
    "Martin P, McGovern A, Orozco G, et al. Capture Hi-C identifies a novel causal gene, IL20RA, in the pan-autoimmune genetic susceptibility region 6q23. Genome Biol 2016;17:212 [PMID: 27724958 DOI: 10.1186/s13059-016-1078-x]",
    "Cynn E, et al. Human macrophage long intergenic non-coding RNA, SIMALR, suppresses inflammatory macrophage apoptosis via Netrin 1. Arterioscler Thromb Vasc Biol 2023 [PMID: 36799758]",
    "Nanaware PP, et al. MHC class I and II immunopeptidomics of human pancreatic islets. Cell Rep 2025 [PMID: 40737125]",
    "GTEx Consortium. The GTEx Consortium atlas of genetic regulatory effects across human tissues. Science 2020;369:1318-1330 [PMID: 32913098 DOI: 10.1126/science.aaz1776]",
    "Vita R, Mahajan S, Overton JA, et al. The Immune Epitope Database (IEDB) 2018 update. Nucleic Acids Res 2019;47:D339-D343 [PMID: 30357371 DOI: 10.1093/nar/gky1006]",
    "Bastian F, Parmentier G, Roux J, et al. The Bgee suite for retrieval and comparison of gene expression patterns across multiple animal species. Bioinformatics 2016;32:3399-3401 [PMID: 27378296 DOI: 10.1093/bioinformatics/btw372]",
    "Miguel-Escalada I, Bonas-Guarch S, Cebola I, et al. Human pancreatic islet three-dimensional chromatin architecture provides insights into the genetics of type 2 diabetes. Nat Genet 2019;51:1137-1148 [PMID: 31253979 DOI: 10.1038/s41588-019-0457-0]",
    "Love MI, Huber W, Anders S. Moderated estimation of fold change and dispersion for RNA-seq data with DESeq2. Genome Biol 2014;15:550 [PMID: 25516281 DOI: 10.1186/s13059-014-0550-8]",
    "Pages H, Aboyoun P, Gentleman R, DebRoy S. Biostrings: Efficient manipulation of biological strings. R package, 2020",
    "Gfeller D, Guillaume P, Michaux J, et al. Improved predictions of MHC class II antigen presentation. bioRxiv 2019 [DOI: 10.1101/589838]",
    "Andreatta M, Karosiene E, Rasmussen M, et al. Accurate pan-specific prediction of peptide-MHC class II binding affinity with improved binding core identification. Immunogenetics 2016;68:871-880 [PMID: 27575705 DOI: 10.1007/s00251-016-0945-7]",
    "Hao Y, Hao S, Andersen-Nissen E, et al. Integrated analysis of multimodal single-cell data. Cell 2021;184:3573-3587 [PMID: 34062119 DOI: 10.1016/j.cell.2021.04.048]",
    "Stuart T, Butler A, Hoffman P, et al. Comprehensive integration of single-cell data. Cell 2019;177:1888-1902 [PMID: 31178118 DOI: 10.1016/j.cell.2019.05.031]",
    "Xu Y, et al. LINC02528/SIMALR is a blood biomarker and functional regulator of macrophage responses in tuberculosis. PLoS Pathog 2025 [PMID: 41308682]",
]

FOOTNOTES = [
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

def add_heading(text):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.bold = True
    r.font.name = "Book Antiqua"
    r.font.size = Pt(14)
    p.paragraph_format.line_spacing = 1.5
    return p

def add_body(text):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.font.name = "Book Antiqua"
    r.font.size = Pt(12)
    p.paragraph_format.line_spacing = 1.5
    return p

# Remove any partial remnants of these sections
for para in list(doc.paragraphs):
    t = para.text.strip()
    if t in ("References", "Footnotes"):
        para._element.getparent().remove(para._element)
    elif (t.startswith("1. Chiou") or
          t.startswith("Institutional review board statement")):
        para._element.getparent().remove(para._element)

# Re-add
add_heading("References")
for n, ref in enumerate(REFS, 1):
    add_body(f"{n}. {ref}")

add_heading("Footnotes")
for f in FOOTNOTES:
    add_body(f)

doc.save(DOCX)
print(f"Re-added {len(REFS)} references and {len(FOOTNOTES)} footnotes.")
