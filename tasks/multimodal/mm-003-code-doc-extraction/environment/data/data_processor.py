"""
Data processing module for handling CSV and JSON transformations.

This module provides utilities for loading, transforming, and exporting
data in various formats. It supports filtering, aggregation, and
custom transformation pipelines.
"""

import csv
import json
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional


class DataLoader:
    """Load data from various file formats.

    Supports CSV, JSON, and line-delimited text files. Handles
    encoding detection and provides consistent output format
    as a list of dictionaries.
    """

    def __init__(self, encoding: str = "utf-8"):
        self.encoding = encoding
        self._cache = {}

    def load_csv(self, filepath: str, delimiter: str = ",") -> List[Dict[str, Any]]:
        """Load data from a CSV file.

        Reads the CSV file and returns a list of dictionaries where
        each dictionary represents a row with column headers as keys.

        Args:
            filepath: Path to the CSV file.
            delimiter: Column delimiter character.

        Returns:
            List of row dictionaries.
        """
        with open(filepath, encoding=self.encoding) as f:
            reader = csv.DictReader(f, delimiter=delimiter)
            return list(reader)

    def load_json(self, filepath: str) -> Any:
        """Load data from a JSON file.

        Parses the JSON file and returns the resulting Python object.
        Supports both JSON arrays and objects at the top level.

        Args:
            filepath: Path to the JSON file.

        Returns:
            Parsed JSON data.
        """
        with open(filepath, encoding=self.encoding) as f:
            return json.load(f)

    def _validate_path(self, filepath: str) -> bool:
        # Internal method - no docstring
        import os
        return os.path.exists(filepath)


class TransformPipeline:
    """Pipeline for chaining data transformations.

    Allows building a sequence of transformation steps that are
    applied in order to the input data. Each step receives the
    output of the previous step.
    """

    def __init__(self):
        """Initialize an empty pipeline."""
        self._steps: List[Callable] = []

    def add_step(self, func: Callable, name: str = "") -> "TransformPipeline":
        """Add a transformation step to the pipeline.

        Args:
            func: A callable that takes data and returns transformed data.
            name: Optional human-readable name for the step.

        Returns:
            Self, for method chaining.
        """
        self._steps.append((func, name))
        return self

    def execute(self, data: Any) -> Any:
        """Execute all pipeline steps on the input data.

        Applies each transformation step in sequence. If any step
        raises an exception, the pipeline stops and the exception
        propagates to the caller.

        Args:
            data: Input data to transform.

        Returns:
            Transformed data after all steps have been applied.
        """
        result = data
        for func, name in self._steps:
            result = func(result)
        return result

    def _log_step(self, step_name, data):
        pass


class DataExporter:
    """Export processed data to output files.

    Supports writing to CSV and JSON formats with configurable
    formatting options.
    """

    def __init__(self, pretty_print: bool = True):
        """Initialize the exporter with formatting options.

        Args:
            pretty_print: Whether to format output for readability.
        """
        self.pretty_print = pretty_print

    def to_json(self, data: Any, filepath: str) -> None:
        """Write data to a JSON file.

        Args:
            data: The data to serialize.
            filepath: Output file path.
        """
        indent = 2 if self.pretty_print else None
        with open(filepath, "w") as f:
            json.dump(data, f, indent=indent, default=str)

    def to_csv(self, data: List[Dict], filepath: str) -> None:
        """Write a list of dictionaries to a CSV file.

        Uses the keys of the first dictionary as column headers.

        Args:
            data: List of row dictionaries.
            filepath: Output file path.
        """
        if not data:
            return
        with open(filepath, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)


def filter_records(
    records: List[Dict], field: str, value: Any
) -> List[Dict]:
    """Filter a list of records by a field value.

    Returns only records where the specified field matches
    the given value. Comparison is done with equality.

    Args:
        records: List of record dictionaries.
        field: Field name to filter on.
        value: Value to match.

    Returns:
        Filtered list of records.
    """
    return [r for r in records if r.get(field) == value]


def aggregate_by(
    records: List[Dict], group_field: str, agg_field: str, func: str = "sum"
) -> Dict[str, Any]:
    """Aggregate records by a grouping field.

    Groups records by the specified field and applies an aggregation
    function to the aggregation field within each group.

    Supported functions: sum, count, avg, min, max.

    Args:
        records: List of record dictionaries.
        group_field: Field to group by.
        agg_field: Field to aggregate.
        func: Aggregation function name.

    Returns:
        Dictionary mapping group values to aggregated results.
    """
    groups: Dict[str, list] = {}
    for r in records:
        key = r.get(group_field)
        groups.setdefault(key, []).append(r.get(agg_field, 0))

    result = {}
    for key, values in groups.items():
        nums = [float(v) for v in values if v is not None]
        if func == "sum":
            result[key] = sum(nums)
        elif func == "count":
            result[key] = len(nums)
        elif func == "avg":
            result[key] = sum(nums) / len(nums) if nums else 0
        elif func == "min":
            result[key] = min(nums) if nums else None
        elif func == "max":
            result[key] = max(nums) if nums else None
    return result


def _internal_helper():
    # No docstring on purpose
    pass
