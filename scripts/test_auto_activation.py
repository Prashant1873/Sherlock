#!/usr/bin/env python3
"""
Sherlock Auto-Activation & Multi-IDE Rules Validator
Verifies:
1. SKILL.md and skills/sherlock/SKILL.md description contains positive semantic triggers
2. SKILL.md and skills/sherlock/SKILL.md description contains negative dormancy boundaries
3. All 4 IDE rules integration files exist in rules/ with proper routing directives
4. 100% parity between root SKILL.md and skills/sherlock/SKILL.md
"""

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

SKILL_FILES = [
    REPO_ROOT / "SKILL.md",
    REPO_ROOT / "skills" / "sherlock" / "SKILL.md",
]

RULE_FILES = [
    REPO_ROOT / "rules" / "CLAUDE.md",
    REPO_ROOT / "rules" / "GEMINI.md",
    REPO_ROOT / "rules" / ".cursorrules",
    REPO_ROOT / "rules" / "AGENTS.md",
]

REQUIRED_POSITIVE_TRIGGERS = [
    "deep research",
    "empirical",
    "benchmarking",
    "market sizing",
    "triangulation",
]

REQUIRED_NEGATIVE_BOUNDARIES = [
    "DO NOT activate for casual",
    "simple factual definitions",
    "quick programming lookups",
]


def extract_frontmatter(file_path: Path):
    """Extracts frontmatter text from a skill markdown file."""
    text = file_path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return ""
    parts = text.split("---")
    if len(parts) < 3:
        return ""
    return parts[1]


def audit_auto_activation():
    errors = []

    # 1. Audit SKILL files frontmatter
    for sf in SKILL_FILES:
        rel = sf.relative_to(REPO_ROOT)
        if not sf.exists():
            errors.append(f"Missing skill file: {rel}")
            continue

        fm = extract_frontmatter(sf)
        if not fm:
            errors.append(f"Malformed frontmatter in {rel}")
            continue

        # Check positive triggers
        for pt in REQUIRED_POSITIVE_TRIGGERS:
            if pt.lower() not in fm.lower():
                errors.append(f"{rel}: Missing positive trigger '{pt}' in frontmatter description")

        # Check negative boundaries
        for nb in REQUIRED_NEGATIVE_BOUNDARIES:
            if nb.lower() not in fm.lower():
                errors.append(f"{rel}: Missing negative boundary '{nb}' in frontmatter description")

    # 2. Check skill parity
    if SKILL_FILES[0].exists() and SKILL_FILES[1].exists():
        content_root = SKILL_FILES[0].read_text(encoding="utf-8")
        content_pkg = SKILL_FILES[1].read_text(encoding="utf-8")
        if content_root != content_pkg:
            errors.append("Mismatch between root SKILL.md and skills/sherlock/SKILL.md")

    # 3. Audit rules integration files
    for rf in RULE_FILES:
        rel = rf.relative_to(REPO_ROOT)
        if not rf.exists():
            errors.append(f"Missing rule integration file: {rel}")
            continue

        text = rf.read_text(encoding="utf-8")
        if "sherlock" not in text.lower():
            errors.append(f"{rel}: Does not reference 'sherlock' skill")
        if "gate 0" not in text.lower():
            errors.append(f"{rel}: Does not mandate Gate 0 intake pause")
        if "negative boundary" not in text.lower():
            errors.append(f"{rel}: Does not specify negative boundary conditions")

    return errors


def main():
    print("=" * 70)
    print("Sherlock Auto-Activation & Multi-IDE Rules Validator")
    print("=" * 70)

    errors = audit_auto_activation()

    print("\n[CHECK] Semantic Trigger Audit ...", "PASS" if not [e for e in errors if "trigger" in e or "boundary" in e] else "FAIL")
    print("[CHECK] Multi-IDE Rule Files Audit ...", "PASS" if not [e for e in errors if "rules" in e] else "FAIL")
    print("[CHECK] Root vs Packaged Skill Parity ...", "PASS" if not [e for e in errors if "Mismatch" in e] else "FAIL")

    print("\n" + "=" * 70)
    if not errors:
        print("RESULT: ALL AUTO-ACTIVATION & RULE AUDITS PASSED. (100% compliant)")
        print("=" * 70)
        sys.exit(0)
    else:
        print(f"RESULT: AUDIT FAILED with {len(errors)} issues:")
        for err in errors:
            print(f"  - {err}")
        print("=" * 70)
        sys.exit(1)


if __name__ == "__main__":
    main()
