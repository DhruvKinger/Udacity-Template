def sort_012(input_list):
    """
    Given an input array consisting on only 0, 1, and 2, sort the array in a single traversal.

    Args:
       input_list(list): List to be sorted
    Returns:
       list: The same list, sorted in place
    """
    next_zero = 0                      # everything before this index is 0
    next_two = len(input_list) - 1     # everything after this index is 2
    current = 0                        # scans the still-unsorted middle

    while current <= next_two:
        if input_list[current] == 0:
            input_list[current], input_list[next_zero] = input_list[next_zero], input_list[current]
            next_zero += 1
            current += 1
        elif input_list[current] == 1:
            current += 1
        else:
            input_list[current], input_list[next_two] = input_list[next_two], input_list[current]
            next_two -= 1              # swapped-in value is unchecked, so don't advance current
    return input_list


def test_function(test_case):
    sorted_array = sort_012(test_case)
    print(sorted_array)
    if sorted_array == sorted(test_case):
        print("Pass")
    else:
        print("Fail")


# Provided tests
test_function([0, 0, 2, 2, 2, 1, 1, 1, 2, 0, 2])
# Expected: [0, 0, 0, 1, 1, 1, 2, 2, 2, 2, 2]
# Expected: Pass
test_function([2, 1, 2, 0, 0, 2, 1, 0, 1, 0, 0, 2, 2, 2, 1, 2, 0, 0, 0, 2, 1, 0, 2, 0, 0, 1])
# Expected: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2]
# Expected: Pass
test_function([0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2])  # already sorted
# Expected: [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2]
# Expected: Pass

# Edge cases
test_function([])
# Expected: []
# Expected: Pass
test_function([1])
# Expected: [1]
# Expected: Pass
test_function([2, 2, 2])  # all the same value
# Expected: [2, 2, 2]
# Expected: Pass
test_function([2, 1, 0])  # reverse order
# Expected: [0, 1, 2]
# Expected: Pass
