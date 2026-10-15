# scripts/60_fix_table4.py
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

DOCX = "manuscript.docx"
doc = Document(DOCX)

# ---------- helper: set cell text preserving book antiqua ----------
def set_cell_text(cell, text, size=10, bold=False, align='left'):
    # clear existing paragraphs
    for p in list(cell.paragraphs):
        p._element.getparent().remove(p._element)
    p = cell.add_paragraph()
    r = p.add_run(text)
    r.font.name = "Book Antiqua"
    r.font.size = Pt(size)
    r.bold = bold
    p.paragraph_format.line_spacing = 1.0
    if align == 'center':
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    elif align == 'right':
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    return p

def set_col_width(cell, width_in):
    cell.width = Inches(width_in)
    # also set tcW so Word respects it
    tcPr = cell._tc.get_or_add_tcPr()
    tcW = tcPr.find(qn('w:tcW'))
    if tcW is None:
        tcW = OxmlElement('w:tcW')
        tcPr.append(tcW)
    tcW.set(qn('w:w'), str(int(width_in * 1440)))  # twips
    tcW.set(qn('w:type'), 'dxa')

# ---------- find Table 4 ----------
# Tables 1..5 in order; Table 4 is index 3
if len(doc.tables) < 4:
    raise SystemExit("Table 4 not found")

t4 = doc.tables[3]

# ---------- 1. Rewrite header row with short names ----------
SHORT_HEADERS = [
    "Peptide",
    "Best allele",
    "Best\n%Rank",
    "Binding core",
    "DRB1*03:01",
    "DRB1*04:01",
    "DQ2.5",
    "DQ8",
]

# Clear header row cell by cell and reset
hdr = t4.rows[0]
for i, cell in enumerate(hdr.cells):
    if i < len(SHORT_HEADERS):
        set_cell_text(cell, SHORT_HEADERS[i], size=10, bold=True, align='center')

# ---------- 2. Set column widths (total ~6.5 in for WJD page) ----------
COL_WIDTHS = [1.45, 0.85, 0.55, 0.85, 0.65, 0.65, 0.5, 0.5]  # inches
for row in t4.rows:
    for i, cell in enumerate(row.cells):
        if i < len(COL_WIDTHS):
            set_col_width(cell, COL_WIDTHS[i])

# ---------- 3. Data row alignment ----------
for row in t4.rows[1:]:
    cells = row.cells
    if len(cells) >= 8:
        set_cell_text(cells[0], cells[0].text.strip(), size=9, align='left')      # Peptide
        set_cell_text(cells[1], cells[1].text.strip(), size=9, align='center')    # Best allele
        set_cell_text(cells[2], cells[2].text.strip(), size=9, align='center')    # Best %Rank
        set_cell_text(cells[3], cells[3].text.strip(), size=9, align='center')    # Core
        set_cell_text(cells[4], cells[4].text.strip(), size=9, align='center')
        set_cell_text(cells[5], cells[5].text.strip(), size=9, align='center')
        set_cell_text(cells[6], cells[6].text.strip(), size=9, align='center')
        set_cell_text(cells[7], cells[7].text.strip(), size=9, align='center')

# ---------- 4. Prevent row from auto-shrinking header ----------
def set_row_height(row, inches, rule='atLeast'):
    trPr = row._tr.get_or_add_trPr()
    trHeight = OxmlElement('w:trHeight')
    trHeight.set(qn('w:val'), str(int(inches * 1440)))
    trHeight.set(qn('w:hRule'), rule)
    trPr.append(trHeight)

set_row_height(t4.rows[0], 0.5, rule='atLeast')

doc.save(DOCX)
print("Table 4 headers shortened, columns widened, cell alignment set.")