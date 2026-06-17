APP_NAME = "DataProcessor"
VERSION = "1.0.0"
MAX_RETRIES = 3
TIMEOUT = 30
SUPPORTED_FORMATS = ["json", "csv", "xml"]


def get_config():
    return {
        "app_name": APP_NAME,
        "version": VERSION,
        "max_retries": MAX_RETRIES,
        "timeout": TIMEOUT,
        "formats": SUPPORTED_FORMATS,
    }
