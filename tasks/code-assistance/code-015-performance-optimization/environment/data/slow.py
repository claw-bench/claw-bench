"""Intentionally slow implementations to be optimized."""


def find_duplicates(items):
    """Find all duplicate values in a list.

    Returns a sorted list of values that appear more than once.
    """
    duplicates = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if items[i] == items[j] and items[i] not in duplicates:
                duplicates.append(items[i])
    return sorted(duplicates)


def count_words(text):
    """Count the frequency of each word in the text.

    Returns a dict mapping word (lowercased) to count.
    Words are split by whitespace and stripped of punctuation.
    """
    import string
    words = text.lower().split()
    cleaned = []
    for word in words:
        clean = ""
        for ch in word:
            if ch not in string.punctuation:
                clean += ch
        if clean:
            cleaned.append(clean)

    result = {}
    for word in cleaned:
        # Inefficient: count occurrences each time
        count = 0
        for w in cleaned:
            if w == word:
                count += 1
        result[word] = count
    return result


def fibonacci(n):
    """Compute the nth Fibonacci number (0-indexed).

    fibonacci(0) = 0, fibonacci(1) = 1, fibonacci(2) = 1, ...
    """
    if n <= 0:
        return 0
    if n == 1:
        return 1
    return fibonacci(n - 1) + fibonacci(n - 2)
