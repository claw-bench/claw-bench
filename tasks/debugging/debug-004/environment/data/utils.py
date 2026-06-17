from config import get_settings


def validate_format(fmt):
    settings = get_settings()
    return fmt in settings["formats"]


def format_output(data):
    settings = get_settings()
    lines = [
        f"{settings['app_name']} Report",
        f"Version: {settings['version']}",
    ]
    for key, value in data.items():
        lines.append(f"{key}: {value}")
    return "\n".join(lines)


def process_data(data, output_format):
    if not validate_format(output_format):
        raise ValueError(f"Unsupported format: {output_format}")
    result = {
        "processed_items": len(data),
        "format": output_format,
        **data,
    }
    return format_output(result)
