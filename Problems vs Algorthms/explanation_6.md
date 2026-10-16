# Problem 6: Max and Min in an Unsorted Array

## Design choices
Sorting the list and taking the first and last items would work, but sorting costs O(n log n) and the problem asks for linear time. Since every value must be looked at anyway, a single pass is enough: I start with both the smallest and largest value set to the first element, then update whichever one a new value beats. This also answers the bonus question: yes, the minimum and maximum can be found in a single traversal.

I use `elif` for the maximum check because a value that is a new minimum cannot also be a new maximum, which saves one comparison for those elements. I loop over indexes (`range(1, len(ints))`) instead of slicing with `ints[1:]`, because a slice would copy the whole list and break the constant-space goal. Empty or missing input returns `None` since there is no meaningful minimum or maximum. The built-in `min` and `max` are not used.

## Efficiency
- **Time: O(n).** The `for` loop visits each of the `n - 1` remaining elements exactly once and does at most two comparisons per element, so the total work grows in direct proportion to the list length.
- **Space: O(1).** The only extra memory is the variables `smallest`, `largest`, `index` and `value`. Because the loop uses `range` and indexing rather than a slice, no copy of the list is made, so the memory used stays the same no matter how long the list is.
