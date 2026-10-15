# scripts/59_force_font_spacing.py
# Force Book Antiqua 12pt + 1.5 line spacing across the entire docx,
# including paragraphs, runs, tables, headers, footers, and styles.

from docx import Document
from docx.shared import Pt
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

DOCX = "manuscript.docx"
doc = Document(DOCX)

FONT = "Book Antiqua"
SIZE = Pt(12)
SPACING = 1.5

def force_run(run):
    run.font.name = FONT
    run.font.size = SIZE
    # Also set east-asian / complex-script fonts so Word doesn't substitute
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = OxmlElement('w:rFonts')
        rPr.append(rFonts)
    rFonts.set(qn('w:ascii'), FONT)
    rFonts.set(qn('w:hAnsi'), FONT)
    rFonts.set(qn('w:cs'), FONT)
    rFonts.set(qn('w:eastAsia'), FONT)

def force_paragraph(para):
    para.paragraph_format.line_spacing = SPACING
    for run in para.runs:
        force_run(run)

# 1. All body paragraphs
for para in doc.paragraphs:
    force_paragraph(para)

# 2. All table cells (including nested — one level of recursion)
def process_table(tbl):
    for row in tbl.rows:
        for cell in row.cells:
            for para in cell.paragraphs:
                force_paragraph(para)
            for nested in cell.tables:
                process_table(nested)

for tbl in doc.tables:
    process_table(tbl)

# 3. Headers and footers
for section in doc.sections:
    for container in (section.header, section.footer,
                      section.first_page_header, section.first_page_footer,
                      section.even_page_header, section.even_page_footer):
        try:
            for para in container.paragraphs:
                force_paragraph(para)
            for tbl in container.tables:
                process_table(tbl)
        except Exception:
            pass

# 4. Update the underlying styles too, so new runs inherit correctly
style_targets = ("Normal", "Body Text", "List Paragraph", "First Paragraph",
                 "Table Grid", "Image Caption", "Caption", "No Spacing")
for sname in style_targets:
    try:
        st = doc.styles[sname]
        st.font.name = FONT
        st.font.size = SIZE
        st.paragraph_format.line_spacing = SPACING
    except KeyError:
        pass

# Headings keep their style but get the font + spacing
for sname in ("Heading 1", "Heading 2", "Heading 3", "Heading 4", "Title", "Subtitle"):
    try:
        st = doc.styles[sname]
        st.font.name = FONT
        st.paragraph_format.line_spacing = SPACING
    except KeyError:
        pass

doc.save(DOCX)

# Report
total_paras = len(doc.paragraphs)
total_table_paras = sum(
    len(c.paragraphs) for t in doc.tables for r in t.rows for c in r.cells
)
print(f"Applied {FONT} {SIZE.pt}pt, spacing {SPACING} to:")
print(f"  - {total_paras} body paragraphs")
print(f"  - {total_table_paras} table cell paragraphs")
print(f"  - {len(doc.tables)} tables")
print(f"  - headers and footers")
print(f"  - styles: Normal, Body Text, Table Grid, Image Caption, headings")
print(f"Saved {DOCX}")