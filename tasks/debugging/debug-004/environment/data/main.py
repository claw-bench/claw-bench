from utils import process_data, validate_format


def main():
    data = {"users": 150, "orders": 340, "revenue": 52000}
    print("json valid:", validate_format("json"))
    print(process_data(data, "json"))


if __name__ == "__main__":
    main()
