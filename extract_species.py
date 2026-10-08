#!/usr/bin/env python3
"""
extract_species.py
------------------
Reads a .docx file and extracts bird species entries.

A paragraph is treated as a species heading if it contains:
  - At least one Arial bold run at 16 pt OR 18 pt  (the English name)
  - AND at least one Arial italic run at 14 pt      (the Latin name)

Only the text of the large bold run(s) is used as the species name.

The paragraph immediately following the heading is captured as the
species description if its first non-empty run is Arial 12 pt italic.

Outputs a two-column CSV: species_name, species_text

Usage:
    python extract_species.py <input.docx> [output.csv]
"""

import sys
import csv
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

# ---------------------------------------------------------------------------
# OOXML helpers
# ---------------------------------------------------------------------------
W = lambda local: f"{{http://schemas.openxmlformats.org/wordprocessingml/2006/main}}{local}"

ARIAL_VARIANTS = {"arial", "ariel", "arial narrow", "arial unicode ms"}  # 'ariel' is a typo present in some entries

def _font(rpr):
    rf = rpr.find(W("rFonts")) if rpr is not None else None
    if rf is None:
        return None
    return rf.get(W("ascii")) or rf.get(W("hAnsi")) or rf.get(W("cs"))

def _size_pt(rpr):
    sz = rpr.find(W("sz")) if rpr is not None else None
    if sz is None:
        return None
    try:
        return float(sz.get(W("val"), 0)) / 2.0
    except (TypeError, ValueError):
        return None

def _is_on(rpr, tag):
    """True if toggle element <w:tag> is present and not explicitly off."""
    el = rpr.find(W(tag)) if rpr is not None else None
    if el is None:
        return False
    return el.get(W("val"), "true").lower() not in ("0", "false")

def _is_arial(font):
    return font is not None and font.strip().lower() in ARIAL_VARIANTS

def _run_text(run_el):
    return "".join(t.text or "" for t in run_el.findall(W("t")))

def _style_rpr(styles_root, style_id):
    if styles_root is None or not style_id:
        return None
    for s in styles_root.findall(W("style")):
        if s.get(W("styleId")) == style_id:
            return s.find(W("rPr"))
    return None

def _para_style_id(para_el):
    ppr = para_el.find(W("pPr"))
    if ppr is None:
        return None
    ps = ppr.find(W("pStyle"))
    return ps.get(W("val")) if ps is not None else None

def _effective_rpr(run_el, style_rpr):
    """Merge run-level rPr with style rPr, run takes precedence."""
    run_rpr = run_el.find(W("rPr"))

    def pick(fn):
        v = fn(run_rpr)
        if v is not None:
            return v
        return fn(style_rpr)

    font   = _font(run_rpr) or _font(style_rpr)
    size   = _size_pt(run_rpr) if _size_pt(run_rpr) is not None else _size_pt(style_rpr)
    italic = _is_on(run_rpr, "i") or _is_on(style_rpr, "i")
    bold   = _is_on(run_rpr, "b") or _is_on(style_rpr, "b")
    return font, size, italic, bold

# ---------------------------------------------------------------------------
# Paragraph analysis
# ---------------------------------------------------------------------------

# Sizes accepted as "large heading" for the English species name
HEADING_SIZES = {16.0, 18.0}
# Tolerance for floating-point half-point rounding
TOL = 0.6

def _analyse_para(para_el, styles_root):
    """
    Returns dict:
      heading_text  – text from large-bold Arial runs (non-empty → heading)
      desc_text     – full paragraph text
      is_desc       – True if first substantive run is Arial 12pt italic
    """
    style_rpr = _style_rpr(styles_root, _para_style_id(para_el))
    runs = para_el.findall(W("r"))

    heading_parts = []
    has_large_bold_arial  = False
    has_latin_italic_arial = False
    full_parts = []
    first_run_checked = False
    is_desc = False

    for run in runs:
        txt  = _run_text(run)
        full_parts.append(txt)
        font, size, italic, bold = _effective_rpr(run, style_rpr)

        if not txt.strip():
            continue

        # Description: first non-empty run is Arial 12pt italic
        if not first_run_checked:
            first_run_checked = True
            if _is_arial(font) and size is not None and abs(size - 12.0) < TOL and italic:
                is_desc = True

        # Heading signals
        if _is_arial(font) and size is not None:
            if any(abs(size - s) < TOL for s in HEADING_SIZES) and bold:
                has_large_bold_arial = True
                heading_parts.append(txt)
            if abs(size - 14.0) < TOL and italic:
                has_latin_italic_arial = True

    # A species heading must have BOTH signals
    heading_text = ""
    if has_large_bold_arial and has_latin_italic_arial:
        heading_text = "".join(heading_parts).strip()

    return {
        "heading_text": heading_text,
        "desc_text":    "".join(full_parts).strip(),
        "is_desc":      is_desc,
    }

# ---------------------------------------------------------------------------
# Extraction
# ---------------------------------------------------------------------------

def extract(docx_path):
    with zipfile.ZipFile(docx_path) as z:
        names = z.namelist()
        doc_xml    = z.read("word/document.xml")
        styles_xml = z.read("word/styles.xml") if "word/styles.xml" in names else None

    doc_root    = ET.fromstring(doc_xml)
    styles_root = ET.fromstring(styles_xml) if styles_xml else None
    body        = doc_root.find(W("body"))
    paras       = [el for el in body if el.tag == W("p")]

    analysed = [_analyse_para(p, styles_root) for p in paras]

    results = []
    i = 0
    while i < len(analysed):
        a = analysed[i]
        if a["heading_text"]:
            species_name = a["heading_text"]
            if i + 1 < len(analysed) and analysed[i + 1]["is_desc"]:
                species_text = analysed[i + 1]["desc_text"]
                i += 2
            else:
                species_text = ""
                i += 1
            results.append((species_name, species_text))
        else:
            i += 1

    return results

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    docx_path = Path(sys.argv[1])
    if not docx_path.exists():
        print(f"Error: file not found: {docx_path}", file=sys.stderr)
        sys.exit(1)

    csv_path = Path(sys.argv[2]) if len(sys.argv) >= 3 else \
               docx_path.with_name(docx_path.stem + "_species.csv")

    print(f"Reading:  {docx_path}")
    rows = extract(docx_path)

    if not rows:
        print("No species headings found.")
        print("Each heading must have: Arial 16pt or 18pt bold (English name)")
        print("                    AND Arial 14pt italic (Latin name) in the same paragraph.")
        sys.exit(0)

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow(["species_name", "species_text"])
        writer.writerows(rows)

    print(f"Written:  {csv_path}")
    print(f"Rows:     {len(rows)}")
    for name, text in rows:
        preview = text[:70] + "…" if len(text) > 70 else text
        print(f"  • {name!r:40s}  → {preview!r}")

if __name__ == "__main__":
    main()
