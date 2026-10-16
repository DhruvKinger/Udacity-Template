# Learner Feedback Templates

Use the feedback under the matching result for each rubric point.

## Rubric Point: Correctness

**Requirement:** The solution meets the project specifications, produces the required behavior, and runs or builds without errors.

### Pass

## Excellent work!

Your submission meets the correctness requirements for this project. The expected behavior is present, the reviewed checks produce the intended results, and the program runs or builds successfully. Your work reflects a solid understanding of the requirements.

Keep this momentum by continuing to verify both typical and boundary cases as you develop or revise your solution.

**Further reading:** [A practical guide to the test pyramid](https://martinfowler.com/articles/practical-test-pyramid.html) discusses ways to build confidence in software through testing.

### Fail

## Keep refining your solution

The submission does not yet meet all of the correctness requirements. Some expected behavior may be missing or produce an unintended result, or the program may encounter an error when it runs or builds. Revisit the project specifications, revise the areas that need attention, and run the relevant checks again to confirm the solution behaves as required.

Work through the requirements systematically and verify that the changes address the underlying behavior. With those issues resolved, the submission will be ready for another review.

**Further reading:** [A practical guide to the test pyramid](https://martinfowler.com/articles/practical-test-pyramid.html) offers general guidance on testing software at different levels.

## Rubric Point: Code Style

**Requirement:** Code is neat and easy to read. Names are straightforward, and spacing and organization support readability.

### Pass

## Clear, thoughtful code

Your submission is easy to read and follow. Names communicate intent, related parts are organized clearly, and consistent formatting helps the reader understand how the solution is structured. These choices make the work easier to review and maintain.

Continue using clear names and consistent conventions as you build on this work.

**Further reading:** [Google's style guides](https://google.github.io/styleguide/) show how consistent naming and formatting can support readable code across multiple languages.

### Fail

## Make the code easier to follow

The code could be clearer and more consistent to meet this rubric point. Unclear names, uneven formatting, or organization that hides the flow can make the solution harder for another person to understand. Use descriptive names, group related logic, and apply consistent spacing and formatting throughout.

Choose conventions that fit the language and tools used in the project, then review the code for naming, indentation, spacing, and organization. These improvements can make the solution more readable without changing what it does.

**Further reading:** [Google's style guides](https://google.github.io/styleguide/) offer examples of naming and formatting conventions for several languages.

## Rubric Point: Simplicity

**Requirement:** The solution accomplishes the task without unnecessary iterations, algorithms, data structures, or other complexity.

### Pass

## Excellent work!

Your solution takes a direct approach to the task and avoids adding steps or structures that do not contribute to the required result. The implementation is focused on the stated requirements, making its logic easier to understand and maintain.

Continue choosing the simplest approach that satisfies the requirements while preserving correctness and readability.

**Further reading:** The [KISS principle](https://en.wikipedia.org/wiki/KISS_principle) is a useful reminder to keep solutions no more complex than they need to be.

### Fail

## Simplify and focus

The solution includes complexity that does not appear necessary to meet the project requirements. Extra passes, overlapping logic, or data structures that do not add needed value can make a solution harder to understand and maintain.

Review the requirements and consider whether each step and structure is essential. Remove redundant work where possible, then verify that the simpler version still produces the required behavior.

**Further reading:** The [KISS principle](https://en.wikipedia.org/wiki/KISS_principle) offers a general guide to avoiding unnecessary complexity.

## Rubric Point: Test Cases

**Requirement:** Provide at least three test inputs with expected outputs, including at least two edge cases such as empty or null inputs, or very large values.

### Pass

## 🧪 Strong test coverage!

Your submission includes enough test cases to demonstrate how the solution behaves, with expected outputs that make the results easy to verify. The examples cover both typical use and relevant edge conditions, helping show that the solution handles more than just the simplest scenario.

Keep adding tests that reflect the requirements and likely boundary conditions as your work evolves.

**Further reading:** [Boundary-value analysis](https://en.wikipedia.org/wiki/Boundary-value_analysis) explains how to choose useful tests around the limits of expected input.

### Fail

## 🔍 Add a few more checks

The current test set does not yet cover the minimum range required by this rubric. Include at least three test inputs and show the expected output for each. Make sure at least two tests cover relevant edge cases, such as empty or null input, unusually large values, or another boundary condition for the task.

These cases will make it easier to confirm the solution handles both ordinary and less typical inputs. Rerun the tests after adding them and check that the actual results match the expected outputs.

**Further reading:** [Boundary-value analysis](https://en.wikipedia.org/wiki/Boundary-value_analysis) describes a practical way to identify edge conditions worth testing.

## Rubric Point: Efficiency

**Requirement:** Provide a clear, accurate efficiency analysis and explain which parts of the code contribute to it.

### Pass

## ⚡ Efficient and well explained

Your efficiency analysis clearly describes how the solution scales and connects that explanation to the code. You identify the relevant time and space costs and explain how operations such as loops, lookups, data structures, or copies contribute to them. This makes it possible to understand not only the stated complexity, but why it fits the implementation.

Keep checking that each operation included in the analysis is accounted for, including work performed inside helper calls or while building intermediate results.

**Further reading:** [Big O notation](https://en.wikipedia.org/wiki/Big_O_notation) explains how to describe algorithm growth as input size increases.

### Fail

## 🔎 Make the efficiency analysis precise

The efficiency explanation needs more detail or correction to meet this rubric point. State the relevant time and space costs, define the input-size terms you use, and connect each cost to the operations in the code. Be sure to account for work inside loops and helper operations, as well as sorting, copying, and auxiliary storage where applicable.

Review the implementation alongside the explanation and verify that the stated bounds reflect all of the work the code performs. A clear, accurate analysis will help readers understand how the solution scales.

**Further reading:** [Big O notation](https://en.wikipedia.org/wiki/Big_O_notation) provides a general framework for describing algorithm efficiency.

## Rubric Point: Code Design

**Requirement:** The explanation discusses design choices made in the code, such as the choice of algorithm or data structure.

### Pass

## 💡 Thoughtful design choices

Your explanation describes the key decisions behind the solution and why they are appropriate for the task. This gives the reader useful context for understanding how the approach works and why it was chosen, rather than only describing what the code does.

Continue making the reasoning behind important choices clear, including any relevant trade-offs.

**Further reading:** [Algorithm design](https://en.wikipedia.org/wiki/Algorithm_design) introduces the process of selecting and developing approaches to solve problems.

### Fail

## 🧭 Explain the design behind your solution

The explanation does not yet provide enough detail about the choices that shaped the solution. Describe the main approach and explain why it fits the task. Where relevant, discuss why a particular algorithm or data structure was selected and what alternatives or trade-offs influenced that decision.

Adding this reasoning will help readers understand not just what the solution does, but why its design is suitable.

**Further reading:** [Algorithm design](https://en.wikipedia.org/wiki/Algorithm_design) provides general context for choosing approaches to computational problems.
