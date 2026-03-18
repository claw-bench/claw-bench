#!/usr/bin/env python3
"""Generate a complete Claw-Bench task from an expert proposal.

This script reads a structured expert proposal (JSON or GitHub Issue body),
calls an LLM to generate all required task files, and writes them to the
tasks/ directory ready for review.

Usage:
    # From a local JSON proposal file (e.g. from data/expert-proposals/)
    python scripts/generate_task_from_proposal.py --proposal data/expert-proposals/xxx.json

    # From a GitHub Issue number (requires GITHUB_TOKEN)
    python scripts/generate_task_from_proposal.py --issue 42

    # Specify a custom LLM model
    python scripts/generate_task_from_proposal.py --proposal proposal.json --model gpt-4.1-mini

Environment variables:
    OPENAI_API_KEY   - Required. API key for the LLM provider.
    OPENAI_BASE_URL  - Optional. Override the base URL for OpenAI-compatible APIs.
    GITHUB_TOKEN     - Required when using --issue mode.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import textwrap
from pathlib import Path
from typing import Any, Optional

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TASKS_DIR = PROJECT_ROOT / "tasks"

# Domain -> directory name mapping
DOMAIN_DIR_MAP = {
    "computer-science": "computer-science",
    "mathematics": "mathematics",
    "physics-engineering": "physics-engineering",
    "biology-chemistry": "biology-chemistry",
    "financial-analysis": "financial-analysis",
    "accounting": "accounting",
    "marketing": "marketing",
    "contract-review": "contract-review",
    "legal-research": "legal-research",
    "clinical-data": "clinical-data",
    "medical-research": "medical-research",
    "sociology": "sociology",
    "education": "education",
}

DEFAULT_MODEL = "gpt-4.1-mini"

# ---------------------------------------------------------------------------
# Proposal parsing
# ---------------------------------------------------------------------------


def load_proposal_from_file(path: str) -> dict[str, Any]:
    """Load a proposal from a local JSON file."""
    with open(path) as f:
        return json.load(f)


def load_proposal_from_issue(issue_number: int) -> dict[str, Any]:
    """Load a proposal from a GitHub Issue using gh CLI."""
    result = subprocess.run(
        ["gh", "issue", "view", str(issue_number), "--json",
         "title,body,labels,author"],
        capture_output=True, text=True, check=True,
    )
    issue = json.loads(result.stdout)
    return parse_issue_body(issue)


def parse_issue_body(issue: dict[str, Any]) -> dict[str, Any]:
    """Parse a GitHub Issue body (from the structured form template) into
    a proposal dict matching the ExpertProposalInput schema."""

    body = issue.get("body", "")
    title = issue.get("title", "")

    def extract_section(heading: str) -> str:
        """Extract text under a ### heading."""
        pattern = rf"###\s*{re.escape(heading)}\s*\n(.*?)(?=\n###|\Z)"
        match = re.search(pattern, body, re.DOTALL)
        return match.group(1).strip() if match else ""

    # Parse domain from dropdown
    domain_raw = extract_section("Professional Domain")
    domain = _map_domain_label_to_key(domain_raw)

    # Parse difficulty
    difficulty_raw = extract_section("Estimated Difficulty")
    difficulty = "L2"  # default
    for level in ("L1", "L2", "L3", "L4"):
        if level in difficulty_raw:
            difficulty = level
            break

    # Parse required actions from text (comma or newline separated)
    actions_raw = extract_section("Required Agent Actions")
    required_actions = _parse_actions_list(actions_raw)

    # Clean title prefix
    task_title = re.sub(r"^\[Task Proposal\]:?\s*", "", title).strip()
    if not task_title:
        task_title = extract_section("Task Title") or "Untitled Task"

    return {
        "domain": domain,
        "taskTitle": task_title,
        "difficulty": difficulty,
        "context": extract_section("Real-world Context"),
        "instruction": extract_section("Agent Instruction"),
        "requiredActions": required_actions,
        "successCriteria": extract_section("Success Criteria"),
        "dataRequirements": extract_section("Data & Resources"),
        "expertName": issue.get("author", {}).get("login", ""),
        "expertEmail": "",
    }


def _map_domain_label_to_key(label: str) -> str:
    """Map a human-readable domain label to the domain key."""
    label_lower = label.lower()
    mapping = {
        "computer science": "computer-science",
        "mathematics": "mathematics",
        "physics": "physics-engineering",
        "engineering": "physics-engineering",
        "biology": "biology-chemistry",
        "chemistry": "biology-chemistry",
        "financial": "financial-analysis",
        "accounting": "accounting",
        "marketing": "marketing",
        "contract": "contract-review",
        "legal research": "legal-research",
        "clinical": "clinical-data",
        "medical": "medical-research",
        "sociology": "sociology",
        "education": "education",
    }
    for keyword, key in mapping.items():
        if keyword in label_lower:
            return key
    return "computer-science"  # fallback


def _parse_actions_list(text: str) -> list[str]:
    """Parse a free-text list of actions into standardized action keys."""
    known_actions = [
        "api-call", "file-read", "file-write", "file-move",
        "database-query", "database-write", "script-execution",
        "environment-setup", "web-navigation", "web-scraping",
        "git-operation", "email-send", "document-conversion",
        "data-visualization", "command-line-tool", "package-install",
    ]
    found = []
    text_lower = text.lower()

    # Direct match
    for action in known_actions:
        if action in text_lower:
            found.append(action)

    # Keyword heuristics
    keyword_map = {
        "api": "api-call", "curl": "api-call", "fetch": "api-call",
        "read": "file-read", "parse": "file-read", "extract": "file-read",
        "write": "file-write", "save": "file-write", "create": "file-write",
        "move": "file-move", "rename": "file-move", "copy": "file-move",
        "sql": "database-query", "sqlite": "database-query", "query": "database-query",
        "database": "database-query", "insert": "database-write",
        "script": "script-execution", "python": "script-execution",
        "execute": "script-execution", "run": "script-execution",
        "install": "package-install", "pip": "package-install",
        "setup": "environment-setup", "configure": "environment-setup",
        "browse": "web-navigation", "navigate": "web-navigation",
        "scrape": "web-scraping", "crawl": "web-scraping",
        "git": "git-operation", "commit": "git-operation", "clone": "git-operation",
        "email": "email-send", "mail": "email-send",
        "convert": "document-conversion", "pdf": "document-conversion",
        "chart": "data-visualization", "plot": "data-visualization",
        "graph": "data-visualization", "matplotlib": "data-visualization",
        "grep": "command-line-tool", "sed": "command-line-tool",
        "awk": "command-line-tool", "ffmpeg": "command-line-tool",
    }
    for keyword, action in keyword_map.items():
        if keyword in text_lower and action not in found:
            found.append(action)

    return found if found else ["script-execution", "file-write"]


# ---------------------------------------------------------------------------
# Task ID generation
# ---------------------------------------------------------------------------


def generate_task_id(domain: str) -> str:
    """Generate the next task ID for a domain (e.g., fin-001, cs-002)."""
    prefix_map = {
        "computer-science": "cs",
        "mathematics": "math",
        "physics-engineering": "phys",
        "biology-chemistry": "bio",
        "financial-analysis": "fin",
        "accounting": "acct",
        "marketing": "mkt",
        "contract-review": "law",
        "legal-research": "lres",
        "clinical-data": "clin",
        "medical-research": "mres",
        "sociology": "soc",
        "education": "edu",
    }
    prefix = prefix_map.get(domain, "task")
    domain_dir = TASKS_DIR / DOMAIN_DIR_MAP.get(domain, domain)

    existing_ids = []
    if domain_dir.exists():
        for d in domain_dir.iterdir():
            if d.is_dir():
                match = re.search(r"-(\d{3})", d.name)
                if match:
                    existing_ids.append(int(match.group(1)))

    next_num = max(existing_ids, default=0) + 1
    return f"{prefix}-{next_num:03d}"


def slugify(text: str) -> str:
    """Convert text to a URL-friendly slug."""
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text[:60].strip("-")


# ---------------------------------------------------------------------------
# LLM interaction
# ---------------------------------------------------------------------------


def call_llm(prompt: str, model: str = DEFAULT_MODEL) -> str:
    """Call the LLM via the OpenAI-compatible API."""
    try:
        from openai import OpenAI
    except ImportError:
        print("ERROR: openai package not installed. Run: pip install openai", file=sys.stderr)
        sys.exit(1)

    client = OpenAI()  # Uses OPENAI_API_KEY and OPENAI_BASE_URL from env
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a benchmark task engineer for Claw-Bench, an AI Agent evaluation framework. "
                    "You generate complete, runnable benchmark tasks from expert proposals. "
                    "Your output must be precise, executable, and follow the exact format specified. "
                    "All tasks MUST test agent ACTION-TAKING capabilities (file operations, API calls, "
                    "database queries, script execution, etc.), NOT just knowledge or Q&A."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
        max_tokens=8000,
    )
    return response.choices[0].message.content or ""


def generate_task_files(proposal: dict[str, Any], model: str = DEFAULT_MODEL) -> dict[str, str]:
    """Call LLM to generate all task files from a proposal.

    Returns a dict mapping relative file paths to their content.
    """
    domain = proposal.get("domain", "computer-science")
    task_id = generate_task_id(domain)
    slug = slugify(proposal.get("taskTitle", "untitled"))
    task_dir_name = f"{task_id}-{slug}"
    difficulty = proposal.get("difficulty", "L2")

    prompt = _build_generation_prompt(proposal, task_id, task_dir_name, difficulty)
    raw_output = call_llm(prompt, model=model)

    # Parse the LLM output into individual files
    files = _parse_llm_output(raw_output, task_id, task_dir_name, domain, difficulty, proposal)
    return files


def _build_generation_prompt(
    proposal: dict[str, Any],
    task_id: str,
    task_dir_name: str,
    difficulty: str,
) -> str:
    """Build the prompt that instructs the LLM to generate task files."""

    actions_str = ", ".join(proposal.get("requiredActions", []))

    return textwrap.dedent(f"""\
    Generate a complete Claw-Bench benchmark task from the following expert proposal.

    ## Expert Proposal
    - **Domain**: {proposal.get("domain", "")}
    - **Title**: {proposal.get("taskTitle", "")}
    - **Difficulty**: {difficulty}
    - **Real-world Context**: {proposal.get("context", "")}
    - **Agent Instruction**: {proposal.get("instruction", "")}
    - **Required Agent Actions**: {actions_str}
    - **Success Criteria**: {proposal.get("successCriteria", "")}
    - **Data Requirements**: {proposal.get("dataRequirements", "")}

    ## Task ID and Directory
    - Task ID: `{task_id}`
    - Directory name: `{task_dir_name}`

    ## Required Output

    Generate the following files. Output each file between markers like:
    ```
    === FILE: <filename> ===
    <content>
    === END FILE ===
    ```

    ### 1. task.toml
    Follow this exact format:
    ```toml
    id = "{task_id}"
    title = "<title>"
    track = "subject-matter"
    domain = "{proposal.get("domain", "")}"
    level = "{difficulty}"
    description = "<one-line description>"
    timeout = <seconds, 120-600 based on complexity>
    capabilities = [<list of capability strings>]
    required_actions = [{', '.join(f'"{a}"' for a in proposal.get("requiredActions", []))}]
    skills_allowed = true
    tags = [<relevant tags>]
    capability_types = [<from: "reasoning", "tool-use", "memory", "multimodal", "collaboration">]
    ```

    ### 2. instruction.md
    Write a clear, detailed instruction for the AI Agent. Include:
    - A title (# Task: ...)
    - Context about what the agent needs to do
    - Step-by-step requirements
    - Expected output format and location
    - Any constraints or important notes
    The instruction MUST require the agent to perform CONCRETE ACTIONS (run scripts, modify files,
    call APIs, query databases, etc.), not just answer questions.

    ### 3. environment/setup.sh
    A bash script that:
    - Creates the workspace directory
    - Generates or copies any required test data files (synthetic/mock data)
    - Installs any required packages (pip install, apt-get, etc.)
    - Starts any mock services if needed (e.g., a simple Flask API server)
    - Must be idempotent and use `set -euo pipefail`
    IMPORTANT: Generate realistic synthetic test data inline in the script.
    Do NOT reference external files that don't exist.

    ### 4. environment/data/ files
    If the task needs input data files (CSV, JSON, SQL, etc.), generate them.
    Output each data file as a separate FILE block.
    Make the data realistic but synthetic (no real PII).

    ### 5. verifier/test_output.py
    A pytest-based verification script that:
    - Uses `@pytest.fixture` for workspace path
    - Tests that the agent produced correct output files
    - Tests that output content matches expected criteria
    - Tests SYSTEM STATE changes (files moved, databases updated, etc.)
    - Tests that required actions were actually performed
    - Uses `@pytest.mark.weight(N)` for scoring (higher N = more important)
    - Includes at least 5 test functions
    - Checks for the specific success criteria from the expert

    The verifier MUST check:
    a) Output file existence and format
    b) Output content correctness (specific values, structures)
    c) System state changes (files created/moved, DB records, etc.)
    d) That the agent didn't just hardcode answers but actually processed data

    ### 6. verifier/expected/ files (optional)
    If there are expected output files for comparison, generate them.

    ### 7. solution/solve.sh
    An oracle solution script that correctly completes the task.
    This proves the task is solvable and serves as a reference.
    Must use `set -euo pipefail` and accept workspace path as $1.

    ## Important Rules
    - All generated data must be SYNTHETIC and realistic
    - The task MUST require the agent to EXECUTE actions, not just produce text
    - The verifier must check both outputs AND system state changes
    - Scripts must be self-contained and runnable in a clean Ubuntu environment
    - Use Python 3.11+ compatible code
    """)


def _parse_llm_output(
    raw: str,
    task_id: str,
    task_dir_name: str,
    domain: str,
    difficulty: str,
    proposal: dict[str, Any],
) -> dict[str, str]:
    """Parse the LLM's output into a dict of filepath -> content."""
    files: dict[str, str] = {}
    domain_dir = DOMAIN_DIR_MAP.get(domain, domain)
    base = f"tasks/{domain_dir}/{task_dir_name}"

    # Extract file blocks
    pattern = r"===\s*FILE:\s*(.+?)\s*===\s*\n(.*?)===\s*END FILE\s*==="
    matches = re.findall(pattern, raw, re.DOTALL)

    for filename, content in matches:
        filename = filename.strip()
        content = content.strip()

        # Remove markdown code fences if present
        content = re.sub(r"^```\w*\n", "", content)
        content = re.sub(r"\n```$", "", content)

        # Map filename to the correct path
        if filename == "task.toml":
            files[f"{base}/task.toml"] = content + "\n"
        elif filename == "instruction.md":
            files[f"{base}/instruction.md"] = content + "\n"
        elif filename == "setup.sh" or filename == "environment/setup.sh":
            files[f"{base}/environment/setup.sh"] = content + "\n"
        elif filename == "test_output.py" or filename == "verifier/test_output.py":
            files[f"{base}/verifier/test_output.py"] = content + "\n"
        elif filename == "solve.sh" or filename == "solution/solve.sh":
            files[f"{base}/solution/solve.sh"] = content + "\n"
        elif filename.startswith("environment/data/") or filename.startswith("data/"):
            clean_name = filename.replace("data/", "environment/data/", 1) if not filename.startswith("environment/") else filename
            files[f"{base}/{clean_name}"] = content + "\n"
        elif filename.startswith("verifier/expected/") or filename.startswith("expected/"):
            clean_name = filename if filename.startswith("verifier/") else f"verifier/{filename}"
            files[f"{base}/{clean_name}"] = content + "\n"
        else:
            # Put unknown files in environment/data/
            files[f"{base}/environment/data/{filename}"] = content + "\n"

    # Ensure we have the minimum required files; generate fallbacks if missing
    if f"{base}/task.toml" not in files:
        files[f"{base}/task.toml"] = _fallback_task_toml(task_id, domain, difficulty, proposal)
    if f"{base}/instruction.md" not in files:
        files[f"{base}/instruction.md"] = _fallback_instruction(proposal)
    if f"{base}/environment/setup.sh" not in files:
        files[f"{base}/environment/setup.sh"] = _fallback_setup_sh()
    if f"{base}/verifier/test_output.py" not in files:
        files[f"{base}/verifier/test_output.py"] = _fallback_verifier(proposal)
    if f"{base}/solution/solve.sh" not in files:
        files[f"{base}/solution/solve.sh"] = _fallback_solution()

    return files


# ---------------------------------------------------------------------------
# Fallback generators (if LLM output is incomplete)
# ---------------------------------------------------------------------------


def _fallback_task_toml(task_id: str, domain: str, difficulty: str, proposal: dict) -> str:
    actions = proposal.get("requiredActions", ["script-execution", "file-write"])
    actions_str = ", ".join(f'"{a}"' for a in actions)
    return textwrap.dedent(f"""\
    id = "{task_id}"
    title = "{proposal.get('taskTitle', 'Untitled Task')}"
    track = "subject-matter"
    domain = "{domain}"
    level = "{difficulty}"
    description = "{proposal.get('taskTitle', 'Expert-contributed task')}"
    timeout = 300
    capabilities = [{actions_str}]
    required_actions = [{actions_str}]
    skills_allowed = true
    tags = ["expert-contributed", "{domain}"]
    capability_types = ["tool-use", "reasoning"]
    """)


def _fallback_instruction(proposal: dict) -> str:
    return textwrap.dedent(f"""\
    # Task: {proposal.get('taskTitle', 'Untitled Task')}

    ## Context
    {proposal.get('context', 'No context provided.')}

    ## Instructions
    {proposal.get('instruction', 'No instruction provided.')}

    ## Success Criteria
    {proposal.get('successCriteria', 'No criteria provided.')}

    ## Output
    Save your results in the `workspace/` directory.
    """)


def _fallback_setup_sh() -> str:
    return textwrap.dedent("""\
    #!/usr/bin/env bash
    set -euo pipefail
    TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
    WORKSPACE="${1:-$TASK_DIR/workspace}"
    mkdir -p "$WORKSPACE"
    echo "Workspace ready at $WORKSPACE"
    """)


def _fallback_verifier(proposal: dict) -> str:
    return textwrap.dedent("""\
    \"\"\"Auto-generated verifier stub. Needs manual review.\"\"\"
    import pytest
    from pathlib import Path

    @pytest.fixture
    def workspace(tmp_path):
        return tmp_path

    @pytest.mark.weight(3)
    def test_output_exists(workspace):
        \"\"\"Check that the agent produced output files.\"\"\"
        files = list(workspace.iterdir())
        assert len(files) > 0, "No output files found in workspace"

    @pytest.mark.weight(1)
    def test_no_placeholder_values(workspace):
        \"\"\"Output files must not contain placeholder markers.\"\"\"
        placeholders = ["TODO", "FIXME", "PLACEHOLDER"]
        for f in workspace.iterdir():
            if f.is_file():
                content = f.read_text(errors="replace").lower()
                for p in placeholders:
                    assert p.lower() not in content, f"Placeholder '{p}' found in {f.name}"
    """)


def _fallback_solution() -> str:
    return textwrap.dedent("""\
    #!/usr/bin/env bash
    # Oracle solution stub — needs manual implementation
    set -euo pipefail
    WORKSPACE="${1:-workspace}"
    mkdir -p "$WORKSPACE"
    echo "TODO: Implement oracle solution" > "$WORKSPACE/README.md"
    """)


# ---------------------------------------------------------------------------
# File writing
# ---------------------------------------------------------------------------


def write_task_files(files: dict[str, str], dry_run: bool = False) -> list[str]:
    """Write generated files to disk. Returns list of created file paths."""
    created = []
    for rel_path, content in files.items():
        full_path = PROJECT_ROOT / rel_path
        if dry_run:
            print(f"  [DRY RUN] Would create: {rel_path}")
            created.append(rel_path)
            continue

        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content)

        # Make shell scripts executable
        if full_path.suffix == ".sh":
            full_path.chmod(0o755)

        created.append(rel_path)
        print(f"  Created: {rel_path}")

    return created


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="Generate a Claw-Bench task from an expert proposal",
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument(
        "--proposal", type=str,
        help="Path to a local JSON proposal file",
    )
    source.add_argument(
        "--issue", type=int,
        help="GitHub Issue number to parse",
    )
    parser.add_argument(
        "--model", type=str, default=DEFAULT_MODEL,
        help=f"LLM model to use (default: {DEFAULT_MODEL})",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print what would be created without writing files",
    )
    args = parser.parse_args()

    # Load proposal
    print("Loading proposal...")
    if args.proposal:
        proposal = load_proposal_from_file(args.proposal)
    else:
        proposal = load_proposal_from_issue(args.issue)

    print(f"  Domain:     {proposal.get('domain', '?')}")
    print(f"  Title:      {proposal.get('taskTitle', '?')}")
    print(f"  Difficulty:  {proposal.get('difficulty', '?')}")
    print(f"  Actions:    {proposal.get('requiredActions', [])}")
    print()

    # Generate task files via LLM
    print(f"Generating task files using {args.model}...")
    files = generate_task_files(proposal, model=args.model)
    print(f"  Generated {len(files)} files")
    print()

    # Write files
    print("Writing files..." if not args.dry_run else "Dry run — not writing files:")
    created = write_task_files(files, dry_run=args.dry_run)
    print()
    print(f"Done! {len(created)} files {'would be ' if args.dry_run else ''}created.")

    if not args.dry_run:
        # Print the task directory for convenience
        domain = proposal.get("domain", "computer-science")
        domain_dir = DOMAIN_DIR_MAP.get(domain, domain)
        task_dirs = [p for p in created if "task.toml" in p]
        if task_dirs:
            task_dir = str(Path(task_dirs[0]).parent)
            print(f"\nTask directory: {task_dir}")
            print(f"\nNext steps:")
            print(f"  1. Review the generated files in {task_dir}")
            print(f"  2. Run the setup script: bash {task_dir}/environment/setup.sh")
            print(f"  3. Test the verifier: pytest {task_dir}/verifier/test_output.py")
            print(f"  4. Run the oracle solution: bash {task_dir}/solution/solve.sh")

    return 0


if __name__ == "__main__":
    sys.exit(main())
