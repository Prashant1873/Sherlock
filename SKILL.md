---
name: sherlock
description: "Autonomous empirical deep research engine where data accuracy is the absolute #1 target. Automatically activate when the user requests comprehensive secondary research, industry or clinical pipeline benchmarking, market sizing, financial/PE due diligence, enterprise IT TCO comparisons, 2+ source triangulation, verbatim quotation scraping, or publication-grade deliverables (.docx, .xlsx, .pdf). Enforces strict 1-chunk-per-turn execution and mandatory interactive human approval gates. DO NOT activate for casual questions, simple factual definitions, quick programming lookups, or shallow summaries."
version: 4.0.0
license: MIT
user-invocable: true
allowed-tools:
  - view_file
  - write_to_file
  - replace_file_content
  - multi_replace_file_content
  - list_dir
  - grep_search
  - search_web
  - read_url_content
  - run_command
  - ask_question
compatibility:
  - antigravity
  - claude-code
  - cursor
  - codex
  - opencode
---

# Sherlock: Empirical Deep Research Protocol

Sherlock is an empirical, zero-hallucination secondary research system where **data accuracy is the absolute #1 target**. Inaccuracies, approximations, and speculative extrapolations are strictly prohibited. It pairs multi-hop search and verbatim scraping with secondary verification queries, 2+ source triangulation, strict 1-chunk-per-turn execution, and mandatory human approval gates.

## Multi-IDE Runtime & Tool Compatibility Matrix

Sherlock operates across Google Antigravity, Anthropic Claude Code, Cursor, OpenAI Codex, and OpenCode. Downstream agents must map functional roles to their host environment tools:

| Functional Role | Antigravity | Claude Code | Cursor | OpenAI Codex | OpenCode |
|---|---|---|---|---|---|
| **Interactive Approval Gate** | `ask_question` | `AskFollowupQuestion` | `ask_followup_question` / `vscode_askquestions` | Terminal user input / prompt | `ask_question` / terminal prompt |
| **Web Search** | `search_web` | `WebSearch` | `web_search` | `search_web` / web search tool | `web_search` / search tool |
| **Web Fetch & Scraping** | `read_url_content` | `WebFetch` | `fetch` / `read_url_content` | `read_url_content` / HTTP fetch | `read_url_content` / HTTP get |
| **Shell & Exporter Runner** | `run_command` | `Bash` | `terminal` / `run_command` | `run_command` / bash | `run_command` / bash |
| **File Reading** | `view_file` | `View` | `read_file` / `view_file` | `view_file` / `cat` | `view_file` / `read_file` |
| **File Writing & Editing** | `write_to_file` / `replace_file_content` | `Edit` / `Write` | `write_to_file` / `edit_file` | `write_to_file` / file edit | `write_to_file` / `edit_file` |

*Invariant rule:* Pause at every gate (Gate 0 Intake, Gate 1 Charter Approval, Gate 2 Chunk Transitions & Report Generation, Gate 3 Handoff) using the interactive prompt tool available in that runtime.

## Non-Negotiable Operational Invariants

1. **Absolute Data Accuracy (#1 Target)**: Zero tolerance for inaccuracies. Claims without 100% empirical verification against retrieved quotes and corroborating secondary search results must be rejected or marked `"triangulation_status": "Undeclared"`.
2. **Mandatory Approval Gates**: Autonomous multi-chunk execution is prohibited. Stop at Gate 0 (Intake), Gate 1 (Charter), Gate 2 (Chunk Transitions/Formats), and Gate 3 (Handoff) via interactive prompt. Max 1 chunk per turn.
3. **Zero Parametric Memory**: Every factual claim must originate directly from retrieved web pages with verbatim quotes.
4. **Triangulation Rule (2+ Independent Sources)**: Candidate points require a primary verbatim quote and an independent secondary grep. To earn `"Highest"` confidence and `"triangulation_status": "Flag as Triangulated"`, at least one source MUST be Tier 1 or Tier 2. Tier 3 only is capped at `"Medium"`.
5. **Resumable State**: Chunks persist in `{topic_slug}/results/chunk_{id:02d}_{slug}.json`. Read existing results and execute only the first uncompleted chunk.
6. **Executive Summary & "So What?"**: Deliverables must open with a synthesized Executive Summary followed by actionable Strategic Implications ("So What?").
7. **Comparative Matrices**: When query requires comparative benchmarks (cohorts, competitors, geographies, treatments), produce structured matrix tables.
8. **Clean Typography**: Zero raw markdown asterisks (`**`) in document bodies; use Segoe UI typography and styled `[DP-#]` citation badges.

---

## Phase 0: Socratic Intake & Problem Formulation (`/sherlock <topic> [domain] [--format all|docx|xlsx|pdf] [--include-datasets]`)

Trigger: User invokes `/sherlock <topic> [domain]` or prompts for empirical research.

### Parameters & Prompt Flags
- Domain: `pharma`, `tech`, `finance`, `legal`, `admin`, `ai`, `general`.
- Format: `--format all` (default), `--format docx`, `--format xlsx`, `--format pdf`, or comma-separated subsets (e.g., `--format docx,pdf`).
- Dataset: `--include-datasets` (extracts tabular datasets into dedicated Excel tabs with native charts).
*(Note: Users interact purely via chat; the agent executes exporter commands transparently).*

### Procedure
1. **Intake Cross-Questioning**:
   - If `[domain]` not supplied, ask user to select from domain registries: `pharma`, `tech`, `finance`, `legal`, `admin`, `ai`, `general`.
   - Probe key intake dimensions: Target Audience (C-Suite, Architects, Regulators), Core Decision at Stake, Scope Boundaries & Exclusions, and Baseline Hypotheses.
2. **Mandatory Gate 0 (Stop & Await User Response)**:
   - Call `ask_question` with intake questionnaire.
   - **HARD STOP**: End turn immediately. Do not generate research plan or execute searches until user responds.

---

## Phase 1: Planning (Post-Intake Gate 0)

Trigger: User responds to Gate 0 with problem context, domain, and scope.

### Procedure
1. **Slugify & Directory Structure**: Convert topic to `{topic_slug}` (lowercase, underscores). Create `./{topic_slug}/` and `./{topic_slug}/results/`.
2. **Research Charter (`{topic_slug}/research_plan.txt`)**: Formalize binding contract:
   - Executive Context & Audience, Scope & Exclusions, Empirical Hypotheses (`[HYP-1]`, `[HYP-2]`), MECE Sub-Questions & Metrics, Triangulation Standards.
3. **Chunk Outline (`{topic_slug}/outline.yaml`)**: Decompose into 3–6 discrete MECE chunks aligned with active domain framework:
   ```yaml
   topic: "<Topic Title>"
   slug: "<topic_slug>"
   domain: "<pharma|tech|finance|legal|admin|ai|general>"
   created_at: "<YYYY-MM-DD>"
   requires_comparative_matrix: true
   chunks:
     - id: 1
       slug: "<chunk_1_slug>"
       title: "<Chunk 1 Title>"
       focus_areas: ["<Focus 1>", "<Focus 2>"]
     - id: 2
       slug: "<chunk_2_slug>"
       title: "<Chunk 2 Title>"
       focus_areas: ["<Focus 1>", "<Focus 2>"]
   ```
4. **Mandatory Gate 1 (Stop & Request Approval)**:
   - Present charter and chunk outline.
   - Invoke `ask_question`:
     - Question: `"Research plan created for {topic} [{domain}]. Approve proceeding to Chunk 1: {chunk_1_title}?"`
     - Options: `["(Recommended) Proceed to Chunk 1", "Modify outline or research plan"]`
   - **HARD STOP**: End turn immediately. Do not execute Chunk 1.

---

## Domain-Specialized Investigation Frameworks

Adhere to the active domain's empirical standards during planning and execution:

| Domain | Focus Areas | Required Metrics & Standards |
|---|---|---|
| **Pharma & Healthcare (`pharma`)** | Clinical trials (Phase I–IV), OS, PFS, ORR, AE grades 3–4, HR, FDA/EMA regulatory status, WAC pricing, LOE dates. | Sample size ($N$), p-values ($p < 0.05$), 95% CI, median duration in months. |
| **Technology & IT (`tech`)** | System architecture, throughput (RPS), p50/p95/p99 latency, GitHub metrics, pricing, SLAs, SOC 2 / ISO 27001. | Benchmark figures, hardware/cloud specs, verified version numbers. |
| **Finance, PE & M&A (`finance`)** | TAM/SAM/SOM, CAGR, EV/ARR, EV/EBITDA, P/E, CAC, LTV, NRR, churn %, gross margins %, CapEx/OpEx. | Audited GAAP/IFRS figures, reporting period (FY24, Q2'25), currency codes. |
| **Legal & Policy (`legal`)** | Governing statutes (CFR, USC, EU Directives), regulatory orders, consent decrees, appellate/Supreme precedent, compliance liabilities. | Official statutory citations, case docket numbers, civil penalty amounts. |
| **Public Admin (`admin`)** | Legislative rollout, congressional appropriations, obligated vs expended funds, beneficiary reach, GAO/OIG performance audits. | Appropriation line items ($), verified participant counts, deficiency counts. |
| **AI & ML (`ai`)** | Benchmark scores (MMLU, HumanEval, Arena Elo), compute/scaling (FLOPs, H100 hours), TTFT, TPS, API pricing, refusal/alignment evaluations. | Exact benchmark %, token pricing with date stamps, model architecture IDs. |
| **General (`general`)** | Problem definition, multi-stakeholder impact, empirical timeline of events, quantitative benchmarks, operational trade-offs. | Verifiable units of measure, baseline years, sample size. |

---

## Source Authority & Whitelist Registries

Curated whitelists serve as starting anchors, never walls. See [references/source_whitelists.md](references/source_whitelists.md) and [references/3_tier_hierarchy.md](references/3_tier_hierarchy.md) for complete details.

### 3-Tier Authority Hierarchy
- **Tier 1 (Primary / Regulatory / Peer-Reviewed)**: Government portals (`fda.gov`, `sec.gov`, `congress.gov`), clinical registries (`clinicaltrials.gov`), peer-reviewed journals (*Lancet*, *NEJM*, *JAMA*, *Nature*, IEEE), central banks (Fed, ECB, BLS).
- **Tier 2 (Institutional / Audited)**: Multilateral bodies (World Bank, IMF, OECD, WHO), standards organizations (ISO, NIST, IETF), audited corporate disclosures, academic repositories (arXiv).
- **Tier 3 (Secondary / Industry Media)**: Trade press (*TechCrunch*, *Endpoints News*, *Bloomberg*), market aggregators (Gartner, Statista), corporate collateral.

### Triangulation Standards
- **Triangulation Rule**: To qualify for `"triangulation_status": "Flag as Triangulated"` and `"confidence_score": "Highest"`, at least one source MUST be Tier 1 or Tier 2. Findings supported solely by Tier 3 sources are assigned `"confidence_score": "Medium"` and `"triangulation_status": "Undeclared"`.
- **Conflict Adjudication**: When authoritative sources disagree, never average or synthesize them. Assign `"triangulation_status": "Conflict"` and `"confidence_score": "Conflict - Adjudicated"` with a structured `conflict_adjudication` block detailing both sources, metrics, and root cause of variance.

---

## Phase 2: Chunk Execution (`/sherlock-deep` or Post-Approval)

Trigger: User approves previous gate or invokes `/sherlock-deep`.

### Procedure (Strictly 1 Chunk Per Turn)
1. **Resume & Chunk Selection**: Read `{topic_slug}/outline.yaml` and inspect `{topic_slug}/results/chunk_*.json`. Select lowest uncompleted chunk.
2. **Progressive 3-Wave Discovery**:
   - *Wave 1 (Whitelist Anchors)*: 2–3 queries targeting domain registries (`site:` operators) for baseline facts.
   - *Wave 2 (Broad Institutional Discovery)*: Expand across open-web academic, government, and industry repositories.
   - *Wave 3 (Open-Web Triangulation)*: Target secondary queries to cross-verify metrics and capture independent grep snippets.
3. **Verbatim Content Scraping**: Fetch top 2–4 URLs via `read_url_content`. Extract exact sentences with statistics.
4. **Secondary Verification Loop**: Formulate secondary search queries via `search_web`. Verify quotes against grep matches.
5. **Persist Chunk JSON (`{topic_slug}/results/chunk_{id:02d}_{slug}.json`)**:
   ```json
   {
     "chunk_id": 1,
     "chunk_slug": "market_overview",
     "chunk_title": "Market Landscape & Fundamentals",
     "sections": [
       {
         "title": "Market Sizing & Growth",
         "bullets": ["Market reached $14.2B in 2024, expanding at 18.5% CAGR [DP-1]."],
         "comparative_matrix": {
           "title": "Segment Growth Benchmark",
           "headers": ["Segment", "Market Size (2024)", "CAGR", "Key Driver"],
           "rows": [["Enterprise", "$9.2B", "21.0%", "Cloud adoption [DP-1]"]]
         },
         "data_points": [
           {
             "data_point": "Market reached $14.2B in 2024, expanding at 18.5% CAGR",
             "exact_url": "https://example.com/report-2024",
             "quoted_text": "The market reached $14.2B in 2024, expanding at an 18.5% CAGR.",
             "source_tier": "Tier 1",
             "verification_query": "\"market reached $14.2B\" \"18.5% CAGR\"",
             "grep_result": "...market reached $14.2B in 2024 with an 18.5% CAGR...",
             "confidence_score": "Highest",
             "triangulation_status": "Flag as Triangulated"
           }
         ]
       }
     ]
   }
   ```
6. **Mandatory Gate 2 (Stop & Request Approval)**:
   - Present chunk summary in chat: verified points count, triangulation rate, and clean bullet points with `[DP-#]` references.
   - If more chunks remain: invoke `ask_question` to approve proceeding to next chunk. **HARD STOP**.
   - If all chunks complete: invoke `ask_question` to select deliverable format (`all`, `docx`, `xlsx`, `pdf`). **HARD STOP**.

---

## Phase 3: Deliverable Generation (`/sherlock-report` or Post-Approval)

Trigger: User approves report generation at Gate 2 or invokes `/sherlock-report`.

### Procedure
1. **Synthesize Metadata (`{topic_slug}/executive_summary.json`)**:
   Write BLUF, executive summary findings, KPI scorecard, strategic implications ("So What?"), comparative matrices, datasets, and evidence quality audit.
2. **Execute Exporter**:
   Map user selection to CLI argument (`all` → `-f all`, `docx` → `-f docx`, `xlsx` → `-f xlsx`, `pdf` → `-f pdf`, or `docx,pdf`):
   ```bash
   python scripts/export_sherlock.py -d "./{topic_slug}" -t "{Topic Title}" -f "{format_flag}"
   ```
3. **Verify Deliverables**:
   - `{topic_slug}_report.xlsx`: Multi-sheet workbook (Verified Data Points with emerald highlights, Executive Summary, Comparative Matrix, and Native OpenPyXL Charts tabs).
   - `{topic_slug}_report.csv`: Machine-readable audit dataset.
   - `{topic_slug}_report.docx`: Executive dossier (Header preamble, 1-page briefing memo with BLUF callout and KPI table, deep-dive findings, conflict log, and data points index in Segoe UI typography).
   - `{topic_slug}_report.pdf`: Direct vector PDF preserving all layout and styling.
4. **Deliver in Chat & Gate 3 (Final Review & Handoff)**:
   - Present executive summary, "So What?", key highlights, and evidence audit scorecard in chat.
   - Provide clickable file links (`file:///...`) for generated deliverables (`.docx`, `.xlsx`, `.pdf`).
   - Gate 3 Handoff Prompt: Ask user via `ask_question` if they would like to explore follow-up hypotheses or conduct additional investigations.
