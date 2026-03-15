"""A module with three syntax errors to fix."""


def greet(name):
    """Return a greeting string."""
    message = f"Hello, {name}!"
    return message


def compute_average(numbers)
    """Compute the average of a list of numbers."""
    if len(numbers) == 0:
        return 0.0
    total = sum(numbers)
    return total / len(numbers)


def build_report(title, items):
    """Build a formatted report string."""
    lines = [f"=== {title} ==="]
    for i, item in enumerate(items):
        lines.append(f"  {i + 1}. {item}"
    summary = f"Total items: {len(items)}"
    lines.append(summary)
    return "\n".join(lines
