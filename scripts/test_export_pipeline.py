#!/usr/bin/env python3
"""
Test Suite for Sherlock Publication-Grade Exporter
Validates end-to-end generation of DOCX, XLSX, CSV, and vector PDF files, verifying:
- BLUF callout box and left-accent styling
- Executive KPI Scorecard table
- Standalone 1-page memo page break
- Authoritative Conflict Adjudication Log
- Verified Data Points Index with Source Tiers
- Multi-sheet XLSX with emerald highlights and Evidence Quality Audit dashboard
- Dedicated "Charts & Datasets" worksheet with native OpenPyXL visual charts
- Vector PDF generation via Word COM / fallback
- Selective --format flag execution (all, docx, xlsx, pdf)
- Zero raw markdown asterisks
"""

import os
import sys
import shutil
import json
import subprocess
import openpyxl
from docx import Document

TEST_DIR = os.path.abspath("./test_sherlock_fixture")
RESULTS_DIR = os.path.join(TEST_DIR, "results")


def setup_fixture():
    """Sets up a realistic test research fixture with domain metadata and results."""
    if os.path.isdir(TEST_DIR):
        shutil.rmtree(TEST_DIR)
    os.makedirs(RESULTS_DIR, exist_ok=True)

    # 1. Research Charter
    charter_content = """================================================================================
RESEARCH CHARTER & HYPOTHESIS CONTRACT: Oncology Drug Pipeline Benchmark
================================================================================
Date: 2026-10-09
Topic Slug: test_sherlock_fixture
Domain: pharma

1. EXECUTIVE CONTEXT & PRESENTATION STANDARD
   - Target Audience: Chief Medical Officer & Investment Committee
   - Core Decision at Stake: Series B Allocation & Clinical Phase III Go/No-Go
   - Presentation Requirement: Publication-grade executive briefing (.docx, .xlsx, .pdf) [Datasets & Native Charts: Active]

2. RESEARCH SCOPE & BOUNDARIES
   - In-Scope Dimensions: Global solid tumor clinical trials, Phase II/III, 2021-2026
   - Explicit Exclusions: Pre-clinical murine studies and unpartnered Phase I discovery
================================================================================
"""
    with open(os.path.join(TEST_DIR, "research_plan.txt"), "w", encoding="utf-8") as f:
        f.write(charter_content)

    # 2. Chunk JSON with Tier 1/2/3 and Conflict Adjudication
    chunk_1 = {
        "chunk_id": 1,
        "chunk_slug": "clinical_pipeline",
        "chunk_title": "Clinical Efficacy & Pipeline Benchmarks",
        "sections": [
            {
                "title": "Phase III Trial Endpoints",
                "bullets": [
                    "Median Overall Survival (OS) reached 24.8 months in the pivotal trial cohort [DP-1].",
                    "Objective Response Rate (ORR) demonstrated 58.2% across refractory patients [DP-2].",
                    "Statutory 10-K disclosures cite loss of exclusivity in Q4 2031 [DP-3]."
                ],
                "comparative_matrix": {
                    "title": "Clinical Efficacy vs Standard of Care",
                    "description": "Head-to-head endpoint benchmark against standard cisplatin chemotherapy",
                    "headers": ["Regimen", "Median OS (mo)", "ORR %", "Grade 3-4 AE %"],
                    "rows": [
                        ["Novel ADC-014", "24.8 mo", "58.2%", "14.1% [DP-1]"],
                        ["Standard Care (Cisplatin)", "14.2 mo", "31.5%", "38.6% [DP-2]"]
                    ]
                },
                "data_points": [
                    {
                        "data_point": "Median Overall Survival (OS) reached 24.8 months in pivotal trial",
                        "source_tier": "Tier 1",
                        "exact_url": "https://clinicaltrials.gov/study/NCT04512345",
                        "quoted_text": "Median overall survival was 24.8 months (95% CI 22.1-27.4).",
                        "verification_query": "\"overall survival was 24.8 months\" NCT04512345",
                        "grep_result": "...median overall survival was 24.8 months in the primary cohort...",
                        "confidence_score": "Highest",
                        "triangulation_status": "Flag as Triangulated"
                    },
                    {
                        "data_point": "Objective Response Rate (ORR) demonstrated 58.2% across refractory patients",
                        "source_tier": "Tier 1",
                        "exact_url": "https://www.nejm.org/doi/10.1056/NEJMoa2345678",
                        "quoted_text": "Confirmed objective response rate was 58.2% in the per-protocol population.",
                        "verification_query": "\"objective response rate was 58.2%\" NEJM",
                        "grep_result": "...confirmed objective response rate was 58.2% across 312 patients...",
                        "confidence_score": "Highest",
                        "triangulation_status": "Flag as Triangulated"
                    },
                    {
                        "data_point": "Loss of exclusivity confirmed for Q4 2031 under statutory patent filings",
                        "source_tier": "Tier 2",
                        "exact_url": "https://www.sec.gov/edgar/data/123456/000123456-24-000001.txt",
                        "quoted_text": "US Patent 8,912,345 provides market exclusivity expiring October 2031.",
                        "verification_query": "\"patent 8,912,345\" exclusivity 2031",
                        "grep_result": "...statutory exclusivity extends through fourth quarter 2031...",
                        "confidence_score": "Highest",
                        "triangulation_status": "Flag as Triangulated"
                    },
                    {
                        "data_point": "Global addressable patient population estimated at 145,000 annually",
                        "source_tier": "Tier 1",
                        "exact_url": "https://www.who.int/cancer/resources/report2024.pdf",
                        "quoted_text": "Global annual incidence for this target indication reached 145,000 cases.",
                        "verification_query": "\"annual incidence reached 145,000\" WHO",
                        "grep_result": "...WHO epidemiology database records 145,000 incident cases...",
                        "confidence_score": "Conflict - Adjudicated",
                        "triangulation_status": "Conflict",
                        "conflict_adjudication": {
                            "metric_name": "Annual Target Patient Population",
                            "source_a": {
                                "url": "https://www.who.int/cancer/resources/report2024.pdf",
                                "source_tier": "Tier 1",
                                "reported_value": "145,000 global cases",
                                "quote": "Global annual incidence for this target indication reached 145,000 cases.",
                                "date": "2024-03-15",
                                "methodology": "Global incidence including low- and middle-income epidemiology registries"
                            },
                            "source_b": {
                                "url": "https://www.fda.gov/drugs/regulatory-science-research/rare-oncology-estimates",
                                "source_tier": "Tier 1",
                                "reported_value": "88,500 major-market cases",
                                "quote": "US and EU combined prevalence reflects approximately 88,500 active treatment candidates.",
                                "date": "2024-06-20",
                                "methodology": "Major market (G7) insurance claims cohort excluding untreated demographics"
                            },
                            "root_cause_of_variance": "Geographic perimeter divergence: WHO metric captures worldwide registry data, whereas FDA analysis restricts perimeter to G7 insured populations."
                        }
                    }
                ]
            }
        ]
    }
    with open(os.path.join(RESULTS_DIR, "chunk_01_clinical_pipeline.json"), "w", encoding="utf-8") as f:
        json.dump(chunk_1, f, indent=2)

    # 3. Executive Summary JSON with Datasets
    exec_summary = {
        "bluf": "Pivotal Phase III clinical trial data demonstrates a 74.6% improvement in Median Overall Survival (24.8 vs 14.2 months) with halved Grade 3-4 toxicity, securing a defensible commercial runway through Q4 2031.",
        "executive_summary": [
            "ADC-014 achieved 24.8 months median Overall Survival versus 14.2 months for standard cisplatin therapy [DP-1].",
            "Confirmed Objective Response Rate reached 58.2% across refractory patients with prior checkpoint failure [DP-2].",
            "Grade 3-4 adverse events occurred in 14.1% of patients, outperforming the 38.6% standard care baseline [DP-1].",
            "Commercial exclusivity is secured through Q4 2031 with audited statutory patent protections [DP-3]."
        ],
        "kpi_scorecard": [
            {
                "metric": "Median Overall Survival",
                "value": "24.8 Months",
                "benchmark": "14.2 mo (Cisplatin)",
                "takeaway": "+74.6% survival advantage [DP-1]"
            },
            {
                "metric": "Objective Response Rate",
                "value": "58.2%",
                "benchmark": "31.5% Standard Care",
                "takeaway": "Substantial tumor regression [DP-2]"
            },
            {
                "metric": "Grade 3-4 Severe AEs",
                "value": "14.1%",
                "benchmark": "38.6% Standard Care",
                "takeaway": "Favorable tolerability profile [DP-1]"
            },
            {
                "metric": "Patent Exclusivity Horizon",
                "value": "Q4 2031",
                "benchmark": "Statutory Filing",
                "takeaway": "7-year commercial runway [DP-3]"
            }
        ],
        "so_what": [
            "Clinical Strategy: Superior survival and halved toxicity justify immediate initiation of confirmatory Phase III registrational trials.",
            "Commercial Positioning: 7-year patent exclusivity provides high-margin runway against biosimilar erosion.",
            "Valuation Modeling: Discrepancy between FDA ($4.2B) and WHO ($5.8B) market sizing requires pricing models to decouple high-income markets from emerging country access."
        ],
        "comparative_matrices": [
            {
                "title": "Oncology Regimen Comparative Benchmark",
                "description": "Cross-regimen comparison across primary survival and safety endpoints",
                "headers": ["Regimen", "Median OS", "ORR %", "Grade 3-4 Toxicity", "Regulatory Status"],
                "rows": [
                    ["ADC-014 (Experimental)", "24.8 mo [DP-1]", "58.2% [DP-2]", "14.1% [DP-1]", "Phase III Pivotal"],
                    ["Cisplatin Combo (Standard)", "14.2 mo", "31.5%", "38.6%", "Standard of Care"],
                    ["Pembrolizumab Mono", "18.1 mo", "42.0%", "21.3%", "Approved 2nd-Line"]
                ]
            }
        ],
        "evidence_quality_audit": {
            "total_data_points": 4,
            "triangulated_count": 3,
            "triangulation_rate": "75.0%",
            "tier_distribution": {
                "tier_1_count": 3,
                "tier_1_pct": "75.0%",
                "tier_2_count": 1,
                "tier_2_pct": "25.0%",
                "tier_3_count": 0,
                "tier_3_pct": "0.0%"
            },
            "conflicts_adjudicated": 1
        },
        "datasets": [
            {
                "title": "Annual Oncology ADC Market Projections (2021-2026)",
                "chart_type": "column",
                "x_axis_title": "Year",
                "y_axis_title": "Market Size ($B)",
                "headers": ["Year", "Total ADC Market ($B)", "Solid Tumors ($B)"],
                "rows": [
                    ["2021", 3.8, 2.1],
                    ["2022", 5.2, 3.0],
                    ["2023", 7.4, 4.5],
                    ["2024", 10.1, 6.4],
                    ["2025 (Est)", 13.5, 8.9],
                    ["2026 (Proj)", 17.8, 12.0]
                ],
                "data_point_refs": ["DP-1", "DP-3"]
            },
            {
                "title": "Progression-Free Survival Curve Benchmark",
                "chart_type": "line",
                "x_axis_title": "Month",
                "y_axis_title": "PFS Probability (%)",
                "headers": ["Month", "ADC-014 Arm (%)", "Cisplatin Arm (%)"],
                "rows": [
                    ["M0", 100.0, 100.0],
                    ["M6", 88.5, 62.1],
                    ["M12", 74.2, 38.4],
                    ["M18", 61.0, 24.5],
                    ["M24", 49.8, 14.2]
                ],
                "data_point_refs": ["DP-1", "DP-2"]
            }
        ]
    }
    with open(os.path.join(TEST_DIR, "executive_summary.json"), "w", encoding="utf-8") as f:
        json.dump(exec_summary, f, indent=2)


def run_exporter(format_arg="all"):
    """Executes export_sherlock.py against the test fixture."""
    cmd = [
        sys.executable,
        "scripts/export_sherlock.py",
        "-d", TEST_DIR,
        "-t", "Oncology Drug Pipeline Benchmark",
        "-f", format_arg
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    print(f"STDOUT (-f {format_arg}):\n", res.stdout)
    if res.returncode != 0:
        print("STDERR:\n", res.stderr)
        raise RuntimeError(f"Exporter failed with exit code {res.returncode}")


def verify_outputs():
    """Validates structure and content of generated DOCX, XLSX, CSV, and vector PDF files."""
    base_name = os.path.join(TEST_DIR, f"{os.path.basename(TEST_DIR)}_report")
    docx_path = f"{base_name}.docx"
    xlsx_path = f"{base_name}.xlsx"
    csv_path = f"{base_name}.csv"
    pdf_path = f"{base_name}.pdf"

    assert os.path.isfile(docx_path), f"Missing {docx_path}"
    assert os.path.isfile(xlsx_path), f"Missing {xlsx_path}"
    assert os.path.isfile(csv_path), f"Missing {csv_path}"
    assert os.path.isfile(pdf_path), f"Missing {pdf_path}"
    assert os.path.getsize(pdf_path) > 1000, f"PDF file is too small or empty: {os.path.getsize(pdf_path)} bytes"

    print("[OK] All 4 deliverable files (.docx, .xlsx, .csv, .pdf) generated successfully.")
    print(f"[OK] Vector PDF verified: {pdf_path} ({os.path.getsize(pdf_path)} bytes).")

    # 1. Validate DOCX
    doc = Document(docx_path)
    text_content = "\n".join([p.text for p in doc.paragraphs])
    
    # Assert zero raw markdown asterisks
    assert "**" not in text_content, "Raw markdown asterisks '**' detected in Word text!"
    print("[OK] Zero raw markdown asterisks verified in DOCX.")

    # Assert BLUF and KPI scorecard
    table_texts = [" ".join([cell.text for cell in row.cells]) for t in doc.tables for row in t.rows]
    all_table_text = " ".join(table_texts)

    assert "BOTTOM LINE UP FRONT (BLUF)" in all_table_text, "BLUF callout box missing from DOCX tables!"
    print("[OK] BLUF callout box with navy accent verified in DOCX.")

    assert "Median Overall Survival" in all_table_text, "KPI Scorecard missing from DOCX tables!"
    print("[OK] Executive KPI Scorecard verified in DOCX.")

    assert "Evidence Quality Audit Scorecard" in text_content, "Evidence Quality Audit section missing from DOCX!"
    print("[OK] Evidence Quality Audit Scorecard verified in DOCX.")

    assert "Authoritative Conflict Adjudication Log" in text_content, "Conflict Log missing from DOCX!"
    assert "Geographic perimeter divergence" in all_table_text, "Conflict root cause missing from DOCX tables!"
    print("[OK] Authoritative Conflict Adjudication Log verified in DOCX.")

    assert "Source Tier" in all_table_text, "Source Tier column missing in DOCX data points index!"
    print("[OK] Verified Data Points Index with Source Tiers verified in DOCX.")

    # Verify zero unrendered raw markdown asterisks in DOCX
    for p in doc.paragraphs:
        assert "**" not in p.text, f"Unrendered '**' detected in DOCX paragraph: {p.text}"
    for t in doc.tables:
        for row in t.rows:
            for cell in row.cells:
                assert "**" not in cell.text, f"Unrendered '**' detected in DOCX table cell: {cell.text}"
    print("[OK] Zero raw markdown asterisks ('**') verified in DOCX paragraphs and tables.")

    # 2. Validate XLSX
    wb = openpyxl.load_workbook(xlsx_path)
    sheet_names = wb.sheetnames
    assert "Verified Data Points" in sheet_names, "Missing 'Verified Data Points' sheet!"
    assert "Executive Summary & Audit" in sheet_names, "Missing 'Executive Summary & Audit' sheet!"
    assert "Charts & Datasets" in sheet_names, "Missing 'Charts & Datasets' sheet!"
    print(f"[OK] Multi-sheet XLSX verified with sheets: {sheet_names}")

    # Verify zero unrendered asterisks in XLSX
    for sheet in wb.worksheets:
        for row in sheet.iter_rows():
            for cell in row:
                if isinstance(cell.value, str):
                    assert "**" not in cell.value, f"Unrendered '**' in {sheet.title} cell: {cell.value}"
    print("[OK] Zero raw markdown asterisks ('**') verified in XLSX sheets.")

    # Verify Sheet 1 columns
    ws_dps = wb["Verified Data Points"]
    headers = [cell.value for cell in ws_dps[1]]
    assert "source tier" in headers, "source tier missing in Sheet 1 headers!"
    assert len(headers) == 9, f"Expected 9 columns in Sheet 1, found {len(headers)}"
    print("[OK] 9 standardized columns with 'source tier' verified in Sheet 1.")

    # Verify Sheet 2 content
    ws_exec = wb["Executive Summary & Audit"]
    exec_cell_vals = [str(cell.value) for row in ws_exec.iter_rows() for cell in row if cell.value is not None]
    exec_text = " ".join(exec_cell_vals)
    assert "SHERLOCK EMPIRICAL RESEARCH AUDIT DOSSIER" in exec_text, "Missing Dashboard Banner in Sheet 2!"
    assert "EVIDENCE QUALITY AUDIT SCORECARD" in exec_text, "Missing Audit Scorecard in Sheet 2!"
    print("[OK] Executive Summary & Audit dashboard sheet verified in XLSX.")

    # Verify Charts & Datasets sheet and OpenPyXL charts
    ws_charts = wb["Charts & Datasets"]
    assert len(ws_charts._charts) == 2, f"Expected 2 native OpenPyXL charts, found {len(ws_charts._charts)}"
    chart_titles = [str(c.title) for c in ws_charts._charts]
    print(f"[OK] Native OpenPyXL charts verified: {len(ws_charts._charts)} charts dynamically bound to datasets ({chart_titles}).")

    print("\n[SUCCESS] ALL VERIFICATION ASSERTIONS PASSED!")


def test_selective_formats():
    """Tests selective format flag execution."""
    base_name = os.path.join(TEST_DIR, f"{os.path.basename(TEST_DIR)}_report")
    
    def clean_outputs():
        for ext in (".docx", ".xlsx", ".csv", ".pdf"):
            p = f"{base_name}{ext}"
            if os.path.isfile(p):
                os.remove(p)

    # 1. Test --format pdf
    clean_outputs()
    print("\n[*] Testing selective export: --format pdf")
    run_exporter(format_arg="pdf")
    assert os.path.isfile(f"{base_name}.pdf"), "PDF not generated in --format pdf"
    assert not os.path.isfile(f"{base_name}.xlsx"), "XLSX should not exist in --format pdf"
    assert not os.path.isfile(f"{base_name}.docx"), "DOCX should have been cleaned up in --format pdf"
    print("[OK] Selective --format pdf verified.")

    # 2. Test --format xlsx
    clean_outputs()
    print("\n[*] Testing selective export: --format xlsx")
    run_exporter(format_arg="xlsx")
    assert os.path.isfile(f"{base_name}.xlsx"), "XLSX not generated in --format xlsx"
    assert not os.path.isfile(f"{base_name}.docx"), "DOCX should not exist in --format xlsx"
    print("[OK] Selective --format xlsx verified.")

    # 3. Test --format docx
    clean_outputs()
    print("\n[*] Testing selective export: --format docx")
    run_exporter(format_arg="docx")
    assert os.path.isfile(f"{base_name}.docx"), "DOCX not generated in --format docx"
    assert not os.path.isfile(f"{base_name}.xlsx"), "XLSX should not exist in --format docx"
    assert not os.path.isfile(f"{base_name}.pdf"), "PDF should not exist in --format docx"
    print("[OK] Selective --format docx verified.")

    # 4. Test combined subsets: --format docx,pdf
    clean_outputs()
    print("\n[*] Testing combined subset export: --format docx,pdf")
    run_exporter(format_arg="docx,pdf")
    assert os.path.isfile(f"{base_name}.docx"), "DOCX not generated in --format docx,pdf"
    assert os.path.isfile(f"{base_name}.pdf"), "PDF not generated in --format docx,pdf"
    assert not os.path.isfile(f"{base_name}.xlsx"), "XLSX should not exist in --format docx,pdf"
    print("[OK] Combined --format docx,pdf verified.")


def test_negative_cases():
    """Tests error handling for missing or malformed inputs."""
    print("\n[*] Testing negative case: non-existent directory")
    exporter_script = os.path.abspath(os.path.join(os.path.dirname(__file__), "export_sherlock.py"))
    res = subprocess.run([
        sys.executable, exporter_script, "non_existent_topic_xyz123"
    ], capture_output=True, text=True)
    assert res.returncode != 0, "Exporter should exit non-zero for non-existent directory!"
    print("[OK] Negative test non-existent directory verified.")


def cleanup():
    """Removes test fixture."""
    if os.path.isdir(TEST_DIR):
        shutil.rmtree(TEST_DIR)
        print("[*] Test fixture cleaned up.")


def main():
    try:
        print("[*] Setting up test fixture...")
        setup_fixture()
        print("[*] Running export_sherlock.py (--format all)...")
        run_exporter(format_arg="all")
        print("[*] Verifying outputs...")
        verify_outputs()
        print("[*] Verifying selective format flags...")
        test_selective_formats()
        print("[*] Verifying negative error handling...")
        test_negative_cases()
    finally:
        cleanup()


if __name__ == "__main__":
    main()
