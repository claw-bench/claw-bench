"""Verifier for mem-007: Instruction Chaining."""

import pytest
from pathlib import Path


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


# --- Step 1 tests ---

def test_step1_exists(workspace):
    """step1_sorted.txt must exist."""
    assert (workspace / "step1_sorted.txt").exists(), "step1_sorted.txt not found"


def test_step1_has_all_items(workspace):
    """step1_sorted.txt must contain all 20 items."""
    content = (workspace / "step1_sorted.txt").read_text().strip()
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    assert len(lines) == 20, f"Expected 20 items, got {len(lines)}"


def test_step1_sorted_descending(workspace):
    """step1_sorted.txt must be sorted by score descending."""
    content = (workspace / "step1_sorted.txt").read_text().strip()
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    scores = []
    for line in lines:
        score = int(line.split()[0])
        scores.append(score)
    assert scores == sorted(scores, reverse=True), (
        f"Scores not in descending order: {scores}"
    )


def test_step1_first_item(workspace):
    """First item must be Quantum Processor with score 92."""
    content = (workspace / "step1_sorted.txt").read_text().strip()
    first_line = content.splitlines()[0].strip()
    assert first_line.startswith("92"), f"Expected first score 92, got: {first_line}"
    assert "Quantum Processor" in first_line, f"Expected Quantum Processor first, got: {first_line}"


def test_step1_last_item(workspace):
    """Last item must be Cryo Cooler with score 31."""
    content = (workspace / "step1_sorted.txt").read_text().strip()
    last_line = content.splitlines()[-1].strip()
    assert last_line.startswith("31"), f"Expected last score 31, got: {last_line}"
    assert "Cryo Cooler" in last_line, f"Expected Cryo Cooler last, got: {last_line}"


# --- Step 2 tests ---

def test_step2_exists(workspace):
    """step2_grouped.txt must exist."""
    assert (workspace / "step2_grouped.txt").exists(), "step2_grouped.txt not found"


def test_step2_has_categories(workspace):
    """step2_grouped.txt must contain Hardware, Networking, Software sections."""
    content = (workspace / "step2_grouped.txt").read_text()
    for cat in ["Hardware", "Networking", "Software"]:
        assert cat in content, f"Missing category section: {cat}"


def test_step2_excludes_low_scores(workspace):
    """step2_grouped.txt must not contain items with score < 50."""
    content = (workspace / "step2_grouped.txt").read_text()
    excluded = ["Cryo Cooler", "Plasma Screen X", "Mesh Router X1",
                "WiFi Amplifier", "VirtManager"]
    for item in excluded:
        assert item not in content, (
            f"Item '{item}' should be excluded (score < 50)"
        )


def test_step2_includes_items_at_50_boundary(workspace):
    """Items with score exactly 50 or above must be included."""
    content = (workspace / "step2_grouped.txt").read_text()
    included = ["Quantum Processor", "Load Balancer G5", "Fiber Hub 200",
                "Photon Switch", "AutoDeploy", "Power Unit 5K",
                "CodeAnalyzer 3"]
    for item in included:
        assert item in content, (
            f"Item '{item}' should be included (score >= 50)"
        )


# --- Step 3 tests ---

def test_step3_exists(workspace):
    """step3_stats.txt must exist."""
    assert (workspace / "step3_stats.txt").exists(), "step3_stats.txt not found"


def test_step3_has_three_categories(workspace):
    """step3_stats.txt must have exactly 3 category lines."""
    content = (workspace / "step3_stats.txt").read_text().strip()
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    assert len(lines) == 3, f"Expected 3 category stats lines, got {len(lines)}"


def test_step3_hardware_stats(workspace):
    """Hardware: count=5, avg=76.2."""
    content = (workspace / "step3_stats.txt").read_text()
    assert "Hardware" in content, "Missing Hardware in stats"
    # Find the hardware line
    for line in content.splitlines():
        if "Hardware" in line:
            assert "count=5" in line, f"Expected Hardware count=5, got: {line}"
            assert "avg=76.2" in line, f"Expected Hardware avg=76.2, got: {line}"
            break


def test_step3_networking_stats(workspace):
    """Networking: count=4, avg=77.7 or 77.8."""
    content = (workspace / "step3_stats.txt").read_text()
    assert "Networking" in content, "Missing Networking in stats"
    for line in content.splitlines():
        if "Networking" in line:
            assert "count=4" in line, f"Expected Networking count=4, got: {line}"
            assert "avg=77.7" in line or "avg=77.8" in line, (
                f"Expected Networking avg=77.7 or 77.8, got: {line}"
            )
            break


def test_step3_software_stats(workspace):
    """Software: count=6, avg=67.5."""
    content = (workspace / "step3_stats.txt").read_text()
    assert "Software" in content, "Missing Software in stats"
    for line in content.splitlines():
        if "Software" in line:
            assert "count=6" in line, f"Expected Software count=6, got: {line}"
            assert "avg=67.5" in line, f"Expected Software avg=67.5, got: {line}"
            break


def test_step3_sorted_by_avg_descending(workspace):
    """Categories must be sorted by average score descending."""
    content = (workspace / "step3_stats.txt").read_text().strip()
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    avgs = []
    for line in lines:
        # Extract avg value after "avg="
        import re
        match = re.search(r'avg=(\d+\.?\d*)', line)
        if match:
            avgs.append(float(match.group(1)))
    assert avgs == sorted(avgs, reverse=True), (
        f"Averages not in descending order: {avgs}"
    )


# --- Step 4 tests ---

def test_step4_exists(workspace):
    """step4_report.txt must exist."""
    assert (workspace / "step4_report.txt").exists(), "step4_report.txt not found"


def test_step4_report_generated(workspace):
    """step4_report.txt must start with REPORT GENERATED."""
    content = (workspace / "step4_report.txt").read_text().strip()
    assert content.splitlines()[0].strip() == "REPORT GENERATED", (
        "First line must be 'REPORT GENERATED'"
    )


def test_step4_total_categories(workspace):
    """step4_report.txt must show Total categories: 3."""
    content = (workspace / "step4_report.txt").read_text()
    assert "Total categories: 3" in content, (
        "Must contain 'Total categories: 3'"
    )


def test_step4_highest_avg(workspace):
    """Highest avg category must be Networking."""
    content = (workspace / "step4_report.txt").read_text()
    assert "Networking" in content, "Highest avg category should be Networking"
    for line in content.splitlines():
        if "Highest" in line or "highest" in line:
            assert "Networking" in line, (
                f"Highest avg category must be Networking, got: {line}"
            )
            break


def test_step4_lowest_avg(workspace):
    """Lowest avg category must be Software."""
    content = (workspace / "step4_report.txt").read_text()
    for line in content.splitlines():
        if "Lowest" in line or "lowest" in line:
            assert "Software" in line, (
                f"Lowest avg category must be Software, got: {line}"
            )
            break


def test_step4_grand_average(workspace):
    """Grand average must be approximately 73.8."""
    content = (workspace / "step4_report.txt").read_text()
    for line in content.splitlines():
        if "Grand average" in line or "grand average" in line:
            import re
            match = re.search(r'(\d+\.?\d*)', line.split(":")[-1])
            assert match, f"Could not find number in grand average line: {line}"
            val = float(match.group(1))
            assert abs(val - 73.8) < 0.5, (
                f"Expected grand average ~73.8, got {val}"
            )
            break
