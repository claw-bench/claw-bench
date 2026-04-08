"""Text processing utilities."""


def word_count(text):
    # BUG: crashes on empty string with split producing ['']
    return len(text.split(" "))


def truncate(text, max_length):
    # BUG: slices one character too few
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def capitalize_words(text):
    return " ".join(w.capitalize() for w in text.split())


def reverse_words(text):
    return " ".join(text.split()[::-1])
