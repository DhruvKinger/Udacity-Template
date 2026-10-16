def rotated_array_search(input_list, number):
    """
    Find the index by searching in a rotated sorted array

    Args:
       input_list(array), number(int): Input array to search and the target
    Returns:
       int: Index or -1
    """
    if not input_list:
        return -1

    low, high = 0, len(input_list) - 1
    while low <= high:
        mid = (low + high) // 2
        if input_list[mid] == number:
            return mid

        if input_list[low] <= input_list[mid]:  # left half is sorted
            if input_list[low] <= number < input_list[mid]:
                high = mid - 1
            else:
                low = mid + 1
        else:  # right half is sorted
            if input_list[mid] < number <= input_list[high]:
                low = mid + 1
            else:
                high = mid - 1
    return -1


def linear_search(input_list, number):
    for index, element in enumerate(input_list):
        if element == number:
            return index
    return -1


def test_function(test_case):
    input_list = test_case[0]
    number = test_case[1]
    if linear_search(input_list, number) == rotated_array_search(input_list, number):
        print("Pass")
    else:
        print("Fail")


# Provided tests
test_function([[6, 7, 8, 9, 10, 1, 2, 3, 4], 6])
# Expected: Pass
test_function([[6, 7, 8, 9, 10, 1, 2, 3, 4], 1])
# Expected: Pass
test_function([[6, 7, 8, 1, 2, 3, 4], 8])
# Expected: Pass
test_function([[6, 7, 8, 1, 2, 3, 4], 1])
# Expected: Pass
test_function([[6, 7, 8, 1, 2, 3, 4], 10])
# Expected: Pass

# Direct results
print(rotated_array_search([4, 5, 6, 7, 0, 1, 2], 0))
# Expected: 4

# Edge cases
print(rotated_array_search([], 5))
# Expected: -1
print(rotated_array_search([5], 5))
# Expected: 0
print(rotated_array_search([1, 2, 3, 4, 5], 4))  # array that is not rotated
# Expected: 3
print(rotated_array_search([3, 4, 5, 1, 2], 99))  # value not present
# Expected: -1
