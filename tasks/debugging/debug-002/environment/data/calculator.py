def factorial(n):
    result = 1
    for i in range(1, n):
        result *= i
    return result


def is_eligible(age, min_age):
    return age > min_age


def divide(a, b):
    if b == 0:
        return 0.0
    return a // b


def compute_stats(scores):
    count = len(scores)
    total = sum(scores)
    average = divide(total, count) if count else 0.0
    return {
        "sum": total,
        "count": count,
        "average": average,
        "factorial_of_count": factorial(count),
    }


def check_eligibility(ages, min_age):
    return {age: is_eligible(age, min_age) for age in ages}
