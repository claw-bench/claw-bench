"""Entry point for the DataProcessor application."""

from config import get_config
from utils import format_output, process_data


def main():
    """Process a sample payload and print the formatted report."""
    result = process_data({"users": 150, "orders": 340, "revenue": 52000}, "json")
    report = format_output(result)
    print(report)


if __name__ == "__main__":
    main()
