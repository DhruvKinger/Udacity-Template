# Problem 1: Square Root of an Integer

## Design choices
The floor of the square root is the largest integer `r` with `r * r <= n`. Because `r * r` grows steadily as `r` grows, the answer can be found by binary search over the candidate values instead of trying them one at a time. I search the range `1` to `n // 2`, since no number above `n / 2` can be the root for `n >= 2`. Whenever `mid * mid` is smaller than `n`, I remember `mid` as the best answer so far and search higher; when it is larger, I search lower. If the loop ends without an exact match, the remembered value is the floor. I handle `0` and `1` directly, and return `None` for negative or non-integer input so that bad input is reported instead of causing a wrong answer or an error.

I used integer arithmetic only, so there are no floating-point rounding errors, even for very large numbers like `10**18`.

## Efficiency
- **Time: O(log n).** Each loop iteration halves the search range `[low, high]`, so the loop runs at most about `log2(n)` times.
- **Space: O(1).** Only a few integer variables (`low`, `high`, `mid`, `floor_root`) are used, regardless of the input size.
