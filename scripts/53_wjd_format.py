# ============================================================
# 53_wjd_format.py
# Post-process manuscript.docx for WJD submission:
#   - Book Antiqua 12pt, 1.5 line spacing (WJD §1 preamble)
#   - Headings forced to black (removes Word default blue)
#   - Placeholder text removed (blue italic "Figure missing...")
#   - Footnotes section appended (WJD §3 ethics statements)
# ============================================================

import re
import sys
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

DOCX = "manuscript.docx"

try:
    doc = Document(DOCX)
except Exception as e:
    sys.exit(f"Cannot open {DOCX}: {e}")

# ------------------------------------------------------------
# 1. Global font + spacing (paragraphs, headings, tables)
# ------------------------------------------------------------
FONT  = "Book Antiqua"
SIZE  = Pt(12)
SPACE = 1.5

def style_paragraph(para):
    para.paragraph_format.line_spacing = SPACE
    for run in para.runs:
        run.font.name = FONT
        run.font.size = SIZE

for para in doc.paragraphs:
    style_paragraph(para)

for table in doc.tables:
    for row in table.rows:
        for cell in row.cells:
            for para in cell.paragraphs:
                style_paragraph(para)

# Also touch the underlying styles so new runs inherit correctly
for style_name in ("Normal", "Body Text", "List Paragraph"):
    try:
        st = doc.styles[style_name]
        st.font.name = FONT
        st.font.size = SIZE
        st.paragraph_format.line_spacing = SPACE
    except KeyError:
        pass

# ------------------------------------------------------------
# 2. Force heading colors to black
#    (Word's Heading 1/2/3 styles apply a dark blue accent)
# ------------------------------------------------------------
BLACK = RGBColor(0, 0, 0)

for style_name in ("Heading 1", "Heading 2", "Heading 3",
                   "Heading 4", "Title", "Subtitle"):
    try:
        st = doc.styles[style_name]
        st.font.color.rgb = BLACK
        st.font.name = FONT
    except KeyError:
        pass

# Also strip any direct blue runs inside headings
def is_blueish(rgb):
    if rgb is None:
        return False
    r, g, b = rgb[0], rgb[1], rgb[2]
    return b > 100 and b > r + 30 and b > g + 20

for para in doc.paragraphs:
    for run in para.runs:
        try:
            c = run.font.color.rgb
            if is_blueish(c):
                run.font.color.rgb = BLACK
        except Exception:
            pass

# ------------------------------------------------------------
# 3. Remove placeholder / markdown artefacts
# ------------------------------------------------------------
# Patterns to delete outright (whole paragraph if it matches)
REMOVE_LINE_PATTERNS = [
    r'^\*\(Figure (file not found|missing).*?\)\*$',   # italic placeholder
    r'^\(Figure (file not found|missing).*?\)$',
    r'^\*\(Table .*? not found.*?\)\*$',
    r'^Figure file not found.*$',
    r'^\s*```\s*$',                                     # stray code fences
    r'^\s*:::\s*$',                                     # stray markdown div markers
    r'^\s*\{#refs\}\s*$',
]

to_delete = []
for i, para in enumerate(doc.paragraphs):
    t = para.text.strip()
    for pat in REMOVE_LINE_PATTERNS:
        if re.search(pat, t):
            to_delete.append(i)
            break

# Delete from the end so indices remain valid
for i in reversed(to_delete):
    p = doc.paragraphs[i]._element
    p.getparent().remove(p)

print(f"Removed {len(to_delete)} placeholder paragraph(s).")

# ------------------------------------------------------------
# 4. Append WJD Footnotes section (WJD §3 ethics statements)
# ------------------------------------------------------------
def add_heading(text, level=1):
    doc.add_heading(text, level=level)

def add_para(text):
    p = doc.add_paragraph(text)
    style_paragraph(p)
    return p

add_heading("Footnotes", level=1)

add_para("Institutional review board statement: Not applicable. The study is entirely computational and uses only publicly available, de-identified human data collected by the original studies under their own institutional review board approvals.")

add_para("Informed consent statement: Not applicable. All analyzed datasets were previously collected and de-identified by the original studies; informed consent procedures are described in the source publications.")

add_para("Conflict-of-interest statement: The author declares no conflict of interest.")

add_para("Data sharing statement: All datasets analyzed in this study are publicly available through their original repositories (GEO, MassIVE, Zenodo, PanKbase). Analysis code is available from the corresponding author upon reasonable request.")

add_para("ARRIVE guidelines statement: Not applicable. No animal experiments were performed.")

add_para("STROBE statement: Not applicable. No observational human cohort was prospectively recruited in this study; all human data were obtained from public repositories of previously completed studies.")

add_para("Open-Access: This article is an open-access article that was selected by an in-house editor and fully peer-reviewed by external reviewers. It is distributed in accordance with the Creative Commons Attribution NonCommercial (CC BY-NC 4.0) license, which permits others to distribute, remix, adapt, build upon this work non-commercially, and license their derivative works on different terms, provided the original work is properly cited and the use is non-commercial. See: https://creativecommons.org/Licenses/by-nc/4.0/")

add_para("Provenance and peer review: Unsolicited article; Externally peer reviewed.")

add_para("Peer-review model: Single blind.")

add_para("Corresponding Author's Membership in Professional Societies: None.")

add_para("Specialty type: Endocrinology and Metabolism.")

add_para("Country/Territory of origin: Iran.")

# ------------------------------------------------------------
# 5. Save
# ------------------------------------------------------------
doc.save(DOCX)
print(f"Saved {DOCX}")
print(f"Applied: font={FONT} {SIZE.pt}pt, line_spacing={SPACE}")
print("Headings set to black, placeholder paragraphs removed, Footnotes appended.")