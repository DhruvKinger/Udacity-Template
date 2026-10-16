def rearrange_digits(input_list):
    """
    Rearranges the elements of the given array to form two numbers such that their sum is maximized.
    The numbers formed have a number of digits differing by no more than one.

    Args:
        input_list (List[int]): A list of integers in the range [0, 9]

    Returns:
        Tuple[int, int]: A tuple containing two integers (None for None input)
    """
    if input_list is None:
        return None
    if any(not isinstance(digit, int) or digit < 0 or digit > 9 for digit in input_list):
        return None  # only single digits 0-9 are valid

    # Counting sort: digits are only 0-9, so no comparison sort is needed
    digit_counts = [0] * 10
    for digit in input_list:
        digit_counts[digit] += 1

    first_digits, second_digits = [], []
    gives_to_first = True
    for digit in range(9, -1, -1):  # largest digits get the highest place values
        for _ in range(digit_counts[digit]):
            if gives_to_first:
                first_digits.append(str(digit))
            else:
                second_digits.append(str(digit))
            gives_to_first = not gives_to_first

    first = int("".join(first_digits)) if first_digits else 0
    second = int("".join(second_digits)) if second_digits else 0
    return first, second


def test_function(test_case):
    output = rearrange_digits(test_case[0])
    solution = test_case[1]
    if sum(output) == sum(solution):
        print("Pass")
    else:
        print("Fail")


# Provided tests
test_function([[1, 2, 3, 4, 5], [542, 31]])
# Expected: Pass
test_function([[4, 6, 2, 5, 9, 8], [964, 852]])
# Expected: Pass

# Direct results
print(rearrange_digits([1, 2, 3, 4, 5]))
# Expected: (531, 42)

# Edge cases
print(rearrange_digits([]))
# Expected: (0, 0)
print(rearrange_digits([7]))
# Expected: (7, 0)
print(rearrange_digits([0, 0, 0, 0]))
# Expected: (0, 0)
print(rearrange_digits([9, 9, 9, 9, 9, 9]))
# Expected: (999, 999)
print(rearrange_digits(None))
# Expected: None
print(rearrange_digits([1, 10, 3]))  # 10 is not a single digit
# Expected: None
