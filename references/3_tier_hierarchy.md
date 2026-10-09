# 3-Tier Source Authority Hierarchy & Triangulation Standard

Every retrieved source and candidate data point in Sherlock is classified into one of three authority tiers based on institutional governance, audit rigour, and regulatory accountability:

---

## Source Authority Tiers

### Tier 1: Primary / Regulatory / Peer-Reviewed
- **Regulatory Authorities & Registries**: `fda.gov`, `ema.europa.eu`, `pmda.go.jp`, `mhra.gov.uk`, `congress.gov`, `sec.gov/edgar`.
- **Primary Clinical Registries**: `clinicaltrials.gov`, `who.int/trialsearch`, `isrctn.com`.
- **Peer-Reviewed Scientific & Medical Journals**: PubMed / PMC, *The Lancet*, *NEJM*, *JAMA*, *Nature*, IEEE, ACM.
- **Central Banks & Statistical Agencies**: Federal Reserve (`fred.stlouisfed.org`), BLS, US Census Bureau, ECB, BIS.
- **Statutory Corporate Filings**: SEC EDGAR (10-K, 10-Q, 8-K filings), audited court dockets.

### Tier 2: Institutional / Audited / Global Standards
- **Multilateral Institutions**: World Bank, IMF, OECD, WHO, WTO.
- **Engineering Standards Bodies**: ISO, NIST, IETF, W3C.
- **Audited Corporate Financial Disclosures**: Annual audited financial statements and annual investor presentations.
- **Academic Working Papers & Repositories**: arXiv, NBER working papers, peer conference proceedings.

### Tier 3: Secondary / Trade Press / Industry Media
- **Specialized Industry Media**: *TechCrunch*, *Endpoints News*, *Fierce Biotech*, *Bloomberg News*, *Reuters*.
- **Commercial Market Research Aggregators**: Gartner summaries, IDC reports, Statista.
- **Corporate Blogs & Marketing Collateral**: Product launch blogs, corporate press releases, general commentary.

---

## Triangulation Invariants

1. **Tier 1 / Tier 2 Requirement**:
   - To achieve `"Highest"` confidence score and `"Flag as Triangulated"`, at least **one** of the corroborating sources MUST be a **Tier 1** or **Tier 2** authority.
   - Points corroborated solely by Tier 3 sources (e.g. two tech news blogs echoing the same press release) are capped at `"Medium"` confidence and marked `"Undeclared"`.
2. **Conflict Adjudication**:
   - When two Tier 1 or Tier 2 sources report conflicting numbers, **never average or smooth them**.
   - Assign `"triangulation_status": "Conflict"` and `"confidence_score": "Conflict - Adjudicated"`.
   - Log both figures, URLs, quotes, dates, methodologies, and the root cause of variance.
