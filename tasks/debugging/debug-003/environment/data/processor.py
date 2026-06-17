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
    processed = []
    for record in records:
        processed.append({
            "name": get_user_name(record.get("user")),
            "theme": get_config_value(record.get("settings", {}), "theme"),
            "primary_tag": get_first_element(record.get("tags", [])),
        })
    return processed


def main():
    records = [
        {
            "user": {"first_name": "Alice", "last_name": "Smith"},
            "settings": {"theme": "dark"},
            "tags": ["admin", "active"],
        },
        {
            "user": None,
            "settings": {},
            "tags": [],
        },
    ]
    print(process_records(records))


if __name__ == "__main__":
    main()
