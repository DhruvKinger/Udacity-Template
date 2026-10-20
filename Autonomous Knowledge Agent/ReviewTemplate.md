# Autonomous Knowledge Agent
## Learner Feedback Templates

Use the feedback under the matching result for each rubric point.

---

# Data Setup and Knowledge Base Preparation

## Rubric Point: Database and Knowledge Base Infrastructure

**Requirement:** Initializes the database infrastructure, creates the required tables, populates the knowledge base with at least 10 additional support articles across different categories, completes database operations without errors, and demonstrates successful data retrieval.

### Pass

## Excellent work!

Your submission establishes the database and knowledge base as the foundation for the support agent. A well-prepared data layer gives the agents a dependable source of information and makes it possible to retrieve support content consistently instead of relying only on general responses. Including articles from different support categories also helps the system handle a wider range of customer questions.

As you refine the setup, verify that initialization can be repeated without creating duplicate or inconsistent records. Check that the required tables and fields are present, that inserts and queries complete without errors, and that articles from different categories can be retrieved correctly. Clear setup steps and a few representative retrieval examples will make this part easier for another developer to reproduce and review.

**Further reading:** [SQLite documentation](https://www.sqlite.org/docs.html)

### Fail

## Keep refining the setup

The database or knowledge base preparation still needs attention before it can reliably support the rest of the agent workflow. Start by running the initialization notebook from a clean state and checking that every required table is created with the expected fields. Then add at least 10 additional support articles across a range of categories, and verify that each record is saved correctly.

Test the basic database operations separately so it is clear whether a problem comes from setup, data insertion, or retrieval. Include simple examples showing that stored articles can be queried and returned without errors. Once these checks pass consistently, the database layer will provide a stronger foundation for implementing and testing the agents.

**Further reading:** [SQLite documentation](https://www.sqlite.org/docs.html)

---

# Multi-Agent Architecture with LangGraph

## Rubric Point: Multi-Agent Architecture Design and Documentation

**Requirement:** Provides a Markdown architecture document with a visual diagram, agent roles and responsibilities, information flow, input/output handling, decision-making, and a recognized architecture pattern.

### Pass

## Clear architecture design

Your architecture document gives the project a shared plan for how the autonomous support agent should operate. Clearly defined agent responsibilities help prevent components from duplicating work, while a visual diagram makes the relationships between agents and supporting services easier to understand. Explaining information flow, inputs, outputs, and decision points also helps connect the design to the behavior that will later be implemented in LangGraph.

To strengthen this work further, make sure the diagram and written explanation agree with each other. Identify the chosen architecture pattern, show how a ticket moves through the system, and explain what happens when routing, retrieval, or a tool call cannot complete successfully. A developer should be able to use the document to understand the intended workflow without needing to infer missing steps from the code.

**Further reading:** [LangGraph documentation](https://docs.langchain.com/oss/python/langgraph/overview)

### Fail

## Make the design easier to follow

The architecture design needs more detail before it can serve as a reliable implementation guide. Create a Markdown document that includes a readable visual diagram and a clear explanation of the system's main components. Define each agent's role and responsibilities, including what information it receives, what decisions it makes, and what output it passes to the next component.

Also explain the overall information flow, how decisions are made, and which recognized architecture pattern the design follows. Check that the written description matches the diagram and covers both the normal ticket path and important alternatives, such as missing knowledge or a failed tool operation. These additions will make the design easier to implement, review, and maintain.

**Further reading:** [LangGraph documentation](https://docs.langchain.com/oss/python/langgraph/overview)

---

## Rubric Point: LangGraph Multi-Agent Implementation

**Requirement:** Implements the documented architecture in LangGraph with at least four specialized agents, clear responsibilities, graph connections, state management, and message passing.

### Pass

## Good implementation work

Your implementation translates the architecture into a coordinated multi-agent workflow. Specialized agents can divide the support process into manageable responsibilities, while LangGraph connections define how work moves between them. State management and message passing are especially important in this type of system because each step may depend on information collected or decisions made earlier in the workflow.

As you continue refining the implementation, compare each agent's actual behavior with its documented role and confirm that the graph supports the intended paths. Check that required state fields are available when an agent runs, that updates are preserved as execution progresses, and that the workflow behaves predictably when an agent returns an unexpected result. Testing individual agents as well as the complete graph will make integration problems easier to identify.

**Further reading:** [LangGraph documentation](https://docs.langchain.com/oss/python/langgraph/overview)

### Fail

## Align implementation with the design

The multi-agent implementation needs further work to demonstrate the complete architecture in practice. Confirm that at least four specialized agents are implemented and that each has a clear responsibility rather than serving as an interchangeable step. Their graph connections should reflect the documented workflow, including how the system moves between classification, retrieval, support operations, and resolution or escalation where applicable.

Review state management and message passing from one node to the next. Check which fields each agent expects, where those fields are created or updated, and whether information remains available throughout multi-step execution. Test agents individually before running the full graph, then use representative tickets to verify that the integrated workflow follows the intended paths. This will help separate agent-level issues from graph or state-related problems.

**Further reading:** [LangGraph documentation](https://docs.langchain.com/oss/python/langgraph/overview)

---

## Rubric Point: Task Routing and Role Assignment

**Requirement:** Classifies incoming tickets and routes them to appropriate agents using ticket content and relevant metadata, with demonstrable routing decisions that follow the architecture design.

### Pass

## Effective routing logic

Your routing logic connects the incoming ticket to the appropriate part of the multi-agent workflow. Using ticket text alongside relevant metadata can make assignment more informative than relying on a single keyword or fixed route. Clear routing decisions also help explain why a ticket was sent to a particular agent and make the system easier to evaluate.

Keep testing with varied examples, including tickets with different categories, urgency levels, complexity, and incomplete metadata. Check that similar cases are routed consistently and that ambiguous or unsupported cases have a sensible fallback rather than silently entering the wrong path. A small set of sample tickets with their expected classifications and destinations will make routing behavior easier to demonstrate and debug.

**Further reading:** [LangGraph workflows and agents](https://docs.langchain.com/oss/python/langgraph/workflows-agents)

### Fail

## Improve task routing

The routing workflow needs clearer evidence that ticket characteristics drive agent assignment. Implement or complete the classification step so it considers the ticket content and relevant metadata, then use that result to select an appropriate route. The routing logic should align with the architecture document rather than introducing unexplained paths that are difficult to review.

Test the behavior with several representative tickets and show the classification result alongside the chosen destination. Include cases that differ in category or urgency, as well as an ambiguous case if relevant. If the available information is insufficient to choose a route confidently, define a safe fallback or escalation path. These checks will help demonstrate that routing is deliberate, consistent, and connected to the overall support workflow.

**Further reading:** [LangGraph workflows and agents](https://docs.langchain.com/oss/python/langgraph/workflows-agents)

---

# Knowledge Retrieval and Tool Usage

## Rubric Point: Knowledge-Based Responses and Escalation

**Requirement:** Retrieves relevant knowledge articles for different ticket types, grounds responses in article content, and uses confidence scoring and escalation logic when relevant knowledge is unavailable.

### Pass

## Well-grounded support responses

Your knowledge-retrieval workflow gives the agent a way to ground its support responses in information from the knowledge base. Retrieving relevant articles for different ticket types helps make responses more specific to the issue, while confidence scoring can provide a consistent signal for deciding whether the available evidence is sufficient. An escalation path is important because the system should not present an unsupported answer as though it were certain.

Continue checking the full chain from ticket to retrieved article to final response. Test cases where useful information is available, where several articles are similar, and where no relevant article can be found. Make sure the response reflects the retrieved content and that low-confidence or unsupported cases trigger the intended escalation behavior. These tests will help improve both the usefulness and trustworthiness of the agent's answers.

**Further reading:** [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401)

### Fail

## Strengthen retrieval and escalation

The retrieval and escalation workflow needs additional verification to show that the agent can answer from relevant support knowledge rather than producing unsupported responses. Check that different ticket types retrieve appropriate articles and that the response uses the substance of those articles. Retrieval should be evaluated by relevance, not simply by whether the system returns any result.

Add or refine confidence scoring so the workflow can distinguish a sufficiently supported answer from a case where the evidence is weak or missing. Define what happens when retrieval fails, returns irrelevant material, or does not provide enough information to resolve the issue. Demonstrate at least one successful retrieval-and-response case and one low-confidence escalation case. This will make the system's limits visible and help ensure that uncertain situations are handled responsibly.

**Further reading:** [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401)

---

## Rubric Point: Support Tools and Database Abstraction

**Requirement:** Implements at least two functional support-operation tools, abstracts database interactions, returns structured responses, validates inputs, handles errors, and integrates the tools into the agent workflow.

### Pass

## Useful tool integration

Your support tools give the agents a controlled way to carry out useful operations during ticket processing. Keeping database interactions behind an abstraction layer separates storage details from agent logic and makes the tools easier to test or modify later. Structured return values also help downstream nodes interpret the result consistently, while validation and error handling reduce the risk of malformed requests disrupting the workflow.

Continue testing each tool with normal inputs, missing or invalid fields, and cases where the database operation fails. Make sure the result clearly communicates success or failure and includes enough information for the calling agent to decide what to do next. Finally, verify that the tools are actually connected to the agent workflow and that their outputs are handled correctly during a complete ticket run.

**Further reading:** [LangChain tools documentation](https://docs.langchain.com/oss/python/langchain/tools)

### Fail

## Complete the support tools

The support-tool layer needs to demonstrate both useful functionality and predictable behavior. Implement at least two functional support-operation tools and keep direct database access behind a clear abstraction so agent logic does not need to manage low-level database details. Each tool should accept well-defined inputs and return structured results that can be interpreted by the next workflow step.

Add validation for missing, malformed, or unexpected inputs, and handle database or execution errors without causing the entire workflow to fail unpredictably. Test successful operations as well as failure cases, then demonstrate that the agents can invoke the tools at the appropriate point in ticket processing. These changes will make tool usage easier to maintain, debug, and evaluate.

**Further reading:** [LangChain tools documentation](https://docs.langchain.com/oss/python/langchain/tools)

---

# Memory and State Management

## Rubric Point: Persistent Customer Interaction History

**Requirement:** Stores customer interaction history in a persistent database, retrieves previous interactions for returning customers, and uses historical context for personalized support.

### Pass

## Good use of customer history

Your persistent interaction history helps the support agent treat a returning customer as part of an ongoing conversation rather than as a completely new case each time. Storing previous interactions and retrieving relevant details can reduce repeated questions, preserve useful context, and support responses that are better aligned with the customer's situation.

Keep checking that each interaction is linked to the correct customer identifier and that the system retrieves history only when it is relevant to the current request. Test a first-time customer and a returning customer separately, and verify that a previous interaction can influence the response when appropriate. It is also useful to confirm what happens when no history exists or a lookup fails, so the agent can continue gracefully without inventing past context.

**Further reading:** [LangGraph memory concepts](https://docs.langchain.com/oss/python/langgraph/add-memory)

### Fail

## Improve persistent memory

The persistent-memory workflow needs clearer evidence that customer history survives beyond a single interaction and is used when a customer returns. Store interaction records in a persistent database, associate them with a reliable customer identifier, and implement retrieval that can find relevant previous context for a new ticket.

Demonstrate the behavior with a simple sequence: save an interaction, start a later interaction for the same customer, retrieve the earlier information, and show how that context is made available to the agent. Also test a customer with no previous history and check that the system handles the empty result appropriately. These steps will help distinguish true persistent history from temporary state that disappears when execution ends.

**Further reading:** [LangGraph memory concepts](https://docs.langchain.com/oss/python/langgraph/add-memory)

---

## Rubric Point: Agent State, Session, and Long-Term Memory

**Requirement:** Maintains state during multi-step execution, supports inspection by thread or session identifier, uses short-term memory within a session, and stores resolved issues or customer preferences across sessions.

### Pass

## Consistent memory management

Your memory design separates information needed to complete the current workflow from context that should remain available later. Maintaining state across multiple steps allows agents to build on earlier decisions during one ticket, while session memory supports continuity throughout an active conversation. Longer-term information, such as resolved issues or customer preferences, can help future sessions avoid repeating work and provide more relevant support.

Continue verifying these scopes independently. Confirm that a workflow's state can be inspected using the appropriate thread or session identifier, that short-term context remains available within the session, and that selected long-term information can be retrieved in a later session. Make sure the system does not confuse one customer's information with another's and that stored memory is used only when it is relevant to the current task.

**Further reading:** [LangGraph memory concepts](https://docs.langchain.com/oss/python/langgraph/add-memory)

### Fail

## Clarify memory scope and state

The memory and state implementation needs to show a clear distinction between the different types of context required by the project. First, verify that state is maintained as a ticket moves through multiple workflow steps and can be inspected using the appropriate thread or session identifier. Then confirm that short-term memory preserves useful information during an active session and that long-term memory makes selected resolved issues or customer preferences available across separate sessions.

Use separate test cases to demonstrate each behavior rather than treating all stored information as one undifferentiated memory store. Check that the correct context is retrieved, that it can influence agent decisions where appropriate, and that unrelated customer information is not mixed into the interaction. These tests will make the memory design easier to understand and help identify whether a problem comes from state updates, session handling, or persistent storage.

**Further reading:** [LangGraph memory concepts](https://docs.langchain.com/oss/python/langgraph/add-memory)

---

# Integration and Testing

## Rubric Point: End-to-End Ticket Processing and Logging

**Requirement:** Demonstrates the complete ticket workflow from submission through classification, routing, knowledge retrieval, tool use, resolution or escalation, with edge-case handling and structured, searchable logs.

### Pass

## Strong end-to-end integration

Your end-to-end workflow brings the project's individual components together into a complete support process. Following a ticket from submission through classification, routing, knowledge retrieval, tool use, and final resolution or escalation helps demonstrate that the agents operate as one system rather than as isolated components. Structured logs add important visibility by recording the decisions and actions that led to an outcome.

Continue testing both ordinary tickets and cases that require escalation, including missing knowledge, invalid inputs, and tool failures. Check that logs capture the relevant steps in a consistent format and can be searched to trace a ticket's progress. A reviewer should be able to follow what happened, understand why a route or escalation was chosen, and identify where a failure occurred without having to reconstruct the run from scattered print statements.

**Further reading:** [LangGraph documentation](https://docs.langchain.com/oss/python/langgraph/overview)

### Fail

## Complete and verify the workflow

The integrated workflow needs additional testing to show that every required stage is connected and behaves as intended. Trace a ticket from the moment it is submitted through classification, routing, knowledge retrieval, any required support-tool operation, and the final resolution or escalation. Confirm that each stage receives the information it needs and passes its result to the next stage correctly.

Add handling for edge cases such as missing information, unsuccessful retrieval, invalid tool inputs, and unexpected agent results. Logging should be structured and searchable, with enough detail to identify the ticket, important decisions, routes taken, tool calls, errors, and final outcome. Demonstrate at least one normal resolution and one escalation scenario, then review the logs to confirm that a developer or reviewer can trace both runs. This will help establish that the system works as a complete workflow rather than only in isolated demonstrations.

**Further reading:** [LangGraph documentation](https://docs.langchain.com/oss/python/langgraph/overview)

---

# Overall Project Feedback

Use the feedback matching the final review result.

## Pass

### 🎉 Congratulations on passing!

Great work! 🎉 Passing this project means you have brought together several important parts of an autonomous support system: a database and knowledge base, a multi-agent architecture, ticket routing, knowledge retrieval, support tools, memory, and end-to-end processing. Coordinating these pieces is a meaningful engineering challenge because each component must do its own job while also exchanging information correctly with the rest of the workflow.

As you move forward, keep testing a broad range of ticket types and checking that responses are grounded in relevant support content. Review how the system behaves when information is incomplete, tools fail, or the available knowledge is not sufficient to resolve a request. Clear logs and traceable routing decisions will make it easier to understand why the agent took a particular action and where improvements are needed.

You can also strengthen the project by keeping the architecture document aligned with the implementation and by making test scenarios easy for someone else to reproduce. Treat passing as a strong milestone, not the end of refinement. Each round of testing and review can improve reliability, maintainability, and the overall usefulness of the agent. Keep building on this foundation! 🚀

## Fail

### 💪 Good effort — keep improving!

Thank you for the effort you have put into this project. 💪 An autonomous knowledge agent combines several connected systems, so it is normal for some parts to need more work before the complete workflow is dependable. The current result should be treated as a set of concrete areas to improve, not as a reason to stop developing the solution.

Work through the rubric one section at a time. Start with the database and knowledge base, because the agents need reliable information to do their jobs. Then check that the architecture is clearly documented and that the routing, retrieval, support tools, and memory follow that design. Once the individual components behave as expected, test them together from ticket submission through resolution or escalation. This staged approach will make it easier to isolate problems instead of trying to debug the entire system at once.

Be sure to test both normal scenarios and failure cases, and use structured logs to understand what the agents did and why. Make small, verifiable changes and rerun the relevant tests after each change. Progress in a project like this often comes from careful iteration: identify a gap, address it, and confirm that the fix works. Keep going — a systematic approach will help bring the project closer to its intended outcome. 🌱

## Ungradable — Required Files Missing

### 📂 Project files required for review

The project cannot be graded fairly because the required submission files are missing or could not be opened. Without the relevant notebooks, source files, architecture documentation, and supporting materials, it is not possible to verify how the system was implemented or whether it meets the rubric requirements.

Please review the submission instructions and upload the complete files in an accessible format. Check that the files open correctly and include the material needed to review the database setup, agent architecture, routing and retrieval logic, support tools, memory handling, and end-to-end workflow. If the project uses multiple files, make sure the required dependencies or brief setup instructions are included where needed to understand the submission.

This status reflects the availability of the materials, not a judgement about your ability or the quality of work that may have been completed. Once the files are available, the project can be reviewed against the same criteria as other submissions. Thank you for taking the time to provide the materials needed for a fair assessment. 👍
