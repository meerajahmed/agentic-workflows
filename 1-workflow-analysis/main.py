#!/usr/bin/env python3
"""
Implementing Agentic Workflows

1. Decompose complex tasks into agent-manageable steps
2. Implement basic agent coordination using ADK
3. Demostrate workflow pattern in action
    - Sequential workflo
    - Coordinator and validator
"""

import os
import sys
from pathlib import Path

from agents.analyzer import TaskAnalyzer

# Add project root to path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def main():
    """
    Main workflow execution - demonstrates sequential agent coordination
    """
    print("=" * 50)
    print("Agentic Workflow Analysis")

    task_description = "Plan a company retreat for 50 employees including venue, catering, and team activities"
    print(f"Task: {task_description}")

    # Task 1: Initialize agents

    project_id = os.getenv("PROJECT_ID")

    analyzer = TaskAnalyzer(project_id)

    print("Agents initialized successfully")


if __name__ == "__main__":
    main()
