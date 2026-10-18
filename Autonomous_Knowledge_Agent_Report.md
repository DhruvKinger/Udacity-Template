# Autonomous Knowledge Agent
## Learner Feedback Templates

Use the feedback under the matching result for each rubric point.

---

# Data Setup and Knowledge Base Preparation

## Rubric Point: Database and Knowledge Base Infrastructure

**Requirement:** Initializes the database infrastructure, creates the required tables, populates the knowledge base with at least 10 additional support articles across different categories, completes database operations without errors, and demonstrates successful data retrieval.

### Pass

## Excellent work!

Your submission establishes the required database and knowledge base foundation. The tables are available, the knowledge base includes additional articles across support categories, and database operations and retrieval work as expected.

Keep checking that the data remains consistent and that retrieval works for different article categories.

**Further reading:** [SQLite documentation](https://www.sqlite.org/docs.html)

### Fail

## Keep refining the setup

The database or knowledge base does not yet meet all requirements. Verify that the initialization notebook runs successfully, all required tables exist, and at least 10 additional support articles cover a range of categories. Check database operations and demonstrate that records can be retrieved without errors.

**Further reading:** [SQLite documentation](https://www.sqlite.org/docs.html)

---

# Multi-Agent Architecture with LangGraph

## Rubric Point: Multi-Agent Architecture Design and Documentation

**Requirement:** Provides a Markdown architecture document with a visual diagram, agent roles and responsibilities, information flow, input/output handling, decision-making, and a recognized architecture pattern.

### Pass

## Clear architecture design

Your architecture document explains the system's structure, agent responsibilities, and how information moves between components. The diagram and description make the selected architecture pattern and decision flow understandable before implementation.

Continue ensuring that the documented design is detailed enough to guide implementation and review.

**Further reading:** [LangGraph documentation](https://docs.langchain.com/oss/python/langgraph/overview)

### Fail

## Make the design easier to follow

The architecture design is incomplete or unclear. Add a Markdown document with a visual diagram, define each agent's responsibilities, explain information flow and expected inputs and outputs, and identify the architecture pattern being used.

**Further reading:** [LangGraph documentation](https://docs.langchain.com/oss/python/langgraph/overview)

---

## Rubric Point: LangGraph Multi-Agent Implementation

**Requirement:** Implements the documented architecture in LangGraph with at least four specialized agents, clear responsibilities, graph connections, state management, and message passing.

### Pass

## Good implementation work

Your implementation follows the documented architecture and includes specialized agents with defined responsibilities. The graph structure, state handling, and message passing provide a clear basis for coordinating multi-step support tasks.

Continue checking that each agent's behavior matches its documented role and that state is passed correctly through the graph.

**Further reading:** [LangGraph documentation](https://docs.langchain.com/oss/python/langgraph/overview)

### Fail

## Align implementation with the design

The multi-agent implementation does not yet meet all requirements. Check that at least four specialized agents are implemented, their responsibilities are clearly defined, and the LangGraph structure connects them correctly. Verify that state management and message passing work throughout the workflow.

**Further reading:** [LangGraph documentation](https://docs.langchain.com/oss/python/langgraph/overview)

---

## Rubric Point: Task Routing and Role Assignment

**Requirement:** Classifies incoming tickets and routes them to appropriate agents using ticket content and relevant metadata, with demonstrable routing decisions that follow the architecture design.

### Pass

## Effective routing logic

Your submission uses ticket characteristics to guide routing and agent assignment. Considering both ticket content and metadata helps direct different cases to suitable agents, and sample tickets make the routing behavior easier to verify.

Continue testing tickets with different urgency levels, complexity, and content to check that routing remains consistent.

**Further reading:** [LangGraph workflows and agents](https://docs.langchain.com/oss/python/langgraph/workflows-agents)

### Fail

## Improve task routing

The routing workflow does not yet demonstrate all required behavior. Ensure tickets are classified and routed using relevant content and metadata, and provide sample cases that show at least one clear classification-based routing decision. Confirm that the routing follows the documented architecture.

**Further reading:** [LangGraph workflows and agents](https://docs.langchain.com/oss/python/langgraph/workflows-agents)

---

# Knowledge Retrieval and Tool Usage

## Rubric Point: Knowledge-Based Responses and Escalation

**Requirement:** Retrieves relevant knowledge articles for different ticket types, grounds responses in article content, and uses confidence scoring and escalation logic when relevant knowledge is unavailable.

### Pass

## Well-grounded support responses

Your submission uses knowledge articles to support responses and includes an escalation path for cases where the available information is insufficient. Confidence scoring helps make the decision to respond or escalate more explicit.

Continue testing both successful retrieval and low-confidence cases to ensure unsupported answers are avoided.

**Further reading:** [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401)

### Fail

## Strengthen retrieval and escalation

The knowledge-based response workflow does not yet meet all requirements. Verify that relevant articles are retrieved for different ticket types, responses are grounded in article content, and confidence scoring triggers escalation when useful knowledge is not found. Demonstrate both successful retrieval and escalation scenarios.

**Further reading:** [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401)

---

## Rubric Point: Support Tools and Database Abstraction

**Requirement:** Implements at least two functional support-operation tools, abstracts database interactions, returns structured responses, validates inputs, handles errors, and integrates the tools into the agent workflow.

### Pass

## Useful tool integration

Your submission provides support-operation tools through a database abstraction layer. Structured responses, validation, and error handling help agents use these tools consistently, while workflow integration makes the operations useful within ticket processing.

Continue testing valid requests, invalid inputs, and database errors to confirm predictable behavior.

**Further reading:** [LangChain tools documentation](https://docs.langchain.com/oss/python/langchain/tools)

### Fail

## Complete the support tools

The tool implementation does not yet meet all requirements. Provide at least two functional support-operation tools, keep database access behind an abstraction layer, return structured results, and add validation and error handling. Demonstrate that agents can invoke the tools within the workflow.

**Further reading:** [LangChain tools documentation](https://docs.langchain.com/oss/python/langchain/tools)

---

# Memory and State Management

## Rubric Point: Persistent Customer Interaction History

**Requirement:** Stores customer interaction history in a persistent database, retrieves previous interactions for returning customers, and uses historical context for personalized support.

### Pass

## Good use of customer history

Your submission stores and retrieves customer interaction history so returning customers can receive context-aware support. Using relevant past interactions can reduce repetition and help tailor responses to the current issue.

Continue checking that history is associated with the correct customer and is retrieved when needed.

**Further reading:** [LangGraph memory concepts](https://docs.langchain.com/oss/python/langgraph/add-memory)

### Fail

## Improve persistent memory

The system does not yet demonstrate all required persistent-memory behavior. Ensure interaction history is stored in a database, can be retrieved for returning customers, and is used to inform responses. Include a sample interaction that demonstrates retrieval of previous context.

**Further reading:** [LangGraph memory concepts](https://docs.langchain.com/oss/python/langgraph/add-memory)

---

## Rubric Point: Agent State, Session, and Long-Term Memory

**Requirement:** Maintains state during multi-step execution, supports inspection by thread or session identifier, uses short-term memory within a session, and stores resolved issues or customer preferences across sessions.

### Pass

## Consistent memory management

Your submission distinguishes workflow state, session context, and longer-term customer information. This supports continuity during an interaction while allowing relevant resolved issues and preferences to inform future sessions.

Continue verifying that state can be inspected using the appropriate identifier and that short- and long-term memory serve their intended purposes.

**Further reading:** [LangGraph memory concepts](https://docs.langchain.com/oss/python/langgraph/add-memory)

### Fail

## Clarify memory scope and state

The workflow does not yet demonstrate all required memory types. Check that agents maintain state during multi-step execution, sessions can be inspected by the appropriate identifier, short-term context persists within a session, and long-term information is available across sessions. Ensure memory informs agent decisions.

**Further reading:** [LangGraph memory concepts](https://docs.langchain.com/oss/python/langgraph/add-memory)

---

# Integration and Testing

## Rubric Point: End-to-End Ticket Processing and Logging

**Requirement:** Demonstrates the complete ticket workflow from submission through classification, routing, knowledge retrieval, tool use, resolution or escalation, with edge-case handling and structured, searchable logs.

### Pass

## Strong end-to-end integration

Your submission demonstrates the ticket-processing workflow from initial input to resolution or escalation. Logging agent decisions, routing, tool usage, and outcomes makes the workflow easier to inspect and troubleshoot. Demonstrating both successful resolution and escalation helps show how the system handles different cases.

Continue testing edge cases and checking that logs remain structured, searchable, and useful for tracing decisions.

**Further reading:** [LangGraph documentation](https://docs.langchain.com/oss/python/langgraph/overview)

### Fail

## Complete and verify the workflow

The end-to-end workflow does not yet demonstrate all required stages. Test ticket processing from submission through classification, routing, retrieval, tool use, and final resolution or escalation. Add error and edge-case handling, and ensure structured logs capture agent decisions, routing, tool calls, and outcomes. Demonstrate both resolution and escalation scenarios.

**Further reading:** [LangGraph documentation](https://docs.langchain.com/oss/python/langgraph/overview)

---

# Overall Project Feedback

Use the feedback matching the final review result.

## Pass

### 🎉 Congratulations on passing!

Great work! 🎉 Your submission brings together the database, knowledge base, multi-agent workflow, tools, and memory needed for an autonomous support agent. Keep testing different ticket types, improving retrieval, and checking that decisions are easy to trace. These refinements will help make the system more reliable and useful. Keep it up! 🚀

## Fail

### 💪 Good effort — keep improving!

Thank you for the work you’ve put into this project. Some requirements still need attention, but you can tackle them step by step. Use the rubric feedback to check the database, architecture, routing, retrieval, tools, memory, and end-to-end workflow. Test both normal cases and escalation scenarios, and make sure the logs explain what happened. Keep going — each improvement brings the system closer to the goal! 🌱

## Ungradable — Required Files Missing

### 📂 Project files required for review

The project cannot be graded because the required files are missing or cannot be opened. Please check the submission requirements and upload the complete files in an accessible format so the work can be reviewed fairly. This is about missing materials, not your ability. Once the files are available, the project can be assessed. 👍
