---
name: sherlock
user-invocable: true
allowed-tools: Read, Write, Glob, WebSearch, Task, AskUserQuestion, Bash
description: Deep, long-running empirical Web RAG research agent. Features multi-hop search, verbatim quotation scraping, double-check verification queries, 1-chunk-per-turn context protection, and multi-format exports (.xlsx, .csv, and fluff-free .docx with bolded numbers).
---

# Sherlock: Empirical Deep Research Agent

Sherlock is an unhurried, zero-hallucination deep research system. It pairs multi-hop web retrieval and page scraping with an empirical double-search verification loop.

---

## Core Operational Principles

1. **Anti-Hallucination & Empirical Grounding**: No unsupported assertions. Every claim must have an exact URL and verbatim quote from the page.
2. **Double-Check Verification Loop**: Every extracted data point must be cross-checked with a secondary targeted verification query. The raw snippet match ("grep") is recorded, and only `Highest` confidence data survives into the final report.
3. **Mandatory Approval Gates & 1 Chunk Per Turn (NON-NEGOTIABLE)**:
   - The agent is **strictly prohibited** from running autonomous multi-chunk chains, auto-advancing across chunks, or auto-generating deliverables without user consent.
   - **Gate 1 (Planning -> Chunk 1)**: User MUST explicitly approve `outline.yaml` before Chunk 1 begins.
   - **Gate 2 (Chunk N -> Chunk N+1)**: User MUST explicitly approve each chunk's findings before the next chunk begins. Exactly 1 chunk per prompt turn.
   - **Gate 3 (Execution -> Reporting)**: User MUST explicitly approve report generation before `export_sherlock.py` is invoked.
   - Use `ask_question` or halt execution with an explicit approval prompt to block execution until user confirmation.
4. **Resumable State**: State is preserved in `results/*.json`. Completed chunks are never re-run.
5. **Separation of Concerns**:
   - **Phase 1: Planning** (`outline.yaml`) - Proposes roadmap, stops for approval.
   - **Phase 2: Execution** (`sherlock-deep`) - Exactly 1 chunk per prompt turn, stops for approval.
   - **Phase 3: Formatting & Reporting** (`sherlock-report`) - Generates `.xlsx`, `.csv`, `.docx` only after explicit confirmation.

---

## Phase 1: Planning (`/sherlock <topic>`)

When the user asks to research a topic or invokes `/sherlock <topic>`:

1. **Deconstruct Topic**:
   - Analyze scope and split into **3 to 8 discrete, self-contained chunks** (e.g., Company History, Financials & Valuation, Core Technology Architecture, Competitive Moats, Regulatory Risks).
2. **Define Directory & Config**:
   - Slugify topic: `{topic_slug}` (lowercase, underscores).
   - Create workspace directory: `./{topic_slug}/` and `./{topic_slug}/results/`.
   - Create `./{topic_slug}/outline.yaml` with:
     ```yaml
     topic: "<Topic Title>"
     slug: "<topic_slug>"
     created_at: "<YYYY-MM-DD>"
     chunks:
       - id: 1
         slug: "market_overview"
         title: "Market Landscape & Fundamentals"
         focus_areas: ["Core definition", "Market size", "Key players"]
       - id: 2
         slug: "financials"
         title: "Financial Performance & Funding"
         focus_areas: ["Total capital raised", "Valuation", "Revenue metrics"]
     ```
3. **Present to User & STOP (MANDATORY GATE 1)**:
   - Display the proposed chunks in chat.
   - **CRITICAL HARD STOP**: DO NOT execute Chunk 1, DO NOT perform searches or scraping for data points, DO NOT write chunk JSONs, and DO NOT generate reports in this turn.
   - Ask for explicit user approval before proceeding (via `ask_question` or text prompt):
     * e.g., "Proposed outline created. Do you approve proceeding to Chunk 1: [Title]?"
   - **STOP HERE**. Wait for user response.

---

## Phase 2: Execution (`/sherlock-deep`)

Triggered ONLY after explicit Phase 1 user approval, or via `/sherlock-deep`:
*NEVER execute automatically in the same turn as Phase 1.*

### Chunk Selection & Resume Check
1. Read `{topic_slug}/outline.yaml`.
2. Inspect `{topic_slug}/results/chunk_*.json`.
3. Identify the **first uncompleted chunk**.
4. If all chunks are completed, notify user and suggest `/sherlock-report`.

### Execution of 1 Chunk (Strict 1 Chunk Per Turn)
For the selected chunk, perform the deep empirical verification loop:

1. **Multi-Hop Search**:
   - Formulate 3–5 targeted search queries covering the chunk's focus areas.
   - Execute `search_web` for each query.
   - Collect candidate URLs (prioritize primary sources, official docs, top reporting).
2. **Deep Content Scraping**:
   - For the top 2–4 authoritative pages, fetch full text using `read_url_content`.
   - Isolate verbatim text segments discussing key claims, statistics, and events.
3. **Data Point Extraction & Empirical Double-Check Loop**:
   - For each candidate data point found in the scraped content:
     - **`data_point`**: Specific, concise claim or metric (e.g., "Raised $45.2M Series B in June 2024").
     - **`exact_url`**: Exact URL of the scraped page.
     - **`quoted_text`**: Verbatim sentence or paragraph directly copied from the page.
     - **`verification_query`**: Secondary targeted search query specifically testing this fact (e.g., `"Company X" "$45.2M" "Series B"`).
     - **`grep_result`**: Run `search_web` with the verification query. Extract the exact matching snippet returned by the search engine.
     - **`confidence_score`**:
       - `Highest`: Direct verbatim quote from high-authority source AND confirmed by secondary search grep.
       - `Medium`: Found in single source, but secondary search query returned partial or conflicting snippets.
       - `Low`: Vague, uncorroborated, or secondary search failed to confirm.
4. **Persist Chunk JSON**:
   - Write `{topic_slug}/results/chunk_{id:02d}_{slug}.json`:
     ```json
     {
       "chunk_id": 1,
       "chunk_slug": "market_overview",
       "chunk_title": "Market Landscape & Fundamentals",
       "sections": [
         {
           "title": "Industry Scale & Key Players",
           "bullets": [
             "Global market reached $12.4B in 2024, expanding at 28.5% CAGR [DP-1].",
             "Top three providers control 64% of total enterprise adoption [DP-2]."
           ],
           "data_points": [
             {
               "data_point": "Global market reached $12.4B in 2024, expanding at 28.5% CAGR",
               "exact_url": "https://example.com/report-2024",
               "quoted_text": "The global market reached an estimated $12.4B in 2024 with a 28.5% CAGR.",
               "verification_query": "\"global market\" \"$12.4B\" \"2024\" \"28.5% CAGR\"",
               "grep_result": "...estimated global market size of $12.4B in 2024 with a CAGR of 28.5%...",
               "confidence_score": "Highest"
             }
           ]
         }
       ]
     }
     ```
5. **Stop and Request Approval (MANDATORY GATE 2)**:
   - Output a clean summary of the completed chunk:
     - Verified data points count
     - Bullet briefing with bolded numbers and `[DP-#]` references
   - **CRITICAL HARD STOP**:
     - DO NOT execute the next chunk in the same turn.
     - DO NOT run `export_sherlock.py` or generate reports in the same turn.
     - Ask the user for explicit confirmation:
       * If more chunks remain in `outline.yaml`: "Chunk {N} complete. Do you approve proceeding to Chunk {N+1}: [Next Title]?"
       * If all chunks are completed: "All chunks finished. Do you approve generating final deliverables (.xlsx, .csv, .docx)?"
   - **STOP HERE**. Wait for user response.

---

## Phase 3: Reporting (`/sherlock-report`)

Triggered ONLY after explicit user confirmation that all chunks are approved, or via `/sherlock-report`:
*NEVER execute automatically in the same turn as chunk execution.*

1. **Execute Multi-Format Exporter**:
   ```bash
   python scripts/export_sherlock.py -d "./{topic_slug}"
   ```
2. **Deliverables Generated**:
   - **`{topic_slug}_report.xlsx`**: Full data points matrix with auto-styled headers, alternating rows, emerald highlights for `Highest` confidence, and text wrapping across the 7 required columns:
     `sr no`, `data point`, `exact url/subpage`, `quoted text from page`, `a search query with that data point`, `grep from running his search query`, `confidence score based on rechecking`.
   - **`{topic_slug}_report.csv`**: Machine-readable UTF-8 CSV with all 7 columns.
   - **`{topic_slug}_report.docx`**:
     - Strict filter: **Highest-confidence data points only**.
     - Style: Direct, human, easy-to-understand language. Zero marketing fluff. Zero hallucinations.
     - Layout: Majority high-density bullet points instead of long paragraphs.
     - Numbers: **All important numbers and metrics automatically bolded** (e.g., **$14.2M**, **99.4%**, **128k**, **3.5x**).
     - Traceability: Every bullet links to `[DP-#]` and maps directly to the verified appendix table.
3. **Present Results in Chat**:
   - Provide clickable file links (`file:///...`) to `.xlsx`, `.csv`, and `.docx`.
   - Print a high-level executive summary of verified findings directly in chat.
