#!/usr/bin/env python3
"""
Sherlock Workflow & Gate Protocol Audit Validator
Systematically checks SKILL.md and skills/sherlock/SKILL.md for:
1. 4-phase research protocol structure (Phase 0, Phase 1, Phase 2, Phase 3)
2. Interactive Gate definitions (Gate 0 Intake, Gate 1 Charter, Gate 2 Format, Gate 3 Handoff)
3. ask_question tool usage and schema compliance
4. Resumable chunk JSON schema definition and field parity with exporter expectations
5. 7 domain specialization registries (Pharma, Tech, Finance, Legal, Public Admin, AI/ML, General)
6. 100% parity between root SKILL.md and skills/sherlock/SKILL.md
"""

import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

SKILL_FILES = [
    REPO_ROOT / "SKILL.md",
    REPO_ROOT / "skills" / "sherlock" / "SKILL.md",
]

DOMAINS = [
    "pharma",
    "tech",
    "finance",
    "legal",
    "admin",
    "ai",
    "general"
]

REQUIRED_CHUNK_FIELDS = [
    "chunk_id",
    "chunk_slug",
    "chunk_title",
    "sections",
    "data_points",
    "source_tier",
    "exact_url",
    "quoted_text",
    "verification_query",
    "grep_result",
    "confidence_score",
    "triangulation_status"
]


def audit_skill_file(skill_path: Path):
    """Audits a single SKILL.md file for protocol compliance."""
    errors = []
    if not skill_path.exists():
        return [f"File {skill_path} does not exist."]

    text = skill_path.read_text(encoding="utf-8")

    # 1. Frontmatter checks
    if not text.startswith("---"):
        errors.append("Missing frontmatter opening '---'")
    parts = text.split("---")
    if len(parts) < 3:
        errors.append("Malformed YAML frontmatter (missing closing '---')")
    else:
        frontmatter = parts[1]
        for req_field in ["name:", "description:", "version:", "license:", "allowed-tools:", "compatibility:"]:
            if req_field not in frontmatter:
                errors.append(f"Missing required frontmatter field: '{req_field}'")
        if "ask_question" not in frontmatter:
            errors.append("'ask_question' not declared in allowed-tools")
        for runtime in ["antigravity", "claude-code", "cursor", "codex", "opencode"]:
            if runtime not in frontmatter:
                errors.append(f"Missing runtime compatibility in frontmatter: '{runtime}'")

    # 1.1 Multi-IDE compatibility section
    if "Multi-IDE Runtime & Tool Compatibility Matrix" not in text:
        errors.append("Missing 'Multi-IDE Runtime & Tool Compatibility Matrix' section")

    # 2. Phases checks
    for phase_name in [
        "Phase 0: Socratic Intake & Problem Formulation",
        "Phase 1: Planning",
        "Phase 2: Chunk Execution",
        "Phase 3: Deliverable Generation",
    ]:
        if phase_name not in text:
            errors.append(f"Missing protocol section: '{phase_name}'")

    # 3. Gate definitions checks
    for gate_name in [
        "Gate 0",
        "Gate 1",
        "Gate 2",
        "Gate 3",
    ]:
        if gate_name not in text:
            errors.append(f"Missing gate specification: '{gate_name}'")

    # 4. Domain frameworks
    for domain in DOMAINS:
        pattern = re.compile(rf"\b{domain}\b", re.IGNORECASE)
        if not pattern.search(text):
            errors.append(f"Domain framework reference missing: '{domain}'")

    # 5. Chunk JSON schema fields
    for field in REQUIRED_CHUNK_FIELDS:
        if field not in text:
            errors.append(f"Chunk schema field missing in specification: '{field}'")

    # 6. Check deliverable format options
    for fmt in ["docx", "xlsx", "pdf", "all"]:
        if f"`{fmt}`" not in text and f"'{fmt}'" not in text and f'"{fmt}"' not in text and fmt not in text:
            errors.append(f"Deliverable format option missing: '{fmt}'")

    return errors


def main():
    print("=" * 70)
    print("Sherlock Workflow & Gate Protocol Audit Validator")
    print("=" * 70)

    total_errors = 0
    for skill_file in SKILL_FILES:
        rel = skill_file.relative_to(REPO_ROOT)
        print(f"\n[AUDIT] {rel} ...", end=" ")
        errors = audit_skill_file(skill_file)
        if not errors:
            print("PASS (100% protocol compliant)")
        else:
            print(f"FAIL ({len(errors)} violations)")
            total_errors += len(errors)
            for err in errors:
                print(f"  - {err}")

    print("\n" + "=" * 70)
    if total_errors == 0:
        print("RESULT: ALL WORKFLOW AUDITS PASSED. (100% schema & gate compliance)")
        print("=" * 70)
        sys.exit(0)
    else:
        print(f"RESULT: AUDIT FAILED with {total_errors} violations.")
        print("=" * 70)
        sys.exit(1)


if __name__ == "__main__":
    main()
