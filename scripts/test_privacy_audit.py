#!/usr/bin/env python3
"""
Sherlock Privacy & Repository Sanitization Validator
Scans all codebase and documentation files to ensure:
1. Zero hardcoded absolute local user paths (Windows, macOS, Linux)
2. Zero leaked API keys, tokens, or credentials
3. Zero developer machine usernames or private environments
"""

import os
import re
import sys
from pathlib import Path

import subprocess

REPO_ROOT = Path(__file__).resolve().parent.parent

# Files and extensions to inspect
INSPECT_EXTS = {".md", ".py", ".json", ".txt", ".yaml", ".yml", ".sh", ".ps1"}

# Directories to skip
SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", ".venv", "venv", "node_modules"}

# Specific files to skip
SKIP_FILES = set()

# Sensitive pattern definitions
PRIVACY_PATTERNS = [
    # Windows local user paths (e.g. C:\Users\username or C:/Users/username)
    (
        "Windows Local User Path",
        re.compile(r"[A-Za-z]:[\\/]Users[\\/][a-zA-Z0-9_.-]+", re.IGNORECASE)
    ),
    # macOS user home paths (/Users/username)
    (
        "macOS User Home Path",
        re.compile(r"(?:^|[\s\"'(=])/Users/[a-zA-Z0-9_.-]+", re.IGNORECASE)
    ),
    # Linux user home paths (/home/username)
    (
        "Linux User Home Path",
        re.compile(r"(?:^|[\s\"'(=])/home/[a-zA-Z0-9_.-]+", re.IGNORECASE)
    ),
    # GitHub Personal Access Tokens
    (
        "GitHub Token",
        re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[a-zA-Z0-9]{20,}\b")
    ),
    # OpenAI / Claude API Key pattern
    (
        "AI Platform API Key",
        re.compile(r"\b(?:sk-[a-zA-Z0-9]{20,}|anthropic-[a-zA-Z0-9]{20,})\b")
    ),
    # Generic API Key / Secret assignments
    (
        "Hardcoded Secret / API Key Assignment",
        re.compile(r"(?:api[_-]?key|secret[_-]?key|auth[_-]?token)\s*[:=]\s*['\"][a-zA-Z0-9_\-]{16,}['\"]", re.IGNORECASE)
    ),
]


def collect_target_files():
    """Collects repository files to audit."""
    files = []
    for root, dirs, filenames in os.walk(REPO_ROOT):
        # Exclude directories
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".planning")]

        for fn in filenames:
            if fn in SKIP_FILES:
                continue
            p = Path(root) / fn
            if p.suffix.lower() in INSPECT_EXTS or fn in ("LICENSE",):
                files.append(p)
    return sorted(files)


def audit_file(path: Path):
    """Scans a file against privacy and security rules."""
    violations = []
    try:
        content = path.read_text(encoding="utf-8")
    except Exception as e:
        return [{"line": 0, "type": "File Read Error", "match": str(e)}]

    lines = content.splitlines()
    for line_num, line in enumerate(lines, 1):
        for rule_name, pattern in PRIVACY_PATTERNS:
            for m in pattern.finditer(line):
                matched_str = m.group(0).strip()
                # Exclude harmless examples or documentation placeholders
                if any(x in matched_str.lower() for x in ("username", "<username>", "$home", "~", "%userprofile%")):
                    continue
                violations.append({
                    "line": line_num,
                    "type": rule_name,
                    "match": matched_str
                })

    return violations


def check_gitignore_hidden():
    """Verifies .gitignore is deleted from disk and not tracked by git."""
    issues = []
    gi_path = REPO_ROOT / ".gitignore"
    if gi_path.exists():
        issues.append("Root .gitignore file exists on disk (must be deleted to hide from GitHub).")

    try:
        res = subprocess.run(
            ["git", "ls-files", ".gitignore"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            check=True
        )
        if res.stdout.strip():
            issues.append(f".gitignore is tracked in git index: {res.stdout.strip()}")
    except Exception as e:
        issues.append(f"Failed to query git ls-files: {e}")

    return issues


def check_git_exclude_rules():
    """Verifies .git/info/exclude exists and contains necessary exclusion rules."""
    issues = []
    exclude_path = REPO_ROOT / ".git" / "info" / "exclude"
    if not exclude_path.exists():
        issues.append(".git/info/exclude file does not exist.")
        return issues

    content = exclude_path.read_text(encoding="utf-8")
    required_patterns = [
        ".planning/",
        "great_ideas.md",
        "neural_map.md",
        "*.xlsx",
        "*.docx",
        "*.pdf",
        "test_*",
    ]
    for pat in required_patterns:
        if pat not in content:
            issues.append(f"Missing required pattern in .git/info/exclude: '{pat}'")

    return issues


def main():
    print("=" * 70)
    print("Sherlock Privacy, Secret Sanitization & Hygiene Validator")
    print("=" * 70)

    # 1. Check .gitignore hiding and .git/info/exclude integrity
    total_violations = 0
    gi_issues = check_gitignore_hidden()
    if gi_issues:
        print("\n[FAIL] Gitignore Hiding Audit:")
        for issue in gi_issues:
            print(f"  {issue}")
        total_violations += len(gi_issues)
    else:
        print("[CHECK] Root .gitignore hidden from git tree ... PASS")

    exclude_issues = check_git_exclude_rules()
    if exclude_issues:
        print("\n[FAIL] Git Info/Exclude Audit:")
        for issue in exclude_issues:
            print(f"  {issue}")
        total_violations += len(exclude_issues)
    else:
        print("[CHECK] .git/info/exclude pattern rules ... PASS")

    # 2. File content privacy audit
    target_files = collect_target_files()
    for tf in target_files:
        rel = tf.relative_to(REPO_ROOT)
        violations = audit_file(tf)
        if violations:
            print(f"\n[FAIL] {rel} ({len(violations)} violations):")
            for v in violations:
                print(f"  Line {v['line']}: [{v['type']}] -> {v['match']}")
            total_violations += len(violations)
        else:
            print(f"[CLEAN] {rel}")

    print("\n" + "=" * 70)
    if total_violations == 0:
        print(f"RESULT: ALL {len(target_files)} FILES SANITIZED & HYGIENE VERIFIED. (0 leaks)")
        print("=" * 70)
        sys.exit(0)
    else:
        print(f"RESULT: HYGIENE & PRIVACY AUDIT FAILED with {total_violations} issues.")
        print("=" * 70)
        sys.exit(1)


if __name__ == "__main__":
    main()
