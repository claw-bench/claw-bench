"""Verifier for data-007: Join Two Datasets."""

from pathlib import Path
import csv
import pytest


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def enriched_rows(workspace):
    path = workspace / "enriched_orders.csv"
    assert path.exists(), "enriched_orders.csv not found"
    with open(path) as f:
        return list(csv.DictReader(f))


def test_enriched_file_exists(workspace):
    assert (workspace / "enriched_orders.csv").exists()


def test_all_orders_present(enriched_rows):
    assert len(enriched_rows) == 25, f"Expected 25 orders, got {len(enriched_rows)}"


def test_correct_column_count(workspace):
    path = workspace / "enriched_orders.csv"
    header = path.read_text().strip().splitlines()[0].split(",")
    assert len(header) == 7, f"Expected 7 columns, got {len(header)}"


def test_customer_info_populated(enriched_rows):
    for row in enriched_rows:
        assert row.get("name", "").strip() != "", f"Missing name for order {row['order_id']}"
        assert row.get("email", "").strip() != "", f"Missing email for order {row['order_id']}"


def test_correct_customer_mapping(enriched_rows):
    """Spot-check a few known mappings."""
    cust_map = {
        "1": "Alice Smith", "2": "Bob Jones", "3": "Carol White",
        "4": "Dave Brown", "5": "Eve Davis", "6": "Frank Miller",
        "7": "Grace Lee", "8": "Hank Wilson", "9": "Iris Taylor",
        "10": "Jack Moore"
    }
    for row in enriched_rows:
        cid = row["customer_id"]
        if cid in cust_map:
            assert row["name"] == cust_map[cid], f"Order {row['order_id']}: expected name {cust_map[cid]}, got {row['name']}"


def test_order_id_preserved(enriched_rows):
    ids = [int(row["order_id"]) for row in enriched_rows]
    assert ids == list(range(1, 26)), "Order IDs not preserved in original order"


# ── Enhanced checks (auto-generated) ────────────────────────────────────────

@pytest.mark.weight(1)
def test_no_placeholder_values(workspace):
    """Output files must not contain placeholder/TODO markers."""
    placeholders = ["PLACEHOLDER", "CHANGEME"]
    for f in workspace.iterdir():
        if f.is_file() and f.suffix in (".json", ".csv", ".txt", ".md", ".py", ".yaml", ".yml", ".html", ".xml"):
            content = f.read_text(errors="replace")
            for p in placeholders:
                assert p not in content, f"Placeholder '{p}' found in {f.name}"

@pytest.mark.weight(1)
def test_encoding_valid(workspace):
    """All text output files must be valid UTF-8."""
    for f in workspace.iterdir():
        if f.is_file() and f.suffix in (".json", ".csv", ".txt", ".md", ".py", ".yaml", ".yml", ".html"):
            try:
                f.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                pytest.fail(f"{f.name} contains invalid UTF-8 encoding")

@pytest.mark.weight(1)
def test_no_duplicate_entries(workspace):
    """Output should not contain exact duplicate rows/objects."""
    import json
    path = workspace / "orders.csv"
    if not path.exists():
        pytest.skip("output file not found")
    text = path.read_text().strip()
    if path.suffix == ".json":
        data = json.loads(text)
        if isinstance(data, list):
            serialized = [json.dumps(item, sort_keys=True) for item in data]
            dupes = len(serialized) - len(set(serialized))
            assert dupes == 0, f"Found {dupes} duplicate entries in {path.name}"
    elif path.suffix == ".csv":
        lines_list = text.splitlines()
        if len(lines_list) > 1:
            data_lines = lines_list[1:]
            dupes = len(data_lines) - len(set(data_lines))
            assert dupes == 0, f"Found {dupes} duplicate rows in {path.name}"

@pytest.mark.weight(1)
def test_no_extraneous_files(workspace):
    """Workspace should not contain debug/temp files."""
    bad_patterns = [".DS_Store", "Thumbs.db", ".bak", ".tmp"]
    for f in workspace.rglob("*"):
        if f.is_file():
            for pat in bad_patterns:
                assert pat not in f.name, f"Extraneous file found: {f.name}"

@pytest.mark.weight(1)
def test_output_not_excessively_large(workspace):
    """Output files should be reasonably sized (< 5MB each)."""
    for f in workspace.iterdir():
        if f.is_file() and f.suffix in (".json", ".csv", ".txt", ".md", ".py", ".yaml", ".yml", ".html"):
            size_mb = f.stat().st_size / (1024 * 1024)
            assert size_mb < 5, f"{f.name} is {size_mb:.1f}MB, exceeds 5MB limit"

@pytest.mark.weight(2)
def test_json_parseable_if_present(workspace):
    """Any .json files in workspace must be valid JSON."""
    import json
    for f in workspace.iterdir():
        if f.is_file() and f.suffix == ".json":
            try:
                json.loads(f.read_text())
            except json.JSONDecodeError:
                pytest.fail(f"{f.name} is not valid JSON")
