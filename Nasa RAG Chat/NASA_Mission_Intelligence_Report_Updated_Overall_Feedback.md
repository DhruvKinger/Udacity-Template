# NASA Mission Intelligence: Developing a RAG-Based Chat System
## Learner Feedback Report

Use the feedback under the matching result for each rubric point. Select **Pass** or **Fail** based on the review outcome. The wording is reusable feedback for submissions assessed against these criteria; it should not be treated as proof that a particular implementation passed or failed.

---

# Embedding & Data Pipeline

## Rubric Point: Chunking Strategy

**Requirement:** Uses configurable `chunk_size` and `chunk_overlap` values, keeps chunks within the configured size, and applies overlap consistently between consecutive chunks.

### Pass

## Excellent work! ✅

Your submission meets the chunking requirements. The configuration is clear, and the chunking process follows the expected size and overlap rules. This helps preserve useful context while preparing documents for retrieval.

Keep testing different document lengths and boundary cases to make sure the behavior stays consistent.

**Further reading:** [A practical guide to the test pyramid](https://martinfowler.com/articles/practical-test-pyramid.html)


### Fail

## A little more refinement needed 🔧

The chunking implementation does not yet meet all the requirements. Check that chunk size and overlap can be configured, that no chunk exceeds the specified limit, and that overlap is applied consistently.

Try short, long, and boundary-length documents, then rerun the checks to confirm the behavior.


---

**Further reading:** [A practical guide to the test pyramid](https://martinfowler.com/articles/practical-test-pyramid.html)

## Rubric Point: Embedding Creation and Metadata

**Requirement:** Uses an OpenAI embedding model, stores source/filepath and mission metadata, and handles existing documents using the specified update mode.

### Pass

## Good work! ✅

Your submission follows the expected embedding and metadata workflow. Keeping source information and relevant labels with each chunk supports traceability and makes filtered retrieval possible. The update behavior also helps manage documents that have already been processed.

Continue checking that metadata remains attached to the correct chunks and that each update mode behaves as expected.

**Further reading:** [Google's style guides](https://google.github.io/styleguide/)


### Fail

## Check the embedding pipeline 🔍

The embedding and metadata workflow is missing one or more required behaviors. Verify that each chunk is embedded, that the required source and mission metadata is stored, and that existing documents are handled according to the selected update mode.

Test both new and previously processed documents to identify where the pipeline needs attention.


---

**Further reading:** [Google's style guides](https://google.github.io/styleguide/)

## Rubric Point: ChromaDB Persistence and Statistics

**Requirement:** Stores embeddings in the configured ChromaDB directory and collection, and provides a statistics mode that reports collection size and at least one aggregate.

### Pass

## Nicely done! ✅

Your submission provides a way to persist and inspect the stored collection. Configurable storage locations and collection names make the workflow easier to manage, while statistics help confirm what has been ingested.

Keep verifying that the reported figures match the actual collection contents.

**Further reading:** [A practical guide to the test pyramid](https://martinfowler.com/articles/practical-test-pyramid.html)


### Fail

## Make storage easier to verify 🛠️

The persistence or statistics behavior does not yet meet all requirements. Check that the configured directory and collection name are used, that data persists between runs, and that the statistics mode reports the required information.

Run the workflow more than once and compare the displayed statistics with the stored collection.

---

**Further reading:** [A practical guide to the test pyramid](https://martinfowler.com/articles/practical-test-pyramid.html)

# Retrieval & LLM Integration

## Rubric Point: Semantic Retrieval from ChromaDB

**Requirement:** Queries ChromaDB using the question embedding, supports configurable top-k results, and applies mission filtering when selected.

### Pass

## Strong retrieval work! ✅

Your submission follows the expected semantic retrieval workflow. Configurable result limits provide flexibility, and metadata filtering can help keep results relevant to the selected scope.

Continue testing different questions, result limits, and filter choices to check that retrieval returns appropriate material.

**Further reading:** [Chroma documentation](https://docs.trychroma.com/)


### Fail

## Improve retrieval reliability 🔎

The retrieval workflow does not yet meet all requirements. Confirm that the question is embedded and used for a similarity query, that the result count can be configured, and that optional mission filtering is applied correctly.

Test questions with clear matches, weak matches, and different mission filters to find the cause of unexpected results.


---

**Further reading:** [Chroma documentation](https://docs.trychroma.com/)

## Rubric Point: Context Construction for the LLM

**Requirement:** Combines retrieved chunks into a clearly separated context with source attribution and avoids repeated snippets through deduplication or score-based ordering.

### Pass

## Clear and organized context! ✅

Your submission prepares retrieved information in a structured way for the language model. Clear separators and source attribution make the context easier to interpret, while ordering or deduplication helps reduce unnecessary repetition.

Keep checking that useful evidence is retained and sources remain identifiable.

**Further reading:** [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401)


### Fail

## Make the context clearer 🧩

The context construction does not yet meet all requirements. Organize retrieved passages with clear separators, preserve source attribution, and remove duplicate snippets or order results appropriately by relevance.

Review the final context sent to the model to ensure it is readable and contains the most useful evidence.


---

**Further reading:** [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401)

## Rubric Point: System Prompt and Conversation Management

**Requirement:** Defines the assistant's role and source-citation behavior, maintains role/content conversation history, and includes only necessary context in each model call.

### Pass

## Good conversation design! ✅

Your submission defines the assistant's expected behavior and manages conversation context in a structured way. Relevant history can support multi-turn interactions, while limiting unnecessary context helps keep requests focused.

Continue testing follow-up questions to ensure history is preserved correctly and source instructions remain effective.

**Further reading:** [OpenAI API documentation](https://platform.openai.com/docs/)


### Fail

## Strengthen conversation handling 📝

The prompt or conversation management does not yet meet all requirements. Review the assistant's role and citation instructions, store conversation turns consistently, and ensure each call includes the relevant history without unnecessary content.

Test a series of related questions to check whether context is carried forward correctly.


---

**Further reading:** [OpenAI API documentation](https://platform.openai.com/docs/)

## Rubric Point: Answers Grounded in Retrieved Context

**Requirement:** Sends retrieved context and the user query to the LLM, and instructs it to rely on that context and state uncertainty when evidence is insufficient.

### Pass

## Well done! ✅

Your submission connects retrieval with answer generation and sets clear expectations for evidence-based responses. Instructing the model to acknowledge missing information helps reduce unsupported claims.

Continue testing questions with complete, partial, and missing evidence to make sure answers reflect the available context.

**Further reading:** [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401)


### Fail

## Keep answers tied to evidence 🔍

The answer-generation workflow does not yet meet all requirements. Check that the retrieved context and user query reach the model, and make the instructions explicit about using the supplied evidence and acknowledging uncertainty.

Test questions that cannot be answered from the available documents and verify that the system does not invent unsupported details.

---

**Further reading:** [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401)

# Real-Time Evaluation

## Rubric Point: Integration of RAGAS Metrics

**Requirement:** Computes Response Relevancy and Faithfulness for each answer and supports any additional documented metrics.

### Pass

## Great evaluation coverage! ✅

Your submission includes the required evaluation metrics. Assessing relevance and faithfulness provides useful insight into whether answers address the question and remain supported by context.

Keep the metric configuration and dependencies documented so that results can be reproduced and interpreted correctly.

**Further reading:** [Ragas documentation](https://docs.ragas.io/)


### Fail

## Complete the evaluation metrics 📊

The evaluation workflow does not yet calculate all required metrics. Verify that Response Relevancy and Faithfulness are computed for each answer, and document any additional metrics that are supported.

Run the evaluator on representative examples and confirm that metric names and values are returned correctly.


---

**Further reading:** [Ragas documentation](https://docs.ragas.io/)

## Rubric Point: Evaluation of a Question, Context, and Answer Triple

**Requirement:** Accepts a question, retrieved context, and model answer; returns structured metric names and values; and handles empty or malformed input without crashing.

### Pass

## Clear evaluation interface! ✅

Your submission provides a structured way to evaluate an answer against its question and context. Clear output and predictable input validation make the evaluator easier to use in both individual and batch workflows.

Continue testing valid inputs as well as empty, incomplete, and malformed records.

**Further reading:** [Purdue OWL – General Writing](https://owl.purdue.edu/owl/general_writing/index.html)


### Fail

## Improve input validation ⚙️

The evaluation interface does not yet meet all requirements. Confirm that it accepts the question, context, and answer, returns structured metric results, and reports invalid inputs clearly instead of crashing.

Test missing fields, empty values, and malformed records, then verify that the error messages are understandable.


---

**Further reading:** [Purdue OWL – General Writing](https://owl.purdue.edu/owl/general_writing/index.html)

## Rubric Point: Batch Evaluation Using a Test Set

**Requirement:** Loads a test set, evaluates each example end-to-end, reports per-question results, and calculates aggregate metric values.

### Pass

## Solid evaluation workflow! ✅

Your submission supports evaluation across a test set and provides both individual and aggregate results. This makes it easier to inspect specific examples and understand overall performance.

Keep checking that each test question is represented in the output and that aggregate values are calculated from valid results.

**Further reading:** [Ragas documentation](https://docs.ragas.io/)


### Fail

## Make batch results complete 📋

The batch evaluation workflow does not yet meet all requirements. Verify that the test set loads correctly, each example is evaluated, per-question results are reported, and aggregate values are calculated for each metric.

Test a small dataset first and check how the workflow handles invalid examples or evaluation errors.

---

**Further reading:** [Ragas documentation](https://docs.ragas.io/)

## Rubric Point: Evaluation Dataset

**Requirement:** Includes a valid evaluation dataset with at least five relevant questions spanning multiple categories, and references it in the evaluation flow or README.

### Pass

## Useful test coverage! ✅

Your submission includes a dataset intended to cover a range of relevant questions. Varied examples help evaluate more than one type of interaction, while clear documentation makes the evaluation easier to reproduce.

Keep the dataset valid, representative, and updated as the system evolves.

**Further reading:** [Boundary-value analysis](https://en.wikipedia.org/wiki/Boundary-value_analysis)


### Fail

## Expand and verify the dataset 🧪

The evaluation dataset does not yet meet all requirements. Ensure that the required file exists, contains at least five relevant questions across the specified categories, loads without errors, and is referenced by the evaluation workflow or README.

Validate the file format and run the evaluation process using the dataset to confirm it is usable.


---

**Further reading:** [Boundary-value analysis](https://en.wikipedia.org/wiki/Boundary-value_analysis)

# Overall Project Feedback

Use **only one** overall result after reviewing all rubric points and confirming that the required project files are available. Select the outcome that best reflects the submission as a whole.

## Overall Pass

### 🎉 Congratulations on passing!

Excellent work! 🎉 Your submission has met the required criteria, showing that you have brought the main parts of the RAG-based mission intelligence system together successfully. Completing a project like this takes planning, careful implementation, and testing across several connected components. Take a moment to recognise the progress you have made.

As you continue improving the project, keep these points in mind:

- **Maintain the data pipeline:** Keep chunking settings consistent, preserve source and mission metadata, and verify that newly added or updated documents are processed correctly.
- **Check retrieval quality:** Test a range of questions and mission filters. Confirm that the retrieved passages are relevant and that the context supplied to the language model contains useful evidence with clear source attribution.
- **Keep answers grounded:** Make sure generated responses use the retrieved context and acknowledge when the available documents do not contain enough information. Avoid treating a fluent answer as proof that it is factually supported.
- **Use evaluation to guide improvements:** Review Response Relevancy and Faithfulness results, inspect individual examples as well as aggregate scores, and investigate unexpected or weak results rather than relying on a single overall metric.
- **Preserve reproducibility:** Keep the dataset, configuration, dependencies, and evaluation instructions clear so that another person can run the workflow and understand the results.

Passing is an important milestone, but it is also a foundation for further learning. Continue experimenting with more challenging questions, edge cases, and incomplete evidence. Each round of testing can help make the system more reliable, easier to maintain, and more useful to its users. Keep it up — you have built a solid base to develop further! 🚀

## Overall Fail

### 💪 Good effort — keep improving!

Thank you for the effort you have put into this project. 💪 The submission does not meet every required criterion yet, but that does not mean the work has been wasted. A RAG-based system combines several stages, and a problem in one stage can affect the behavior of the stages that follow it. The best approach is to use the rubric feedback as a practical checklist and work through the gaps in a clear order.

Here is a suggested way to organise the next round of improvements:

- **Start with the data pipeline:** Confirm that chunk size and overlap are configurable and applied correctly. Check that embeddings, source information, mission metadata, ChromaDB persistence, and collection statistics behave as required.
- **Verify retrieval before changing generation:** Test whether the question embedding retrieves suitable passages, whether the top-k setting works, and whether mission filtering is applied when selected. Inspect the actual retrieved chunks to identify problems.
- **Review context and prompts:** Ensure retrieved chunks are clearly separated, sources are identifiable, repeated snippets are handled, and the system prompt explains the assistant's role and citation expectations.
- **Check evidence-based responses:** Confirm that both the user query and retrieved context reach the language model. Test questions with strong evidence, partial evidence, and no supporting evidence to see whether the system expresses uncertainty instead of inventing details.
- **Run evaluation on representative examples:** Check that the required RAGAS metrics are calculated, the evaluator accepts a question-context-answer triple, and invalid or empty input is handled without crashing.
- **Validate batch evaluation and the dataset:** Make sure each test example is processed, per-question results are reported, aggregate metrics are calculated correctly, and the dataset contains at least five relevant questions across multiple categories and is referenced in the workflow or README.
- **Retest after each change:** Run the relevant checks again and keep track of which requirements are now satisfied. This makes it easier to isolate regressions and demonstrate that a fix has worked.

You do not need to resolve every issue at once. Prioritise the missing requirements, test each change, and then run the complete workflow to check that the components work together. The goal is not simply to make the code run, but to make retrieval, generated answers, and evaluation results dependable and understandable. Keep going — steady, well-tested improvements can bring the project closer to the expected standard. 🌱

## Overall Ungradable — Required Files Missing

### 📂 Project files required for review

The submission cannot be graded fairly because one or more required project files are missing, inaccessible, or cannot be opened. Without the materials needed to inspect the implementation and run or verify the relevant workflow, there is not enough evidence to decide whether the rubric requirements have been met. This outcome is about the availability of the submission materials; it is **not** a judgment of your ability or the quality of work that could not be reviewed.

Before requesting another review, use this checklist:

- **Check the submission requirements:** Confirm which notebooks, source files, configuration files, datasets, and documentation are required for this project.
- **Upload the complete project materials:** Include the files needed to understand the data pipeline, retrieval and generation workflow, and evaluation process.
- **Verify file accessibility:** Make sure the files open correctly and are provided in a supported format. Avoid submitting broken links or empty files.
- **Include the evaluation resources:** If the rubric requires a test dataset or README reference, make sure those resources are included and their locations are clear.
- **Review the folder structure:** Use understandable file and folder names so the reviewer can identify the relevant materials without guessing where they are stored.
- **Check before resubmitting:** Open the uploaded files once more and confirm that the required content is present.

Once the required files are available, the project can be reviewed against the rubric and you can receive feedback based on the work itself. Please treat this as a fixable submission issue: gather the missing materials, check that they are accessible, and submit again for review. 👍
