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

REPO_ROOT = Path(__file__).resolve().parent.parent

# Files and extensions to inspect
INSPECT_EXTS = {".md", ".py", ".json", ".txt", ".yaml", ".yml", ".sh", ".ps1"}

# Directories to skip
SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", ".venv", "venv", "node_modules"}

# Specific files to skip (binary/ephemeral)
SKIP_FILES = {".gitignore"}

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


def main():
    print("=" * 70)
    print("Sherlock Privacy & Secret Sanitization Validator")
    print("=" * 70)

    target_files = collect_target_files()
    total_violations = 0

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
        print(f"RESULT: ALL {len(target_files)} FILES SANITIZED. (0 leaks detected)")
        print("=" * 70)
        sys.exit(0)
    else:
        print(f"RESULT: PRIVACY AUDIT FAILED with {total_violations} leaks.")
        print("=" * 70)
        sys.exit(1)


if __name__ == "__main__":
    main()
