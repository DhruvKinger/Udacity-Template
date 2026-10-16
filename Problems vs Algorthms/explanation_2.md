# Problem 2: Search in a Rotated Sorted Array

## Design choices
A rotated sorted array is not fully sorted, but it has a useful property: if I split it at the middle, at least one of the two halves is always sorted. So I use a modified binary search. At each step I compare `input_list[low]` with `input_list[mid]` to find out which half is sorted, then check whether the target lies within the range of that sorted half. If it does, I keep that half; otherwise I discard it and keep the other one. This throws away half of the array on every step, just like a normal binary search, without needing to first find the pivot point.

Because the problem guarantees no duplicates, the comparison `input_list[low] <= input_list[mid]` reliably identifies the sorted half. Empty input returns `-1` straight away.

## Efficiency
- **Time: O(log n).** Every iteration halves the portion of the array still being searched.
- **Space: O(1).** The search is iterative and only keeps three index variables, so no extra memory grows with the input.
