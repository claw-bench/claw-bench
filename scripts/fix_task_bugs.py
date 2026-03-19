#!/usr/bin/env python3
"""Batch fix task framework bugs reported in the Manus bug report.

Fixes 5 categories of issues:
1. Missing data/ directories in setup.sh — remove broken cp commands
2. Heredoc f-string variable scope — add os.environ.get at top of Python blocks
3. Verifier workspace override — replace CLAW_WORKSPACE with --workspace fixture
4. WORKSPACE not exported — add export statement
5. Hardcoded workspace path (fin-006) — use $1 parameter

Usage:
    python scripts/fix_task_bugs.py          # dry-run
    python scripts/fix_task_bugs.py --apply  # apply fixes
"""

import argparse
import re
from pathlib import Path

TASKS_ROOT = Path(__file__).resolve().parent.parent / "tasks"

stats = {"data_dir": 0, "heredoc": 0, "verifier": 0, "export": 0, "hardcoded": 0}


def fix_missing_data_dir(apply: bool):
    """Fix setup.sh that copies from non-existent data/ directory."""
    for setup in sorted(TASKS_ROOT.rglob("environment/setup.sh")):
        task_dir = setup.parent.parent
        data_dir = task_dir / "environment" / "data"
        content = setup.read_text()

        if not data_dir.exists() and ("data/" in content or "data\"" in content):
            new_content = content
            new_content = re.sub(
                r'cp\s+.*?["\']?\$.*?/environment/data/["\']?\*?\s+.*?\n',
                '', new_content
            )
            new_content = re.sub(
                r'cp\s+-r?\s*.*?data/\*?\s+.*?\n',
                '', new_content
            )
            new_content = re.sub(
                r'cp\s+.*?"?\$\(dirname.*?\)/data/"?\*\s+.*?\n',
                '', new_content
            )
            if new_content != content:
                stats["data_dir"] += 1
                if apply:
                    setup.write_text(new_content)
                print(f"  [data_dir] {task_dir.name}: removed broken cp from setup.sh")


def fix_heredoc_fstring(apply: bool):
    """Fix Python f-strings in heredocs that reference undefined WORKSPACE variable."""
    for sh_file in sorted(TASKS_ROOT.rglob("*.sh")):
        content = sh_file.read_text()

        if "f'{WORKSPACE}" not in content and 'f"{WORKSPACE}' not in content:
            continue
        if "os.environ" in content and "WORKSPACE" in content:
            continue

        task_name = sh_file.parent.parent.name if sh_file.parent.name in ("solution", "environment") else sh_file.parent.name

        fix_line = "import os; WORKSPACE = os.environ.get('WORKSPACE', os.getcwd())\n"

        new_content = content
        # Find Python heredoc blocks and inject os.environ at the top
        patterns = [
            (r"(python3\s+-\s*<<\s*'?EOF'?\s*\n)", r"\1" + fix_line),
            (r"(python3\s*<<\s*'?EOF'?\s*\n)", r"\1" + fix_line),
            (r"(python3\s+-c\s*')", None),
        ]

        for pat, repl in patterns:
            if repl:
                new_content = re.sub(pat, repl, new_content)

        # Also handle cases where python3 -c is used with f-strings
        if new_content == content:
            # Fallback: replace f'{WORKSPACE} with proper os.environ usage
            new_content = new_content.replace(
                "f'{WORKSPACE}", "f'{os.environ.get(\"WORKSPACE\", os.getcwd())}"
            )
            new_content = new_content.replace(
                'f"{WORKSPACE}', 'f"{os.environ.get(\\"WORKSPACE\\", os.getcwd())}'
            )

        if new_content != content:
            stats["heredoc"] += 1
            if apply:
                sh_file.write_text(new_content)
            print(f"  [heredoc] {task_name}: fixed f-string in {sh_file.name}")


def fix_verifier_workspace(apply: bool):
    """Fix verifiers that use CLAW_WORKSPACE/os.environ instead of --workspace."""
    correct_fixture = '''@pytest.fixture
def workspace(request):
    """Resolve workspace from --workspace CLI option."""
    ws = request.config.getoption("--workspace")
    if ws:
        return Path(ws)
    return Path(os.environ.get("CLAW_WORKSPACE", os.environ.get("WORKSPACE", "workspace")))
'''

    for vf in sorted(TASKS_ROOT.rglob("verifier/test_output.py")):
        content = vf.read_text()
        task_name = vf.parent.parent.name

        if "request.config.getoption" in content:
            continue

        has_claw_ws = "CLAW_WORKSPACE" in content
        has_os_env_ws = "os.environ" in content and "WORKSPACE" in content

        if not has_claw_ws and not has_os_env_ws:
            continue

        new_content = content

        # Replace the workspace fixture/variable
        # Pattern 1: WORKSPACE = os.environ.get("CLAW_WORKSPACE", ...)
        new_content = re.sub(
            r'WORKSPACE\s*=\s*os\.environ\.get\s*\(\s*["\']CLAW_WORKSPACE["\'].*?\)\s*\n',
            '',
            new_content
        )
        new_content = re.sub(
            r'WORKSPACE\s*=\s*os\.environ\s*\[\s*["\']CLAW_WORKSPACE["\']\s*\]\s*\n',
            '',
            new_content
        )
        new_content = re.sub(
            r'WORKSPACE\s*=\s*os\.environ\.get\s*\(\s*["\']WORKSPACE["\'].*?\)\s*\n',
            '',
            new_content
        )

        # Replace any @pytest.fixture def workspace that reads env
        new_content = re.sub(
            r'@pytest\.fixture\s*\ndef\s+workspace\s*\(\s*\).*?(?=\n(?:@|def |class |\Z))',
            correct_fixture.rstrip(),
            new_content,
            flags=re.DOTALL,
        )

        # If there's no workspace fixture at all but uses WORKSPACE global, add one
        if "def workspace" not in new_content and "WORKSPACE" in new_content:
            # Add import Path if missing
            if "from pathlib import Path" not in new_content:
                new_content = "from pathlib import Path\n" + new_content
            if "import os" not in new_content:
                new_content = "import os\n" + new_content

            # Replace bare WORKSPACE references with workspace fixture calls
            # This is tricky — for class-based tests, we need a different approach
            # Just add the fixture and a helper
            fixture_block = f"\n\n{correct_fixture}\n"
            # Insert after imports
            import_end = 0
            for m in re.finditer(r'^(import |from )', new_content, re.MULTILINE):
                import_end = new_content.index('\n', m.end()) + 1
            if import_end > 0:
                new_content = new_content[:import_end] + fixture_block + new_content[import_end:]

        if new_content != content:
            stats["verifier"] += 1
            if apply:
                vf.write_text(new_content)
            print(f"  [verifier] {task_name}: fixed workspace fixture")


def fix_workspace_export(apply: bool):
    """Add 'export WORKSPACE' where it's used by embedded Python but not exported."""
    for sh_file in sorted(TASKS_ROOT.rglob("*.sh")):
        content = sh_file.read_text()

        if "WORKSPACE=" not in content:
            continue
        if "os.environ" not in content:
            continue
        if "export WORKSPACE" in content:
            continue

        task_name = sh_file.parent.parent.name if sh_file.parent.name in ("solution", "environment") else sh_file.parent.name

        # Add export after WORKSPACE= assignment
        new_content = re.sub(
            r'(WORKSPACE=("[^"]*"|\$\{[^}]*\}|[^\s]*))\n',
            r'\1\nexport WORKSPACE\n',
            content,
            count=1,
        )

        if new_content != content:
            stats["export"] += 1
            if apply:
                sh_file.write_text(new_content)
            print(f"  [export] {task_name}: added export WORKSPACE in {sh_file.name}")


def fix_fin006_hardcoded(apply: bool):
    """Fix fin-006 setup.sh that ignores $1 parameter."""
    setup = TASKS_ROOT / "financial-analysis" / "fin-006-analyze-stock-portfolio-risk-using-var-and-cvar" / "environment" / "setup.sh"
    if not setup.exists():
        return

    content = setup.read_text()
    if "mkdir -p workspace" in content or ("$1" not in content and "WORKSPACE" not in content):
        new_content = re.sub(
            r'mkdir -p workspace\n',
            'WORKSPACE="${1:-workspace}"\nmkdir -p "$WORKSPACE"\n',
            content,
        )
        new_content = re.sub(r'cd workspace\n', 'cd "$WORKSPACE"\n', new_content)
        new_content = new_content.replace(
            'workspace/', '"$WORKSPACE"/'
        )

        if new_content != content:
            stats["hardcoded"] += 1
            if apply:
                setup.write_text(new_content)
            print(f"  [hardcoded] fin-006: fixed setup.sh to use $1")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    mode = "APPLY" if args.apply else "DRY-RUN"
    print(f"[{mode}] Fixing task framework bugs...\n")

    fix_missing_data_dir(args.apply)
    fix_heredoc_fstring(args.apply)
    fix_verifier_workspace(args.apply)
    fix_workspace_export(args.apply)
    fix_fin006_hardcoded(args.apply)

    print(f"\n[{mode}] Summary:")
    print(f"  data_dir fixes: {stats['data_dir']}")
    print(f"  heredoc fixes:  {stats['heredoc']}")
    print(f"  verifier fixes: {stats['verifier']}")
    print(f"  export fixes:   {stats['export']}")
    print(f"  hardcoded fixes: {stats['hardcoded']}")
    print(f"  TOTAL: {sum(stats.values())}")


if __name__ == "__main__":
    main()
