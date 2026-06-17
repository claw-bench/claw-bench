def find_duplicates(items):
    duplicates = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if items[i] == items[j] and items[i] not in duplicates:
                duplicates.append(items[i])
    return sorted(duplicates)


def find_common_elements(list_a, list_b):
    common = []
    for a in list_a:
        for b in list_b:
            if a == b and a not in common:
                common.append(a)
    return sorted(common)


def count_unique(items):
    unique = []
    for item in items:
        found = False
        for existing in unique:
            if item == existing:
                found = True
                break
        if not found:
            unique.append(item)
    return len(unique)


def has_pair_with_sum(numbers, target):
    for i in range(len(numbers)):
        for j in range(i + 1, len(numbers)):
            if numbers[i] + numbers[j] == target:
                return True
    return False
