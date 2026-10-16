# Problem 4: Dutch National Flag

## Design choices
Counting the 0s, 1s and 2s and then rewriting the array would be O(n), but it needs two traversals, which the problem does not count as a single traversal. Instead I use the classic three-pointer approach, which sorts the list in place in one pass.

The list is kept divided into regions: everything before `next_zero` is a 0, everything after `next_two` is a 2, and the `current` pointer scans the unknown values in between. When `current` sees a 0, I swap it to the front region and move both pointers forward. A 1 is already in the right region (the middle), so I just move on. A 2 is swapped to the back region, but I do not move `current` forward in that case, because the value swapped in from the back has not been looked at yet. Working in place with swaps means no second list is needed, and no built-in sort is used.

## Efficiency
- **Time: O(n).** `current` and `next_two` move toward each other, and each element is examined only once or twice by a constant number of swaps, so the list is traversed a single time.
- **Space: O(1).** The sort happens in place using only three index variables.
