# Sherlock: Empirical Deep Research Agent

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Version: 4.0.0](https://img.shields.io/badge/Version-4.0.0-emerald.svg)](SKILL.md)
[![Compatibility: Universal Multi-IDE](https://img.shields.io/badge/Compatibility-Antigravity%20%7C%20Claude%20%7C%20Cursor%20%7C%20Codex%20%7C%20OpenCode-blueviolet.svg)](SKILL.md)
[![Zero Hallucinations](https://img.shields.io/badge/Triangulation-2%2B%20Sources-brightgreen.svg)](references/3_tier_hierarchy.md)

> **Zero-hallucination empirical secondary research protocol for AI agents where data accuracy is the absolute #1 target.**

Sherlock is an open-source agent skill designed for major AI environments (**Google Antigravity**, **Anthropic Claude Code**, **Cursor**, **OpenAI Codex**, and **OpenCode**) that elevates your AI agent into an exhaustive, publication-grade research analyst. It pairs targeted multi-hop search and verbatim source scraping with secondary verification queries, 2+ source triangulation, strict 1-chunk-per-turn context preservation, and interactive human-in-the-loop approval gates.

---

## ⚡ How It Works (Zero Scripts Needed)

> **Important**: You interact with Sherlock **purely through your AI chat interface**. You do **not** need to run Python scripts or terminal commands manually. Sherlock conducts the investigation, manages state, synthesizes findings, and automatically renders publication-grade deliverables on your behalf.

### Quick Start

Simply type the slash command in your agent chat:

```bash
/sherlock <topic> [domain] [flags]
```

#### Examples:

- **Pharma & Healthcare:**
  ```bash
  /sherlock "ADC clinical trial survival rates" pharma --format all --include-datasets
  ```
- **Enterprise Technology:**
  ```bash
  /sherlock "Kubernetes vs serverless TCO in banking" tech --format docx,pdf
  ```
- **Finance & Private Equity:**
  ```bash
  /sherlock "Global enterprise SaaS EBITDA multiples 2024" finance --format all
  ```
- **General / Cross-Domain Research:**
  ```bash
  /sherlock "Renewable energy battery storage capex trends" --include-datasets
  ```

---

## 🎛️ Command Options & Flags

When invoking `/sherlock`, you can pass optional parameters to tailor the investigation upfront:

| Option / Flag | Purpose | Examples / Values |
|---------------|---------|-------------------|
| `[domain]` | Focuses research on specialized investigation frameworks and trusted whitelists | `pharma`, `tech`, `finance`, `legal`, `admin`, `ai`, `general` |
| `--format <selection>` | Specifies which deliverable files to generate at completion | `all` (default), `docx`, `xlsx`, `pdf`, `docx,pdf`, `xlsx,pdf` |
| `--include-datasets` | Pulls structured quantitative series into dedicated Excel tabs with native interactive charts | Flag present / omitted |

*(Note: Even if you do not specify flags upfront, Sherlock will interactively prompt you at Gate 0 and Gate 2).*

---

## 🚦 Human-in-the-Loop Workflow (The 4 Gates)

Sherlock is built on strict **context preservation** and **human oversight**. It never runs wild or generates unchecked volumes. Between every stage, Sherlock pauses and presents clear choices:

```mermaid
graph TD
    A["/sherlock topic"] --> B["Gate 0: Socratic Intake"]
    B -->|User answers scope & audience| C["Phase 1: Research Charter & Outline"]
    C --> D["Gate 1: Charter Approval"]
    D -->|User approves plan| E["Phase 2: Chunk 1 Execution"]
    E --> F["Gate 2: Chunk Review"]
    F -->|User approves next chunk| G["Phase 2: Chunk N Execution"]
    G --> H["Gate 2: Final Format Selection"]
    H -->|User selects formats| I["Phase 3: Automated Deliverable Generation"]
    I --> J["Publication Files: .docx, .xlsx, .pdf"]
    J --> K["Gate 3: Final Review & Handoff"]
```

### Gate 0: Socratic Problem Formulation
Before doing any searches or plans, Sherlock stops to ask 5 clarifying questions:
1. **Domain Expertise Selection**: Chooses between Pharma, Tech, Finance, Legal, Admin, AI, or General.
2. **Target Audience**: Who is reading this? (e.g., C-Suite Executives, Board of Directors, Clinical Officers, Technical Architects).
3. **Core Decision at Stake**: What strategic, operational, or capital decision rides on this data?
4. **Scope Boundaries & Exclusions**: What geographies, demographics, or timeframes are in-scope vs excluded?
5. **Baseline Hypotheses**: What working numbers or hypotheses should be empirically verified or disproven?

### Gate 1: Research Charter Approval
Sherlock formalizes your answers into a binding `research_plan.txt` contract and presents a MECE chunk outline. You review and approve before any deep web crawling begins.

### Gate 2: Turn-by-Turn Chunk Review
Sherlock executes **strictly one chunk per turn** to avoid context window pollution and hallucination creep. At the end of each chunk, you see:
- Verified data points count
- Triangulation rate (% backed by 2+ sources)
- Clean bullet findings with citation references (`[DP-#]`)
- An interactive prompt asking whether to proceed to the next chunk or revise.

### Final Gate 2: Deliverable Format Selection
When all chunks are complete, Sherlock presents an interactive menu to choose your desired outputs:
- **(Recommended) All Formats (.docx, .xlsx, .pdf)**
- **Executive Word Dossier only (.docx)**
- **Analytical Data Spreadsheet only (.xlsx)**
- **Vector PDF Briefing only (.pdf)**
- **Word + PDF Dossiers (.docx, .pdf)**

Once you select your preference, Sherlock automatically runs the internal export engine and provides clickable file links in chat.

### Gate 3: Final Review & Handoff
Sherlock presents high-density executive findings directly in chat, delivers clickable deliverable links, and prompts for follow-up hypotheses or additional investigations.

---

## 📦 The Three Deliverables

Sherlock produces up to three publication-grade deliverables tailored for leadership and executive review:

### 1. Executive Dossier (`.docx`)
Designed specifically for boardrooms, investment committees, and executive directors:
- **Bottom-Line-Up-Front (BLUF)**: Navy left-accent callout box with core strategic takeaway.
- **Executive KPI Scorecard**: 4-column summary table benchmarking key empirical findings.
- **Standalone 1-Page Memo**: Self-contained briefing section followed by a clean page break.
- **Strategic Implications ("So What?")**: Actionable executive takeaways answering practical business impacts.
- **Comparative Analysis & Matrices**: Structured benchmark tables across cohorts or competitors.
- **Authoritative Conflict Adjudication Log**: Clear accounting of variances between trusted sources without artificial smoothing.
- **Verified Data Points Index**: Full audit table with Source Tier badges and exact verbatim quotes.
- **Zero Markdown Asterisks Standard**: Clean corporate typography without raw asterisks (`**`) or arbitrary number bolding.

### 2. Direct Vector PDF Briefing (`.pdf`)
A publication-ready vector PDF generated directly from the executive dossier:
- High-fidelity typography and layout.
- Crisp vector text, lines, and borders that remain sharp at any zoom level.
- Multi-engine rendering cascade: Word COM (Windows native), LibreOffice headless, or Playwright Chromium vector fallback (cross-platform).

### 3. Analytical Data Workbook (`.xlsx`) & CSV
An enterprise-grade financial/analytical spreadsheet:
- **Sheet 1 ("Verified Data Points")**: Full 9-column audit dataset with emerald green highlights for triangulated points and source tier badges.
- **Sheet 2 ("Executive Summary & Audit")**: Domain metadata banner, BLUF card, KPI scorecard, and Evidence Quality Audit metrics (Tier 1/2 distribution % and triangulation rate).
- **Sheet 3+ ("Comparative Matrices")**: Styled benchmark tables.
- **Sheet ("Charts & Datasets")** *(when `--include-datasets` is enabled)*: Dedicated tables of quantitative series dynamically bound to native **OpenPyXL visual charts** (Bar, Column, Line) with corporate color palettes.
- **Accompanying `.csv` files**: UTF-8 machine-readable tables for programmatic downstream workflows.

---

## 🛡️ Non-Negotiable Empirical Invariants

Sherlock was designed to overcome the fatal flaw of standard LLM research: **hallucinations and uncorroborated assertions**.

1. **Absolute Data Accuracy as #1 Target**: Zero tolerance for inaccuracies. If a number cannot be verified against retrieved text, it is rejected.
2. **Zero Parametric Memory**: Sherlock is forbidden from relying on internal model weights for factual claims. Every metric must come from live retrieved pages.
3. **3-Tier Source Authority Hierarchy**:
   - **Tier 1 (Primary / Regulatory / Peer-Reviewed)**: FDA, SEC EDGAR, ClinicalTrials.gov, PubMed, Central Banks, Census Bureau.
   - **Tier 2 (Institutional / Audited)**: World Bank, IMF, OECD, ISO, NIST, audited financial reports.
   - **Tier 3 (Secondary / Industry Media)**: TechCrunch, trade press, market blogs.
4. **2+ Independent Source Triangulation**: To earn "Highest" confidence, a claim must have a verbatim primary source quote AND be corroborated by an independent secondary search grep—with at least one Tier 1 or Tier 2 authority.
5. **Authoritative Conflict Adjudication**: When two authoritative sources conflict (e.g. FDA vs WHO), Sherlock **never averages or smooths** the figures. It logs both values, dates, and methodologies, diagnosing the root cause of variance.
6. **Clean Typography**: Eliminates markdown formatting noise—zero raw asterisks around text or metrics.

---

## 🌐 Universal Multi-IDE Compatibility

Sherlock supports all leading AI developer runtimes through standardized frontmatter and dynamic tool mapping:

| Runtime | Skill Installation Path | Tool Mapping |
|---|---|---|
| **Google Antigravity** | `~/.gemini/config/skills/sherlock` or `.agents/skills/sherlock` | `ask_question`, `search_web`, `read_url_content`, `run_command` |
| **Anthropic Claude Code** | `~/.claude/skills/sherlock` or `.claude/skills/sherlock` | `AskFollowupQuestion`, `WebSearch`, `WebFetch`, `Bash` |
| **Cursor** | `.cursor/skills/sherlock` or `.cursorrules` | `ask_followup_question`, `web_search`, `fetch`, `terminal` |
| **OpenAI Codex** | `.codex/skills/sherlock` or `.agents/skills/sherlock` | Native terminal prompt, web search, scraper, `run_command` |
| **OpenCode** | `.opencode/skills/sherlock` or `.agents/skills/sherlock` | `ask_question`, `web_search`, `read_url_content`, `run_command` |

---

## 🔧 Installation & Setup

### 1-Command Installation

#### Google Antigravity
```bash
git clone https://github.com/Prashant1873/Sherlock.git ~/.gemini/config/skills/sherlock
```
*Windows PowerShell:*
```powershell
git clone https://github.com/Prashant1873/Sherlock.git "$HOME\.gemini\config\skills\sherlock"
```

#### Anthropic Claude Code
```bash
git clone https://github.com/Prashant1873/Sherlock.git ~/.claude/skills/sherlock
```

#### Cursor
```bash
git clone https://github.com/Prashant1873/Sherlock.git .cursor/skills/sherlock
```

#### OpenAI Codex / OpenCode
```bash
git clone https://github.com/Prashant1873/Sherlock.git .agents/skills/sherlock
```

### Python Dependencies

Install the export engine libraries:

```bash
pip install openpyxl python-docx pandas playwright
playwright install chromium
```
*(On Windows, `pywin32` is optional for native Word COM vector PDF export. If running in Linux/macOS or headless environments, Playwright or LibreOffice automatically handles vector PDF generation).*

---

## 🤖 Auto-Activation & Multi-IDE Rules Integration

Sherlock supports **zero-command semantic auto-activation**. When configured, the host AI agent automatically detects prompts requiring empirical secondary research, clinical benchmarking, or market due diligence, and enters Sherlock Phase 0 Intake—while remaining completely dormant on everyday queries.

### Integration Templates (`rules/`)

Drop the matching template from `rules/` into your workspace root or global agent config:

| IDE Platform | Template File | Installation Target |
|---|---|---|
| **Google Antigravity** | `rules/GEMINI.md` | Workspace `GEMINI.md` or `.agents/GEMINI.md` |
| **Anthropic Claude Code** | `rules/CLAUDE.md` | Workspace `CLAUDE.md` or `~/.claude/CLAUDE.md` |
| **Cursor** | `rules/.cursorrules` | Workspace `.cursorrules` or `.cursor/rules/` |
| **OpenAI Codex / OpenCode** | `rules/AGENTS.md` | Workspace `AGENTS.md` or `.agents/AGENTS.md` |

### Trigger Semantics

- **Positive Activation**: Comprehensive secondary research, clinical/pharma trial benchmarking, market sizing/TAM analysis, M&A due diligence, enterprise IT TCO comparisons, 2+ source triangulation, or requests requiring publication deliverables (.docx, .xlsx, .pdf).
- **Negative Dormancy Boundaries**: Casual trivia, simple factual definitions ("What is mRNA?"), quick syntax lookups ("Python dict loop"), shallow summaries, or creative drafting.

---

## 🧪 Verification & Test Suite

Sherlock includes an automated end-to-end test suite verifying link integrity, workflow gate protocols, privacy sanitization, auto-activation rules, and export execution:

```bash
# 1. Link & cross-reference integrity (9 files)
python scripts/test_link_integrity.py

# 2. Workflow schema & approval gate audit
python scripts/test_workflow_audit.py

# 3. Privacy, local-path & secret sanitization
python scripts/test_privacy_audit.py

# 4. Auto-activation semantic triggers & rules audit
python scripts/test_auto_activation.py

# 5. Multi-format export pipeline regression
python scripts/test_export_pipeline.py
```

---

## 📁 Repository Structure

```text
sherlock/
  ├── LICENSE                               # Permissive MIT License
  ├── README.md                             # Comprehensive documentation & setup guide
  ├── SKILL.md                              # Root Universal Agent Skill Specification
  ├── skills/
  │   └── sherlock/
  │       └── SKILL.md                      # Packaged skill file for multi-IDE discovery
  ├── rules/
  │   ├── CLAUDE.md                         # Anthropic Claude Code auto-activation rules
  │   ├── GEMINI.md                         # Google Antigravity auto-activation rules
  │   ├── .cursorrules                      # Cursor auto-activation rules
  │   └── AGENTS.md                         # OpenAI Codex & OpenCode auto-activation rules
  ├── scripts/
  │   ├── export_sherlock.py                # Publication-grade multi-format export engine
  │   ├── test_export_pipeline.py           # Exporter regression test suite
  │   ├── test_link_integrity.py            # Link & path cross-reference validator
  │   ├── test_workflow_audit.py            # Protocol schema & gate validator
  │   ├── test_privacy_audit.py             # Privacy & secret sanitization validator
  │   └── test_auto_activation.py           # Semantic trigger & rule validator
  ├── templates/
  │   ├── research_plan_template.txt        # Binding research charter contract template
  │   └── executive_summary_template.json   # Executive BLUF, scorecard & datasets schema
  └── references/
      ├── 3_tier_hierarchy.md               # Source authority hierarchy & triangulation rules
      └── source_whitelists.md              # Curated domain registries & search launchpads
```

---

## 📄 License

Sherlock is licensed under the [MIT License](LICENSE). Copyright (c) 2026 Sherlock Contributors.
