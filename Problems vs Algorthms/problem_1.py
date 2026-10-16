def sqrt(number):
    """
    Calculate the floored square root of a number

    Args:
       number(int): Number to find the floored squared root
    Returns:
       int: Floored Square Root (None for negative or non-integer input)
    """
    if not isinstance(number, int) or number < 0:
        return None
    if number < 2:
        return number

    low, high = 1, number // 2
    floor_root = 1
    while low <= high:
        mid = (low + high) // 2
        square = mid * mid
        if square == number:
            return mid
        if square < number:
            floor_root = mid  # best candidate so far
            low = mid + 1
        else:
            high = mid - 1
    return floor_root


# Provided tests
print(sqrt(9))
# Expected: 3
print(sqrt(0))
# Expected: 0
print(sqrt(16))
# Expected: 4
print(sqrt(1))
# Expected: 1
print(sqrt(27))
# Expected: 5

# Edge cases
print(sqrt(-4))
# Expected: None
print(sqrt(None))
# Expected: None
print(sqrt(10 ** 18))
# Expected: 1000000000
print(sqrt(10 ** 18 - 1))
# Expected: 999999999
