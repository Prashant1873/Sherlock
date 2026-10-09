#!/usr/bin/env python3
"""
Sherlock Link and Path Cross-Reference Integrity Validator
Scans markdown documentation and code files to verify:
1. Markdown links [text](target) point to existing files or headings
2. Code path mentions (scripts/..., templates/..., references/...) point to existing files
3. Root SKILL.md and skills/sherlock/SKILL.md have 100% parity
"""

import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

TARGET_FILES = [
    REPO_ROOT / "SKILL.md",
    REPO_ROOT / "README.md",
    REPO_ROOT / "skills" / "sherlock" / "SKILL.md",
    REPO_ROOT / "references" / "3_tier_hierarchy.md",
    REPO_ROOT / "references" / "source_whitelists.md",
    REPO_ROOT / "rules" / "CLAUDE.md",
    REPO_ROOT / "rules" / "GEMINI.md",
    REPO_ROOT / "rules" / ".cursorrules",
    REPO_ROOT / "rules" / "AGENTS.md",
]

# Patterns
MD_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
PATH_MENTION_RE = re.compile(r"(?:`|'|\")([a-zA-Z0-9_\-./]+\.(?:py|md|json|txt|mjs))(?:`|'|\")")


def extract_headings(file_path: Path):
    """Extracts markdown heading anchors from a file."""
    headings = set()
    try:
        content = file_path.read_text(encoding="utf-8")
        for line in content.splitlines():
            m = re.match(r"^#{1,6}\s+(.+)$", line)
            if m:
                heading_text = m.group(1).strip()
                # GitHub style anchor: lowercase, punctuation removed, spaces to hyphens
                anchor = re.sub(r"[^\w\s-]", "", heading_text).strip().lower()
                anchor = re.sub(r"[-\s]+", "-", anchor)
                headings.add(anchor)
    except Exception:
        pass
    return headings


def check_file_integrity(file_path: Path):
    """Validates links and file references in a markdown file."""
    if not file_path.exists():
        return [{"line": 0, "target": str(file_path), "error": "Source file does not exist"}]

    errors = []
    content = file_path.read_text(encoding="utf-8")
    lines = content.splitlines()
    self_headings = extract_headings(file_path)

    for line_num, line in enumerate(lines, 1):
        # 1. Check markdown links [text](target)
        for m in MD_LINK_RE.finditer(line):
            text, target = m.group(1), m.group(2).strip()

            # Ignore web links, mailto, etc.
            if target.startswith(("http://", "https://", "mailto:", "ftp://")):
                continue

            # Anchor link in same file: #heading
            if target.startswith("#"):
                anchor = target[1:].lower()
                # Clean query strings if any
                anchor = anchor.split("?")[0]
                # Allow broad match on headings or common section anchors
                if anchor and anchor not in self_headings:
                    # Also check loose match
                    if not any(anchor in h for h in self_headings):
                        errors.append({
                            "line": line_num,
                            "target": target,
                            "error": f"Internal anchor '{target}' not found in headings",
                        })
                continue

            # File link: path/to/file or path/to/file#anchor
            target_path_str = target.split("#")[0].split("?")[0]
            if not target_path_str:
                continue

            target_path = (file_path.parent / target_path_str).resolve()
            alt_repo_path = (REPO_ROOT / target_path_str.lstrip("/")).resolve()

            if not (target_path.exists() or alt_repo_path.exists()):
                # Allow placeholder templates like {topic_slug}/results
                if "{" in target_path_str or "<" in target_path_str:
                    continue
                errors.append({
                    "line": line_num,
                    "target": target,
                    "error": f"Target path '{target_path_str}' does not exist on disk",
                })

        # 2. Check backticked path mentions (e.g. `scripts/export_sherlock.py`)
        for m in PATH_MENTION_RE.finditer(line):
            path_str = m.group(1)
            # Only check recognized directories
            if any(path_str.startswith(prefix) for prefix in ("scripts/", "templates/", "references/", "skills/")):
                candidate = (REPO_ROOT / path_str).resolve()
                if not candidate.exists():
                    errors.append({
                        "line": line_num,
                        "target": path_str,
                        "error": f"Referenced code/template file '{path_str}' does not exist",
                    })

    return errors


def check_skill_parity():
    """Verifies that root SKILL.md and skills/sherlock/SKILL.md match."""
    root_skill = REPO_ROOT / "SKILL.md"
    nested_skill = REPO_ROOT / "skills" / "sherlock" / "SKILL.md"

    if not root_skill.exists() or not nested_skill.exists():
        return False, "One of root SKILL.md or skills/sherlock/SKILL.md is missing."

    root_text = root_skill.read_text(encoding="utf-8").strip()
    nested_text = nested_skill.read_text(encoding="utf-8").strip()

    if root_text != nested_text:
        return False, "Content mismatch between root SKILL.md and skills/sherlock/SKILL.md."

    return True, "Root SKILL.md and skills/sherlock/SKILL.md are in 100% parity."


def main():
    print("=" * 70)
    print("Sherlock Link & Path Integrity Validator")
    print("=" * 70)

    all_passed = True
    total_checked = 0
    total_errors = 0

    # Check target files
    for target in TARGET_FILES:
        rel_path = target.relative_to(REPO_ROOT)
        print(f"\n[CHECK] {rel_path} ...", end=" ")
        errors = check_file_integrity(target)
        total_checked += 1

        if not errors:
            print("PASS (0 issues)")
        else:
            print(f"FAIL ({len(errors)} issues)")
            all_passed = False
            total_errors += len(errors)
            for err in errors:
                print(f"  Line {err['line']}: {err['target']} -> {err['error']}")

    # Check SKILL parity
    print("\n[CHECK] Skill Parity (Root vs skills/sherlock/SKILL.md) ...", end=" ")
    parity_ok, msg = check_skill_parity()
    if parity_ok:
        print("PASS")
    else:
        print(f"FAIL -> {msg}")
        all_passed = False
        total_errors += 1

    print("\n" + "=" * 70)
    if all_passed:
        print(f"RESULT: ALL CHECKS PASSED. ({total_checked} files inspected, 0 errors)")
        print("=" * 70)
        sys.exit(0)
    else:
        print(f"RESULT: INTEGRITY ISSUES DETECTED. ({total_errors} total errors)")
        print("=" * 70)
        sys.exit(1)


if __name__ == "__main__":
    main()
