#!/usr/bin/env python3
"""Render a digest body HTML fragment into a compact PDF (base-14 fonts, no embedding).

The compact build exists because the emailed attachment travels as inline base64
through the Gmail connector, so smaller is safer. Usage:

    python3 build_compact_pdf.py body.html "Title line" output.pdf
"""
import re
import sys
from html import unescape

from reportlab import rl_config
rl_config.useA85 = 0  # raw Flate streams; ~25% smaller output, safer to email

from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate, Frame, HRFlowable, ListFlowable, ListItem,
    PageTemplate, Paragraph, Spacer,
)

ACCENT = "#7a2518"
INK = "#1c1c1e"

STYLES = {
    "kicker": ParagraphStyle("kicker", fontName="Helvetica", fontSize=7.5,
                             textColor="#8e6a1f", spaceAfter=10, leading=10),
    "h1": ParagraphStyle("h1", fontName="Times-Bold", fontSize=22, leading=26,
                         textColor=INK, spaceAfter=12),
    "h2": ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=13, leading=16,
                         textColor=INK, spaceBefore=16, spaceAfter=6),
    "h3": ParagraphStyle("h3", fontName="Helvetica-Bold", fontSize=11, leading=14,
                         textColor=INK, spaceBefore=10, spaceAfter=4),
    "body": ParagraphStyle("body", fontName="Times-Roman", fontSize=11, leading=15.5,
                           textColor=INK, spaceAfter=7, alignment=TA_JUSTIFY),
    "li": ParagraphStyle("li", fontName="Times-Roman", fontSize=11, leading=15,
                         textColor=INK, spaceAfter=3),
    "source": ParagraphStyle("source", fontName="Times-Roman", fontSize=9.5, leading=13,
                             textColor=INK, spaceAfter=3),
}


def inline(html):
    """Convert the fragment's inline tags to reportlab Paragraph markup."""
    s = html
    s = re.sub(r"<strong>(.*?)</strong>", rf'<b><font color="{ACCENT}">\1</font></b>', s, flags=re.S)
    s = re.sub(r'<a href="([^"]+)"[^>]*>(.*?)</a>', r'<a href="\1" color="#234e70"><u>\2</u></a>', s, flags=re.S)
    s = re.sub(r"</?(em|i)>", lambda m: "<i>" if not m.group(0).startswith("</") else "</i>", s)
    s = re.sub(r"<(?!/?(b|i|u|a|font)\b)[^>]+>", " ", s)  # strip anything else
    return re.sub(r"\s+", " ", s).strip()


def blocks(html):
    for m in re.finditer(r"<(h1|h2|h3|p|ul|ol)>(.*?)</\1>", html, flags=re.S):
        yield m.group(1), m.group(2)


def build(body_path, title, out_path):
    html = open(body_path, encoding="utf-8").read()
    story = [Paragraph("PERSONAL BRIEFING &nbsp;&middot;&nbsp; PREPARED FOR DAVID", STYLES["kicker"]),
             HRFlowable(width="100%", thickness=1.5, color=INK, spaceAfter=10)]
    in_sources = False
    for tag, content in blocks(html):
        if tag in ("h1", "h2", "h3"):
            text = inline(content)
            if tag == "h2":
                story.append(HRFlowable(width="100%", thickness=0.5, color="#d8d3c8",
                                        spaceBefore=10, spaceAfter=0))
            story.append(Paragraph(text, STYLES[tag]))
            if "Sources" in unescape(text) and tag == "h2":
                in_sources = True
        elif tag == "p":
            story.append(Paragraph(inline(content), STYLES["body"]))
        elif tag in ("ul", "ol"):
            style = STYLES["source"] if in_sources else STYLES["li"]
            items = []
            for li in re.finditer(r"<li>(.*?)</li>", content, flags=re.S):
                items.append(ListItem(Paragraph(inline(li.group(1)), style), leftIndent=14))
            story.append(ListFlowable(items, bulletType="1" if tag == "ol" else "bullet",
                                      bulletFontName="Times-Roman", bulletFontSize=9,
                                      leftIndent=14, spaceBefore=2, spaceAfter=7))

    def page_number(canvas, doc):
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor("#6e6e73")
        canvas.drawCentredString(letter[0] / 2, 0.45 * inch, str(canvas.getPageNumber()))

    doc = BaseDocTemplate(out_path, pagesize=letter, title=title,
                          leftMargin=0.85 * inch, rightMargin=0.85 * inch,
                          topMargin=0.8 * inch, bottomMargin=0.8 * inch)
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="main")
    doc.addPageTemplates([PageTemplate(id="page", frames=[frame], onPage=page_number)])
    doc.build(story)


if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2], sys.argv[3])
    print(f"Wrote {sys.argv[3]}")
