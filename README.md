# Sherlock: Empirical Deep Research Agent

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](https://www.python.org/)
[![Status: Production](https://img.shields.io/badge/Status-Production-emerald.svg)](#)

**Sherlock** is an unhurried, zero-hallucination empirical deep research skill for autonomous coding and research agents. It combines multi-hop web retrieval and verbatim page scraping with an empirical double-search verification loop, strict 1-chunk-per-turn context preservation, and automated multi-format reporting (`.xlsx`, `.csv`, `.docx`).

---

## Key Pillars

1. **Zero Hallucination & Verbatim Grounding**: No unsupported claims. Every single assertion must have an exact URL and verbatim quotation scraped directly from the authoritative page.
2. **Empirical Double-Check Verification Loop**: Every candidate data point is cross-verified via a secondary targeted search engine query. The exact search engine snippet match is logged. Only corroborated, `Highest`-confidence data points survive into the executive report.
3. **1 Chunk Per Prompt Turn**: Deep research quickly exhausts LLM context windows. Sherlock decomposes any topic into 3–8 self-contained chunks and processes **strictly 1 chunk per prompt turn** with human-in-the-loop checkpoints. This reserves 100% of the model's context for scraping, deep reasoning, and verification.
4. **Resumable State**: Results are persisted per chunk in `results/chunk_*.json`. If interrupted, Sherlock resumes automatically at the first uncompleted chunk without repeating prior work.
5. **Polished Multi-Format Deliverables**:
   - **`.xlsx`**: Formatted spreadsheet with deep navy headers, alternating row striping, auto-adjusted column widths, and emerald highlights for `Highest` confidence claims.
   - **`.csv`**: UTF-8 machine-readable tabular matrix containing all 7 standard audit columns.
   - **`.docx`**: Fluff-free, high-density bullet dossier with **all numbers, metrics, and currency automatically bolded** and linked to source data point citations (`[DP-#]`).

---

## 3-Phase Lifecycle

```
┌────────────────────────────────────────────────────────┐
│ Phase 1: Planning (/sherlock <topic>)                  │
│ • Deconstruct topic into 3–8 focus chunks              │
│ • Generate ./<topic_slug>/outline.yaml                 │
│ • User reviews and confirms outline                    │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│ Phase 2: Execution (/sherlock-deep)                    │
│ • 1 Chunk Per Prompt Turn                              │
│ • Multi-hop search -> Verbatim scraping                │
│ • Secondary search verification loop (Snippet Grep)    │
│ • Save ./<topic_slug>/results/chunk_NN_<slug>.json     │
│ • Human-in-the-loop approval before next chunk         │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│ Phase 3: Reporting (/sherlock-report)                  │
│ • Run scripts/export_sherlock.py                       │
│ • Generate <topic>_report.xlsx (Styled matrix)         │
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
