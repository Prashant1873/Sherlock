# OpenAI Codex & OpenCode Instructions: Sherlock Deep Research Directive

## Semantic Auto-Activation Rules

When the user requests deep secondary research, empirical investigation, clinical/pharma trial benchmarking, market sizing, financial/PE due diligence, enterprise IT architecture/TCO comparisons, or demands zero hallucinations with 2+ source triangulation:
1. **Activate Skill**: Invoke the `sherlock` skill protocol (or execute `/sherlock "<topic>"`).
2. **Execute Phase 0 Intake**: Formulate clarifying questions probing target audience, decision at stake, scope boundaries, and baseline hypotheses.
3. **Enforce Gate 0 Stop**: Prompt the user via interactive terminal input or question tool and await response before executing web searches.
4. **Enforce Operational Invariants**:
   - Zero parametric memory (all metrics must originate from retrieved web pages with verbatim quotes).
   - Strict 1-chunk-per-turn execution with user approval gates between chunks.
   - 2+ independent source triangulation (requiring at least one Tier 1 or Tier 2 authority).
   - Automated export of publication-grade executive deliverables (.docx, .xlsx, .pdf).

## Negative Boundary Conditions (Dormancy Guarantees)

Do NOT invoke Sherlock for:
- Casual trivia or simple definitions ("What is mRNA?", "Who founded Apple?").
- Everyday coding or syntax lookups ("How to invert a dictionary in Python").
- Shallow summaries or quick bullet-point overviews.
- Conversational chat or creative writing.

Answer those inquiries directly without activating the Sherlock research protocol.
