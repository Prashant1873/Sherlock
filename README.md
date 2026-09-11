# Sherlock: Empirical Deep Research Agent

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](https://www.python.org/)
[![Status: Production](https://img.shields.io/badge/Status-Production-emerald.svg)](#)

**Sherlock** is an unhurried, zero-hallucination empirical deep research skill for autonomous coding and research agents. It combines multi-hop web retrieval and verbatim page scraping with an empirical double-search verification loop, strict 1-chunk-per-turn context preservation, and automated multi-format reporting (`.xlsx`, `.csv`, `.docx`).

---

## Quality & Verification Hierarchy

Every data point, metric, citation, and analytical claim must survive this strict 5-tier verification chain:

```
Traceability -> Triangulation -> Recency -> Consistency -> Narrative
```

1. **Traceability**: Zero reliance on parametric memory. Every data point MUST trace back directly to an exact primary/secondary URL and a verbatim quotation scraped from that page.
2. **Triangulation**: Require **2+ independent sources** to triangulate any data point before certifying it. Formally mark verified data as `"Flag as Triangulated"`.
3. **Recency**: Prioritize the freshest available primary data and latest reported fiscal/clinical time horizons. Explicitly timestamp all metrics.
4. **Consistency**: Reconcile contradictory metrics across sources. If ambiguous or uncorroborated, formally classify and mark as `"Undeclared"` rather than speculating or guessing.
5. **Narrative**: Zero marketing fluff. High-density, numbers-bolded strategic findings synthesized strictly from corroborated ground truth.

---

## The 5-Step Secondary Research Process Chain

```
┌───────────┐     ┌───────────┐     ┌───────────┐     ┌───────────────┐     ┌───────────┐
│ 1. Scope  │ ──> │  2. Map   │ ──> │ 3. Extract│ ──> │ 4. Triangulate│ ──> │5.Synthesis│
└───────────┘     └───────────┘     └───────────┘     └───────────────┘     └───────────┘
```

1. **Scope**: Grounded by framing a concrete research plan stored as a `.txt` file (`./<topic_slug>/research_plan.txt`) to be edited by the user and read directly by the system. Strictly relies on external sources with zero reliance on memory.
2. **Map**: Break down topics into MECE (Mutually Exclusive, Collectively Exhaustive) sub-questions and 3–8 focus chunks in `outline.yaml`. **(Gate 1: Stop for user approval)**.
3. **Extract**: Drive targeted searches using phrasing and query variations, standardizing the data through structured, MECE tabular extraction templates.
4. **Triangulate**: Cross-verify across **2+ independent sources**, capture snippet grep matches, tabulate matrices, resolve ambiguities (explicitly mark unknown as `"Undeclared"`), and formally mark data as `"Flag as Triangulated"`. **(Gate 2: Strictly 1 chunk per turn, stop for user approval)**.
5. **Synthesis**: Aggregate corroborated data points into high-confidence strategic findings. **(Gate 3: Explicit approval before running export engine)**.

---

## Polished Multi-Format Deliverables

- **`.xlsx`**: Formatted 8-column spreadsheet with deep navy headers, alternating row striping, auto-adjusted column widths, and emerald highlights for `Highest` confidence claims and `Flag as Triangulated` status.
- **`.csv`**: UTF-8 machine-readable tabular matrix containing all 8 standard audit columns.
- **`.docx`**: Fluff-free, high-density bullet dossier with **all numbers, metrics, and currency automatically bolded** and linked to source data point citations (`[DP-#]`).

---

## 3-Phase Lifecycle & Approval Gates

```
┌────────────────────────────────────────────────────────┐
│ Phase 1: Planning (/sherlock <topic>)                  │
│ • Frame ./<topic_slug>/research_plan.txt               │
│ • Deconstruct topic into 3–8 MECE focus chunks         │
│ • Generate ./<topic_slug>/outline.yaml                 │
│ • [GATE 1]: User reviews and approves before Chunk 1   │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│ Phase 2: Execution (/sherlock-deep)                    │
│ • Strictly 1 Chunk Per Prompt Turn                     │
│ • Multi-hop search (query variations) -> Scraping      │
│ • Triangulate across 2+ independent sources            │
│ • Secondary search verification loop (Snippet Grep)    │
│ • Mark "Flag as Triangulated" or "Undeclared"          │
│ • Save ./<topic_slug>/results/chunk_NN_<slug>.json     │
│ • [GATE 2]: User approval before next chunk            │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│ Phase 3: Reporting (/sherlock-report)                  │
│ • [GATE 3]: User explicitly confirms report generation │
│ • Run scripts/export_sherlock.py                       │
│ • Generate <topic>_report.xlsx (8-column matrix)       │
│ • Generate <topic>_report.csv (Raw data points)        │
│ • Generate <topic>_report.docx (Bolded metric dossier) │
└────────────────────────────────────────────────────────┘
```

---

## Repository Structure

```
sherlock-skill/
├── .gitignore
├── LICENSE
├── README.md
├── SKILL.md                 # Universal agent skill specification
├── requirements.txt         # Python dependencies for report exporter
├── scripts/
│   └── export_sherlock.py   # Multi-format export engine (XLSX, CSV, DOCX)
└── examples/
    ├── outline.example.yaml # Reference outline specification
    └── chunk_01_example.json# Reference verified data point chunk
```

---

## Installation & Setup

### 1. Python Environment

The export engine requires Python 3.10+ and standard spreadsheet/document libraries:

```bash
pip install -r requirements.txt
```

### 2. Installing to Agent Frameworks

#### Google Antigravity / Gemini CLI
To install globally across all workspaces:
```bash
# Windows
mkdir "%USERPROFILE%\.gemini\config\skills\sherlock"
xcopy /E /I sherlock-skill "%USERPROFILE%\.gemini\config\skills\sherlock"

# macOS / Linux
mkdir -p ~/.gemini/config/skills/sherlock
cp -r ./* ~/.gemini/config/skills/sherlock/
```

To install for a single workspace:
```bash
mkdir -p .agents/skills/sherlock
cp -r ./* .agents/skills/sherlock/
```

#### Claude Code
Link or copy into your Claude Code skills or rules directory:
```bash
mkdir -p .claude/skills/sherlock
cp -r ./* .claude/skills/sherlock/
```

#### OpenAI Codex / Cursor / Custom Agents
Place `SKILL.md` inside your agent's custom instructions or prompt system.

---

## Usage

### 1. Start an Investigation
In your agent session, run:
```
/sherlock <topic>
```
*Example:* `/sherlock European Neobanks Unit Economics`

Sherlock creates `./european_neobanks/outline.yaml` and presents the proposed research chunks for approval.

### 2. Execute Research Chunks
Run each chunk interactively:
```
/sherlock-deep
```
Sherlock processes chunk 1, conducts search queries, scrapes primary pages, runs secondary verification queries, saves `results/chunk_01_*.json`, and pauses for user review. Repeat until all chunks are complete.

### 3. Generate Reports
Export all findings to `.xlsx`, `.csv`, and `.docx`:
```
/sherlock-report
```
Or run the Python export engine directly from the command line:

```bash
python scripts/export_sherlock.py -d "./european_neobanks" -t "European Neobanks Unit Economics"
```

Output files generated:
- `./european_neobanks/european_neobanks_report.xlsx`
- `./european_neobanks/european_neobanks_report.csv`
- `./european_neobanks/european_neobanks_report.docx`

---

## 7 Standard Audit Columns

Every data point extracted by Sherlock adheres to this exact verification schema:

| Column | Description |
|---|---|
| `sr no` | Unique sequential identifier (`1`, `2`, `3`...) |
| `data point` | Concise, specific fact or quantitative metric |
| `exact url/subpage` | Full canonical URL where fact was found |
| `quoted text from page` | Verbatim text string copied from the scraped page |
| `a search query with that data point` | Secondary targeted query used to verify fact |
| `grep from running his search query` | Exact matching snippet returned by search engine |
| `confidence score based on rechecking` | `Highest` (corroborated), `Medium`, or `Low` |

---

## License

MIT License. See [LICENSE](LICENSE) for details.
