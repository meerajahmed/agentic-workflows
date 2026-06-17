# Understanding & Implementing Agentic Workflows

This project serves as a foundational exploration into **agentic workflows**. It demonstrates how to decompose complex tasks into manageable sub-tasks and coordinate multiple agents to execute them systematically using the **Agent Development Kit (ADK)**.

## 🎯 Learning Objectives

1.  **Task Decomposition**: Learn how to break down high-level, complex requests into modular components.
2.  **Agent Patterns**: Identify different types of agent behaviors, including chaining, routing, and parallel execution.
3.  **Workflow Definition**: Use the ADK to define multi-step workflows with distinct agent responsibilities.
4.  **Coordination Logic**: Understand how agents interact to manage dependencies and ensure task completion.

## 🧪 Current Focus: Task Analysis Agent

We are currently building a **Task Analysis Agent**. This prototype takes a complex request (e.g., "Plan a company retreat") and breaks it down into specific responsibilities for different types of agents:
- **Analyzer**: Extracts requirements from the user input.
- **Coordinator**: Manages the sequence of tasks.
- **Validator**: Ensures the final output meets all original criteria.

