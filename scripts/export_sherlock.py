#!/usr/bin/env python3
"""
Sherlock Export Engine
Generates:
1. <topic>.xlsx - Tabular data point matrix with custom styling and formatting
2. <topic>.csv  - Machine-readable data point records
3. <topic>.docx - Clean, direct, fluff-free narrative dossier with bolded numbers & bullet points
"""

import os
import sys
import json
import glob
import re
import argparse
from pathlib import Path
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

REQUIRED_COLUMNS = [
    "sr no",
    "data point",
    "exact url/subpage",
    "quoted text from page",
    "a search query with that data point",
    "grep from running his search query",
    "confidence score based on rechecking",
    "triangulation status",
]


def load_all_data_points(results_dir):
    """Loads and standardizes data points from all chunk JSON files."""
    json_files = sorted(glob.glob(os.path.join(results_dir, "*.json")))
    all_dps = []
    chunk_summaries = []
    current_sr = 1

    for jf in json_files:
        try:
            with open(jf, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"[WARN] Failed to read {jf}: {e}", file=sys.stderr)
            continue

        chunk_title = data.get("chunk_title", Path(jf).stem.replace("_", " ").title())
        sections = data.get("sections", [])
        
        # Also handle flat data_points list if present
        raw_dps = data.get("data_points", [])
        if raw_dps and not sections:
            sections = [{"title": chunk_title, "bullets": [], "data_points": raw_dps}]

        for sec in sections:
            sec_title = sec.get("title", chunk_title)
            bullets = sec.get("bullets", [])
            sec_dps = sec.get("data_points", [])

            processed_sec_dps = []
            for dp in sec_dps:
                conf = dp.get("confidence_score") or dp.get("confidence_score_based_on_rechecking") or "Highest"
                triangulated = dp.get("triangulation_status") or dp.get("flag_as_triangulated") or (
                    "Flag as Triangulated" if str(conf).strip().lower() in ("highest", "high") else "Undeclared"
                )
                std_dp = {
                    "sr no": current_sr,
                    "data point": dp.get("data_point") or dp.get("datapoint") or "",
                    "exact url/subpage": dp.get("exact_url") or dp.get("exact_url/subpage") or dp.get("url") or "",
                    "quoted text from page": dp.get("quoted_text") or dp.get("quoted_text_from_page") or "",
                    "a search query with that data point": dp.get("verification_query") or dp.get("a_search_query_with_that_data_point") or "",
                    "grep from running his search query": dp.get("grep_result") or dp.get("grep_from_running_his_search_query") or "",
                    "confidence score based on rechecking": conf,
                    "triangulation status": triangulated,
                    "section": sec_title,
                    "chunk": chunk_title,
                }
                all_dps.append(std_dp)
                processed_sec_dps.append(std_dp)
                current_sr += 1

            chunk_summaries.append({
                "chunk": chunk_title,
                "section": sec_title,
                "bullets": bullets,
                "data_points": processed_sec_dps,
            })

    return all_dps, chunk_summaries


def export_tabular(data_points, output_base):
    """Exports data points to XLSX and CSV with styling."""
    if not data_points:
        print("[WARN] No data points to export to tabular formats.", file=sys.stderr)
        return None, None

    df = pd.DataFrame(data_points)
    # Ensure exact required columns in correct order
    tabular_df = df[REQUIRED_COLUMNS]

    # 1. Export CSV
    csv_path = f"{output_base}.csv"
    tabular_df.to_csv(csv_path, index=False, encoding="utf-8")
    print(f"[OK] CSV exported: {csv_path}")

    # 2. Export Styled XLSX
    xlsx_path = f"{output_base}.xlsx"
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Verified Data Points"
    ws.views.sheetView[0].showGridLines = True

    # Headers
    headers = REQUIRED_COLUMNS
    ws.append(headers)

    header_font = Font(name="Segoe UI", size=10, bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="1A365D", end_color="1A365D", fill_type="solid") # Deep navy
    thin_border = Border(
        left=Side(style='thin', color='D0D5DD'),
        right=Side(style='thin', color='D0D5DD'),
        top=Side(style='thin', color='D0D5DD'),
        bottom=Side(style='thin', color='D0D5DD')
    )

    for col_idx, col_name in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_idx)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = thin_border

    ws.row_dimensions[1].height = 28

    # Data Rows
    body_font = Font(name="Segoe UI", size=9, color="1F2937")
    mono_font = Font(name="Consolas", size=8.5, color="374151")
    high_conf_fill = PatternFill(start_color="ECFDF5", end_color="ECFDF5", fill_type="solid") # subtle emerald
    alt_row_fill = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")

    for row_idx, row_data in enumerate(tabular_df.values.tolist(), 2):
        for col_idx, val in enumerate(row_data, 1):
            cell = ws.cell(row=row_idx, column=col_idx, value=val)
            cell.border = thin_border
            cell.font = mono_font if col_idx in (3, 4, 6) else body_font
            
            # Highlight confidence and triangulation
            if col_idx == 7 and str(val).strip().lower() in ("highest", "high"):
                cell.fill = high_conf_fill
                cell.font = Font(name="Segoe UI", size=9, bold=True, color="065F46")
            elif col_idx == 8 and "triangulated" in str(val).strip().lower():
                cell.fill = high_conf_fill
                cell.font = Font(name="Segoe UI", size=9, bold=True, color="065F46")
            elif row_idx % 2 == 0:
                cell.fill = alt_row_fill

            # Alignments
            if col_idx == 1:
                cell.alignment = Alignment(horizontal="center", vertical="top")
            elif col_idx in (2, 4, 6):
                cell.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
            elif col_idx in (7, 8):
                cell.alignment = Alignment(horizontal="center", vertical="top")
            else:
                cell.alignment = Alignment(horizontal="left", vertical="top")

    # Column Widths
    col_widths = {
        1: 8,   # sr no
        2: 36,  # data point
        3: 30,  # exact url
        4: 42,  # quoted text
        5: 26,  # search query
        6: 38,  # grep result
        7: 16,  # confidence score
        8: 22,  # triangulation status
    }
    for col_idx, width in col_widths.items():
        col_letter = openpyxl.utils.get_column_letter(col_idx)
        ws.column_dimensions[col_letter].width = width

    wb.save(xlsx_path)
    print(f"[OK] XLSX exported: {xlsx_path}")

    return csv_path, xlsx_path


NUMBER_REGEX = re.compile(r"""
    (?<![\w])                        # not preceded by word char
    (
        \$?\d+(?:,\d{3})*(?:\.\d+)?  # number with optional currency / commas / decimals
        (?:%|k|M|B|T|x|X|bn)?        # common units / multipliers
        (?:\s*(?:percent|million|billion|trillion|users|tokens|points|stars|USD|EUR))?
    )
    (?![\w])                         # not followed by word char
""", re.VERBOSE | re.IGNORECASE)


def add_formatted_bullet(paragraph, text):
    """
    Renders a bullet point into a python-docx paragraph:
    - Bolds important numbers and metrics automatically
    - Highlights [DP-#] tags as superscript or bold markers
    """
    paragraph.paragraph_format.space_after = Pt(4)
    paragraph.paragraph_format.line_spacing = 1.15

    # Tokenize by [DP-#] and bold markers
    dp_pattern = re.compile(r"(\[DP-\d+\])")
    tokens = dp_pattern.split(text)

    for token in tokens:
        if not token:
            continue
        if dp_pattern.match(token):
            # Format DP citation
            run = paragraph.add_run(token)
            run.font.name = "Segoe UI"
            run.font.size = Pt(8.5)
            run.font.bold = True
            run.font.color.rgb = RGBColor(37, 99, 235) # Blue accent
        else:
            # Parse numbers to bold
            parts = NUMBER_REGEX.split(token)
            for part in parts:
                if not part:
                    continue
                run = paragraph.add_run(part)
                run.font.name = "Segoe UI"
                run.font.size = Pt(10.5)
                run.font.color.rgb = RGBColor(30, 41, 59)
                if NUMBER_REGEX.fullmatch(part) and not part.strip().isalpha():
                    run.font.bold = True


def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Sets padding for DOCX table cells."""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m_name, m_val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m_name}')
        node.set(qn('w:w'), str(m_val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)


def export_docx(data_points, chunk_summaries, topic, output_base):
    """
    Builds a professional, zero-fluff, bullet-heavy DOCX dossier.
    Filters strictly for highest-confidence data points.
    """
    doc = Document()

    # Configure Margins (0.75 in for dense readability)
    for section in doc.sections:
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)

    # Filter for Highest Confidence Data Points
    highest_conf_dps = [
        dp for dp in data_points 
        if str(dp.get("confidence score based on rechecking", "")).strip().lower() in ("highest", "high")
    ]
    highest_dp_ids = {dp["sr no"] for dp in highest_conf_dps}

    # Document Header
    title_p = doc.add_paragraph()
    title_p.paragraph_format.space_before = Pt(0)
    title_p.paragraph_format.space_after = Pt(2)
    t_run = title_p.add_run(f"Sherlock Deep Investigation: {topic}")
    t_run.font.name = "Segoe UI"
    t_run.font.size = Pt(20)
    t_run.font.bold = True
    t_run.font.color.rgb = RGBColor(15, 23, 42) # slate-900

    sub_p = doc.add_paragraph()
    sub_p.paragraph_format.space_after = Pt(16)
    sub_run = sub_p.add_run(
        f"Verified Empirical Dossier | Total Verified Data Points: {len(highest_conf_dps)} | Filter: Highest Confidence Only"
    )
    sub_run.font.name = "Segoe UI"
    sub_run.font.size = Pt(9.5)
    sub_run.font.color.rgb = RGBColor(100, 116, 139) # slate-500

    # Executive Summary Card
    summary_head = doc.add_paragraph()
    summary_head.paragraph_format.space_before = Pt(8)
    summary_head.paragraph_format.space_after = Pt(6)
    sh_run = summary_head.add_run("1. Executive Briefing")
    sh_run.font.name = "Segoe UI"
    sh_run.font.size = Pt(13)
    sh_run.font.bold = True
    sh_run.font.color.rgb = RGBColor(30, 41, 59)

    # Walk through sections and bullets
    sec_counter = 2
    for cs in chunk_summaries:
        sec_title = cs["section"]
        bullets = cs["bullets"]
        sec_dps = [dp for dp in cs["data_points"] if dp["sr no"] in highest_dp_ids]

        if not bullets and not sec_dps:
            continue

        sec_head = doc.add_paragraph()
        sec_head.paragraph_format.space_before = Pt(14)
        sec_head.paragraph_format.space_after = Pt(6)
        h_run = sec_head.add_run(f"{sec_counter}. {sec_title}")
        h_run.font.name = "Segoe UI"
        h_run.font.size = Pt(13)
        h_run.font.bold = True
        h_run.font.color.rgb = RGBColor(30, 41, 59)
        sec_counter += 1

        # Primary bullets from chunk summary
        if bullets:
            for b in bullets:
                p = doc.add_paragraph(style='List Bullet')
                add_formatted_bullet(p, b)
        else:
            # If no manual bullets, construct direct human bullet points from highest confidence data points
            for dp in sec_dps:
                p = doc.add_paragraph(style='List Bullet')
                bullet_text = f"{dp['data point']} [DP-{dp['sr no']}]"
                add_formatted_bullet(p, bullet_text)

    # Data Point Reference Index
    ref_head = doc.add_paragraph()
    ref_head.paragraph_format.space_before = Pt(20)
    ref_head.paragraph_format.space_after = Pt(8)
    rf_run = ref_head.add_run(f"{sec_counter}. Verified Data Points Index (Corroborated Ground Truth)")
    rf_run.font.name = "Segoe UI"
    rf_run.font.size = Pt(13)
    rf_run.font.bold = True
    rf_run.font.color.rgb = RGBColor(30, 41, 59)

    # Table of Highest-Confidence Data Points
    table = doc.add_table(rows=1, cols=4)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    col_widths = [Inches(0.7), Inches(2.2), Inches(2.8), Inches(1.3)]
    for i, col in enumerate(table.columns):
        col.width = col_widths[i]

    # Header Row
    hdr_cells = table.rows[0].cells
    hdr_titles = ["Ref", "Verified Claim", "Source Quote & Triangulation", "Source Link"]
    for i, title in enumerate(hdr_titles):
        hdr_cells[i].text = title
        set_cell_margins(hdr_cells[i], top=120, bottom=120, left=120, right=120)
        # Background fill
        shading_xml = parse_xml(f'<w:shd {nsdecls("w")} w:fill="1E293B"/>')
        hdr_cells[i]._tc.get_or_add_tcPr().append(shading_xml)
        for p in hdr_cells[i].paragraphs:
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            for run in p.runs:
                run.font.name = "Segoe UI"
                run.font.size = Pt(9)
                run.font.bold = True
                run.font.color.rgb = RGBColor(255, 255, 255)

    # Data Rows
    for dp in highest_conf_dps:
        row_cells = table.add_row().cells
        ref_text = f"DP-{dp['sr no']}"
        claim_text = dp["data point"]
        quote_text = f'"{dp["quoted text from page"]}"\n[Grep Match]: {dp["grep from running his search query"]}\n[Triangulation]: {dp.get("triangulation status", "Flag as Triangulated")}'
        url_text = dp["exact url/subpage"]

        row_cells[0].text = ref_text
        row_cells[1].text = claim_text
        row_cells[2].text = quote_text
        row_cells[3].text = url_text

        for i in range(4):
            set_cell_margins(row_cells[i], top=80, bottom=80, left=100, right=100)
            shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="F8FAFC"/>') if dp["sr no"] % 2 == 0 else parse_xml(f'<w:shd {nsdecls("w")} w:fill="FFFFFF"/>')
            row_cells[i]._tc.get_or_add_tcPr().append(shd)
            for p in row_cells[i].paragraphs:
                for run in p.runs:
                    run.font.name = "Segoe UI"
                    run.font.size = Pt(8.5)
                    run.font.color.rgb = RGBColor(51, 65, 85)
                    if i == 0:
                        run.font.bold = True
                        run.font.color.rgb = RGBColor(37, 99, 235)

    docx_path = f"{output_base}.docx"
    doc.save(docx_path)
    print(f"[OK] DOCX exported: {docx_path}")
    return docx_path


def main():
    parser = argparse.ArgumentParser(description="Sherlock Multi-Format Exporter")
    parser.add_argument("-d", "--dir", required=True, help="Path to topic directory containing results/")
    parser.add_argument("-t", "--topic", help="Topic title for report headers")
    parser.add_argument("-o", "--output", help="Output basename path (defaults to <topic_dir>/<topic_slug>)")
    args = parser.parse_args()

    topic_dir = os.path.abspath(args.dir)
    results_dir = os.path.join(topic_dir, "results")

    if not os.path.isdir(results_dir):
        print(f"[ERROR] Results directory not found: {results_dir}", file=sys.stderr)
        sys.exit(1)

    topic_name = args.topic or Path(topic_dir).name.replace("_", " ").title()
    output_base = args.output or os.path.join(topic_dir, f"{Path(topic_dir).name}_report")

    print(f"[*] Processing Sherlock results in: {results_dir}")
    data_points, chunk_summaries = load_all_data_points(results_dir)

    print(f"[*] Total data points extracted: {len(data_points)}")
    csv_path, xlsx_path = export_tabular(data_points, output_base)
    docx_path = export_docx(data_points, chunk_summaries, topic_name, output_base)

    print(f"\n[DONE] Successfully generated 3 deliverables:")
    print(f"  1. Table (XLSX): {xlsx_path}")
    print(f"  2. Table (CSV):  {csv_path}")
    print(f"  3. Dossier (DOCX): {docx_path}")


if __name__ == "__main__":
    main()
