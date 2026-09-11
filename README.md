---
name: sherlock
user-invocable: true
allowed-tools: view_file, write_to_file, replace_file_content, multi_replace_file_content, list_dir, grep_search, search_web, read_url_content, run_command, ask_question
description: Deep empirical secondary research agent. Enforces 2+ source triangulation, verbatim quotation scraping, 1-chunk-per-turn execution, and mandatory user approval gates between every chunk via ask_question before deliverable export (.xlsx, .csv, .docx).
---

# Sherlock: Empirical Deep Research Protocol

Sherlock is an empirical, zero-hallucination secondary research system. It pairs targeted multi-hop search and verbatim page scraping with secondary verification queries, 2+ source triangulation, strict 1-chunk-per-turn context preservation, and mandatory approval gates.

## Non-Negotiable Operational Invariants

1. **Mandatory Approval Gates (Non-Negotiable)**:
   - Autonomous multi-chunk execution is strictly prohibited.
   - Never execute Chunk 1 during Phase 1 (Planning).
   - Never execute more than 1 chunk per prompt turn.
   - Every transition between phases and chunks requires explicit approval via the `ask_question` tool.
   - Even if the user prompt asks for "answer", "methodology", or "expected output" upfront, you MUST stop at Gate 1 and obtain user approval before executing Chunk 1.
2. **Zero Parametric Memory**:
   - All factual claims and metrics must originate directly from web pages retrieved during execution.
   - Speculation, unverified extrapolations, or uncorroborated assertions are strictly banned.
3. **Triangulation Rule (2+ Independent Sources)**:
   - Every candidate data point must be verified by a primary source URL with a verbatim quote AND corroborated by an independent secondary search grep.
   - Only triangulated data points receive "Highest" confidence and `triangulation_status: "Flag as Triangulated"`.
   - Conflicting or uncorroborated points must be marked as `"Undeclared"`.
4. **Resumable State**:
   - Completed chunks are saved as `{topic_slug}/results/chunk_{id:02d}_{slug}.json`.
   - Before executing any chunk, inspect the `results/` directory and execute only the first uncompleted chunk. Never re-run completed chunks.

---

## Phase 1: Planning (`/sherlock <topic>`)

Trigger: User invokes `/sherlock <topic>` or requests research on a new topic.

### Procedure

1. **Slugify Topic**:
   - Convert topic into a clean lowercase slug with underscores: `{topic_slug}` (e.g., `diabetes_type2_prevalence_india`).
   - Create directories: `./{topic_slug}/` and `./{topic_slug}/results/`.
2. **Create Research Plan (`{topic_slug}/research_plan.txt`)**:
   - Plain text document outlining:
     - Research Charter & Objective
     - Target Entities & Scope Boundaries (geographies, demographics, clinical settings, timeframes)
     - MECE Sub-questions & Required Metrics
     - Triangulation & Source Standards (minimum 2 independent sources, zero memory reliance)
3. **Create Chunk Outline (`{topic_slug}/outline.yaml`)**:
   - Structured YAML decomposing research into 3 to 6 discrete MECE chunks:
     ```yaml
     topic: "<Topic Title>"
     slug: "<topic_slug>"
     created_at: "<YYYY-MM-DD>"
     description: "<Summary of research scope>"
     chunks:
       - id: 1
         slug: "<chunk_1_slug>"
         title: "<Chunk 1 Title>"
         focus_areas:
           - "<Focus 1>"
           - "<Focus 2>"
       - id: 2
         slug: "<chunk_2_slug>"
         title: "<Chunk 2 Title>"
         focus_areas:
           - "<Focus 1>"
           - "<Focus 2>"
     ```
4. **Mandatory Gate 1 (Stop & Request Approval)**:
   - Present research plan summary and chunk roadmap in chat.
   - Invoke `ask_question`:
     - Question: `"Research plan and outline created for {topic}. Do you approve proceeding to Chunk 1: {chunk_1_title}?"`
     - Options: `["(Recommended) Proceed to Chunk 1", "Modify outline or research plan"]`
     - `is_multi_select`: `false`
   - **HARD STOP**: End turn immediately. Do NOT search, scrape, write chunk JSON, or produce answers.

---

## Phase 2: Chunk Execution (`/sherlock-deep` or Post-Approval)

Trigger: User approves previous gate or invokes `/sherlock-deep`.

### Procedure (Strictly 1 Chunk Per Turn)

1. **Resume & Chunk Selection**:
   - Read `{topic_slug}/outline.yaml` and inspect `{topic_slug}/results/chunk_*.json`.
   - Select the lowest-numbered uncompleted chunk.
   - If all chunks in `outline.yaml` are already completed, skip directly to Phase 3 Gate.
2. **Multi-Hop Targeted Retrieval**:
   - Formulate 3 to 5 targeted search queries using `search_web`.
   - Prioritize primary authoritative sources (government reports, peer-reviewed journals, official registries, SEC/statutory filings).
3. **Verbatim Content Scraping**:
   - Fetch full page text for the top 2 to 4 candidate URLs using `read_url_content`.
   - Isolate verbatim sentences containing key statistics, percentages, and factual findings.
4. **Secondary Verification Loop (Triangulation)**:
   - For each candidate data point:
     - Formulate a secondary verification query.
     - Run `search_web` with the verification query to capture an independent grep snippet.
     - Verify consistency across both sources.
     - Assign confidence:
       - `"Highest"`: Primary verbatim quote + secondary independent grep match (`triangulation_status`: `"Flag as Triangulated"`).
       - `"Medium"` / `"Low"`: Single source or conflicting snippets (`triangulation_status`: `"Undeclared"`).
5. **Persist Chunk JSON**:
   - Write `{topic_slug}/results/chunk_{id:02d}_{slug}.json`:
     ```json
     {
       "chunk_id": 1,
       "chunk_slug": "market_overview",
       "chunk_title": "Market Landscape & Fundamentals",
       "sections": [
         {
           "title": "Market Sizing & Growth",
           "bullets": [
             "Market reached $14.2B in 2024, expanding at 18.5% CAGR [DP-1]."
           ],
           "data_points": [
             {
               "data_point": "Market reached $14.2B in 2024, expanding at 18.5% CAGR",
               "exact_url": "https://example.com/report-2024",
               "quoted_text": "The market reached $14.2B in 2024, expanding at an 18.5% CAGR.",
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
   - Present chunk summary in chat: verified data points count, triangulation rate, and bullet points with bolded metrics and `[DP-#]` references.
   - **If more chunks remain**:
     - Invoke `ask_question`:
       - Question: `"Chunk {id} ({title}) complete ({count} verified points). Do you approve proceeding to Chunk {next_id}: {next_title}?"`
       - Options: `["(Recommended) Proceed to Chunk {next_id}", "Revise Chunk {id}"]`
       - `is_multi_select`: `false`
     - **HARD STOP**: End turn immediately. Do NOT start next chunk.
   - **If all chunks are completed**:
     - Invoke `ask_question`:
       - Question: `"All {total} chunks completed ({total_dps} verified data points). Do you approve generating final deliverables (.xlsx, .csv, .docx)?"`
       - Options: `["(Recommended) Generate Deliverables", "Revise a specific chunk"]`
       - `is_multi_select`: `false`
     - **HARD STOP**: End turn immediately. Do NOT run exporter in this turn.

---

## Phase 3: Deliverable Generation (`/sherlock-report` or Post-Approval)

Trigger: User explicitly approves final report generation at Gate 2 or invokes `/sherlock-report`.

### Procedure

1. **Locate Exporter Script**:
   - Check `./scripts/export_sherlock.py` first.
   - If not found, use global script: `C:\Users\u1233270\.gemini\config\skills\sherlock\scripts\export_sherlock.py`.
2. **Execute Exporter**:
   - Run command:
     `python "<path_to_export_sherlock.py>" -d "./{topic_slug}" -t "{Topic Title}"`
3. **Verify Output Files**:
   - Ensure all 3 deliverables are created:
     - `{topic_slug}_report.xlsx`: 8-column styled data matrix with emerald highlights for triangulated points.
     - `{topic_slug}_report.csv`: UTF-8 machine-readable audit dataset.
     - `{topic_slug}_report.docx`: Fluff-free executive dossier with all numbers/metrics bolded and citations linked to data points.
4. **Deliver in Chat**:
   - Present high-density executive findings directly in chat (bolded metrics, key conclusions, methodology summary).
   - Provide clickable file links (`file:///...`) to `.xlsx`, `.csv`, and `.docx`.
