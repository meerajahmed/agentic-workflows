#!/usr/bin/env python3
"""
Implementing Agentic Workflows

1. Decompose complex tasks into agent-manageable steps
2. Implement basic agent coordination using ADK
3. Demonstrate workflow pattern in action
    - Sequential workflow
    - Coordinator and validator
"""

import os
import sys
from pathlib import Path

from agents.analyzer import TaskAnalyzer
from dotenv import load_dotenv
from utils.workflow import TaskRequest

load_dotenv()

# Add project root to path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def main():
    """
    Main workflow execution - demonstrates sequential agent coordination
    """
    print("=" * 50)
    print("Agentic Workflow Analysis")

    tasks = [
        "Plan a company retreat for 50 employees including venue, catering, and team activities"
    ]

    # Task 1: Initialize agents

    project_id = os.getenv("PROJECT_ID")

    analyzer = TaskAnalyzer(project_id)

    print("Agents initialized successfully")

    # Task 2: Implement workflow coordination
    print("Processing tasks through workflow...")

    for i, task in enumerate(tasks):
        print(f"--- Task {i + 1}: {task} ---")

        # Create task request
        task_request = TaskRequest(
            description=task, complexity_level="medium", deadline_days=30
        )

        # Step 1: Break down the task into components
        print("Step 1: Analyzing task components...")
        analysis_result = analyzer.analyze_task(task_request)
        print(
            f"Analysis complete: {len(analysis_result.components)} components identified"
        )


if __name__ == "__main__":
    main()
