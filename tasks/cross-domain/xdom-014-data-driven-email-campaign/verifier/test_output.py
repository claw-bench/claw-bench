from pathlib import Path
"""Verifier for xdom-014: Data-Driven Email Campaign."""

import json
import os
import re

import pytest


@pytest.fixture
def workspace(request):
    """Resolve workspace from --workspace CLI option."""
    ws = request.config.getoption("--workspace")
    if ws:
        return Path(ws)
    return Path(os.environ.get("CLAW_WORKSPACE", os.environ.get("WORKSPACE", "workspace")))


WORKSPACE = os.environ.get(
    "WORKSPACE",
    os.path.join(os.path.dirname(__file__), "..", "workspace"),
)

OUTPUT_DIR = os.path.join(WORKSPACE, "output")


@pytest.fixture
def summary():
    path = os.path.join(OUTPUT_DIR, "campaign_summary.json")
    assert os.path.exists(path), "campaign_summary.json not found in output/"
    with open(path) as f:
        return json.load(f)


class TestOutputDirectoryExists:
    def test_output_dir(self):
        assert os.path.isdir(OUTPUT_DIR), "output/ directory not found in workspace"


class TestCampaignSummaryStructure:
    REQUIRED_FIELDS = [
        "total_customers",
        "eligible_customers",
        "excluded_customers",
        "segments",
        "emails_generated",
    ]

    def test_required_fields(self, summary):
        for field in self.REQUIRED_FIELDS:
            assert field in summary, f"Missing field: {field}"

    def test_total_customers(self, summary):
        assert summary["total_customers"] == 20, (
            f"total_customers should be 20, got {summary['total_customers']}"
        )

    def test_eligible_plus_excluded_equals_total(self, summary):
        total = summary.get("eligible_customers", 0) + summary.get("excluded_customers", 0)
        assert total == summary["total_customers"], (
            f"eligible ({summary.get('eligible_customers')}) + excluded ({summary.get('excluded_customers')}) "
            f"!= total ({summary['total_customers']})"
        )

    def test_emails_generated_matches_eligible(self, summary):
        assert summary["emails_generated"] == summary["eligible_customers"], (
            "emails_generated should equal eligible_customers"
        )

    def test_segments_present(self, summary):
        segs = summary.get("segments", {})
        assert len(segs) >= 3, f"Expected at least 3 segments, got {len(segs)}"


class TestCustomerEligibility:
    """Verify correct filtering based on rules.toml criteria."""

    # Opted-out customers: 1010 (James, loyal, opted_in=false),
    #   1012 (Leo, lapsed, false), 1017 (Quinn, premium, false)
    # These should never have email files.

    OPTED_OUT_IDS = ["1010", "1012", "1017"]

    def test_opted_out_customers_excluded(self):
        for cid in self.OPTED_OUT_IDS:
            path = os.path.join(OUTPUT_DIR, f"{cid}.html")
            assert not os.path.exists(path), (
                f"Customer {cid} is opted out and should not have an email file"
            )

    # Premium: min_lifetime_value=5000, opted_in=true
    # Eligible premium: 1001 (12500), 1002 (9800.50), 1009 (15200), 1013 (8700)
    PREMIUM_IDS = ["1001", "1002", "1009", "1013"]

    def test_premium_emails_generated(self):
        for cid in self.PREMIUM_IDS:
            path = os.path.join(OUTPUT_DIR, f"{cid}.html")
            assert os.path.exists(path), f"Premium customer {cid} should have an email"

    # New: max_purchase_count=5, opted_in=true
    # Eligible new: 1005 (2), 1006 (1), 1011 (3), 1015 (1), 1019 (2)
    NEW_IDS = ["1005", "1006", "1011", "1015", "1019"]

    def test_new_customer_emails_generated(self):
        for cid in self.NEW_IDS:
            path = os.path.join(OUTPUT_DIR, f"{cid}.html")
            assert os.path.exists(path), f"New customer {cid} should have an email"


class TestTemplateSubstitution:
    """Verify variables are substituted in generated emails."""

    def test_no_raw_placeholders(self):
        """No {{variable}} placeholders should remain in any output file."""
        for fname in os.listdir(OUTPUT_DIR):
            if not fname.endswith(".html"):
                continue
            with open(os.path.join(OUTPUT_DIR, fname)) as f:
                content = f.read()
            matches = re.findall(r'\{\{[a-z_]+\}\}', content)
            assert not matches, (
                f"File {fname} has unsubstituted placeholders: {matches}"
            )

    def test_premium_customer_has_offer_code(self):
        """Premium emails should contain VIP25SPRING."""
        path = os.path.join(OUTPUT_DIR, "1001.html")
        if os.path.exists(path):
            with open(path) as f:
                content = f.read()
            assert "VIP25SPRING" in content, (
                "Premium email should contain offer code VIP25SPRING"
            )

    def test_winback_customer_has_offer_code(self):
        """Lapsed/winback emails should contain COMEBACK30."""
        # 1007 is lapsed and opted in
        path = os.path.join(OUTPUT_DIR, "1007.html")
        if os.path.exists(path):
            with open(path) as f:
                content = f.read()
            assert "COMEBACK30" in content, (
                "Winback email should contain offer code COMEBACK30"
            )

    def test_new_customer_has_bonus_item(self):
        """New customer emails should mention the Acme Tote Bag."""
        path = os.path.join(OUTPUT_DIR, "1005.html")
        if os.path.exists(path):
            with open(path) as f:
                content = f.read()
            assert "Acme Tote Bag" in content, (
                "New customer email should mention bonus item"
            )

    def test_customer_name_substituted(self):
        """Emails should contain the customer's first name."""
        path = os.path.join(OUTPUT_DIR, "1001.html")
        if os.path.exists(path):
            with open(path) as f:
                content = f.read()
            assert "Alice" in content, "Email for 1001 should contain 'Alice'"

    def test_emails_are_valid_html(self):
        """Each email should have basic HTML structure."""
        for fname in os.listdir(OUTPUT_DIR):
            if not fname.endswith(".html"):
                continue
            with open(os.path.join(OUTPUT_DIR, fname)) as f:
                content = f.read()
            assert "<html" in content.lower(), f"{fname} missing <html> tag"
            assert "</html>" in content.lower(), f"{fname} missing </html> tag"


class TestABTestVariants:
    """Verify A/B test logic."""

    def test_ab_test_distribution_in_summary(self, summary):
        ab = summary.get("ab_test_distribution", {})
        # Premium and lapsed should have ab_test
        has_ab = False
        for seg_name, dist in ab.items():
            if "variant_a" in dist and "variant_b" in dist:
                has_ab = True
                assert dist["variant_a"] + dist["variant_b"] > 0
        assert has_ab, "At least one segment should have A/B test distribution"

    def test_premium_ab_even_odd_split(self):
        """Premium: 1001(odd->B), 1002(even->A), 1009(odd->B), 1013(odd->B)."""
        # 1002 (even) should get subject_a, 1001 (odd) should get subject_b
        path_a = os.path.join(OUTPUT_DIR, "1002.html")
        path_b = os.path.join(OUTPUT_DIR, "1001.html")
        if os.path.exists(path_a) and os.path.exists(path_b):
            with open(path_a) as f:
                content_a = f.read()
            with open(path_b) as f:
                content_b = f.read()
            # Variant A has "Exclusive VIP Offer", Variant B has "VIP Rewards Are Waiting"
            # At least one of them should differ
            assert ("Exclusive VIP Offer" in content_a or "VIP Rewards Are Waiting" in content_b), (
                "A/B test variants should use different subject lines"
            )

    def test_email_count(self):
        """Verify reasonable number of email files generated."""
        html_files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith(".html")]
        # 20 total - 3 opted out = 17 potential; some may fail segment criteria
        assert len(html_files) >= 10, (
            f"Expected at least 10 email files, got {len(html_files)}"
        )
        assert len(html_files) <= 20, (
            f"Expected at most 20 email files, got {len(html_files)}"
        )


# ── Enhanced checks (auto-generated) ────────────────────────────────────────

@pytest.mark.weight(1)
def test_no_placeholder_values(workspace):
    """Output files must not contain placeholder/TODO markers."""
    placeholders = ["TODO", "FIXME", "XXX", "PLACEHOLDER", "CHANGEME", "your_"]
    for f in workspace.iterdir():
        if f.is_file() and f.suffix in (".json", ".csv", ".txt", ".md", ".py", ".yaml", ".yml", ".html", ".xml"):
            content = f.read_text(errors="replace").lower()
            for p in placeholders:
                assert p.lower() not in content, f"Placeholder '{p}' found in {f.name}"

@pytest.mark.weight(2)
def test_no_empty_critical_fields(workspace):
    """JSON output must not have empty-string or null values in top-level fields."""
    import json
    path = workspace / "campaign_summary.json"
    if not path.exists():
        pytest.skip("output file not found")
    data = json.loads(path.read_text())
    items = data if isinstance(data, list) else [data]
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            continue
        for k, v in item.items():
            assert v is not None, f"Item {i}: field '{k}' is null"
            if isinstance(v, str):
                assert v.strip() != "", f"Item {i}: field '{k}' is empty string"

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
def test_consistent_key_naming(workspace):
    """JSON keys should use a consistent naming convention."""
    import json, re
    path = workspace / "campaign_summary.json"
    if not path.exists():
        pytest.skip("output file not found")
    data = json.loads(path.read_text())
    items = data if isinstance(data, list) else [data]
    all_keys = set()
    for item in items:
        if isinstance(item, dict):
            all_keys.update(item.keys())
    if len(all_keys) < 2:
        return
    snake = sum(1 for k in all_keys if re.match(r'^[a-z][a-z0-9_]*$', k))
    camel = sum(1 for k in all_keys if re.match(r'^[a-z][a-zA-Z0-9]*$', k) and not re.match(r'^[a-z][a-z0-9_]*$', k))
    pascal = sum(1 for k in all_keys if re.match(r'^[A-Z][a-zA-Z0-9]*$', k))
    dominant = max(snake, camel, pascal)
    consistency = dominant / len(all_keys) if all_keys else 1
    assert consistency >= 0.7, f"Key naming inconsistent: {snake} snake, {camel} camel, {pascal} pascal out of {len(all_keys)} keys"

@pytest.mark.weight(1)
def test_no_duplicate_entries(workspace):
    """Output should not contain exact duplicate rows/objects."""
    import json
    path = workspace / "customers.csv"
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
    bad_patterns = [".pyc", "__pycache__", ".DS_Store", "Thumbs.db", ".log", ".bak", ".tmp"]
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
