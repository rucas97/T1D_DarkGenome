# scripts/58_wjd_final_polish.py
# WJD submission final polish — all fixes in one pass.
#
# 1.  Greek letters (beta -> β, gamma -> γ, alpha -> α)
# 2.  HLA allele notation (DRB103:01 -> DRB1*03:01, etc.)
# 3.  Scientific notation (2.9e-45 -> 2.9 × 10⁻⁴⁵)
# 4.  Biostatistics statement into Methods
# 5.  Table 3 caption + header clarification
# 6.  Olsson reference [3] full citation
# 7.  Table formatting (bold header, horizontal rules only)
# 8.  Figure Legends section (extracted before References)
#
# Run:  python scripts/58_wjd_final_polish.py

import re
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

DOCX = "manuscript.docx"
doc = Document(DOCX)

# ============================================================
# helpers
# ============================================================
def replace_in_paragraph(para, replacements):
    """Replace across run boundaries by concatenating text, applying
    replacements, and writing back to the first run."""
    if not para.runs:
        return False
    full = "".join(r.text for r in para.runs)
    new = full
    for pat, repl in replacements:
        new = re.sub(pat, repl, new)
    if new == full:
        return False
    # put everything into first run, clear the rest
    para.runs[0].text = new
    for r in para.runs[1:]:
        r.text = ""
    return True

def set_cell_border(cell, **kwargs):
    """Set cell borders. Pass top=dict(sz=.., val='single'), etc."""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcBorders = tcPr.find(qn('w:tcBorders'))
    if tcBorders is None:
        tcBorders = OxmlElement('w:tcBorders')
        tcPr.append(tcBorders)
    for edge in ('top', 'left', 'bottom', 'right'):
        if edge in kwargs:
            tag = 'w:{}'.format(edge)
            element = tcBorders.find(qn(tag))
            if element is None:
                element = OxmlElement(tag)
                tcBorders.append(element)
            for key, val in kwargs[edge].items():
                element.set(qn('w:{}'.format(key)), str(val))

# ============================================================
# 1–3. Text replacements across the whole document
# ============================================================
REPLACEMENTS = [
    # --- Greek letters ---
    (r'\bbeta-cells\b', 'β-cells'),
    (r'\bbeta-cell\b',  'β-cell'),
    (r'\bbeta cell\b',  'β cell'),
    (r'\bIFN-gamma\b',  'IFN-γ'),
    (r'\bTNF-alpha\b',  'TNF-α'),
    (r'\bIL-1beta\b',   'IL-1β'),
    (r'\bIFNg\b',       'IFN-γ'),
    (r'\bTNFa\b',       'TNF-α'),
    (r'\bIL-1b\b',      'IL-1β'),

    # --- HLA allele notation ---
    (r'DRB103:01', 'DRB1*03:01'),
    (r'DRB104:01', 'DRB1*04:01'),
    (r'DRB1_03_01', 'DRB1*03:01'),
    (r'DRB1_04_01', 'DRB1*04:01'),
    (r'DQA105:01/DQB102:01', 'DQA1*05:01/DQB1*02:01'),
    (r'DQA103:01/DQB103:02', 'DQA1*03:01/DQB1*03:02'),
    (r'DQA1_05_01__DQB1_02_01', 'DQA1*05:01/DQB1*02:01'),
    (r'DQA1_03_01__DQB1_03_02', 'DQA1*03:01/DQB1*03:02'),

    # --- Scientific notation ---
    (r'2\.9e-45',  '2.9 × 10⁻⁴⁵'),
    (r'4\.6e-06',  '4.6 × 10⁻⁶'),
    (r'1\.4e-65',  '1.4 × 10⁻⁶⁵'),
    (r'9\.2e-47',  '9.2 × 10⁻⁴⁷'),
    (r'4\.9e-59',  '4.9 × 10⁻⁵⁹'),
    (r'\bminus\s+0\.(\d+)', r'−0.\1'),
]

n_para_changed = 0
for para in doc.paragraphs:
    if replace_in_paragraph(para, REPLACEMENTS):
        n_para_changed += 1

n_cell_changed = 0
for table in doc.tables:
    for row in table.rows:
        for cell in row.cells:
            for para in cell.paragraphs:
                if replace_in_paragraph(para, REPLACEMENTS):
                    n_cell_changed += 1

print(f"Text replaced in {n_para_changed} paragraphs, {n_cell_changed} table cells.")

# ============================================================
# 4. Biostatistics statement into Methods
# ============================================================
BIO_STAT = (
    "The statistical methods of this study were reviewed by "
    "[NAME], [QUALIFICATION], from [ORGANIZATION]. "
    "All statistical analyses followed standard non-parametric "
    "procedures (Wilcoxon rank-sum, Kruskal-Wallis, Fisher exact), "
    "with Benjamini-Hochberg correction for multiple testing."
)

methods_para_idx = None
for i, para in enumerate(doc.paragraphs):
    if para.text.strip().startswith("Unless otherwise noted, tests are non-parametric"):
        methods_para_idx = i
        break

if methods_para_idx is not None:
    # Insert new paragraph after the statistical framework paragraph
    target = doc.paragraphs[methods_para_idx]
    new_p = OxmlElement('w:p')
    target._element.addnext(new_p)
    from docx.text.paragraph import Paragraph
    new_para = Paragraph(new_p, target._parent)
    run = new_para.add_run(BIO_STAT)
    run.font.name = "Book Antiqua"
    run.font.size = Pt(12)
    new_para.paragraph_format.line_spacing = 1.5
    print("Added biostatistics statement placeholder to Methods.")
else:
    print("WARN: statistical framework paragraph not found; biostatistics statement skipped.")

# ============================================================
# 5. Table 3 caption + header cleanup
# ============================================================
for para in doc.paragraphs:
    t = para.text.strip()
    if t.startswith("Table 3 Per-donor SIMALR induction"):
        replace_in_paragraph(para, [
            (r"^Table 3 Per-donor SIMALR induction in cytokine-treated primary human islets.*$",
             "Table 3 Per-donor SIMALR induction in cytokine-treated primary human islets. "
             "control and treated columns report DESeq2-normalized counts. log2FC computed with a "
             "pseudocount of 1 read added to both conditions for donors where control = 0. "
             "n = 19 paired donors, mean +5.06 log2FC, range 3.36 to 6.50."),
        ])

# Fix Table 3 header row: "donor" -> "Donor ID"
if len(doc.tables) >= 3:
    t3 = doc.tables[2]
    if t3.rows and t3.rows[0].cells:
        h0 = t3.rows[0].cells[0].paragraphs[0]
        if h0.text.strip().lower() in ("donor", "donor id"):
            for r in h0.runs:
                r.text = ""
            if h0.runs:
                h0.runs[0].text = "Donor ID"
            else:
                h0.add_run("Donor ID")
            print("Table 3 header renamed to 'Donor ID'.")

# ============================================================
# 6. Olsson reference [3] full citation
# ============================================================
OLSSON_FULL = (
    "3. Olsson LM, Lindqvist AK, Källberg H, et al. A case-control study "
    "of rheumatoid arthritis identifies an eQTL for TNFAIP3 at the 6q23 "
    "risk locus. Arthritis Rheum 2015 [PMID: 25707945]"
)
for para in doc.paragraphs:
    t = para.text.strip()
    if t.startswith("3. Olsson"):
        for r in para.runs:
            r.text = ""
        if para.runs:
            para.runs[0].text = OLSSON_FULL
        else:
            para.add_run(OLSSON_FULL)
        print("Olsson reference [3] expanded.")
        break

# ============================================================
# 7. Table formatting (bold header, horizontal rules only)
# ============================================================
def style_table(tbl):
    # Remove existing borders on all cells, then draw only top/bottom/header
    for r_idx, row in enumerate(tbl.rows):
        for cell in row.cells:
            set_cell_border(cell,
                top={"val": "single", "sz": 8, "color": "000000"},
                bottom={"val": "single", "sz": 8, "color": "000000"},
                left={"val": "nil"},
                right={"val": "nil"},
            )

    # Bold header row
    if tbl.rows:
        for cell in tbl.rows[0].cells:
            for para in cell.paragraphs:
                for run in para.runs:
                    run.bold = True
                    run.font.name = "Book Antiqua"
                    run.font.size = Pt(11)
                para.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Body cells in Book Antiqua 10pt
    for row in tbl.rows[1:]:
        for cell in row.cells:
            for para in cell.paragraphs:
                for run in para.runs:
                    run.font.name = "Book Antiqua"
                    run.font.size = Pt(10)
                para.paragraph_format.line_spacing = 1.0

n_tbl_styled = 0
for tbl in doc.tables:
    style_table(tbl)
    n_tbl_styled += 1
print(f"Styled {n_tbl_styled} table(s).")

# ============================================================
# 8. Move figure legends to a "Figure Legends" section
# ============================================================
# Collect all paragraphs styled "Image Caption"
legend_paras = [p for p in doc.paragraphs if (p.style.name or "") == "Image Caption"]

if legend_paras:
    # Grab text before deletion
    legend_texts = [p.text for p in legend_paras]

    # Delete them from current location
    for p in legend_paras:
        p._element.getparent().remove(p._element)

    # Find the References heading and insert Figure Legends before it
    refs_idx = None
    for i, para in enumerate(doc.paragraphs):
        if para.text.strip() == "References" and (para.style.name or "").lower().startswith("heading"):
            refs_idx = i
            break

    if refs_idx is not None:
        # Insert heading + legend paragraphs before References
        refs_para = doc.paragraphs[refs_idx]
        # Build in reverse so ordering is preserved when inserting before
        new_elements = []
        for txt in legend_texts:
            new_p = OxmlElement('w:p')
            new_elements.append((new_p, txt, False))  # False = normal
        # heading paragraph
        heading_p = OxmlElement('w:p')
        new_elements.insert(0, (heading_p, "Figure Legends", True))

        for elem, txt, is_heading in new_elements:
            refs_para._element.addprevious(elem)
            from docx.text.paragraph import Paragraph
            np = Paragraph(elem, refs_para._parent)
            if is_heading:
                # style as Heading 1
                try:
                    np.style = doc.styles['Heading 1']
                except KeyError:
                    pass
            else:
                r = np.add_run(txt)
                r.font.name = "Book Antiqua"
                r.font.size = Pt(12)
                np.paragraph_format.line_spacing = 1.5
        print(f"Moved {len(legend_texts)} figure legend(s) to a new 'Figure Legends' section.")
    else:
        print("WARN: References heading not found; could not relocate legends.")
else:
    print("No 'Image Caption' paragraphs found; figure legends not moved.")

# ============================================================
# 9. Force all headings to black + Book Antiqua (belt and braces)
# ============================================================
for para in doc.paragraphs:
    st = (para.style.name or "").lower()
    if st.startswith("heading") or st in ("title", "subtitle"):
        for run in para.runs:
            run.font.color.rgb = RGBColor(0, 0, 0)
            run.font.name = "Book Antiqua"

# ============================================================
# Save
# ============================================================
doc.save(DOCX)
print()
print("=" * 60)
print(f"Saved {DOCX}")
print("=" * 60)
print()
print("MANUAL STEP REMAINING:")
print("  - Open manuscript.docx in Word")
print("  - Find [NAME], [QUALIFICATION], [ORGANIZATION] in Methods")
print("  - Replace with your biostatistics reviewer's info,")
print("    or delete the entire sentence if none available")
print()