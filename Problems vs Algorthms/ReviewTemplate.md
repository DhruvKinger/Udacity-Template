## Rubric Point: Correctness

**Requirement:** Code produces the correct solution to the question. There are no runtime or compile-time errors, and the project specifications are met.

### Pass

**What you did well:**

The correctness checks for this submission are successful. Each of the seven programs completed the reviewed examples and returned the expected results. For instance, the square-root function handled both `9` and the large value `10 ** 18 - 1`, while the router correctly resolved its root, defined route, and not-found cases. Taken together, these results show that your implementations meet the requirements covered by the checks.

No changes are needed for correctness at this stage. One possible refinement for future work is to place demonstration calls behind a main guard; this keeps examples runnable while making the functions easier to import and test elsewhere.

**Further reading:** [Python's `unittest` documentation](https://docs.python.org/3/library/unittest.html) covers ways to build repeatable tests for function behavior.

### Fail

**What to work on:**

This rubric item is **not yet a PASS**. One or more solutions do not currently meet the required behavior, produce an incorrect result, or encounter a runtime or compile-time error. Please review the problem specifications and update the affected solution so it returns the expected result for the required examples and edge cases. Then run the project's checks again to confirm the scripts execute successfully.

Focus on correcting the behavior while preserving the constraints in each problem, such as the required algorithm, traversal count, or in-place operation. Once the affected solution works for the required cases without errors, this rubric item can be reviewed again.

**Resources:** [Project test runner](run_all_tests.py) | [Python's `unittest` documentation](https://docs.python.org/3/library/unittest.html) explains how to organize repeatable checks for function outputs. For algorithm refreshers, see [binary search](https://en.wikipedia.org/wiki/Binary_search_algorithm), [counting sort](https://en.wikipedia.org/wiki/Counting_sort), the [Dutch National Flag problem](https://en.wikipedia.org/wiki/Dutch_national_flag_problem), [tries](https://en.wikipedia.org/wiki/Trie), and [minimum and maximum algorithms](https://en.wikipedia.org/wiki/Minimum_and_maximum).

## Rubric Point: Code Style

**Requirement:** Code is neat and easy to read. Variables, functions, and methods have straightforward names, and spacing makes the code easy to follow.

### Pass

**What you did well:**

Your code is organized into clearly named functions and classes, and the spacing between logical parts makes each solution straightforward to scan. Names such as `floor_root`, `next_zero`, `next_two`, and `not_found_handler` communicate what those values are used for without requiring the reader to trace every line first.

The style requirement is met. As a small consistency improvement, consider renaming the trie instance `MyTrie` to `my_trie`, since Python convention uses lowercase with underscores for variable and instance names.

**Resource:** [PEP 8](https://peps.python.org/pep-0008/) describes Python conventions for naming and code layout.

### Fail

**What to work on:**

The code style requirement is not met yet because some names or formatting make parts of the solutions harder to understand at a glance. Choose names that describe each variable or function's purpose, use a consistent naming style, and add spacing to separate related steps. These changes will make the logic easier for another reader to follow without changing how the program works.

For Python, use `lowercase_with_underscores` for variables and functions, and `CapWords` for class names. Review the affected files for unclear abbreviations, inconsistent capitalization, and crowded blocks, then make the formatting consistent throughout.

**Resource:** [PEP 8](https://peps.python.org/pep-0008/) provides examples and recommendations for Python naming and layout.
# Learner Feedback Template
