"""Record processing utilities (contains edge-case crash bugs)."""


def get_user_name(user):
    """Extract the full name from a user dict."""
    return user["first_name"] + " " + user["last_name"]


def get_config_value(config, key):
    """Get a configuration value by key."""
    return config[key]


def get_first_element(items):
    """Get the first element from a list."""
    return items[0]


def process_records(records):
    """Process a list of records into normalized result dicts."""
    results = []
    for record in records:
        user = record.get("user")
        settings = record.get("settings", {})
        tags = record.get("tags", [])
        results.append(
            {
                "name": get_user_name(user),
                "theme": get_config_value(settings, "theme"),
                "primary_tag": get_first_element(tags),
            }
        )
    return results


def main():
    """Run a small demonstration of the processing pipeline."""
    records = [
        {
            "user": {"first_name": "Alice", "last_name": "Smith"},
            "settings": {"theme": "dark"},
            "tags": ["admin"],
        },
        {
            "user": None,
            "settings": {},
            "tags": [],
        },
    ]
    for result in process_records(records):
        print(result)


if __name__ == "__main__":
    main()
