"""Verifier for mm-003: Code Documentation Extraction."""

from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def doc_text(workspace):
    path = workspace / "documentation.md"
    assert path.exists(), "documentation.md not found in workspace"
    return path.read_text()


def test_output_file_exists(workspace):
    assert (workspace / "documentation.md").exists()


def test_module_heading(doc_text):
    assert "# data_processor" in doc_text


def test_module_docstring(doc_text):
    assert "Data processing module" in doc_text
    assert "CSV and JSON transformations" in doc_text


def test_class_dataloader(doc_text):
    assert "## DataLoader" in doc_text
    assert "Load data from various file formats" in doc_text


def test_class_transformpipeline(doc_text):
    assert "## TransformPipeline" in doc_text
    assert "Pipeline for chaining data transformations" in doc_text


def test_class_dataexporter(doc_text):
    assert "## DataExporter" in doc_text
    assert "Export processed data to output files" in doc_text


def test_method_load_csv(doc_text):
    assert "### DataLoader.load_csv" in doc_text
    assert "Load data from a CSV file" in doc_text


def test_method_load_json(doc_text):
    assert "### DataLoader.load_json" in doc_text
    assert "Load data from a JSON file" in doc_text


def test_method_add_step(doc_text):
    assert "### TransformPipeline.add_step" in doc_text
    assert "Add a transformation step" in doc_text


def test_method_execute(doc_text):
    assert "### TransformPipeline.execute" in doc_text
    assert "Execute all pipeline steps" in doc_text


def test_method_init_pipeline(doc_text):
    assert "### TransformPipeline.__init__" in doc_text
    assert "Initialize an empty pipeline" in doc_text


def test_method_to_json(doc_text):
    assert "### DataExporter.to_json" in doc_text
    assert "Write data to a JSON file" in doc_text


def test_method_to_csv(doc_text):
    assert "### DataExporter.to_csv" in doc_text
    assert "Write a list of dictionaries to a CSV file" in doc_text


def test_function_filter_records(doc_text):
    assert "## filter_records" in doc_text
    assert "Filter a list of records by a field value" in doc_text


def test_function_aggregate_by(doc_text):
    assert "## aggregate_by" in doc_text
    assert "Aggregate records by a grouping field" in doc_text


def test_no_private_validate_path(doc_text):
    """_validate_path has no docstring and should not appear."""
    assert "_validate_path" not in doc_text


def test_no_internal_helper(doc_text):
    """_internal_helper has no docstring and should not appear."""
    assert "_internal_helper" not in doc_text


def test_no_private_log_step(doc_text):
    """_log_step has no docstring and should not appear."""
    assert "_log_step" not in doc_text


def test_order_classes_before_functions(doc_text):
    """Classes should appear before standalone functions (matching source order)."""
    pos_dataloader = doc_text.index("## DataLoader")
    pos_filter = doc_text.index("## filter_records")
    assert pos_dataloader < pos_filter


def test_order_within_classes(doc_text):
    """Methods should appear in source order within their class."""
    pos_load_csv = doc_text.index("### DataLoader.load_csv")
    pos_load_json = doc_text.index("### DataLoader.load_json")
    assert pos_load_csv < pos_load_json
