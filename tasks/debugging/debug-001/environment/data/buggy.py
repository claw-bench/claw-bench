def greet(name):
    if name == "World"
        return "Hello, World!"
    return "Hi, " + name + "!"


def calculate_sum(numbers):
    total = 0
    for n in numbers:
        total += n
  return total


def format_output(values):
    result = "Output: " + (
        ", ".join(str(v) for v in values)
    return result


def main():
    print(greet("World"))
    print("Sum:", calculate_sum([1, 2, 3, 4, 5]))
    print(format_output([1, 2, 3, 4, 5]))


if __name__ == "__main__":
    main()
