import random


def get_min_max(ints):
    """
    Return a tuple(min, max) out of list of unsorted integers.

    Args:
       ints(list): list of integers containing one or more integers
    Returns:
       tuple: (min, max), or None for an empty or missing list
    """
    if not ints:
        return None

    smallest = largest = ints[0]
    for index in range(1, len(ints)):  # index loop avoids copying the list
        value = ints[index]
        if value < smallest:
            smallest = value
        elif value > largest:
            largest = value
    return smallest, largest


# Example test case of ten integers
l = [i for i in range(0, 10)]  # a list containing 0 - 9
random.shuffle(l)
print("Pass" if ((0, 9) == get_min_max(l)) else "Fail")
# Expected: Pass

print(get_min_max([4, -2, 17, 8, 0]))
# Expected: (-2, 17)

# Edge cases
print(get_min_max([]))
# Expected: None
print(get_min_max(None))
# Expected: None
print(get_min_max([5]))
# Expected: (5, 5)
print(get_min_max([-5, -1, -10]))  # all negative
# Expected: (-10, -1)
print(get_min_max([10 ** 12, -10 ** 12, 3]))  # very large magnitudes
# Expected: (-1000000000000, 1000000000000)
