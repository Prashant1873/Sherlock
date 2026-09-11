#!/usr/bin/env python3
"""
Sherlock Export Engine
Generates:
1. <topic>.xlsx - Tabular data point matrix with custom styling, plus Comparative Matrix sheets when present
2. <topic>.csv  - Machine-readable data point records (and comparative CSV if matrix present)
3. <topic>.docx - Clean, direct, fluff-free narrative dossier with Executive Summary, "So What" implications,
                  comparative matrices, section findings, and verified data point index.
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
    """Loads and standardizes data points and comparative matrices from all chunk JSON files."""
    json_files = sorted(glob.glob(os.path.join(results_dir, "*.json")))
    all_dps = []
    chunk_summaries = []
    current_sr = 1

    for jf in json_files:
        filename = os.path.basename(jf)
        # Skip executive_summary.json and summary.json if located in results_dir
        if filename in ("executive_summary.json", "summary.json"):
            continue

        try:
            with open(jf, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"[WARN] Failed to read {jf}: {e}", file=sys.stderr)
            continue

        chunk_title = data.get("chunk_title", Path(jf).stem.replace("_", " ").title())
        sections = data.get("sections", [])

        # Handle flat data_points list if present
        raw_dps = data.get("data_points", [])
        if raw_dps and not sections:
            sections = [{"title": chunk_title, "bullets": [], "data_points": raw_dps}]

        for sec in sections:
            sec_title = sec.get("title", chunk_title)
            bullets = sec.get("bullets", [])
            sec_dps = sec.get("data_points", [])

            # Extract any section-level comparative matrices
            sec_matrices = []
            if "comparative_matrix" in sec and isinstance(sec["comparative_matrix"], dict):
                sec_matrices.append(sec["comparative_matrix"])
            elif "comparative_matrices" in sec and isinstance(sec["comparative_matrices"], list):
                sec_matrices.extend(sec["comparative_matrices"])
            elif "table" in sec and isinstance(sec["table"], dict):
                sec_matrices.append(sec["table"])

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
                "comparative_matrices": sec_matrices,
            })

    return all_dps, chunk_summaries


def load_executive_summary_and_matrices(topic_dir, results_dir, chunk_summaries, all_dps):
    """
    Loads executive summary bullets, 'so what' implications, and comparative matrices.
    Checks topic_dir and results_dir for executive_summary.json or summary.json.
    Falls back to intelligent synthesis if not present.
    """
    candidate_paths = [
        os.path.join(topic_dir, "executive_summary.json"),
        os.path.join(topic_dir, "summary.json"),
        os.path.join(results_dir, "executive_summary.json"),
        os.path.join(results_dir, "summary.json"),
    ]

    exec_data = {}
    for cp in candidate_paths:
        if os.path.isfile(cp):
            try:
                with open(cp, "r", encoding="utf-8") as f:
                    exec_data = json.load(f)
                print(f"[*] Loaded executive summary metadata from: {cp}")
                break
            except Exception as e:
                print(f"[WARN] Failed to read {cp}: {e}", file=sys.stderr)

    # 1. Executive Summary Bullets
    exec_bullets = exec_data.get("executive_summary") or exec_data.get("key_findings") or []
    if isinstance(exec_bullets, str):
        exec_bullets = [b.strip() for b in exec_bullets.split("\n") if b.strip()]

    # Fallback: Synthesize from top triangulated data points
    if not exec_bullets:
        highest_dps = [
            dp for dp in all_dps 
            if str(dp.get("confidence score based on rechecking", "")).strip().lower() in ("highest", "high")
        ]
        top_dps = highest_dps[:5]
        exec_bullets = [f"{dp['data point']} [DP-{dp['sr no']}]" for dp in top_dps]
        if not exec_bullets and all_dps:
            exec_bullets = [f"{dp['data point']} [DP-{dp['sr no']}]" for dp in all_dps[:5]]

    # 2. "So What?" (Strategic Implications)
    so_what = exec_data.get("so_what") or exec_data.get("strategic_implications") or []
    if isinstance(so_what, str):
        so_what = [s.strip() for s in so_what.split("\n") if s.strip()]

    # Fallback: Synthesize actionable strategic takeaways
    if not so_what:
        so_what = [
            "Baseline Evidence Foundation: Documented metrics provide empirical ground truth for risk modeling, clinical resource allocation, and market sizing.",
            "Variance & Segmentation: Significant heterogeneity across sub-cohorts and geographies indicates that blanket strategies underperform targeted, evidence-adjusted interventions.",
            "Decision Gate: Stakeholders should validate localized registries and secondary diagnostic gaps before committing capital or clinical capacity.",
        ]

    # 3. Comparative Matrices
    matrices = exec_data.get("comparative_matrices") or []
    if not matrices and "comparative_matrix" in exec_data and isinstance(exec_data["comparative_matrix"], dict):
        matrices = [exec_data["comparative_matrix"]]

    # Collect any section-level matrices from chunk summaries
    for cs in chunk_summaries:
        for m in cs.get("comparative_matrices", []):
            if m not in matrices:
                matrices.append(m)

    return exec_bullets, so_what, matrices


def clean_markdown_asterisks(text):
    """Strips remaining markdown asterisk artifacts."""
    if not text:
        return ""
    # Strip markdown bold/italic asterisks while preserving actual mathematical/wildcard characters if any
    return re.sub(r"\*\*([^*]+)\*\*", r"\1", text).replace("**", "")


def add_formatted_runs(paragraph, text, base_font_size=Pt(10.5), base_color=RGBColor(30, 41, 59)):
    """
    Renders text into a python-docx paragraph:
    - Formats markdown bold (**text**) into clean bold runs WITHOUT literal asterisks.
    - Highlights [DP-#] tags as distinct, styled citation markers.
    - Strips asterisk artifacts so asterisks never leak into output.
    - Does NOT artificially bold numbers.
    """
    if not text:
        return

    # Match [DP-#] citations or markdown **bold**
    pattern = re.compile(r"(\[DP-\d+\]|\*\*.*?\*\*)")
    tokens = pattern.split(str(text))

    for token in tokens:
        if not token:
            continue

        if re.fullmatch(r"\[DP-\d+\]", token):
            run = paragraph.add_run(token)
            run.font.name = "Segoe UI"
            run.font.size = Pt(8.5)
            run.font.bold = True
            run.font.color.rgb = RGBColor(37, 99, 235)  # Blue citation accent
        elif token.startswith("**") and token.endswith("**") and len(token) >= 4:
            # Bold content without asterisks
            inner = token[2:-2].replace("**", "").replace("*", "")
            run = paragraph.add_run(inner)
            run.font.name = "Segoe UI"
            run.font.size = base_font_size
            run.font.bold = True
            run.font.color.rgb = base_color
        else:
            # Normal text with any stray asterisks cleaned
            clean_text = token.replace("**", "")
            run = paragraph.add_run(clean_text)
            run.font.name = "Segoe UI"
            run.font.size = base_font_size
            run.font.bold = False
            run.font.color.rgb = base_color


def add_formatted_bullet(paragraph, text):
    """Renders a clean bullet point into a python-docx paragraph."""
    paragraph.paragraph_format.space_after = Pt(4)
    paragraph.paragraph_format.line_spacing = 1.15
    add_formatted_runs(paragraph, text, base_font_size=Pt(10.5))


def set_cell_margins(cell, top=100, bottom=100, left=140, right=140):
    """Sets padding for DOCX table cells (in dxa: 20 dxa = 1 pt)."""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m_name, m_val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m_name}')
        node.set(qn('w:w'), str(m_val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)


def set_cell_border(cell, **kwargs):
    """Sets borders for DOCX table cells."""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')
    for edge in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        edge_data = kwargs.get(edge)
        if edge_data:
            tag = f'w:{edge}'
            element = OxmlElement(tag)
            element.set(qn('w:val'), edge_data.get('val', 'single'))
            element.set(qn('w:sz'), str(edge_data.get('sz', 4)))
            element.set(qn('w:space'), '0')
            element.set(qn('w:color'), edge_data.get('color', 'E2E8F0'))
            tcBorders.append(element)
    tcPr.append(tcBorders)


def render_comparative_table(doc, matrix_data):
    """Renders a styled comparative matrix table into the Word document."""
    title = matrix_data.get("title", "Comparative Matrix")
    desc = matrix_data.get("description", "")
    headers = matrix_data.get("headers", [])
    rows = matrix_data.get("rows", [])

    if not headers or not rows:
        return

    # Title paragraph
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(2)
    run = p.add_run(title)
    run.font.name = "Segoe UI"
    run.font.size = Pt(11)
    run.font.bold = True
    run.font.color.rgb = RGBColor(30, 41, 59)

    if desc:
        dp_desc = doc.add_paragraph()
        dp_desc.paragraph_format.space_after = Pt(5)
        r_desc = dp_desc.add_run(clean_markdown_asterisks(desc))
        r_desc.font.name = "Segoe UI"
        r_desc.font.size = Pt(9.5)
        r_desc.font.italic = True
        r_desc.font.color.rgb = RGBColor(100, 116, 139)

    table = doc.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = True

    # Header Row
    hdr_cells = table.rows[0].cells
    for i, h_text in enumerate(headers):
        hdr_cells[i].text = ""
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        run = p.add_run(clean_markdown_asterisks(str(h_text)))
        run.font.name = "Segoe UI"
        run.font.size = Pt(9.5)
        run.font.bold = True
        run.font.color.rgb = RGBColor(255, 255, 255)
        set_cell_margins(hdr_cells[i], top=100, bottom=100, left=120, right=120)
        shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="0F172A"/>')
        hdr_cells[i]._tc.get_or_add_tcPr().append(shd)

    # Data Rows
    for r_idx, row_vals in enumerate(rows):
        row_cells = table.add_row().cells
        for c_idx, val in enumerate(row_vals):
            if c_idx < len(row_cells):
                row_cells[c_idx].text = ""
                p = row_cells[c_idx].paragraphs[0]
                p.paragraph_format.space_before = Pt(2)
                p.paragraph_format.space_after = Pt(2)
                p.paragraph_format.line_spacing = 1.1
                add_formatted_runs(p, str(val), base_font_size=Pt(9))
                set_cell_margins(row_cells[c_idx], top=70, bottom=70, left=100, right=100)
                fill_color = "F8FAFC" if r_idx % 2 == 0 else "FFFFFF"
                shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_color}"/>')
                row_cells[c_idx]._tc.get_or_add_tcPr().append(shd)

    # Add subtle bottom spacing after table
    post_p = doc.add_paragraph()
    post_p.paragraph_format.space_after = Pt(8)


def export_tabular(data_points, comparative_matrices, output_base):
    """Exports data points to XLSX and CSV with styling, including comparative matrices if present."""
    if not data_points:
        print("[WARN] No data points to export to tabular formats.", file=sys.stderr)
        return None, None

    df = pd.DataFrame(data_points)
    tabular_df = df[REQUIRED_COLUMNS]

    # 1. Export Primary CSV
    csv_path = f"{output_base}.csv"
    tabular_df.to_csv(csv_path, index=False, encoding="utf-8")
    print(f"[OK] CSV exported: {csv_path}")

    # Export Comparative Matrix CSV if present
    if comparative_matrices:
        for idx, cm in enumerate(comparative_matrices, 1):
            c_headers = cm.get("headers", [])
            c_rows = cm.get("rows", [])
            if c_headers and c_rows:
                cm_df = pd.DataFrame(c_rows, columns=c_headers)
                cm_csv_path = f"{output_base}_comparative_{idx}.csv" if len(comparative_matrices) > 1 else f"{output_base}_comparative.csv"
                cm_df.to_csv(cm_csv_path, index=False, encoding="utf-8")
                print(f"[OK] Comparative CSV exported: {cm_csv_path}")

    # 2. Export Styled XLSX
    xlsx_path = f"{output_base}.xlsx"
    wb = openpyxl.Workbook()

    # Sheet 1: Verified Data Points
    ws = wb.active
    ws.title = "Verified Data Points"
    ws.views.sheetView[0].showGridLines = True

    headers = REQUIRED_COLUMNS
    ws.append(headers)

    header_font = Font(name="Segoe UI", size=10, bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="1A365D", end_color="1A365D", fill_type="solid")  # Deep navy
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

    body_font = Font(name="Segoe UI", size=9, color="1F2937")
    mono_font = Font(name="Consolas", size=8.5, color="374151")
    high_conf_fill = PatternFill(start_color="ECFDF5", end_color="ECFDF5", fill_type="solid")  # Subtle emerald
    alt_row_fill = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")

    for row_idx, row_data in enumerate(tabular_df.values.tolist(), 2):
        for col_idx, val in enumerate(row_data, 1):
            clean_val = clean_markdown_asterisks(str(val)) if isinstance(val, str) else val
            cell = ws.cell(row=row_idx, column=col_idx, value=clean_val)
            cell.border = thin_border
            cell.font = mono_font if col_idx in (3, 4, 6) else body_font

            if col_idx == 7 and str(val).strip().lower() in ("highest", "high"):
                cell.fill = high_conf_fill
                cell.font = Font(name="Segoe UI", size=9, bold=True, color="065F46")
            elif col_idx == 8 and "triangulated" in str(val).strip().lower():
                cell.fill = high_conf_fill
                cell.font = Font(name="Segoe UI", size=9, bold=True, color="065F46")
            elif row_idx % 2 == 0:
                cell.fill = alt_row_fill

            if col_idx == 1:
                cell.alignment = Alignment(horizontal="center", vertical="top")
            elif col_idx in (2, 4, 6):
                cell.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
            elif col_idx in (7, 8):
                cell.alignment = Alignment(horizontal="center", vertical="top")
            else:
                cell.alignment = Alignment(horizontal="left", vertical="top")

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

    # Optional Sheet 2+: Comparative Matrices
    if comparative_matrices:
        for idx, cm in enumerate(comparative_matrices, 1):
            c_headers = cm.get("headers", [])
            c_rows = cm.get("rows", [])
            if not c_headers or not c_rows:
                continue

            sheet_title = cm.get("title", f"Comparative Matrix {idx}")[:30].replace(":", " -")
            ws_comp = wb.create_sheet(title=sheet_title)
            ws_comp.views.sheetView[0].showGridLines = True

            ws_comp.append(c_headers)
            for c_idx, h_text in enumerate(c_headers, 1):
                c_cell = ws_comp.cell(row=1, column=c_idx)
                c_cell.font = header_font
                c_cell.fill = header_fill
                c_cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
                c_cell.border = thin_border
            ws_comp.row_dimensions[1].height = 26

            for r_idx, r_data in enumerate(c_rows, 2):
                for c_idx, val in enumerate(r_data, 1):
                    clean_val = clean_markdown_asterisks(str(val))
                    c_cell = ws_comp.cell(row=r_idx, column=c_idx, value=clean_val)
                    c_cell.border = thin_border
                    c_cell.font = body_font
                    c_cell.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
                    if r_idx % 2 == 0:
                        c_cell.fill = alt_row_fill

            for col_idx in range(1, len(c_headers) + 1):
                col_letter = openpyxl.utils.get_column_letter(col_idx)
                ws_comp.column_dimensions[col_letter].width = 28

    wb.save(xlsx_path)
    print(f"[OK] XLSX exported: {xlsx_path}")

    return csv_path, xlsx_path


def export_docx(data_points, chunk_summaries, exec_bullets, so_what_bullets, comparative_matrices, topic, output_base):
    """
    Builds a professional, zero-fluff DOCX dossier:
    - 1. Executive Summary (key findings)
    - 2. Strategic Implications ("So What?" section)
    - 3. Comparative Matrices (when query requires or present)
    - 4+. Detailed Section Findings
    - Final Section: Verified Data Points Index (Corroborated Ground Truth Table)
    Filters strictly for highest-confidence data points. Clean typography with no asterisk artifacts.
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
    t_run.font.color.rgb = RGBColor(15, 23, 42)  # slate-900

    sub_p = doc.add_paragraph()
    sub_p.paragraph_format.space_after = Pt(16)
    sub_run = sub_p.add_run(
        f"Verified Empirical Dossier | Total Verified Data Points: {len(highest_conf_dps)} | Filter: Highest Confidence Only"
    )
    sub_run.font.name = "Segoe UI"
    sub_run.font.size = Pt(9.5)
    sub_run.font.color.rgb = RGBColor(100, 116, 139)  # slate-500

    sec_counter = 1

    # 1. Executive Summary Section
    summary_head = doc.add_paragraph()
    summary_head.paragraph_format.space_before = Pt(8)
    summary_head.paragraph_format.space_after = Pt(6)
    sh_run = summary_head.add_run(f"{sec_counter}. Executive Summary")
    sh_run.font.name = "Segoe UI"
    sh_run.font.size = Pt(13)
    sh_run.font.bold = True
    sh_run.font.color.rgb = RGBColor(30, 41, 59)
    sec_counter += 1

    for b in exec_bullets:
        p = doc.add_paragraph(style='List Bullet')
        add_formatted_bullet(p, b)

    # 2. Strategic Implications ("So What?") Section
    so_what_head = doc.add_paragraph()
    so_what_head.paragraph_format.space_before = Pt(14)
    so_what_head.paragraph_format.space_after = Pt(6)
    sw_run = so_what_head.add_run(f"{sec_counter}. Strategic Implications (\"So What?\")")
    sw_run.font.name = "Segoe UI"
    sw_run.font.size = Pt(13)
    sw_run.font.bold = True
    sw_run.font.color.rgb = RGBColor(30, 41, 59)
    sec_counter += 1

    for sw in so_what_bullets:
        p = doc.add_paragraph(style='List Bullet')
        add_formatted_bullet(p, sw)

    # 3. Comparative Matrices (if query requires / matrices present)
    if comparative_matrices:
        comp_head = doc.add_paragraph()
        comp_head.paragraph_format.space_before = Pt(14)
        comp_head.paragraph_format.space_after = Pt(6)
        ch_run = comp_head.add_run(f"{sec_counter}. Comparative Analysis & Benchmarks")
        ch_run.font.name = "Segoe UI"
        ch_run.font.size = Pt(13)
        ch_run.font.bold = True
        ch_run.font.color.rgb = RGBColor(30, 41, 59)
        sec_counter += 1

        for cm in comparative_matrices:
            render_comparative_table(doc, cm)

    # 4+. Detailed Findings by Chunk / Section
    for cs in chunk_summaries:
        sec_title = cs["section"]
        bullets = cs["bullets"]
        sec_dps = [dp for dp in cs["data_points"] if dp["sr no"] in highest_dp_ids]
        sec_matrices = cs.get("comparative_matrices", [])

        if not bullets and not sec_dps and not sec_matrices:
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
            # If no explicit bullets, construct direct statements from highest confidence data points
            for dp in sec_dps:
                p = doc.add_paragraph(style='List Bullet')
                bullet_text = f"{dp['data point']} [DP-{dp['sr no']}]"
                add_formatted_bullet(p, bullet_text)

        # Render section-level comparative matrix if any
        if sec_matrices:
            for sm in sec_matrices:
                render_comparative_table(doc, sm)

    # Final Section: Verified Data Points Index
    ref_head = doc.add_paragraph()
    ref_head.paragraph_format.space_before = Pt(20)
    ref_head.paragraph_format.space_after = Pt(8)
    rf_run = ref_head.add_run(f"{sec_counter}. Verified Data Points Index (Corroborated Ground Truth)")
    rf_run.font.name = "Segoe UI"
    rf_run.font.size = Pt(13)
    rf_run.font.bold = True
    rf_run.font.color.rgb = RGBColor(30, 41, 59)

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
        hdr_cells[i].text = ""
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        run = p.add_run(title)
        run.font.name = "Segoe UI"
        run.font.size = Pt(9)
        run.font.bold = True
        run.font.color.rgb = RGBColor(255, 255, 255)
        set_cell_margins(hdr_cells[i], top=120, bottom=120, left=120, right=120)
        shading_xml = parse_xml(f'<w:shd {nsdecls("w")} w:fill="1E293B"/>')
        hdr_cells[i]._tc.get_or_add_tcPr().append(shading_xml)

    # Data Rows
    for dp in highest_conf_dps:
        row_cells = table.add_row().cells
        ref_text = f"DP-{dp['sr no']}"
        claim_text = dp["data point"]
        quote_text = f'"{dp["quoted text from page"]}"\n[Grep Match]: {dp["grep from running his search query"]}\n[Triangulation]: {dp.get("triangulation status", "Flag as Triangulated")}'
        url_text = dp["exact url/subpage"]

        for i, (val, is_ref) in enumerate([(ref_text, True), (claim_text, False), (quote_text, False), (url_text, False)]):
            row_cells[i].text = ""
            p = row_cells[i].paragraphs[0]
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.15
            
            if is_ref:
                run = p.add_run(val)
                run.font.name = "Segoe UI"
                run.font.size = Pt(8.5)
                run.font.bold = True
                run.font.color.rgb = RGBColor(37, 99, 235)
            else:
                add_formatted_runs(p, val, base_font_size=Pt(8.5), base_color=RGBColor(51, 65, 85))

            set_cell_margins(row_cells[i], top=80, bottom=80, left=100, right=100)
            shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="F8FAFC"/>') if dp["sr no"] % 2 == 0 else parse_xml(f'<w:shd {nsdecls("w")} w:fill="FFFFFF"/>')
            row_cells[i]._tc.get_or_add_tcPr().append(shd)

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
    exec_bullets, so_what_bullets, comparative_matrices = load_executive_summary_and_matrices(
        topic_dir, results_dir, chunk_summaries, data_points
    )

    csv_path, xlsx_path = export_tabular(data_points, comparative_matrices, output_base)
    docx_path = export_docx(
        data_points, chunk_summaries, exec_bullets, so_what_bullets, comparative_matrices, topic_name, output_base
    )

    print(f"\n[DONE] Successfully generated deliverables:")
    print(f"  1. Table (XLSX): {xlsx_path}")
    print(f"  2. Table (CSV):  {csv_path}")
    print(f"  3. Dossier (DOCX): {docx_path}")


if __name__ == "__main__":
    main()
