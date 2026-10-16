# Problem 3: Rearrange Array Elements

## Design choices
To make the sum of two numbers as large as possible, the biggest digits must sit in the highest place values. That means sorting the digits in descending order and then dealing them out alternately: the first digit goes to the first number, the second to the second number, the third to the first number, and so on. Alternating also means the two numbers' lengths differ by no more than one digit, which the problem requires.

Python's sorting functions are not allowed, and the problem allows O(n log n), but every element is a single digit from 0 to 9. That makes a counting sort a better choice than writing my own merge sort or quicksort: I count how many times each digit appears in a list of 10 counters, then walk from 9 down to 0 and hand out the digits. This gives a sorted order in linear time, with simpler code than a comparison sort. Empty input returns `(0, 0)`, and a single digit returns `(digit, 0)`.

## Efficiency
- **Time: O(n).** One pass counts the digits, and the second pass visits each digit once while distributing it (the outer loop is always exactly 10 iterations, a constant). This is better than the O(n log n) the problem allows.
- **Space: O(n).** The two lists of digit strings together hold all `n` digits. The counting array itself is a fixed size of 10, so it is O(1).
